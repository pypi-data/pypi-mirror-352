import os
from scode.heuristic_layer.config_loader import ConfigLoader
from .evaluation_framework import EvaluationFramework

CONFIG_DIR = os.path.join(os.path.dirname(__file__), '../configs')
SURFACE_CODE_CONFIG = os.path.join(CONFIG_DIR, 'surface_code_config.yaml')

def main():
    config = ConfigLoader.load_yaml(SURFACE_CODE_CONFIG)
    evaluator = EvaluationFramework(config)
    # Example dummy data for stubs
    layout = {'dummy': True}
    hardware = {'dummy': True}
    noise_model = {'dummy': True}
    training_log = {'dummy': True}
    results = {'dummy': True}
    ler = evaluator.evaluate_logical_error_rate(layout, hardware, noise_model)
    res_eff = evaluator.evaluate_resource_efficiency(layout)
    learn_eff = evaluator.evaluate_learning_efficiency(training_log)
    hw_adapt = evaluator.evaluate_hardware_adaptability(results)
    print(f"Logical Error Rate: {ler}")
    print(f"Resource Efficiency: {res_eff}")
    print(f"Learning Efficiency: {learn_eff}")
    print(f"Hardware Adaptability: {hw_adapt}")

if __name__ == '__main__':
    main() 