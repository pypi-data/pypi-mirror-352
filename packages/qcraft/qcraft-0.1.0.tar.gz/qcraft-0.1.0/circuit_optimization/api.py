from circuit_optimization.circuit_optimizer import CircuitOptimizer
from configuration_management.config_manager import ConfigManager
from typing import Dict, Any, Optional, List

class CircuitOptimizationAPI:
    """
    API for the Circuit Optimization Module. Exposes all required methods for frontend/backend integration.
    All configuration is loaded via the configuration management module.
    """
    def __init__(self, config_path: str = None, config_dir: str = 'configs'):
        if config_path is None:
            config_path = ConfigManager.config_registry.get('optimization', 'configs/optimizer_config.yaml')
        self.optimizer = CircuitOptimizer(config_path=config_path, config_dir=config_dir)

    def optimize_circuit(self, circuit: Dict, device_info: Dict, config_overrides: Optional[Dict] = None) -> Dict:
        """
        Optimize the input circuit for the given device. Returns the optimized circuit as a data structure.
        """
        return self.optimizer.optimize_circuit(circuit, device_info, config_overrides)

    def get_optimization_report(self, original_circuit: Dict, optimized_circuit: Dict) -> Dict:
        """
        Return a report comparing the original and optimized circuits (gate count, depth, SWAPs, resource usage, etc.).
        """
        return self.optimizer.get_optimization_report(original_circuit, optimized_circuit)

    def validate_circuit(self, circuit: Dict, device_info: Dict) -> bool:
        """
        Validate that the circuit is compatible with the device (native gates, connectivity, qubit count, etc.).
        """
        return self.optimizer.validate_circuit(circuit, device_info)

    def export_circuit(self, circuit: Dict, format: str, path: str) -> None:
        """
        Export the optimized circuit to a file in the specified format (QASM, JSON, YAML).
        """
        self.optimizer.export_circuit(circuit, format, path)

    def import_circuit(self, path: str, format: str) -> Dict:
        """
        Import a circuit from a file in the specified format.
        """
        return self.optimizer.import_circuit(path, format)

    def get_supported_optimization_passes(self) -> List[str]:
        """
        Return a list of supported optimization passes (e.g., gate fusion, SWAP minimization, scheduling).
        """
        return self.optimizer.get_supported_optimization_passes()

    def get_circuit_summary(self, circuit: Dict) -> Dict:
        """
        Return a summary of the circuit (qubit count, gate count, depth, etc.) for display in the frontend.
        """
        return self.optimizer.get_circuit_summary(circuit) 