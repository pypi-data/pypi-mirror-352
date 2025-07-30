from typing import Dict, Any, List
import networkx as nx

class SurfaceCodeObject:
    def __init__(
        self,
        qubit_layout: Dict[int, Any],
        stabilizer_map: Dict[str, Any],
        logical_operators: Dict[str, Any],
        adjacency_matrix: Any,
        code_distance: int,
        layout_type: str,
        grid_connectivity: str = None
    ):
        self.qubit_layout = qubit_layout
        self.stabilizer_map = stabilizer_map
        self.logical_operators = logical_operators
        self.adjacency_matrix = adjacency_matrix
        self.code_distance = code_distance
        self.layout_type = layout_type
        self.grid_connectivity = grid_connectivity
        self.validate()

    def validate(self):
        # Basic checks for validity
        assert isinstance(self.qubit_layout, dict) and len(self.qubit_layout) > 0, "Invalid qubit layout"
        assert isinstance(self.stabilizer_map, dict) and len(self.stabilizer_map) > 0, "Invalid stabilizer map"
        assert isinstance(self.logical_operators, dict) and len(self.logical_operators) > 0, "Invalid logical operators"
        if isinstance(self.adjacency_matrix, nx.Graph):
            assert self.adjacency_matrix.number_of_nodes() > 0, "Adjacency matrix is empty"
        self._validate_stabilizers()

    def _validate_stabilizers(self):
        # Example: check that all stabilizers are mapped to valid qubits
        for stab, qubits in self.stabilizer_map.items():
            for q in qubits:
                assert q in self.qubit_layout, f"Stabilizer {stab} references invalid qubit {q}" 