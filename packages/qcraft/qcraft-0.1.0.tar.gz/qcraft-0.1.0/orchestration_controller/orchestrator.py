import os
import yaml
import json
import uuid
from typing import Dict, Any, List, Optional
from configuration_management.config_manager import ConfigManager
from hardware_abstraction.device_abstraction import DeviceAbstraction
from circuit_optimization.api import CircuitOptimizationAPI
from scode.api import SurfaceCodeAPI
# from code_switcher.api import CodeSwitcherAPI  # Placeholder for real code switcher
# from execution_simulation.api import ExecutionSimulatorAPI  # Placeholder for real execution
import importlib.resources

class OrchestratorController:
    """
    Orchestration/Controller Module for managing the workflow of quantum circuit design, optimization, mapping, code switching, and execution.
    All configuration is YAML/JSON-driven and APIs are pure Python for frontend/backend integration.
    """
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = ConfigManager.config_registry.get('workflow_policy')
        self.config_path = config_path
        self.config = self._load_config(config_path)
        # Try to get workflow_policy from config, or use the whole config if not nested
        if 'workflow_policy' in self.config:
            self.current_policy = self.config['workflow_policy']
        else:
            self.current_policy = self.config
        self.optimizer_api = CircuitOptimizationAPI()
        self.surface_code_api = SurfaceCodeAPI()
        # self.code_switcher_api = CodeSwitcherAPI()  # Uncomment when available
        # self.execution_api = ExecutionSimulatorAPI()  # Uncomment when available

    def _load_config(self, path: str) -> dict:
        fname = os.path.basename(path)
        try:
            with importlib.resources.open_text('configs', fname) as f:
                if fname.endswith('.yaml') or fname.endswith('.yml'):
                    return yaml.safe_load(f)
                elif fname.endswith('.json'):
                    return json.load(f)
        except (FileNotFoundError, ModuleNotFoundError):
            if path.endswith('.yaml') or path.endswith('.yml'):
                with open(path, 'r') as f:
                    return yaml.safe_load(f)
            elif path.endswith('.json'):
                with open(path, 'r') as f:
                    return json.load(f)
        raise ValueError("Unsupported config file format.")

    def run_workflow(self, circuit: dict, user_config: Optional[dict] = None, progress_callback=None) -> dict:
        """
        Execute the full workflow: design, optimize, map, code switch, build, and execute the circuit. Returns a summary/result.
        """
        workflow_id = str(uuid.uuid4())
        self.workflow_status[workflow_id] = {'status': 'running', 'steps': []}
        try:
            if progress_callback:
                progress_callback("Loading device info...", 0.05)
            # 1. Load device info
            hardware_json_path = ConfigManager.config_registry.get('hardware', 'configs/hardware.json')
            device_info = DeviceAbstraction.load_selected_device(hardware_json_path)
            self.workflow_status[workflow_id]['steps'].append('device_loaded')

            # 2. Decide surface code
            if progress_callback:
                progress_callback("Selecting surface code...", 0.10)
            code_params = self.decide_surface_code(device_info, circuit, user_config)
            self.workflow_status[workflow_id]['steps'].append({'surface_code': code_params})

            # 3. Generate surface code layout
            if progress_callback:
                progress_callback("Generating surface code layout...", 0.20)
            layout = self.generate_surface_code_layout(
                code_params['layout'], code_params['distance'], device_info.get('name') or device_info.get('device_name'),
                user_config, progress_callback=progress_callback
            )
            self.workflow_status[workflow_id]['steps'].append('surface_code_layout_generated')

            # 4. Optimize circuit
            if progress_callback:
                progress_callback("Optimizing circuit...", 0.30)
            optimized_circuit = self.optimize_circuit(circuit, device_info, user_config, progress_callback=progress_callback)
            self.workflow_status[workflow_id]['steps'].append('circuit_optimized')

            # 5. Map circuit to surface code
            if progress_callback:
                progress_callback("Mapping circuit to surface code...", 0.40)
            mapping_info = self.map_circuit_to_surface_code(
                optimized_circuit, device_info.get('name') or device_info.get('device_name'),
                code_params['layout'], code_params['distance'], None, user_config, progress_callback=progress_callback
            )
            self.workflow_status[workflow_id]['steps'].append('circuit_mapped')

            # 6. Build fault-tolerant circuit
            if progress_callback:
                progress_callback("Building fault-tolerant circuit...", 0.60)
            code_spaces = []  # TODO: fetch from mapping_info or surface code API if available
            ft_circuit = self.assemble_fault_tolerant_circuit(
                optimized_circuit, mapping_info, code_spaces, device_info, user_config, progress_callback=progress_callback
            )
            self.workflow_status[workflow_id]['steps'].append('ft_circuit_built')

            # 7. (Optional) Code switching, execution, etc. can be added here

            self.workflow_status[workflow_id]['status'] = 'completed'
            if progress_callback:
                progress_callback("Workflow completed.", 1.0)
            return {
                'workflow_id': workflow_id,
                'device_info': device_info,
                'surface_code': code_params,
                'surface_code_layout': layout,
                'optimized_circuit': optimized_circuit,
                'mapping_info': mapping_info,
                'ft_circuit': ft_circuit,
                'status': 'completed',
                'steps': self.workflow_status[workflow_id]['steps']
            }
        except Exception as e:
            self.workflow_status[workflow_id]['status'] = 'failed'
            self.workflow_status[workflow_id]['error'] = str(e)
            if progress_callback:
                progress_callback(f"Error: {str(e)}", 1.0)
            return {'workflow_id': workflow_id, 'status': 'failed', 'error': str(e)}

    def optimize_circuit(self, circuit: dict, device_info: dict, config_overrides: Optional[dict] = None, progress_callback=None) -> dict:
        if progress_callback:
            progress_callback("Running advanced circuit optimization...", 0.35)
        # Use hybrid optimizer if available
        return self.optimizer_api.optimize_circuit(circuit, device_info, config_overrides)

    def get_optimization_report(self, original_circuit: dict, optimized_circuit: dict) -> dict:
        return self.optimizer_api.get_optimization_report(original_circuit, optimized_circuit)

    def generate_surface_code_layout(self, layout_type: str, code_distance: int, device: str, config_overrides: Optional[dict] = None, progress_callback=None) -> dict:
        if progress_callback:
            progress_callback("Generating surface code layout...", 0.20)
        return self.surface_code_api.generate_surface_code_layout(layout_type, code_distance, device)

    def map_circuit_to_surface_code(self, circuit: dict, device: str, layout_type: str, code_distance: int, provider: str = None, config_overrides: Optional[dict] = None, progress_callback=None) -> dict:
        if progress_callback:
            progress_callback("Mapping circuit to surface code...", 0.40)
        # Real implementation using RL agent/environment
        from stable_baselines3 import PPO
        from stable_baselines3.common.vec_env import DummyVecEnv
        from scode.heuristic_layer.heuristic_initialization_layer import HeuristicInitializationLayer
        from scode.graph_transformer.graph_transformer import ConnectivityAwareGraphTransformer
        from scode.rl_agent.environment import RLEnvironment
        from hardware_abstraction.hardware_config_loader import HardwareConfigLoader
        config = self.surface_code_api._load_config()
        if config_overrides:
            config.update(config_overrides)
        hw_loader = HardwareConfigLoader(self.surface_code_api.config_dir, config)
        device_info = hw_loader.load_device_config()
        h_layer = HeuristicInitializationLayer(config, device_info)
        surface_code = h_layer.generate_surface_code(code_distance, layout_type, visualize=False)
        transformer = ConnectivityAwareGraphTransformer(
            config=config,
            hardware_graph=device_info,
            native_gates=device_info['native_gates'],
            gate_error_rates=device_info['gate_error_rates'],
            qubit_error_rates={q: device_info['qubit_properties'][q]['readout_error'] for q in device_info['qubit_properties']}
        )
        transformed = transformer.transform(surface_code)
        def make_env():
            return RLEnvironment(
                transformed_layout=transformed,
                hardware_specs=device_info,
                error_profile=device_info['qubit_properties'],
                config=config
            )
        env = DummyVecEnv([make_env])
        agent_path = self.surface_code_api._find_agent_artifact(device, layout_type, code_distance, provider)
        model = PPO.load(agent_path, env=env)
        # Encode the circuit as environment state
        obs = env.reset(circuit=circuit, device_info=device_info)
        done = False
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, info = env.step(action)
            done = done[0] if isinstance(done, (list, tuple)) else done
        # Decode the mapped circuit from the environment
        mapped_circuit = env.get_attr('get_circuit_from_obs')[0](obs)
        mapping_info = {
            'agent_path': agent_path,
            'device': device,
            'layout_type': layout_type,
            'code_distance': code_distance,
            'provider': provider,
            'mapping_status': 'success',
        }
        return {'mapped_circuit': mapped_circuit, 'mapping_info': mapping_info}

    def assemble_fault_tolerant_circuit(self, logical_circuit: dict, mapping_info: dict, code_spaces: List[dict], device_info: dict, config_overrides: Optional[dict] = None, progress_callback=None) -> dict:
        if progress_callback:
            progress_callback("Assembling fault-tolerant circuit...", 0.60)
        return self.ft_builder.assemble_fault_tolerant_circuit(logical_circuit, mapping_info, code_spaces, device_info)

    def decide_surface_code(self, device_info: dict, circuit: dict, user_prefs: Optional[dict] = None) -> dict:
        """
        Decide which surface code (layout, distance) to use for the given device and circuit.
        Uses policy, device, and circuit info.
        """
        policy = self.current_policy.get('code_selection', {})
        allowed_layouts = policy.get('allowed_layouts', ['planar', 'rotated'])
        prefer_low_error = policy.get('prefer_low_error', True)
        prefer_short_depth = policy.get('prefer_short_depth', False)
        # Example: choose layout and distance based on device and circuit size
        layout = allowed_layouts[0] if allowed_layouts else 'planar'
        # Heuristic: code distance = min(5, device qubit count // 10)
        qubit_count = device_info.get('qubit_count', 5)
        distance = min(5, max(3, qubit_count // 10))
        if user_prefs:
            if 'layout' in user_prefs:
                layout = user_prefs['layout']
            if 'distance' in user_prefs:
                distance = user_prefs['distance']
        return {'layout': layout, 'distance': distance}

    def decide_code_switching(self, circuit: dict, code_info: dict, device_info: dict) -> List[dict]:
        """
        Decide if/where code switching is required and which protocols to use.
        Uses policy, code info, and device constraints.
        """
        policy = self.current_policy.get('code_switching', {})
        enable = policy.get('enable', True)
        preferred_protocols = policy.get('preferred_protocols', ['magic_state_injection', 'lattice_surgery'])
        if not enable:
            return []
        # Example: find all gates in circuit not supported by current code, and assign protocol
        unsupported_gates = []
        supported_gates = code_info.get('supported_gates', ['X', 'Z', 'CNOT'])
        for gate in circuit.get('gates', []):
            if gate['name'] not in supported_gates:
                unsupported_gates.append({'gate': gate['name'], 'location': gate.get('location', None), 'protocol': preferred_protocols[0]})
        return unsupported_gates

    def coordinate_modules(self, modules: List[str], data: dict) -> dict:
        """
        Coordinate the execution of a sequence of modules, passing data between them as needed.
        """
        result = data
        for module in modules:
            if module == 'optimizer':
                hardware_json_path = ConfigManager.config_registry.get('hardware', 'configs/hardware.json')
                device_info = DeviceAbstraction.load_selected_device(hardware_json_path)
                result = self.optimizer_api.optimize_circuit(result, device_info)
            elif module == 'surface_code':
                hardware_json_path = ConfigManager.config_registry.get('hardware', 'configs/hardware.json')
                device_info = DeviceAbstraction.load_selected_device(hardware_json_path)
                code_params = self.decide_surface_code(device_info, result)
                result = self.surface_code_api.generate_surface_code_layout(
                    layout_type=code_params['layout'],
                    code_distance=code_params['distance'],
                    device=device_info.get('name') or device_info.get('device_name')
                )
            # Add more modules as needed (code_switcher, execution, etc.)
        return result

    def get_workflow_status(self, workflow_id: str) -> dict:
        """
        Retrieve the status and progress of a running workflow.
        """
        return self.workflow_status.get(workflow_id, {'status': 'unknown'})

    def cancel_workflow(self, workflow_id: str) -> None:
        """
        Cancel a running workflow.
        """
        if workflow_id in self.workflow_status:
            self.workflow_status[workflow_id]['status'] = 'cancelled'

    def set_workflow_policy(self, policy: dict) -> None:
        """
        Set or update workflow policies (e.g., priorities, fallback strategies).
        """
        self.current_policy = policy
        self.config['workflow_policy'] = policy
        with open(self.config_path, 'w') as f:
            yaml.safe_dump(self.config, f)

    def get_workflow_policy(self) -> dict:
        """
        Retrieve the current workflow policy.
        """
        return self.current_policy

# Alias for backward/test compatibility
Orchestrator = OrchestratorController

   