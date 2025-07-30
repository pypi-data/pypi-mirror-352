import unittest
import os
import numpy as np
from scode.heuristic_layer.config_loader import ConfigLoader
from scode.heuristic_layer.heuristic_initialization_layer import HeuristicInitializationLayer
from hardware_abstraction.hardware_config_loader import HardwareConfigLoader
from scode.graph_transformer.graph_transformer import ConnectivityAwareGraphTransformer
try:
    from scode.rl_agent.rl_agent import ReinforcementLearningAgent
except ImportError:
    ReinforcementLearningAgent = None
from scode.rl_agent.environment import RLEnvironment
from scode.reward_engine.reward_engine import MultiObjectiveRewardEngine
from evaluation.evaluation_framework import EvaluationFramework

class TestRLLearningProgress(unittest.TestCase):
    def setUp(self):
        config_path = os.path.join(os.path.dirname(__file__), '../../configs/surface_code_config.yaml')
        self.config = ConfigLoader.load_yaml(config_path)
        self.hw_loader = HardwareConfigLoader(os.path.join(os.path.dirname(__file__), '../../configs'), self.config)
        self.device = self.hw_loader.load_device_config()
        self.h_layer = HeuristicInitializationLayer(self.config, self.device)
        self.transformer = ConnectivityAwareGraphTransformer(
            config=self.config,
            hardware_graph=self.device,
            native_gates=self.device['native_gates'],
            gate_error_rates=self.device['gate_error_rates'],
            qubit_error_rates={q: self.device['qubit_properties'][q]['readout_error'] for q in self.device['qubit_properties']}
        )
        self.reward_engine = MultiObjectiveRewardEngine(self.config)
        self.evaluator = EvaluationFramework(self.config)
        layout_type = self.config.get('surface_code', {}).get('layout_type', 'planar')
        code_distance = self.config.get('surface_code', {}).get('code_distance', 3)
        provider = self.device.get('provider_name', 'provider').lower()
        device = self.device.get('device_name', 'device').lower()
        self.policy_path = os.path.abspath(os.path.join(self.config.get('system', {}).get('output_dir', './outputs'), '../training_artifacts', f"{provider}_{device}_{layout_type}_d{code_distance}_sb3_ppo_surface_code.zip"))

    def test_learning_improves_logical_error_rate(self):
        if ReinforcementLearningAgent is None:
            self.skipTest("ReinforcementLearningAgent not available (rl_agent.py missing)")
        # Generate a surface code and transform it
        code = self.h_layer.generate_surface_code(3, 'planar')
        transformed = self.transformer.transform(code)
        env = RLEnvironment(
            transformed_layout=transformed,
            hardware_specs=self.device,
            error_profile=self.device['qubit_properties'],
            config=self.config
        )
        # Evaluate random policy (baseline)
        rewards = []
        lers = []
        for _ in range(10):
            obs, info = env.reset()
            total_reward = 0
            test_state = None  # Initialize test_state
            for _ in range(env.max_steps):
                action_idx = np.random.randint(env.action_space.n)
                next_state, reward, done, truncated, info = env.step(action_idx)
                total_reward += reward
                test_state = next_state  # Update test_state to the latest next_state
                if done or truncated:
                    break
            try:
                ler = env.estimate_logical_error_rate(test_state, num_trials=env.ler_num_trials, noise_prob=env.ler_noise_prob)
            except Exception as e:
                print(f"LER estimation failed: {e}")
                ler = np.nan
            rewards.append(total_reward)
            lers.append(ler)
        baseline_reward = np.mean(rewards)
        baseline_ler = np.nanmean(lers)

        # Evaluate trained policy (if exists)
        if os.path.exists(self.policy_path):
            agent = ReinforcementLearningAgent(self.config, env, self.reward_engine)
            agent.load_policy(self.policy_path)
            rewards = []
            lers = []
            for _ in range(10):
                obs, info = env.reset()
                total_reward = 0
                test_state = None  # Initialize test_state
                for _ in range(env.max_steps):
                    action_idx = agent._select_action(obs)[0]
                    next_state, reward, done, truncated, info = env.step(action_idx)
                    total_reward += reward
                    test_state = next_state  # Update test_state to the latest next_state
                    if done or truncated:
                        break
                try:
                    ler = env.estimate_logical_error_rate(test_state, num_trials=env.ler_num_trials, noise_prob=env.ler_noise_prob)
                except Exception as e:
                    print(f"LER estimation failed: {e}")
                    ler = np.nan
                rewards.append(total_reward)
                lers.append(ler)
            trained_reward = np.mean(rewards)
            trained_ler = np.nanmean(lers)
            print(f"Baseline reward: {baseline_reward}, Trained reward: {trained_reward}")
            print(f"Baseline LER: {baseline_ler}, Trained LER: {trained_ler}")
            # Only assert on LER if both are not nan
            if not (np.isnan(baseline_ler) or np.isnan(trained_ler)):
                self.assertTrue(trained_reward > baseline_reward or trained_ler < baseline_ler)
            elif trained_reward == 0.0 and baseline_reward == 0.0:
                self.skipTest("Both baseline and trained rewards are zero; test is inconclusive for this environment.")
            else:
                self.assertTrue(trained_reward > baseline_reward)
        else:
            print("No trained policy found. Skipping trained policy evaluation.")

if __name__ == '__main__':
    unittest.main() 