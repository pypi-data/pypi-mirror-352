import os
import json
from scode.heuristic_layer.config_loader import ConfigLoader
from typing import Dict, Any, List
import glob
import importlib.resources

class HardwareConfigLoader:
    def __init__(self, config_dir: str, config: dict):
        self.config_dir = config_dir
        self.config = config

    def load_device_config(self) -> Dict[str, Any]:
        # Load provider and device from hardware.json
        hardware_json_path = os.path.join(self.config_dir, 'hardware.json')
        hw = self.load_hardware_json(hardware_json_path)
        provider = hw['provider_name'].lower()
        device_name = hw['device_name']
        yaml_file = f"{provider}_devices.yaml"
        yaml_path = os.path.join(self.config_dir, yaml_file)
        devices = ConfigLoader.load_yaml(yaml_path)
        key = f"{provider}_devices"
        for dev in devices.get(key, []):
            if dev['device_name'] == device_name:
                return dev
        raise ValueError(f"Device {device_name} not found in {yaml_file}")

    def list_devices(self) -> List[str]:
        # Scan all *_devices.yaml files in config_dir and return all device names
        device_names = []
        for yaml_file in glob.glob(os.path.join(self.config_dir, '*_devices.yaml')):
            devices = ConfigLoader.load_yaml(yaml_file)
            for key in devices:
                if key.endswith('_devices'):
                    for dev in devices[key]:
                        if 'device_name' in dev:
                            device_names.append(dev['device_name'])
        return device_names

    def load_hardware_json(self, hardware_json_path):
        try:
            with importlib.resources.open_text('configs', 'hardware.json') as f:
                return json.load(f)
        except (FileNotFoundError, ModuleNotFoundError):
            with open(hardware_json_path, 'r') as f:
                return json.load(f) 