import os
import yaml
import json
from typing import List, Dict, Any, Optional, Callable
from configuration_management.config_manager import ConfigManager

try:
    from qiskit import QuantumCircuit
except ImportError:
    QuantumCircuit = None

class ConfigLoader:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or 'configs/ft_builder_config.yaml'
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

class FaultTolerantCircuitBuilder:
    def __init__(self, config_path: str = None):
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.config
        self.export_formats = self.config.get('export_formats', ['qasm', 'json', 'yaml'])
        self.code_switching_protocols = self.config.get('code_switching_protocols', [])
        # Extensibility: dynamic protocol and handler registration
        self.protocol_registry = {p['name']: p for p in self.code_switching_protocols}
        self.export_handlers = {}
        self.import_handlers = {}
        self.code_space_annotation_hooks: List[Callable[[dict, List[dict]], dict]] = []
        self.validation_hooks: List[Callable[[dict, dict], bool]] = []
        self.summary_hooks: List[Callable[[dict], dict]] = []

    # --- Extensibility APIs ---
    def register_code_switching_protocol(self, protocol: dict):
        self.protocol_registry[protocol['name']] = protocol

    def register_export_handler(self, fmt: str, handler: Callable[[dict, str], None]):
        self.export_handlers[fmt] = handler
        if fmt not in self.export_formats:
            self.export_formats.append(fmt)

    def register_import_handler(self, fmt: str, handler: Callable[[str], dict]):
        self.import_handlers[fmt] = handler
        if fmt not in self.export_formats:
            self.export_formats.append(fmt)

    def register_code_space_annotation_hook(self, hook: Callable[[dict, List[dict]], dict]):
        self.code_space_annotation_hooks.append(hook)

    def register_validation_hook(self, hook: Callable[[dict, dict], bool]):
        self.validation_hooks.append(hook)

    def register_summary_hook(self, hook: Callable[[dict], dict]):
        self.summary_hooks.append(hook)

    def reload_config(self):
        self.config_loader.reload()
        self.config = self.config_loader.config
        self.export_formats = self.config.get('export_formats', ['qasm', 'json', 'yaml'])
        self.code_switching_protocols = self.config.get('code_switching_protocols', [])
        self.protocol_registry = {p['name']: p for p in self.code_switching_protocols}

    # --- Main APIs ---
    def assemble_fault_tolerant_circuit(self, logical_circuit: dict, mapping_info: dict, code_spaces: List[dict], device_info: dict) -> dict:
        circuit = self._apply_mapping(logical_circuit, mapping_info, code_spaces)
        if not self.validate_fault_tolerant_circuit(circuit, device_info):
            raise ValueError("Assembled circuit is not valid for the target device.")
        return circuit

    def _apply_mapping(self, logical_circuit: dict, mapping_info: dict, code_spaces: List[dict]) -> dict:
        circuit = {'qubits': logical_circuit.get('qubits', []), 'gates': []}
        logical_to_physical = mapping_info.get('logical_to_physical', {})
        for gate in logical_circuit.get('gates', []):
            mapped_gate = gate.copy()
            mapped_gate['qubits'] = [logical_to_physical.get(q, q) for q in gate.get('qubits', [])]
            # Flexible code space annotation
            for hook in self.code_space_annotation_hooks:
                mapped_gate = hook(mapped_gate, code_spaces)
            # Default annotation if no hook
            if not any(hook for hook in self.code_space_annotation_hooks):
                for cs in code_spaces:
                    if gate['name'] in cs.get('supported_gates', []):
                        mapped_gate['code_space'] = cs['name']
            circuit['gates'].append(mapped_gate)
        circuit['code_spaces'] = code_spaces
        return circuit

    def insert_code_switching(self, circuit: dict, switching_points: List[dict], code_spaces: List[dict]) -> dict:
        gates = circuit.get('gates', [])
        new_gates = []
        for i, gate in enumerate(gates):
            new_gates.append(gate)
            for sp in switching_points:
                if sp['index'] == i:
                    protocol = self.protocol_registry.get(sp['to_code_space']) or next((cs for cs in code_spaces if cs['name'] == sp['to_code_space']), None)
                    if protocol:
                        new_gates.append({'name': f'code_switch_{protocol["name"]}', 'qubits': gate['qubits'], 'params': [], 'code_space': protocol['name']})
        circuit['gates'] = new_gates
        return circuit

    def validate_fault_tolerant_circuit(self, circuit: dict, device_info: dict) -> bool:
        # Built-in validation
        if len(circuit.get('qubits', [])) > device_info.get('qubit_count', 0):
            return False
        native_gates = set(device_info.get('native_gates', []))
        for gate in circuit.get('gates', []):
            if gate['name'] not in native_gates and not gate['name'].startswith('code_switch_'):
                return False
        # Extensible validation
        for hook in self.validation_hooks:
            if not hook(circuit, device_info):
                return False
        return True

    def export_circuit(self, circuit: dict, format: str, path: str) -> None:
        if format in self.export_handlers:
            self.export_handlers[format](circuit, path)
        elif format == 'json':
            with open(path, 'w') as f:
                json.dump(circuit, f, indent=2)
        elif format in ('yaml', 'yml'):
            with open(path, 'w') as f:
                yaml.safe_dump(circuit, f)
        elif format == 'qasm':
            if QuantumCircuit is None:
                raise ImportError("qiskit is required for QASM export. Please install qiskit.")
            qc = self._dict_to_qiskit_circuit(circuit)
            with open(path, 'w') as f:
                f.write(qc.qasm())
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def import_circuit(self, path: str, format: str) -> dict:
        if format in self.import_handlers:
            return self.import_handlers[format](path)
        elif format == 'json':
            with open(path, 'r') as f:
                return json.load(f)
        elif format in ('yaml', 'yml'):
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        elif format == 'qasm':
            if QuantumCircuit is None:
                raise ImportError("qiskit is required for QASM import. Please install qiskit.")
            qc = QuantumCircuit.from_qasm_file(path)
            return self._qiskit_circuit_to_dict(qc)
        else:
            raise ValueError(f"Unsupported import format: {format}")

    def get_supported_export_formats(self) -> List[str]:
        return self.export_formats

    def get_circuit_summary(self, circuit: dict) -> dict:
        qubit_count = len(circuit.get('qubits', []))
        gate_count = len(circuit.get('gates', []))
        depth = self._calculate_depth(circuit)
        code_switch_points = [i for i, g in enumerate(circuit.get('gates', [])) if g['name'].startswith('code_switch_')]
        summary = {
            'qubit_count': qubit_count,
            'gate_count': gate_count,
            'depth': depth,
            'code_switch_points': code_switch_points,
        }
        # Extensible summary
        for hook in self.summary_hooks:
            summary.update(hook(circuit))
        return summary

    def _calculate_depth(self, circuit: dict) -> int:
        if not circuit.get('gates'):
            return 0
        qubit_timesteps = {q: 0 for q in circuit.get('qubits', [])}
        for gate in circuit['gates']:
            max_t = max([qubit_timesteps.get(q, 0) for q in gate.get('qubits', [])], default=0)
            for q in gate.get('qubits', []):
                qubit_timesteps[q] = max_t + 1
        return max(qubit_timesteps.values(), default=0)

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
            gate = {'name': instr.name, 'qubits': [q.index for q in qargs]}
            if instr.params:
                gate['params'] = [float(p) for p in instr.params]
            circuit['gates'].append(gate)
        return circuit 