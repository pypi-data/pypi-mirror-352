from typing import Dict, Any
import networkx as nx
from scode.heuristic_layer.surface_code_object import SurfaceCodeObject

class ConnectivityAwareGraphTransformer:
    def __init__(self, config: Dict[str, Any], hardware_graph: Dict[str, Any], native_gates: list, gate_error_rates: Dict[str, float], qubit_error_rates: Dict[int, float]):
        self.config = config
        self.hardware_graph = hardware_graph
        self.native_gates = native_gates
        self.gate_error_rates = gate_error_rates
        self.qubit_error_rates = qubit_error_rates

    def transform(self, surface_code_object: SurfaceCodeObject) -> Dict[str, Any]:
        # Pre-transfer validation
        try:
            surface_code_object.validate()
        except Exception as e:
            raise ValueError(f"SurfaceCodeObject validation failed before graph transformation: {e}")
        # Parse hardware coupling map
        hw_graph = self._parse_hardware_graph(self.hardware_graph)
        # Map logical qubits to physical qubits (simple mapping for now)
        mapping = {lq: lq for lq in surface_code_object.qubit_layout.keys()}
        # Remap stabilizers and logical ops
        hardware_stabilizer_map = self._remap_stabilizers(surface_code_object.stabilizer_map, mapping)
        # Calculate connectivity overhead (SWAPs, delays, cost)
        connectivity_overhead_info = self._compute_connectivity_overhead(hw_graph, mapping)
        # Annotated graph
        annotated_graph = self._annotate_graph(hw_graph)
        return {
            'transformed_layout': mapping,
            'hardware_stabilizer_map': hardware_stabilizer_map,
            'connectivity_overhead_info': connectivity_overhead_info,
            'annotated_graph': annotated_graph
        }

    def _parse_hardware_graph(self, hardware_graph: Dict[str, Any]) -> nx.Graph:
        G = nx.Graph()
        for q, neighbors in hardware_graph['qubit_connectivity'].items():
            for n in neighbors:
                G.add_edge(int(q), int(n))
        return G

    def _remap_stabilizers(self, stabilizer_map: Dict[str, Any], mapping: Dict[int, int]) -> Dict[str, Any]:
        remapped = {}
        for stab, qubits in stabilizer_map.items():
            remapped[stab] = [mapping[q] for q in qubits]
        return remapped

    def _compute_connectivity_overhead(self, hw_graph: nx.Graph, mapping: Dict[int, int]) -> Dict[str, Any]:
        # Estimate SWAPs, delays, and cost for mapped layout
        swaps = 0
        delays = 0
        cost = 0.0
        # For each logical-physical mapping, check if mapped qubits are neighbors; if not, count as SWAP
        for lq, pq in mapping.items():
            for lq2, pq2 in mapping.items():
                if lq < lq2:
                    if not hw_graph.has_edge(pq, pq2):
                        swaps += 1
                        delays += 1  # Simplified: 1 delay per SWAP
                        cost += 1.0  # Simplified: 1 cost per SWAP
        return {'SWAPs': swaps, 'delays': delays, 'cost': cost}

    def _annotate_graph(self, hw_graph: nx.Graph) -> nx.Graph:
        # Add gate latency/fidelity as edge attributes if available
        for u, v in hw_graph.edges():
            hw_graph[u][v]['latency'] = self.gate_error_rates.get('latency', 1.0)
            hw_graph[u][v]['fidelity'] = 1.0 - self.gate_error_rates.get('error_rate', 0.01)
        for n in hw_graph.nodes():
            hw_graph.nodes[n]['qubit_error_rate'] = self.qubit_error_rates.get(n, 0.0)
        return hw_graph 