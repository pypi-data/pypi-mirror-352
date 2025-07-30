import yaml
from typing import Dict, Any

class CodeSwitcher:
    def __init__(self, switcher_config_path: str):
        with open(switcher_config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def switch(self, old_mapping: Dict[str, Any], new_mapping: Dict[str, Any], protocol: str = None, **kwargs):
        protocols = [p for p in self.config['switching_protocols'] if p['enabled']]
        if protocol:
            selected = next((p for p in protocols if p['name'] == protocol), None)
            if not selected:
                raise ValueError(f"Protocol {protocol} not enabled or not found in config.")
        else:
            # Select the first enabled protocol
            selected = protocols[0] if protocols else None
        if not selected:
            raise RuntimeError("No enabled switching protocol found in config.")
        # Implement the switching logic based on the selected protocol
        # (e.g., lattice surgery, magic state injection, teleportation)
        # All parameters must be passed via API or config
        print(f"Switching code from {old_mapping} to {new_mapping} using protocol {selected['name']}")
        # ... actual switching logic here, parameterized by selected and kwargs ...
        return {'protocol': selected['name'], 'old_mapping': old_mapping, 'new_mapping': new_mapping} 