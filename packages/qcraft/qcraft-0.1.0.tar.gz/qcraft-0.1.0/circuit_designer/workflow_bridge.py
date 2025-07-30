import os
import json
from typing import Dict, Any, Optional, List
from orchestration_controller.orchestrator import OrchestratorController
from circuit_optimization.api import CircuitOptimizationAPI
from scode.api import SurfaceCodeAPI
from code_switcher.code_switcher import CodeSwitcherAPI
from execution_simulation.execution_simulator import ExecutionSimulatorAPI
from logging_results.logging_results_manager import LoggingResultsManager
from fault_tolerant_circuit_builder.ft_circuit_builder import FaultTolerantCircuitBuilder
from evaluation.evaluation_framework import EvaluationFramework
from hardware_abstraction.device_abstraction import DeviceAbstraction
from configuration_management.config_manager import ConfigManager
import importlib.resources

# Ensure config registry is loaded before any config access
ConfigManager.load_registry()

def get_provider_and_device(config_dir):
    import importlib.resources
    import os
    try:
        with importlib.resources.open_text('configs', 'hardware.json') as f:
            hw = json.load(f)
    except (FileNotFoundError, ModuleNotFoundError):
        hardware_json_path = os.path.join(config_dir, 'hardware.json')
        with open(hardware_json_path, 'r') as f:
            hw = json.load(f)
    return hw['provider_name'], hw['device_name']

class QuantumWorkflowBridge:
    def __init__(self, config_dir=None):
        self.config_dir = config_dir or os.path.abspath(os.path.join(os.path.dirname(__file__), '../configs'))
        self.provider, self.device = get_provider_and_device(self.config_dir)
        self.orchestrator = OrchestratorController()
        self.optimizer = CircuitOptimizationAPI()
        self.surface_code_api = SurfaceCodeAPI()
        self.code_switcher = CodeSwitcherAPI()
        self.executor = ExecutionSimulatorAPI()
        self.logger = LoggingResultsManager()
        self.ft_builder = FaultTolerantCircuitBuilder()
        self.evaluator = None  # Created per config as needed

    # --- Orchestrated Workflow ---
    def run_full_workflow(self, circuit: Dict, user_config: Optional[Dict] = None, progress_callback=None) -> Dict:
        return self.orchestrator.run_workflow(circuit, user_config, progress_callback=progress_callback)

    def get_workflow_status(self, workflow_id: str) -> Dict:
        return self.orchestrator.get_workflow_status(workflow_id)

    # --- Circuit Optimization ---
    def optimize_circuit(self, circuit: Dict, device_info: Dict, config_overrides: Optional[Dict] = None, progress_callback=None) -> Dict:
        return self.orchestrator.optimize_circuit(circuit, device_info, config_overrides, progress_callback=progress_callback)

    def get_optimization_report(self, original_circuit: Dict, optimized_circuit: Dict) -> Dict:
        return self.orchestrator.get_optimization_report(original_circuit, optimized_circuit)

    # --- Surface Code Generation & Mapping ---
    def generate_surface_code_layout(self, layout_type: str, code_distance: int, device: str, config_overrides: Optional[Dict] = None, progress_callback=None) -> Dict:
        return self.orchestrator.generate_surface_code_layout(layout_type, code_distance, device, config_overrides, progress_callback=progress_callback)

    def map_circuit_to_surface_code(self, circuit: Dict, device: str, layout_type: str, code_distance: int, provider: str = None, config_overrides: Optional[Dict] = None, progress_callback=None) -> Dict:
        return self.orchestrator.map_circuit_to_surface_code(circuit, device, layout_type, code_distance, provider, config_overrides, progress_callback=progress_callback)

    # --- Code Switching ---
    def identify_switching_points(self, circuit: Dict, code_info: Dict) -> List[Dict]:
        # Only pass natively supported gates, never SWAP
        natively_supported = [g for g in code_info.get('supported_gates', []) if g != 'SWAP']
        code_info = dict(code_info)
        code_info['supported_gates'] = natively_supported
        return self.code_switcher.identify_switching_points(circuit, code_info)

    def select_switching_protocol(self, gate: str, available_protocols: List[str], config: Dict = None) -> str:
        # Always include 'teleportation' for SWAP
        if gate.upper() == 'SWAP' and 'teleportation' not in available_protocols:
            available_protocols = available_protocols + ['teleportation']
        print(f"[DEBUG] WorkflowBridge: Selecting protocol for gate {gate} from {available_protocols}")
        return self.code_switcher.select_switching_protocol(gate, available_protocols, config)

    def apply_code_switching(self, circuit: Dict, switching_points: List[Dict], protocols: List[Dict], device_info: Dict) -> Dict:
        return self.code_switcher.apply_code_switching(circuit, switching_points, protocols, device_info)

    # --- Execution/Simulation ---
    def list_backends(self) -> List[str]:
        return self.executor.list_backends()

    def run_circuit(self, circuit: Dict, backend_name: str, run_config: Dict = None) -> str:
        return self.executor.run_circuit(circuit, backend_name, run_config)

    def get_job_status(self, job_id: str) -> Dict:
        return self.executor.get_job_status(job_id)

    def get_job_result(self, job_id: str) -> Dict:
        return self.executor.get_job_result(job_id)

    # --- Logging & Results ---
    def log_event(self, event: str, details: Dict = None, level: str = 'INFO') -> None:
        self.logger.log_event(event, details, level)

    def log_metric(self, metric_name: str, value: float, step: int = None, run_id: str = None) -> None:
        self.logger.log_metric(metric_name, value, step, run_id)

    def store_result(self, run_id: str, result: Dict) -> None:
        self.logger.store_result(run_id, result)

    def get_result(self, run_id: str) -> Dict:
        return self.logger.get_result(run_id)

    # --- Fault-Tolerant Circuit Builder ---
    def assemble_fault_tolerant_circuit(self, logical_circuit: Dict, mapping_info: Dict, code_spaces: List[Dict], device_info: Dict, config_overrides: Optional[Dict] = None, progress_callback=None) -> Dict:
        return self.orchestrator.assemble_fault_tolerant_circuit(logical_circuit, mapping_info, code_spaces, device_info, config_overrides, progress_callback=progress_callback)

    def validate_fault_tolerant_circuit(self, circuit: Dict, device_info: Dict) -> bool:
        return self.ft_builder.validate_fault_tolerant_circuit(circuit, device_info)

    # --- Evaluation ---
    def evaluate_logical_error_rate(self, layout: Dict, hardware: Dict, noise_model: Dict) -> float:
        if self.evaluator is None:
            self.evaluator = EvaluationFramework(self.surface_code_api._load_config())
        return self.evaluator.evaluate_logical_error_rate(layout, hardware, noise_model)

    def evaluate_resource_efficiency(self, layout: Dict) -> Dict:
        if self.evaluator is None:
            self.evaluator = EvaluationFramework(self.surface_code_api._load_config())
        return self.evaluator.evaluate_resource_efficiency(layout)

    def evaluate_learning_efficiency(self, training_log: Any) -> Dict:
        if self.evaluator is None:
            self.evaluator = EvaluationFramework(self.surface_code_api._load_config())
        return self.evaluator.evaluate_learning_efficiency(training_log)

    def evaluate_hardware_adaptability(self, results: Any) -> Dict:
        if self.evaluator is None:
            self.evaluator = EvaluationFramework(self.surface_code_api._load_config())
        return self.evaluator.evaluate_hardware_adaptability(results)

    # --- Device Abstraction ---
    def get_device_info(self, provider_name: str, device_name: str) -> Dict:
        return DeviceAbstraction.get_device_info(provider_name, device_name)

    def list_devices(self, provider_name: str) -> List[str]:
        return DeviceAbstraction.list_devices(provider_name)

    # --- Config Management ---
    def get_config(self, module_name: str) -> Dict:
        return ConfigManager.get_config(module_name)

    def update_config(self, module_name: str, updates: Dict) -> None:
        ConfigManager.update_config(module_name, updates)

    # --- Config Management (Extended) ---
    def list_configs(self) -> list:
        return ConfigManager.list_configs()

    def get_schema(self, module_name: str) -> dict:
        return ConfigManager.get_schema(module_name)

    def save_config(self, module_name: str, config: dict) -> None:
        ConfigManager.save_config(module_name, config=config)

    # --- Training APIs ---
    def train_surface_code_agent(self, provider: str, device: str, layout_type: str, code_distance: int, config_overrides: dict = None, log_callback=None, run_id=None) -> dict:
        return self.surface_code_api.train_surface_code_agent(provider, device, layout_type, code_distance, config_overrides, log_callback=log_callback, run_id=run_id)

    def get_surface_code_training_status(self, agent_path: str) -> dict:
        return self.surface_code_api.get_training_status(agent_path)

    # --- Optimizer Training (Stub) ---
    def train_optimizer_agent(self, circuit: dict, device_info: dict, config_overrides: dict = None) -> str:
        # Placeholder: implement RL/ML optimizer training if available
        raise NotImplementedError('Optimizer training not implemented yet.')

    def get_optimizer_training_status(self, agent_path: str) -> dict:
        # Placeholder: implement optimizer training status if available
        raise NotImplementedError('Optimizer training status not implemented yet.')

    # --- API Key Management ---
    def get_api_key(self, provider_name: str) -> str:
        return ConfigManager.get_api_key(provider_name)

    def set_api_key(self, provider_name: str, api_key: str) -> None:
        ConfigManager.set_api_key(provider_name, api_key)

    def get_current_provider_api_key(self) -> str:
        provider = DeviceAbstraction.get_current_provider_name()
        return ConfigManager.get_api_key(provider) if provider else None 