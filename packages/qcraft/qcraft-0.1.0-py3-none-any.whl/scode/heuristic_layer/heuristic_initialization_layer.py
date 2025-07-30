from typing import Dict, Any
import networkx as nx
from .surface_code_object import SurfaceCodeObject
import matplotlib.pyplot as plt

class HeuristicInitializationLayer:
    def __init__(self, config: Dict[str, Any], device: Dict[str, Any]):
        self.config = config
        self.device = device

    def generate_surface_code(self, code_distance: int, layout_type: str, visualize: bool = False) -> SurfaceCodeObject:
        # Use device connectivity for adjacency matrix
        qubit_layout = self._generate_qubit_layout(code_distance, layout_type)
        stabilizer_map = self._generate_stabilizer_map(code_distance, layout_type, qubit_layout)
        logical_operators = self._generate_logical_operators(code_distance, layout_type, qubit_layout)
        adjacency_matrix = self._generate_adjacency_matrix_from_device(qubit_layout)
        surface_code = SurfaceCodeObject(
            qubit_layout=qubit_layout,
            stabilizer_map=stabilizer_map,
            logical_operators=logical_operators,
            adjacency_matrix=adjacency_matrix,
            code_distance=code_distance,
            layout_type=layout_type,
            grid_connectivity=self.device.get('topology_type', 'unknown')
        )
        if visualize:
            self._visualize_layout(surface_code)
        return surface_code

    def _generate_qubit_layout(self, code_distance, layout_type):
        if layout_type == 'planar':
            # Existing planar logic
            qubit_layout = {}
            idx = 0
            for x in range(code_distance):
                for y in range(code_distance):
                    qubit_layout[idx] = {'x': x, 'y': y, 'type': 'data'}
                    idx += 1
            ancilla_idx = idx
            for x in range(code_distance):
                for y in range(code_distance):
                    if (x + y) % 2 == 0:
                        qubit_layout[ancilla_idx] = {'x': x + 0.3, 'y': y + 0.3, 'type': 'ancilla_X'}
                        ancilla_idx += 1
                    else:
                        qubit_layout[ancilla_idx] = {'x': x + 0.7, 'y': y + 0.7, 'type': 'ancilla_Z'}
                        ancilla_idx += 1
            return qubit_layout
        elif layout_type == 'rotated':
            # Rotated: place data qubits along diagonals
            qubit_layout = {}
            idx = 0
            for x in range(code_distance):
                for y in range(code_distance):
                    # Rotate by 45 degrees: (x, y) -> (x-y, x+y)
                    qubit_layout[idx] = {'x': (x - y) / 1.414, 'y': (x + y) / 1.414, 'type': 'data'}
                    idx += 1
            ancilla_idx = idx
            for x in range(code_distance):
                for y in range(code_distance):
                    if (x + y) % 2 == 0:
                        qubit_layout[ancilla_idx] = {'x': (x - y) / 1.414 + 0.3, 'y': (x + y) / 1.414 + 0.3, 'type': 'ancilla_X'}
                        ancilla_idx += 1
                    else:
                        qubit_layout[ancilla_idx] = {'x': (x - y) / 1.414 + 0.7, 'y': (x + y) / 1.414 + 0.7, 'type': 'ancilla_Z'}
                        ancilla_idx += 1
            return qubit_layout
        elif layout_type == 'color':
            raise NotImplementedError('Color code layout not implemented yet.')
        else:
            raise ValueError(f'Unknown layout_type: {layout_type}')

    def _generate_stabilizer_map(self, code_distance, layout_type, qubit_layout):
        # Assign each stabilizer to its ancilla qubit
        stabilizer_map = {'X': [], 'Z': []}
        for q, info in qubit_layout.items():
            if info['type'] == 'ancilla_X':
                stabilizer_map['X'].append(q)
            elif info['type'] == 'ancilla_Z':
                stabilizer_map['Z'].append(q)
        return stabilizer_map

    def _generate_logical_operators(self, code_distance, layout_type, qubit_layout):
        # Assign logical X to the first row, logical Z to the last column of data qubits
        data_qubits = [q for q, info in qubit_layout.items() if info['type'] == 'data']
        # Build a 2D grid mapping for data qubits
        grid = {}
        for q in data_qubits:
            x, y = qubit_layout[q]['x'], qubit_layout[q]['y']
            grid[(round(x), round(y))] = q
        logical_x = []
        logical_z = []
        if layout_type in ('planar', 'rotated'):
            # Logical X: first row (y=0)
            logical_x = [grid[(x, 0)] for x in range(code_distance) if (x, 0) in grid]
            # Logical Z: last column (x=code_distance-1)
            logical_z = [grid[(code_distance-1, y)] for y in range(code_distance) if (code_distance-1, y) in grid]
        else:
            raise NotImplementedError(f'Logical operator assignment not implemented for layout_type={layout_type}')
        return {'X': logical_x, 'Z': logical_z}

    def _generate_adjacency_matrix_from_device(self, qubit_layout):
        G = nx.Graph()
        for q, pos in qubit_layout.items():
            G.add_node(q, **pos)
        # Use device's qubit_connectivity
        connectivity = self.device.get('qubit_connectivity', {})
        for q, neighbors in connectivity.items():
            for n in neighbors:
                if int(q) in qubit_layout and int(n) in qubit_layout:
                    G.add_edge(int(q), int(n))
        return G

    def _visualize_layout(self, surface_code: SurfaceCodeObject):
        qubit_layout = surface_code.qubit_layout
        data_x, data_y = [], []
        anc_x, anc_y, anc_types = [], [], []
        for q, info in qubit_layout.items():
            if info['type'] == 'data':
                data_x.append(info['x'])
                data_y.append(info['y'])
            else:
                anc_x.append(info['x'])
                anc_y.append(info['y'])
                anc_types.append(info['type'])
        plt.figure(figsize=(7, 7))
        plt.scatter(data_x, data_y, c='blue', label='Data Qubits', s=100)
        if anc_x:
            for t in set(anc_types):
                idxs = [i for i, typ in enumerate(anc_types) if typ == t]
                plt.scatter([anc_x[i] for i in idxs], [anc_y[i] for i in idxs], label=t, s=80, marker='x' if 'X' in t else 'o')
        plt.title(f"Surface Code Layout: d={surface_code.code_distance}, {surface_code.layout_type}")
        plt.xlabel('x')
        plt.ylabel('y')
        plt.legend()
        plt.grid(True)
        plt.show() 