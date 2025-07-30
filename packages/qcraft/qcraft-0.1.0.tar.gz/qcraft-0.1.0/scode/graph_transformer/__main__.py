import os
from scode.heuristic_layer.config_loader import ConfigLoader
from scode.heuristic_layer.heuristic_initialization_layer import HeuristicInitializationLayer
from hardware_abstraction.hardware_config_loader import HardwareConfigLoader
from .graph_transformer import ConnectivityAwareGraphTransformer

CONFIG_DIR = os.path.join(os.path.dirname(__file__), '../configs')
SURFACE_CODE_CONFIG = os.path.join(CONFIG_DIR, 'surface_code_config.yaml')

def main():
    config = ConfigLoader.load_yaml(SURFACE_CODE_CONFIG)
    hw_loader = HardwareConfigLoader(CONFIG_DIR, config)
    device = hw_loader.load_device_config()
    h_layer = HeuristicInitializationLayer(config, device)
    params = config['surface_code']
    surface_code = h_layer.generate_surface_code(
        code_distance=params['code_distance'],
        layout_type=params['layout_type'],
        visualize=params['visualize']
    )
    transformer = ConnectivityAwareGraphTransformer(
        config=config,
        hardware_graph=device,
        native_gates=device['native_gates'],
        gate_error_rates=device['gate_error_rates'],
        qubit_error_rates={q: device['qubit_properties'][q]['readout_error'] for q in device['qubit_properties']}
    )
    result = transformer.transform(surface_code)
    print(f"Transformed layout: {result['transformed_layout']}")
    print(f"Hardware stabilizer map: {result['hardware_stabilizer_map']}")
    print(f"Connectivity overhead: {result['connectivity_overhead_info']}")
    print(f"Annotated graph nodes: {result['annotated_graph'].nodes(data=True)}")

if __name__ == '__main__':
    main() 