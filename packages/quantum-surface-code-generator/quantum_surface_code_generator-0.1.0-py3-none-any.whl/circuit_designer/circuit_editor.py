import os
import yaml
import json
from typing import List, Dict, Any, Optional, Callable
from configuration_management.config_manager import ConfigManager

try:
    from qiskit import QuantumCircuit
except ImportError:
    QuantumCircuit = None

def get_provider_and_device(config_dir):
    hardware_json_path = os.path.join(config_dir, 'hardware.json')
    with open(hardware_json_path, 'r') as f:
        hw = json.load(f)
    return hw['provider_name'], hw['device_name']

class ConfigLoader:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or 'configs/editor_config.yaml'
        self.config = self.load_config(self.config_path)

    def load_config(self, path: str) -> dict:
        if path.endswith('.yaml') or path.endswith('.yml'):
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        elif path.endswith('.json'):
            with open(path, 'r') as f:
                return json.load(f)
        else:
            raise ValueError("Unsupported config file format.")

    def get_setting(self, key: str, default=None):
        return self.config.get(key, default)

    def reload(self):
        self.config = self.load_config(self.config_path)

class GatePalette:
    def __init__(self, gate_config: str = None):
        self.gate_config_path = gate_config or 'configs/gates.yaml'
        self.gates = self._load_gates(self.gate_config_path)

    def _load_gates(self, path: str) -> List[dict]:
        if path.endswith('.yaml') or path.endswith('.yml'):
            with open(path, 'r') as f:
                return yaml.safe_load(f).get('gates', [])
        elif path.endswith('.json'):
            with open(path, 'r') as f:
                return json.load(f).get('gates', [])
        else:
            raise ValueError("Unsupported gate config file format.")

    def get_gates(self) -> List[dict]:
        return self.gates

    def get_gate(self, name: str) -> dict:
        for g in self.gates:
            if g['name'] == name:
                return g
        raise ValueError(f"Gate {name} not found in palette.")

class QubitManager:
    def __init__(self, default_num_qubits: int = 5, max_qubits: int = 50):
        self.default_num_qubits = default_num_qubits
        self.max_qubits = max_qubits
        self.qubits = list(range(default_num_qubits))

    def add_qubit(self) -> int:
        if len(self.qubits) < self.max_qubits:
            new_idx = max(self.qubits) + 1 if self.qubits else 0
            self.qubits.append(new_idx)
            return new_idx
        raise ValueError("Maximum number of qubits reached.")

    def remove_qubit(self, idx: int) -> None:
        if idx in self.qubits:
            self.qubits.remove(idx)
        else:
            raise ValueError(f"Qubit {idx} not found.")

    def get_qubits(self) -> List[int]:
        return self.qubits

class CircuitEditor:
    def __init__(self, config_path: str = None, gate_config: str = None):
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.config
        self.palette = GatePalette(gate_config)
        self.default_num_qubits = self.config.get('default_num_qubits', 5)
        self.max_qubits = self.config.get('max_qubits', 50)
        self.grid_size = self.config.get('grid_size', 40)
        self.color_scheme = self.config.get('color_scheme', {})
        self.qubit_manager = QubitManager(self.default_num_qubits, self.max_qubits)
        self.circuit = {'qubits': self.qubit_manager.get_qubits(), 'gates': []}
        self.undo_stack: List[dict] = []
        self.redo_stack: List[dict] = []
        self.change_callbacks: List[Callable[[dict], None]] = []
        # --- Integration with backend workflow ---
        from .workflow_bridge import QuantumWorkflowBridge
        self.workflow_bridge = QuantumWorkflowBridge()

    # --- Qubit Management ---
    def add_qubit(self) -> int:
        idx = self.qubit_manager.add_qubit()
        self._push_undo()
        self.circuit['qubits'] = self.qubit_manager.get_qubits()
        self._notify_change()
        return idx

    def remove_qubit(self, idx: int) -> None:
        self.qubit_manager.remove_qubit(idx)
        self._push_undo()
        self.circuit['qubits'] = self.qubit_manager.get_qubits()
        # Remove gates on this qubit
        self.circuit['gates'] = [g for g in self.circuit['gates'] if idx not in g['qubits']]
        self._notify_change()

    # --- Gate Management ---
    def add_gate(self, gate_name: str, qubit: int, time: int, params: Optional[List[float]] = None) -> str:
        gate = self.palette.get_gate(gate_name)
        gate_id = f"g{len(self.circuit['gates'])}_{gate_name}_{qubit}_{time}"
        gate_obj = {
            'id': gate_id,
            'name': gate_name,
            'qubits': [qubit],
            'time': time,
            'params': params or [],
        }
        self._push_undo()
        self.circuit['gates'].append(gate_obj)
        self._notify_change()
        return gate_id

    def add_multi_qubit_gate(self, gate_name: str, qubits: List[int], time: int, params: Optional[List[float]] = None) -> str:
        gate = self.palette.get_gate(gate_name)
        if len(qubits) != gate.get('arity', 1):
            raise ValueError(f"Gate {gate_name} requires {gate.get('arity', 1)} qubits.")
        gate_id = f"g{len(self.circuit['gates'])}_{gate_name}_{'_'.join(map(str, qubits))}_{time}"
        gate_obj = {
            'id': gate_id,
            'name': gate_name,
            'qubits': qubits,
            'time': time,
            'params': params or [],
        }
        self._push_undo()
        self.circuit['gates'].append(gate_obj)
        self._notify_change()
        return gate_id

    def remove_gate(self, gate_id: str) -> None:
        self._push_undo()
        self.circuit['gates'] = [g for g in self.circuit['gates'] if g['id'] != gate_id]
        self._notify_change()

    def move_gate(self, gate_id: str, new_qubit: int, new_time: int) -> None:
        self._push_undo()
        for g in self.circuit['gates']:
            if g['id'] == gate_id:
                g['qubits'] = [new_qubit]
                g['time'] = new_time
        self._notify_change()

    def move_multi_qubit_gate(self, gate_id: str, new_qubits: List[int], new_time: int) -> None:
        self._push_undo()
        for g in self.circuit['gates']:
            if g['id'] == gate_id:
                g['qubits'] = new_qubits
                g['time'] = new_time
        self._notify_change()

    # --- Undo/Redo ---
    def _push_undo(self):
        self.undo_stack.append(json.loads(json.dumps(self.circuit)))
        self.redo_stack.clear()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(json.loads(json.dumps(self.circuit)))
            self.circuit = self.undo_stack.pop()
            self._notify_change()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(json.loads(json.dumps(self.circuit)))
            self.circuit = self.redo_stack.pop()
            self._notify_change()

    # --- Import/Export ---
    def export_circuit(self, path: str, format: str) -> None:
        if format == 'json':
            with open(path, 'w') as f:
                json.dump(self.circuit, f, indent=2)
        elif format in ('yaml', 'yml'):
            with open(path, 'w') as f:
                yaml.safe_dump(self.circuit, f)
        elif format == 'qasm':
            if QuantumCircuit is None:
                raise ImportError("qiskit is required for QASM export. Please install qiskit.")
            qc = self._dict_to_qiskit_circuit(self.circuit)
            with open(path, 'w') as f:
                f.write(qc.qasm())
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def import_circuit(self, path: str, format: str) -> None:
        if format == 'json':
            with open(path, 'r') as f:
                self.circuit = json.load(f)
        elif format in ('yaml', 'yml'):
            with open(path, 'r') as f:
                self.circuit = yaml.safe_load(f)
        elif format == 'qasm':
            if QuantumCircuit is None:
                raise ImportError("qiskit is required for QASM import. Please install qiskit.")
            qc = QuantumCircuit.from_qasm_file(path)
            self.circuit = self._qiskit_circuit_to_dict(qc)
        else:
            raise ValueError(f"Unsupported import format: {format}")
        self._notify_change()

    def _dict_to_qiskit_circuit(self, circuit: dict) -> 'QuantumCircuit':
        if QuantumCircuit is None:
            raise ImportError("qiskit is required for QASM export. Please install qiskit.")
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

    def _qiskit_circuit_to_dict(self, qc: 'QuantumCircuit') -> dict:
        circuit = {'qubits': list(range(qc.num_qubits)), 'gates': []}
        for instr, qargs, cargs in qc.data:
            gate = {'id': f"g{len(circuit['gates'])}_{instr.name}", 'name': instr.name, 'qubits': [q.index for q in qargs], 'params': [float(p) for p in instr.params] if instr.params else [], 'time': len(circuit['gates'])}
            circuit['gates'].append(gate)
        return circuit

    # --- Circuit Access & Notification ---
    def get_circuit(self) -> dict:
        return self.circuit

    def set_circuit(self, circuit: dict) -> None:
        self._push_undo()
        self.circuit = json.loads(json.dumps(circuit))
        self._notify_change()

    def register_change_callback(self, callback: Callable[[dict], None]):
        self.change_callbacks.append(callback)

    def _notify_change(self):
        for cb in self.change_callbacks:
            cb(self.circuit)

    # --- Backend Integration Methods ---
    def optimize_circuit_backend(self, device_info: dict, config_overrides: Optional[dict] = None, progress_callback=None) -> dict:
        return self.workflow_bridge.optimize_circuit(self.circuit, device_info, config_overrides, progress_callback=progress_callback)

    def generate_surface_code_layout_backend(self, layout_type: str, code_distance: int, device: str, config_overrides: Optional[dict] = None, progress_callback=None) -> dict:
        return self.workflow_bridge.generate_surface_code_layout(layout_type, code_distance, device, config_overrides, progress_callback=progress_callback)

    def map_circuit_to_surface_code_backend(self, device: str, layout_type: str, code_distance: int, provider: str = None, config_overrides: Optional[dict] = None, progress_callback=None) -> dict:
        return self.workflow_bridge.map_circuit_to_surface_code(self.circuit, device, layout_type, code_distance, provider, config_overrides, progress_callback=progress_callback)

    def identify_switching_points_backend(self, code_info: dict) -> list:
        return self.workflow_bridge.identify_switching_points(self.circuit, code_info)

    def select_switching_protocol_backend(self, gate: str, available_protocols: list, config: dict = None) -> str:
        return self.workflow_bridge.select_switching_protocol(gate, available_protocols, config)

    def apply_code_switching_backend(self, switching_points: list, protocols: list, device_info: dict) -> dict:
        return self.workflow_bridge.apply_code_switching(self.circuit, switching_points, protocols, device_info)

    def run_circuit_backend(self, backend_name: str, run_config: dict = None) -> str:
        return self.workflow_bridge.run_circuit(self.circuit, backend_name, run_config)

    def assemble_fault_tolerant_circuit_backend(self, mapping_info: dict, code_spaces: list, device_info: dict) -> dict:
        return self.workflow_bridge.assemble_fault_tolerant_circuit(self.circuit, mapping_info, code_spaces, device_info)

    def validate_fault_tolerant_circuit_backend(self, circuit: dict, device_info: dict) -> bool:
        return self.workflow_bridge.validate_fault_tolerant_circuit(circuit, device_info)

    def evaluate_logical_error_rate_backend(self, layout: dict, hardware: dict, noise_model: dict) -> float:
        return self.workflow_bridge.evaluate_logical_error_rate(layout, hardware, noise_model)

    def evaluate_resource_efficiency_backend(self, layout: dict) -> dict:
        return self.workflow_bridge.evaluate_resource_efficiency(layout)

    def evaluate_learning_efficiency_backend(self, training_log: any) -> dict:
        return self.workflow_bridge.evaluate_learning_efficiency(training_log)

    def evaluate_hardware_adaptability_backend(self, results: any) -> dict:
        return self.workflow_bridge.evaluate_hardware_adaptability(results)

    def log_event_backend(self, event: str, details: dict = None, level: str = 'INFO') -> None:
        self.workflow_bridge.log_event(event, details, level)

    def log_metric_backend(self, metric_name: str, value: float, step: int = None, run_id: str = None) -> None:
        self.workflow_bridge.log_metric(metric_name, value, step, run_id)

    def store_result_backend(self, run_id: str, result: dict) -> None:
        self.workflow_bridge.store_result(run_id, result)

    def get_result_backend(self, run_id: str) -> dict:
        return self.workflow_bridge.get_result(run_id)

    def run_full_workflow_backend(self, user_config: Optional[dict] = None) -> dict:
        return self.workflow_bridge.run_full_workflow(self.circuit, user_config)

    def get_workflow_status_backend(self, workflow_id: str) -> dict:
        return self.workflow_bridge.get_workflow_status(workflow_id)

    def run_full_fault_tolerant_workflow(self, device_info: dict, layout_type: str, code_distance: int, backend_name: str, run_config: dict = None) -> str:
        """
        Full workflow: optimize -> analyze for code switching -> apply code switching -> generate surface code layout ->
        transform to fault-tolerant circuit -> execute on hardware. Updates circuit and notifies UI at each step.
        Returns job_id for execution.
        """
        # 1. Optimize
        optimized = self.optimize_circuit_backend(device_info)
        self.circuit = optimized
        self._notify_change()

        # 2. Analyze for code switching (get supported gates from surface code API if available)
        # For demo, use a default set; in production, fetch from surface code API
        code_info = {"supported_gates": ["X", "Z", "CNOT"]}
        switching_points = self.identify_switching_points_backend(code_info)
        protocols = []
        if switching_points:
            # Select protocols for each switching point
            for sp in switching_points:
                proto = self.select_switching_protocol_backend(sp['gate'], ["magic_state_injection", "lattice_surgery"])
                protocols.append({"name": proto})
            # Apply code switching
            self.circuit = self.apply_code_switching_backend(switching_points, protocols, device_info)
            self._notify_change()

        # 3. Generate surface code layout
        layout = self.generate_surface_code_layout_backend(layout_type, code_distance, device_info['name'])

        # 4. Transform to fault-tolerant circuit
        mapping_info = {}  # Placeholder; in production, get from mapping step or surface code API
        code_spaces = []   # Placeholder; in production, get from surface code API
        ft_circuit = self.assemble_fault_tolerant_circuit_backend(mapping_info, code_spaces, device_info)
        self.circuit = ft_circuit
        self._notify_change()

        # 5. Execute on hardware
        job_id = self.run_circuit_backend(backend_name, run_config)
        return job_id 