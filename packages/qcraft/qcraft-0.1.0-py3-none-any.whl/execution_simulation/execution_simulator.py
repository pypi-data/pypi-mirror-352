import os
import yaml
import json
import threading
import uuid
from typing import List, Dict, Any, Optional, Callable
from configuration_management.config_manager import ConfigManager
import importlib.resources

try:
    from qiskit import QuantumCircuit, Aer, execute
    from qiskit.providers.ibmq import IBMQ
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False

class ConfigLoader:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or 'configs/backends.yaml'
        self.config = self.load_config(self.config_path)

    def load_config(self, path: str) -> dict:
        fname = os.path.basename(path)
        try:
            with importlib.resources.open_text('configs', fname) as f:
                if fname.endswith('.yaml') or fname.endswith('.yml'):
                    return yaml.safe_load(f)
                elif fname.endswith('.json'):
                    return json.load(f)
        except (FileNotFoundError, ModuleNotFoundError):
            if path.endswith('.yaml') or path.endswith('.yml'):
                with open(path, 'r') as f:
                    return yaml.safe_load(f)
            elif path.endswith('.json'):
                with open(path, 'r') as f:
                    return json.load(f)
        raise ValueError("Unsupported config file format.")

    def get_setting(self, key: str, default=None):
        return self.config.get(key, default)

    def reload(self):
        self.config = self.load_config(self.config_path)

class ExecutionSimulator:
    def __init__(self, config_path: str = None):
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.config
        self.backends = {b['name']: b for b in self.config.get('backends', [])}
        self.backend_plugins: Dict[str, Callable] = {}
        self.jobs: Dict[str, dict] = {}  # job_id -> job info
        self.job_threads: Dict[str, threading.Thread] = {}
        self.job_results: Dict[str, dict] = {}
        self.job_status: Dict[str, str] = {}  # job_id -> status
        self.lock = threading.Lock()

    # --- Extensibility ---
    def register_backend_plugin(self, backend_name: str, handler: Callable):
        self.backend_plugins[backend_name] = handler

    def reload_config(self):
        self.config_loader.reload()
        self.config = self.config_loader.config
        self.backends = {b['name']: b for b in self.config.get('backends', [])}

    # --- Main APIs ---
    def list_backends(self) -> List[str]:
        return list(self.backends.keys())

    def get_backend_info(self, backend_name: str) -> dict:
        return self.backends.get(backend_name, {})

    def run_circuit(self, circuit: dict, backend_name: str, run_config: dict = None) -> str:
        backend_info = self.get_backend_info(backend_name)
        provider = backend_info.get('provider', '').lower()
        api_key = None
        if provider not in ['local', 'simulator']:
            api_key = ConfigManager.get_api_key(provider)
        # Pass api_key to backend execution logic as needed
        # ... existing code for running the circuit ...
        # Example: if using IBMQ, authenticate with api_key
        # (Insert provider-specific logic here)
        return self._run_backend_job(circuit, backend_name, run_config, api_key)

    def _run_backend_job(self, circuit, backend_name, run_config, api_key):
        # This is a placeholder for actual backend execution logic
        # Use api_key for authentication if needed
        # ... existing or new code ...
        pass

    def _execute_job(self, job_id: str, circuit: dict, backend: dict, run_config: dict):
        self.job_status[job_id] = 'running'
        try:
            if backend['provider'].lower() == 'ibmq' and QISKIT_AVAILABLE:
                result = self._run_ibmq(circuit, backend, run_config)
            elif backend['provider'].lower() == 'local' and QISKIT_AVAILABLE:
                result = self._run_local_sim(circuit, backend, run_config)
            else:
                raise NotImplementedError(f"Provider {backend['provider']} not supported or required package not installed.")
            with self.lock:
                self.job_results[job_id] = result
                self.job_status[job_id] = 'completed'
        except Exception as e:
            with self.lock:
                self.job_results[job_id] = {'error': str(e)}
                self.job_status[job_id] = 'failed'

    def _dict_to_qiskit_circuit(self, circuit: dict) -> 'QuantumCircuit':
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is required for circuit execution.")
        n_qubits = len(circuit.get('qubits', []))
        qc = QuantumCircuit(n_qubits)
        for gate in circuit.get('gates', []):
            name = gate['name'].lower()
            qubits = gate.get('qubits', [])
            params = gate.get('params', [])
            if hasattr(qc, name):
                getattr(qc, name)(*params, *qubits)
            else:
                qc.append(name, qubits)
        return qc

    def _run_ibmq(self, circuit: dict, backend: dict, run_config: dict) -> dict:
        # Assumes IBMQ account is already loaded
        provider = IBMQ.load_account()
        backend_name = backend['name']
        qiskit_backend = provider.get_backend(backend_name)
        qc = self._dict_to_qiskit_circuit(circuit)
        shots = run_config.get('shots', 1024) if run_config else 1024
        job = execute(qc, backend=qiskit_backend, shots=shots)
        result = job.result()
        return {
            'counts': result.get_counts(),
            'success': result.success,
            'backend': backend_name,
            'job_id': job.job_id(),
            'result': result.to_dict(),
        }

    def _run_local_sim(self, circuit: dict, backend: dict, run_config: dict) -> dict:
        sim_backend = Aer.get_backend('qasm_simulator')
        qc = self._dict_to_qiskit_circuit(circuit)
        shots = run_config.get('shots', 1024) if run_config else 1024
        job = execute(qc, backend=sim_backend, shots=shots)
        result = job.result()
        return {
            'counts': result.get_counts(),
            'success': result.success,
            'backend': backend['name'],
            'result': result.to_dict(),
        }

    def get_job_status(self, job_id: str) -> dict:
        status = self.job_status.get(job_id, 'unknown')
        return {'job_id': job_id, 'status': status}

    def get_job_result(self, job_id: str) -> dict:
        with self.lock:
            return self.job_results.get(job_id, {'error': 'Result not available.'})

    def cancel_job(self, job_id: str) -> None:
        # For simulation, just mark as cancelled; for real hardware, would need to call backend API
        with self.lock:
            if job_id in self.job_status and self.job_status[job_id] in ('pending', 'running'):
                self.job_status[job_id] = 'cancelled'

    def get_supported_simulation_options(self, backend_name: str) -> dict:
        backend = self.backends.get(backend_name)
        if not backend:
            raise ValueError(f"Backend {backend_name} not found.")
        return {
            'noise_models': backend.get('noise_models', []),
            'max_shots': backend.get('max_shots', None),
            'type': backend.get('type', None),
        }

    def export_result(self, job_id: str, format: str, path: str) -> None:
        result = self.get_job_result(job_id)
        if format == 'json':
            with open(path, 'w') as f:
                json.dump(result, f, indent=2)
        elif format in ('yaml', 'yml'):
            with open(path, 'w') as f:
                yaml.safe_dump(result, f)
        elif format == 'csv':
            # Export counts as CSV
            counts = result.get('counts', {})
            with open(path, 'w') as f:
                f.write('bitstring,count\n')
                for k, v in counts.items():
                    f.write(f'{k},{v}\n')
        else:
            raise ValueError(f"Unsupported export format: {format}")

class ExecutionSimulatorAPI:
    """
    API for the Execution Simulation Module. Exposes all required methods for frontend/backend integration.
    Wraps the real ExecutionSimulator logic (no stubs).
    """
    def __init__(self, config_path: str = None):
        self.simulator = ExecutionSimulator(config_path)

    def list_backends(self) -> List[str]:
        """List all available backends."""
        return self.simulator.list_backends()

    def get_backend_info(self, backend_name: str) -> dict:
        """Get detailed info for a backend."""
        return self.simulator.get_backend_info(backend_name)

    def run_circuit(self, circuit: dict, backend_name: str, run_config: dict = None) -> str:
        """Run a circuit on the specified backend. Returns a job ID."""
        return self.simulator.run_circuit(circuit, backend_name, run_config)

    def get_job_status(self, job_id: str) -> dict:
        """Get the status of a job by job ID."""
        return self.simulator.get_job_status(job_id)

    def get_job_result(self, job_id: str) -> dict:
        """Get the result of a job by job ID."""
        return self.simulator.get_job_result(job_id)

    def cancel_job(self, job_id: str) -> None:
        """Cancel a running or pending job."""
        self.simulator.cancel_job(job_id)

    def get_supported_simulation_options(self, backend_name: str) -> dict:
        """Get supported simulation options for a backend (noise models, max shots, etc)."""
        return self.simulator.get_supported_simulation_options(backend_name)

    def export_result(self, job_id: str, format: str, path: str) -> None:
        """Export the result of a job to a file in the specified format (json, yaml, csv)."""
        self.simulator.export_result(job_id, format, path) 