from hardware_abstraction.hardware_config_loader import HardwareConfigLoader

class RuleBasedOptimizer:
    """
    Rule-based circuit optimizer implementing basic passes: gate fusion, commutation, SWAP insertion, scheduling, qubit mapping.
    Passes are enabled/disabled via config.
    """
    def __init__(self, config=None):
        self.config = config or {}
        self.passes = self.config.get('optimization_passes', [
            {'name': 'gate_fusion', 'enabled': True},
            {'name': 'commutation', 'enabled': True},
            {'name': 'swap_insertion', 'enabled': True},
            {'name': 'scheduling', 'enabled': True},
            {'name': 'qubit_mapping', 'enabled': True},
        ])

    def optimize(self, circuit: dict, device_info: dict) -> dict:
        for p in self.passes:
            if not p.get('enabled', True):
                continue
            if p['name'] == 'gate_fusion':
                circuit = self.gate_fusion(circuit)
            elif p['name'] == 'commutation':
                circuit = self.commutation(circuit)
            elif p['name'] == 'swap_insertion':
                circuit = self.swap_insertion(circuit, device_info)
            elif p['name'] == 'scheduling':
                circuit = self.scheduling(circuit)
            elif p['name'] == 'qubit_mapping':
                circuit = self.qubit_mapping(circuit, device_info)
        return circuit

    def gate_fusion(self, circuit: dict) -> dict:
        # Simple gate fusion: merge consecutive single-qubit gates of the same type on the same qubit
        gates = circuit.get('gates', [])
        if not gates:
            return circuit
        fused_gates = []
        prev_gate = None
        for gate in gates:
            if prev_gate and gate['name'] == prev_gate['name'] and gate.get('qubits') == prev_gate.get('qubits') and len(gate.get('qubits', [])) == 1:
                # Fuse: skip this gate (in real fusion, would update params)
                continue
            fused_gates.append(gate)
            prev_gate = gate
        circuit['gates'] = fused_gates
        return circuit

    def commutation(self, circuit: dict) -> dict:
        # Simple commutation: move non-overlapping gates earlier if possible
        gates = circuit.get('gates', [])
        if not gates:
            return circuit
        new_gates = []
        for gate in gates:
            inserted = False
            for i in range(len(new_gates)):
                if set(gate.get('qubits', [])) & set(new_gates[i].get('qubits', [])):
                    continue
                # Commute gate earlier
                new_gates.insert(i, gate)
                inserted = True
                break
            if not inserted:
                new_gates.append(gate)
        circuit['gates'] = new_gates
        return circuit

    def swap_insertion(self, circuit: dict, device_info: dict) -> dict:
        # Simple SWAP insertion: for each 2-qubit gate, if qubits are not neighbors, insert a SWAP (naive)
        gates = circuit.get('gates', [])
        connectivity = device_info.get('qubit_connectivity', {})
        new_gates = []
        for gate in gates:
            qubits = gate.get('qubits', [])
            if len(qubits) == 2:
                q0, q1 = qubits
                if q1 not in connectivity.get(str(q0), []) and q0 not in connectivity.get(str(q1), []):
                    # Insert a SWAP before this gate (naive: swap q0 and q1)
                    new_gates.append({'name': 'SWAP', 'qubits': [q0, q1]})
            new_gates.append(gate)
        circuit['gates'] = new_gates
        return circuit

    def scheduling(self, circuit: dict) -> dict:
        # Simple ASAP scheduling: assign each gate a 'time' field so that gates on the same qubit are sequential
        gates = circuit.get('gates', [])
        if not gates:
            return circuit
        qubit_time = {}
        for gate in gates:
            qubits = gate.get('qubits', [])
            # Find the max time among all involved qubits
            t = max([qubit_time.get(q, 0) for q in qubits], default=0)
            gate['time'] = t
            # Update time for all involved qubits
            for q in qubits:
                qubit_time[q] = t + 1
        return circuit

    def qubit_mapping(self, circuit: dict, device_info: dict) -> dict:
        # Simple 1-to-1 mapping: logical qubit i -> physical qubit i (if possible)
        logical_qubits = circuit.get('qubits', [])
        physical_qubits = list(device_info.get('qubit_connectivity', {}).keys())
        mapping = {lq: pq for lq, pq in zip(logical_qubits, physical_qubits)}
        # Update all gates to use mapped qubits
        for gate in circuit.get('gates', []):
            gate['qubits'] = [mapping.get(q, q) for q in gate.get('qubits', [])]
        circuit['mapping'] = mapping
        return circuit

    def validate_with_device(self, circuit: dict, config_dir: str) -> bool:
        # Use HardwareConfigLoader to validate circuit against device
        loader = HardwareConfigLoader(config_dir, self.config)
        device_info = loader.load_device_config()
        # Example: check qubit count
        if len(circuit.get('qubits', [])) > device_info.get('qubit_count', 0):
            return False
        # Example: check native gates
        native_gates = set(device_info.get('native_gates', []))
        for gate in circuit.get('gates', []):
            if gate['name'] not in native_gates:
                return False
        return True 