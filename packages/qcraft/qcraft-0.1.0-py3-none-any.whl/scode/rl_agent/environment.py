import numpy as np
import gymnasium as gym
from gymnasium import spaces
import stim
import pymatching
from scode.reward_engine.reward_engine import MultiObjectiveRewardEngine

class RLEnvironment(gym.Env):
    """
    RL Environment for surface code generation.
    Pass the full dict returned by the graph transformer as transformed_layout, not just the mapping.
    This ensures stabilizer_map and other info are available for reward calculation.
    """
    def __init__(self, transformed_layout: dict, hardware_specs: dict, error_profile: dict, config: dict):
        # Static config
        self.hardware_specs = hardware_specs
        self.error_profile = error_profile
        self.config = config
        self.transformed_layout = transformed_layout

        # Reward engine
        self.reward_engine = MultiObjectiveRewardEngine(config)

        # LER computation parameters from config
        rl_agent_cfg = config.get('rl_agent', {})
        self.ler_frequency = rl_agent_cfg.get('ler_frequency', 1)  # Compute LER every N steps (default: 1)
        self.ler_num_trials = rl_agent_cfg.get('ler_num_trials', 100)  # Number of MC trials per LER estimate
        self.ler_noise_prob = rl_agent_cfg.get('ler_noise_prob', 0.001)  # Noise probability for LER estimation
        self._last_ler = 0.0
        self._last_ler_step = -1

        # Qubit info
        self.qubits = np.array(sorted([int(q) for q in hardware_specs['qubit_connectivity'].keys()]), dtype=np.int32)
        self.n_qubits = len(self.qubits)
        self.native_gates = hardware_specs['native_gates']
        self.max_swaps = config.get('actions', {}).get('max_swaps_per_episode', 10)
        self.max_steps = config.get('rl_agent', {}).get('max_steps_per_episode', 200)
        self.enabled_types = config.get('actions', {}).get('enabled_types', ['swap', 'rewire', 'assign_gate'])

        # Precompute static adjacency
        self.adj_flat = self._build_adjacency_flat(hardware_specs['qubit_connectivity'])

        # State arrays (mutable per episode)
        self.gates = np.zeros(self.n_qubits, dtype=np.int32)
        self.swaps = 0
        self.step_count = 0

        # Action space
        self._actions = self._generate_action_list()
        self.action_space = spaces.Discrete(len(self._actions))

        # Observation space
        obs_dim = self.n_qubits * self.n_qubits + self.n_qubits * 2 + 2
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(obs_dim,), dtype=np.float32)

    def _build_adjacency_flat(self, connectivity):
        adj = np.zeros((self.n_qubits, self.n_qubits), dtype=np.int8)
        for i, q1 in enumerate(self.qubits):
            for j, q2 in enumerate(self.qubits):
                if str(q2) in connectivity.get(str(q1), []):
                    adj[i, j] = 1
        return adj.flatten()

    def _generate_action_list(self):
        actions = []
        for t in self.enabled_types:
            if t == 'swap':
                for i in range(self.n_qubits):
                    for j in range(i+1, self.n_qubits):
                        actions.append({'type': 'swap', 'q1': self.qubits[i], 'q2': self.qubits[j]})
            elif t == 'rewire':
                for i in range(self.n_qubits):
                    for j in range(self.n_qubits):
                        if i != j:
                            actions.append({'type': 'rewire', 'source': self.qubits[i], 'target': self.qubits[j]})
            elif t == 'assign_gate':
                for idx, q in enumerate(self.qubits):
                    for gate in self.native_gates:
                        actions.append({'type': 'assign_gate', 'qubit': q, 'gate': gate})
        return actions if actions else [{}]

    def reset(self, *, seed=None, options=None):
        # Reset state arrays in-place
        self.gates.fill(0)
        self.swaps = 0
        self.step_count = 0
        # (If you have other state, reset here)
        return self._get_obs(), {}

    def step(self, action_idx):
        action = self._actions[action_idx]
        action_type = action.get('type')
        terminated = False
        truncated = False
        info = {}

        if action_type not in self.enabled_types:
            terminated = True
            info['error'] = f'Invalid action type: {action_type}. Enabled types: {self.enabled_types}'
            return self._get_obs(), 0.0, terminated, truncated, info

        if action_type == 'swap':
            if self.swaps >= self.max_swaps:
                terminated = True
                info['error'] = f'Maximum swaps ({self.max_swaps}) exceeded'
            else:
                q1 = np.where(self.qubits == action['q1'])[0][0]
                q2 = np.where(self.qubits == action['q2'])[0][0]
                self.gates[q1], self.gates[q2] = self.gates[q2], self.gates[q1]
                self.swaps += 1
        elif action_type == 'rewire':
            # (Implement rewire logic if needed, using arrays)
            pass
        elif action_type == 'assign_gate':
            qidx = np.where(self.qubits == action['qubit'])[0][0]
            self.gates[qidx] = self.native_gates.index(action['gate'])

        self.step_count += 1
        done = self.step_count >= self.max_steps or terminated
        # Compute circuit metrics (including stabilizer_score, logical_error_rate)
        circuit_metrics = self._compute_circuit_metrics(done)
        # Check for hardware overflow penalty
        if circuit_metrics.get('hardware_overflow_penalty', False):
            reward = -1e6
            done = True
            info['hardware_overflow_penalty'] = True
            info['reward'] = reward
            return self._get_obs(), reward, done, truncated, info
        # Use reward engine for multi-objective reward
        reward_weights = self.config.get('curriculum', {}).get('phases', [{}])[0].get('reward_weights', {
            'alpha1': 1.0, 'alpha2': 1.0, 'beta': 1.0, 'gamma': 1.0, 'delta': 1.0, 'epsilon': 1.0, 'zeta': 1.0
        })
        reward, breakdown = self.reward_engine.compute_reward(
            hardware_graph=self.hardware_specs,
            circuit_metrics=circuit_metrics,
            stabilizer_mapping={},
            reward_weights=reward_weights
        )
        # Add metrics to info for logging/progress bar
        info['swaps'] = self.swaps
        info['step_count'] = self.step_count
        info['reward'] = reward
        info['stabilizer_score'] = circuit_metrics.get('stabilizer_score', 0.0)
        info['logical_error_rate'] = circuit_metrics.get('logical_error_rate', 0.0)
        info['weighted_single_qubit_gate_error'] = circuit_metrics.get('weighted_single_qubit_gate_error', 0.0)
        info['weighted_two_qubit_gate_error'] = circuit_metrics.get('weighted_two_qubit_gate_error', 0.0)
        return self._get_obs(), reward, done, truncated, info

    def _get_obs(self):
        # Build observation as a single NumPy array
        error_rates = []
        for q in self.qubits:
            # Try string key, then int key, then default
            if str(q) in self.error_profile:
                error_rates.append(self.error_profile[str(q)].get('readout_error', 0.0))
            elif int(q) in self.error_profile:
                error_rates.append(self.error_profile[int(q)].get('readout_error', 0.0))
            else:
                error_rates.append(0.0)
        error_rates = np.array(error_rates, dtype=np.float32)
        obs = np.concatenate([
            self.adj_flat,
            error_rates,
            self.gates.astype(np.float32),
            np.array([self.swaps, self.step_count], dtype=np.float32)
        ])
        return obs

    def _compute_circuit_metrics(self, end_of_episode=False):
        # Compute the number of qubits required by the current code (data + ancilla)
        required_qubits = 0
        code_qubits = set()
        used_gates = set()
        if 'surface_code' in self.transformed_layout:
            code = self.transformed_layout['surface_code']
            if hasattr(code, 'qubit_layout'):
                code_qubits = set(code.qubit_layout.keys())
            elif isinstance(code, dict) and 'qubit_layout' in code:
                code_qubits = set(code['qubit_layout'].keys())
            # Try to infer used gates from logical_operators and stabilizer_map (if available)
            if hasattr(code, 'logical_operators') and hasattr(code, 'stabilizer_map'):
                # This is a simplification: assume all native gates are used for each logical/stabilizer op
                used_gates = set(self.native_gates)
            elif isinstance(code, dict):
                used_gates = set(self.native_gates)
        else:
            code_qubits = set(self.qubits)
            used_gates = set(self.native_gates)
        required_qubits = len(code_qubits)
        num_physical_qubits = self.n_qubits
        # Weighted qubit error: sum readout_error for all code qubits
        weighted_qubit_error = 0.0
        for q in code_qubits:
            q_str = str(q)
            weighted_qubit_error += self.error_profile.get(q_str, {}).get('readout_error', 0)
        # Weighted gate error: sum error rates for all used gates
        weighted_gate_error = 0.0
        weighted_single_qubit_gate_error = 0.0
        weighted_two_qubit_gate_error = 0.0
        gate_error_rates = self.hardware_specs.get('gate_error_rates', {})
        # Define single- and two-qubit gates (IBM: 'cx' is two-qubit, rest are single)
        single_qubit_gates = {'id', 'rz', 'sx', 'x'}
        two_qubit_gates = {'cx'}
        for gate in used_gates:
            err = gate_error_rates.get(gate, 0)
            weighted_gate_error += err
            if gate in single_qubit_gates:
                weighted_single_qubit_gate_error += err
            elif gate in two_qubit_gates:
                weighted_two_qubit_gate_error += err
        total_swap_gates = self.swaps
        circuit_depth = self.step_count
        stabilizer_score = np.count_nonzero(self.gates) / num_physical_qubits if num_physical_qubits > 0 else 0.0
        logical_error_rate = self._last_ler
        if end_of_episode and (self.step_count % self.ler_frequency == 0):
            try:
                logical_error_rate = self.estimate_logical_error_rate({}, num_trials=self.ler_num_trials, noise_prob=self.ler_noise_prob)
                self._last_ler = logical_error_rate
                self._last_ler_step = self.step_count
            except Exception:
                logical_error_rate = self._last_ler
        # Penalize if required qubits > available
        if required_qubits > num_physical_qubits:
            return {
                'weighted_gate_error': weighted_gate_error,
                'weighted_single_qubit_gate_error': weighted_single_qubit_gate_error,
                'weighted_two_qubit_gate_error': weighted_two_qubit_gate_error,
                'weighted_qubit_error': weighted_qubit_error,
                'total_swap_gates': total_swap_gates,
                'circuit_depth': circuit_depth,
                'logical_error_rate': logical_error_rate,
                'num_physical_qubits': required_qubits,  # for legacy
                'stabilizer_score': stabilizer_score,
                'hardware_overflow_penalty': True
            }
        return {
            'weighted_gate_error': weighted_gate_error,
            'weighted_single_qubit_gate_error': weighted_single_qubit_gate_error,
            'weighted_two_qubit_gate_error': weighted_two_qubit_gate_error,
            'weighted_qubit_error': weighted_qubit_error,
            'total_swap_gates': total_swap_gates,
            'circuit_depth': circuit_depth,
            'logical_error_rate': logical_error_rate,
            'num_physical_qubits': required_qubits,  # for legacy
            'stabilizer_score': stabilizer_score
        }

    def estimate_logical_error_rate(self, state, num_trials=100, noise_prob=0.001):
        # print(f"[DEBUG] estimate_logical_error_rate called with num_trials={num_trials}")
        circuit = self.build_surface_code_circuit(state, noise_prob=noise_prob)
        dem = circuit.detector_error_model(decompose_errors=True)
        matching = pymatching.Matching(dem)
        num_logical_errors = 0
        sampler = circuit.compile_detector_sampler()
        samples = sampler.sample(shots=num_trials, append_observables=True)
        for sample in samples:
            logical = sample[-1]
            syndrome = sample[:-1]
            correction = matching.decode(syndrome)
            if correction != logical:
                num_logical_errors += 1
        return num_logical_errors / num_trials

    def build_surface_code_circuit(self, state, noise_prob=0.001):
        circuit = stim.Circuit()
        qubits = sorted([int(q) for q in self.hardware_specs.get('qubit_connectivity', {}).keys()])
        # Initialize all qubits in a single operation
        circuit.append_operation("R", qubits)
        # Add batch stabilizer measurements if possible
        if 'stabilizer_map' in state:
            if state['stabilizer_map'].get('X'):
                circuit.append_operation("MX", state['stabilizer_map']['X'])
            if state['stabilizer_map'].get('Z'):
                circuit.append_operation("MZ", state['stabilizer_map']['Z'])
        # Add noise in batch
        circuit.append_operation("DEPOLARIZE1", qubits, noise_prob)
        # Logical measurement: use logical operator if available, else last qubit
        logical_qubits = None
        if 'logical_operators' in state and state['logical_operators'].get('Z'):
            logical_qubits = state['logical_operators']['Z']
        if logical_qubits:
            circuit.append_operation("M", logical_qubits)
            import stim as _stim
            for i in range(len(logical_qubits)):
                circuit.append_operation("OBSERVABLE_INCLUDE", [_stim.target_rec(-1 - i)])
        else:
            circuit.append_operation("M", [qubits[-1]])
            import stim as _stim
            circuit.append_operation("OBSERVABLE_INCLUDE", [_stim.target_rec(-1)])
        return circuit 