import os
try:
    from stable_baselines3 import PPO
except ImportError:
    PPO = None

class RLBasedOptimizer:
    """
    RL-based circuit optimizer. Uses a trained RL agent (e.g., PPO) to optimize the circuit.
    Config-driven model loading and agent selection.
    """
    def _get_artifacts_dir(self):
        output_dir = self.config.get('system', {}).get('output_dir', './outputs')
        return os.path.abspath(os.path.join(output_dir, 'training_artifacts'))

    def _resolve_model_path(self, model_path):
        if os.path.isabs(model_path):
            return model_path
        artifacts_dir = self._get_artifacts_dir()
        return os.path.join(artifacts_dir, model_path)

    def __init__(self, config=None):
        self.config = config or {}
        self.model_path = self.config.get('rl_config', {}).get('model_path', None)
        self.agent = None
        if self.model_path:
            resolved_path = self._resolve_model_path(self.model_path)
            if os.path.exists(resolved_path):
                self._load_agent(resolved_path)

    def _load_agent(self, path):
        if PPO is None:
            raise ImportError("stable-baselines3 is required for RL-based optimization. Please install it.")
        self.agent = PPO.load(path)

    def _circuit_to_obs(self, circuit, device_info, env):
        # Use the RL environment's reset method to encode the circuit and device info
        obs = env.reset(circuit=circuit, device_info=device_info)
        return obs

    def _obs_to_circuit(self, obs, env):
        # Use the RL environment's method to decode observation to circuit
        return env.get_circuit_from_obs(obs)

    def optimize(self, circuit: dict, device_info: dict) -> dict:
        if self.agent is None:
            raise RuntimeError("RL agent not loaded. Please provide a valid model path.")
        from scode.rl_agent.environment import RLEnvironment
        from stable_baselines3.common.vec_env import DummyVecEnv
        config = self.config.get('rl_config', {})
        def make_env():
            return RLEnvironment(config=config, hardware_specs=device_info, error_profile=device_info.get('qubit_properties', {}))
        env = DummyVecEnv([make_env])
        obs = self._circuit_to_obs(circuit, device_info, env)
        done = False
        while not done:
            action, _ = self.agent.predict(obs, deterministic=True)
            obs, reward, done, info = env.step(action)
            done = done[0] if isinstance(done, (list, tuple)) else done
        optimized_circuit = self._obs_to_circuit(obs, env)
        return optimized_circuit 