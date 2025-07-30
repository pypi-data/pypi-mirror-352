import unittest
from scode.reward_engine.reward_engine import MultiObjectiveRewardEngine
from scode.heuristic_layer.config_loader import ConfigLoader
import os

class TestRewardEngine(unittest.TestCase):
    def setUp(self):
        config_path = os.path.join(os.path.dirname(__file__), '../../configs/surface_code_config.yaml')
        self.config = ConfigLoader.load_yaml(config_path)
        self.engine = MultiObjectiveRewardEngine(self.config)

    def test_compute_reward(self):
        circuit_metrics = {
            'weighted_single_qubit_gate_error': 0.005,
            'weighted_two_qubit_gate_error': 0.005,
            'weighted_gate_error': 0.01,  # legacy, ignored
            'total_swap_gates': 2,
            'circuit_depth': 10,
            'logical_error_rate': 0.001,
            'weighted_qubit_error': 0.09,
            'stabilizer_score': 0.9
        }
        reward_weights = {
            'alpha1': 1.0,
            'alpha2': 1.0,
            'beta': 1.0,
            'gamma': 1.0,
            'delta': 1.0,
            'epsilon': 1.0,
            'zeta': 1.0
        }
        reward, breakdown = self.engine.compute_reward(None, circuit_metrics, {}, reward_weights)
        self.assertIsInstance(reward, float)
        self.assertIsInstance(breakdown, dict)
        self.assertIn('weighted_single_qubit_gate_error', breakdown)
        self.assertIn('weighted_two_qubit_gate_error', breakdown)

if __name__ == '__main__':
    unittest.main() 