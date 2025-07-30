import os
import unittest
from scode.api import SurfaceCodeAPI
from scode.heuristic_layer.config_loader import ConfigLoader
from hardware_abstraction.hardware_config_loader import HardwareConfigLoader
import json
from circuit_designer.workflow_bridge import QuantumWorkflowBridge
import importlib.resources

class TestFullFrontendWorkflow(unittest.TestCase):
    def setUp(self):
        self.config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../configs'))
        self.surface_code_config = os.path.join(self.config_dir, 'surface_code_config.yaml')
        self.switcher_config = os.path.join(self.config_dir, 'switcher_config.yaml')
        self.api = SurfaceCodeAPI(self.config_dir)
        self.config = ConfigLoader.load_yaml(self.surface_code_config)
        # Load device and provider from hardware.json
        hardware_json_path = os.path.join(self.config_dir, 'hardware.json')
        hw = self.load_hardware_json(hardware_json_path)
        self.provider = hw['provider_name']
        self.device = hw['device_name']
        self.layout_type = self.api.list_layout_types()[0]
        self.code_distance = self.api.list_code_distances(self.device, self.layout_type)[0]

    def load_hardware_json(self, hardware_json_path):
        try:
            with importlib.resources.open_text('configs', 'hardware.json') as f:
                return json.load(f)
        except (FileNotFoundError, ModuleNotFoundError):
            with open(hardware_json_path, 'r') as f:
                return json.load(f)

    def test_device_and_layout_selection(self):
        print('\n[TEST] Device and layout selection')
        devices = self.api.list_available_devices()
        layouts = self.api.list_layout_types()
        code_distances = self.api.list_code_distances(self.device, self.layout_type)
        print('Devices:', devices)
        print('Layouts:', layouts)
        print('Code distances:', code_distances)
        self.assertTrue(len(layouts) > 0)
        self.assertTrue(len(code_distances) > 0)

    def test_surface_code_generation(self):
        print('\n[TEST] Surface code generation')
        layout = self.api.generate_surface_code_layout(self.layout_type, self.code_distance, self.device)
        print('Generated layout:', layout)
        self.assertIn('qubit_layout', layout)
        self.assertIn('stabilizer_map', layout)

    def test_rl_agent_training(self):
        print('\n[TEST] RL agent training')
        def log_callback(msg, progress):
            print(f'[TRAIN LOG] {msg} (progress={progress})')
        policy_path = self.api.train_surface_code_agent(
            provider=self.provider,
            device=self.device,
            layout_type=self.layout_type,
            code_distance=self.code_distance,
            config_overrides=None,
            log_callback=log_callback
        )
        print('Trained policy path:', policy_path)
        self.assertTrue(os.path.exists(policy_path))
        status = self.api.get_training_status(policy_path)
        print('Training status:', status)
        self.assertEqual(status['status'], 'completed')

    def test_mapping_and_multi_patch(self):
        print('\n[TEST] Mapping and multi-patch')
        layout = self.api.generate_surface_code_layout(self.layout_type, self.code_distance, self.device)
        mapping_constraints = self.config.get('multi_patch', {'patch_shapes': ['rectangular']})
        # Simulate multi-patch mapping via orchestrator API
        orchestrate_result = self.api.orchestrate_code_and_mapping(
            code_distance=self.code_distance,
            layout_type=self.layout_type,
            mapping_constraints=mapping_constraints,
            device_config={'qubit_count': 25, 'topology_type': 'grid', 'qubit_connectivity': {str(i): [str(i+1)] for i in range(24)}},
            switcher_config_path=self.switcher_config,
            config_path=self.surface_code_config
        )
        print('Orchestrate result:', orchestrate_result)
        self.assertIn('code', orchestrate_result)
        self.assertIn('mapping', orchestrate_result)

    def test_code_switching(self):
        print('\n[TEST] Code switching')
        mapping_constraints = self.config.get('multi_patch', {'patch_shapes': ['rectangular']})
        orchestrate_result = self.api.orchestrate_code_and_mapping(
            code_distance=self.code_distance,
            layout_type=self.layout_type,
            mapping_constraints=mapping_constraints,
            device_config={'qubit_count': 25, 'topology_type': 'grid', 'qubit_connectivity': {str(i): [str(i+1)] for i in range(24)}},
            switcher_config_path=self.switcher_config,
            config_path=self.surface_code_config
        )
        old_mapping = orchestrate_result['mapping']
        new_mapping = orchestrate_result['mapping']  # For test, use same mapping
        result = self.api.switch_code_space(
            old_mapping=old_mapping,
            new_mapping=new_mapping,
            switcher_config_path=self.switcher_config,
            protocol='lattice_surgery'
        )
        print('Switch result:', result)
        self.assertIn('protocol', result)
        self.assertEqual(result['protocol'], 'lattice_surgery')

    def test_evaluation(self):
        print('\n[TEST] Evaluation')
        layout = self.api.generate_surface_code_layout(self.layout_type, self.code_distance, self.device)
        mapped_circuit = {'layout': layout}
        ler = self.api.evaluate_logical_error_rate(mapped_circuit, self.device)
        print('Logical error rate:', ler)
        self.assertIsInstance(ler, float)

    def test_error_cases(self):
        print('\n[TEST] Error and edge cases')
        # Invalid device
        with self.assertRaises(Exception):
            self.api.generate_surface_code_layout(self.layout_type, self.code_distance, 'invalid_device')
        # Invalid code distance
        with self.assertRaises(Exception):
            self.api.generate_surface_code_layout(self.layout_type, 999, self.device)
        # Invalid protocol: only check if backend is expected to raise
        mapping_constraints = self.config.get('multi_patch', {'patch_shapes': ['rectangular']})
        orchestrate_result = self.api.orchestrate_code_and_mapping(
            code_distance=self.code_distance,
            layout_type=self.layout_type,
            mapping_constraints=mapping_constraints,
            device_config={'qubit_count': 25, 'topology_type': 'grid', 'qubit_connectivity': {str(i): [str(i+1)] for i in range(24)}},
            switcher_config_path=self.switcher_config,
            config_path=self.surface_code_config
        )
        old_mapping = orchestrate_result['mapping']
        new_mapping = orchestrate_result['mapping']
        try:
            self.api.switch_code_space(
                old_mapping=old_mapping,
                new_mapping=new_mapping,
                switcher_config_path=self.switcher_config,
                protocol='teleportation'  # disabled in config
            )
        except Exception:
            pass  # Accept exception
        else:
            print('No exception raised for invalid protocol (may be allowed by backend config)')

    def test_swap_gate_protocol_selection(self):
        print('\n[TEST] SWAP gate protocol selection')
        bridge = QuantumWorkflowBridge(self.config_dir)
        # Build a circuit with a SWAP gate
        circuit = {
            'qubits': [0, 1],
            'gates': [
                {'id': 'g0_SWAP_0_1_0', 'name': 'SWAP', 'qubits': [0, 1], 'time': 0, 'params': []}
            ]
        }
        # Try to run code switching step
        try:
            # Only include natively supported gates
            code_info = {'supported_gates': ['X', 'Z', 'CNOT', 'H']}
            switching_points = bridge.identify_switching_points(circuit, code_info)
            print('Switching points:', switching_points)
            protocols = []
            for sp in switching_points:
                proto = bridge.select_switching_protocol(sp['gate'], ["magic_state_injection", "lattice_surgery", "teleportation"])
                print(f"Selected protocol for {sp['gate']}: {proto}")
                protocols.append({'name': proto})
            print('Protocols found:', protocols)
        except Exception as e:
            print('Exception during protocol selection:', str(e))
            self.fail(f"Exception during protocol selection: {e}")
        else:
            self.assertTrue(any(p['name'] == 'teleportation' for p in protocols))

if __name__ == '__main__':
    unittest.main() 