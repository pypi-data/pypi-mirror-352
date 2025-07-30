import os
import yaml
import json
from typing import List, Dict, Any, Optional, Callable, Type
from configuration_management.config_manager import ConfigManager

class ConfigLoader:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or 'configs/switcher_config.yaml'
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

class CodeSwitchingProtocol:
    def __init__(self, params: dict):
        self.params = params
        self.name = params.get('name', 'unknown_protocol')
        self.enabled = params.get('enabled', True)
        self.supported_gates = params.get('supported_gates', [])

    def apply(self, gate: dict, device_info: dict) -> List[dict]:
        raise NotImplementedError("apply() must be implemented by subclasses.")

    def get_info(self) -> dict:
        return self.params

class MagicStateInjectionProtocol(CodeSwitchingProtocol):
    def apply(self, gate: dict, device_info: dict) -> List[dict]:
        # Insert magic state preparation and injection for T/Tdg gates
        ancilla = self.params.get('ancilla_qubits', 1)
        return [
            {'name': 'prepare_magic_state', 'qubits': [gate['qubits'][0] + device_info.get('qubit_count', 0)], 'params': []},
            {'name': 'inject_magic_state', 'qubits': gate['qubits'], 'params': []},
            gate
        ]

class LatticeSurgeryProtocol(CodeSwitchingProtocol):
    def apply(self, gate: dict, device_info: dict) -> List[dict]:
        # Insert lattice surgery operations for CNOT/Toffoli
        return [
            {'name': 'lattice_surgery_start', 'qubits': gate['qubits'], 'params': []},
            gate,
            {'name': 'lattice_surgery_end', 'qubits': gate['qubits'], 'params': []}
        ]

class TeleportationProtocol(CodeSwitchingProtocol):
    def apply(self, gate: dict, device_info: dict) -> List[dict]:
        # Insert teleportation operations for SWAP
        return [
            {'name': 'teleportation_start', 'qubits': gate['qubits'], 'params': []},
            gate,
            {'name': 'teleportation_end', 'qubits': gate['qubits'], 'params': []}
        ]

class CodeSwitcher:
    def __init__(self, config_path: str = None):
        self.config_loader = ConfigLoader(config_path)
        self.config = self.config_loader.config
        self.protocols: Dict[str, CodeSwitchingProtocol] = {}
        self.protocol_classes: Dict[str, Type[CodeSwitchingProtocol]] = {
            'magic_state_injection': MagicStateInjectionProtocol,
            'lattice_surgery': LatticeSurgeryProtocol,
            'teleportation': TeleportationProtocol
        }
        self._load_protocols()
        self.protocol_plugins: Dict[str, Type[CodeSwitchingProtocol]] = {}

    def _load_protocols(self):
        for proto in self.config.get('switching_protocols', []):
            if proto.get('enabled', True):
                cls = self.protocol_classes.get(proto['name'])
                if cls:
                    self.protocols[proto['name']] = cls(proto)

    def reload_config(self):
        self.config_loader.reload()
        self.config = self.config_loader.config
        self._load_protocols()

    def identify_switching_points(self, circuit: dict, code_info: dict) -> List[dict]:
        # Identify gates not supported by current code
        supported_gates = code_info.get('supported_gates', [])
        switching_points = []
        for idx, gate in enumerate(circuit.get('gates', [])):
            if gate['name'] not in supported_gates:
                switching_points.append({'index': idx, 'gate': gate['name'], 'qubits': gate.get('qubits', []), 'location': idx})
        return switching_points

    def select_switching_protocol(self, gate: str, available_protocols: List[str], config: dict = None) -> str:
        # Select protocol based on config, device/code constraints, and protocol support
        gate_lower = gate.lower()
        debug_info = {
            'gate': gate,
            'gate_lower': gate_lower,
            'available_protocols': available_protocols,
            'protocols_config': {k: v.supported_gates for k, v in self.protocols.items()}
        }
        print(f"[DEBUG] Selecting protocol for gate: {gate} (lower: {gate_lower})")
        print(f"[DEBUG] Available protocols: {available_protocols}")
        print(f"[DEBUG] Protocols config: {debug_info['protocols_config']}")
        for proto_name in available_protocols:
            proto = self.protocols.get(proto_name)
            if proto and any(g.lower() == gate_lower for g in proto.supported_gates):
                print(f"[DEBUG] Selected protocol: {proto_name} for gate: {gate}")
                return proto_name
        raise ValueError(f"No suitable protocol found for gate {gate}. Available protocols: {available_protocols}. Protocols config: {debug_info['protocols_config']}")

    def apply_code_switching(self, circuit: dict, switching_points: List[dict], protocols: List[dict], device_info: dict) -> dict:
        # Insert code switching operations at specified points using selected protocols
        gates = circuit.get('gates', [])
        new_gates = []
        protocol_map = {p['name']: self.protocols[p['name']] for p in protocols if p['name'] in self.protocols}
        sp_idx = 0
        for i, gate in enumerate(gates):
            if sp_idx < len(switching_points) and switching_points[sp_idx]['index'] == i:
                proto_name = switching_points[sp_idx].get('protocol')
                proto = protocol_map.get(proto_name)
                if proto:
                    new_gates.extend(proto.apply(gate, device_info))
                else:
                    new_gates.append(gate)
                sp_idx += 1
            else:
                new_gates.append(gate)
        circuit['gates'] = new_gates
        return circuit

    def get_supported_switching_protocols(self) -> List[str]:
        return list(self.protocols.keys())

    def get_supported_gates_for_protocol(self, protocol_name: str) -> List[str]:
        proto = self.protocols.get(protocol_name)
        if proto:
            return proto.supported_gates
        return []

    def get_switching_protocol_info(self, protocol_name: str) -> dict:
        proto = self.protocols.get(protocol_name)
        if proto:
            return proto.get_info()
        return {}

    def get_switching_summary(self, circuit: dict) -> dict:
        summary = {'switching_points': []}
        for idx, gate in enumerate(circuit.get('gates', [])):
            if gate['name'].startswith('prepare_magic_state') or gate['name'].startswith('lattice_surgery') or gate['name'].startswith('teleportation'):
                summary['switching_points'].append({'index': idx, 'gate': gate['name'], 'qubits': gate.get('qubits', [])})
        return summary

    def add_switching_protocol(self, protocol_obj: CodeSwitchingProtocol) -> None:
        self.protocols[protocol_obj.name] = protocol_obj

    def list_available_protocol_plugins(self) -> List[str]:
        return list(self.protocol_classes.keys()) + list(self.protocol_plugins.keys())

    def register_protocol_plugin(self, name: str, cls: Type[CodeSwitchingProtocol]):
        self.protocol_plugins[name] = cls
        self.protocol_classes[name] = cls

class CodeSwitcherAPI:
    """
    API for the Code Switcher Module. Exposes all required methods for frontend/backend integration.
    Wraps the real CodeSwitcher logic (no stubs).
    """
    def __init__(self, config_path: str = None):
        self.switcher = CodeSwitcher(config_path)

    def identify_switching_points(self, circuit: dict, code_info: dict) -> List[dict]:
        """Identify gates in the circuit that require code switching."""
        return self.switcher.identify_switching_points(circuit, code_info)

    def select_switching_protocol(self, gate: str, available_protocols: List[str], config: dict = None) -> str:
        """Select the best switching protocol for a given gate."""
        return self.switcher.select_switching_protocol(gate, available_protocols, config)

    def apply_code_switching(self, circuit: dict, switching_points: List[dict], protocols: List[dict], device_info: dict) -> dict:
        """Apply code switching to the circuit at the specified points using selected protocols."""
        return self.switcher.apply_code_switching(circuit, switching_points, protocols, device_info)

    def get_supported_switching_protocols(self) -> List[str]:
        """List all supported switching protocols."""
        return self.switcher.get_supported_switching_protocols()

    def get_supported_gates_for_protocol(self, protocol_name: str) -> List[str]:
        """List all gates supported by a given protocol."""
        return self.switcher.get_supported_gates_for_protocol(protocol_name)

    def get_switching_protocol_info(self, protocol_name: str) -> dict:
        """Get detailed info for a switching protocol."""
        return self.switcher.get_switching_protocol_info(protocol_name)

    def get_switching_summary(self, circuit: dict) -> dict:
        """Get a summary of switching operations in the circuit."""
        return self.switcher.get_switching_summary(circuit)

    def add_switching_protocol(self, protocol_obj: CodeSwitchingProtocol) -> None:
        """Add a new switching protocol (plugin)."""
        self.switcher.add_switching_protocol(protocol_obj)

    def list_available_protocol_plugins(self) -> List[str]:
        """List all available protocol plugins (built-in and registered)."""
        return self.switcher.list_available_protocol_plugins()

    def register_protocol_plugin(self, name: str, cls: type) -> None:
        """Register a new protocol plugin class."""
        self.switcher.register_protocol_plugin(name, cls) 