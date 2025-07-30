import os
from scode.heuristic_layer.config_loader import ConfigLoader
from scode.heuristic_layer.heuristic_initialization_layer import HeuristicInitializationLayer
from hardware_abstraction.hardware_config_loader import HardwareConfigLoader
from .multi_patch_mapper import MultiPatchMapper

CONFIG_DIR = os.path.join(os.path.dirname(__file__), '../configs')
SURFACE_CODE_CONFIG = os.path.join(CONFIG_DIR, 'surface_code_config.yaml')

def main():
    config = ConfigLoader.load_yaml(SURFACE_CODE_CONFIG)
    hw_loader = HardwareConfigLoader(CONFIG_DIR, config)
    device = hw_loader.load_device_config()
    h_layer = HeuristicInitializationLayer(config, device)
    params = config['surface_code']
    multi_patch_cfg = config['multi_patch']
    num_patches = multi_patch_cfg['num_patches']
    patch_shapes = multi_patch_cfg['patch_shapes']
    surface_codes = [
        h_layer.generate_surface_code(
            code_distance=params['code_distance'],
            layout_type=params['layout_type'],
            visualize=False
        ) for _ in range(num_patches)
    ]
    mapping_constraints = multi_patch_cfg
    mapper = MultiPatchMapper(config, device)
    result = mapper.map_patches(surface_codes, mapping_constraints)
    print(f"Multi-patch layout: {result['multi_patch_layout']}")
    print(f"Inter-patch connectivity: {result['inter_patch_connectivity']}")
    print(f"Resource allocation: {result['resource_allocation']}")
    print(f"Optimization metrics: {result['optimization_metrics']}")

if __name__ == '__main__':
    main() 