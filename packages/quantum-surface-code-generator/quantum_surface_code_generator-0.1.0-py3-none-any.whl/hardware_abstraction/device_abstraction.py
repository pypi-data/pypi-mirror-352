import os
import yaml
import json
from typing import List, Dict, Any
from configuration_management.config_manager import ConfigManager

class DeviceAbstraction:
    """
    Device Abstraction Module for managing device information, validation, and config-driven device logic.
    All configuration is YAML/JSON-driven and APIs are pure Python for frontend/backend integration.
    """
    @staticmethod
    def load_selected_device(hardware_json_path: str) -> dict:
        """
        Load the provider and device name from hardware.json, select the correct provider config file, and return the features of the specified device.
        """
        with open(hardware_json_path, 'r') as f:
            hw = json.load(f)
        provider = hw['provider_name'].lower()
        device_name = hw['device_name']
        config_path = ConfigManager.resolve_device_config(provider)
        with open(config_path, 'r') as f:
            devices = yaml.safe_load(f)
        key = 'devices'
        for dev in devices.get(key, []):
            if dev.get('name') == device_name or dev.get('device_name') == device_name:
                return dev
        raise ValueError(f"Device {device_name} not found in {config_path}")

    @staticmethod
    def list_devices(provider_name: str) -> List[str]:
        """
        Return a list of all available device names for a given provider.
        """
        config_path = ConfigManager.resolve_device_config(provider_name)
        with open(config_path, 'r') as f:
            devices_yaml = yaml.safe_load(f)
        # Try 'devices' first
        device_list = devices_yaml.get('devices', None)
        used_key = 'devices'
        if device_list is None:
            # Fallback: find the first key ending with '_devices'
            for key in devices_yaml:
                if key.endswith('_devices'):
                    device_list = devices_yaml[key]
                    used_key = key
                    break
        if device_list is None:
            print(f"[DeviceAbstraction] No devices found in {config_path}")
            return []
        print(f"[DeviceAbstraction] Using key '{used_key}' from {config_path} for device list.")
        return [dev.get('name') or dev.get('device_name') for dev in device_list]

    @staticmethod
    def get_device_info(provider_name: str, device_name: str) -> dict:
        """
        Return detailed information for the specified device from the correct provider config file.
        """
        config_path = ConfigManager.resolve_device_config(provider_name)
        with open(config_path, 'r') as f:
            devices = yaml.safe_load(f)
        for dev in devices.get('devices', []):
            if dev.get('name') == device_name or dev.get('device_name') == device_name:
                return dev
        raise ValueError(f"Device {device_name} not found in {config_path}")

    @staticmethod
    def validate_device_config(device_config: dict) -> bool:
        """
        Validate a device configuration against the required schema.
        """
        # Use schema from schemas/{provider}_devices.schema.yaml
        provider = device_config.get('provider_name', '').lower() or device_config.get('name', '').split('_')[0]
        schema_path = f'schemas/{provider}_devices.schema.yaml'
        if not os.path.exists(schema_path):
            return True  # No schema, assume valid
        with open(schema_path, 'r') as f:
            schema = yaml.safe_load(f)
        # Simple validation: check required fields
        required = schema.get('required', [])
        for field in required:
            if field not in device_config:
                return False
        return True

    @staticmethod
    def add_device(provider_name: str, device_config: dict) -> None:
        """
        Add a new device configuration to the correct provider config file at runtime.
        """
        config_path = ConfigManager.resolve_device_config(provider_name)
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        if 'devices' not in data:
            data['devices'] = []
        data['devices'].append(device_config)
        with open(config_path, 'w') as f:
            yaml.safe_dump(data, f)

    @staticmethod
    def remove_device(provider_name: str, device_name: str) -> None:
        """
        Remove a device configuration from the correct provider config file.
        """
        config_path = ConfigManager.resolve_device_config(provider_name)
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        data['devices'] = [dev for dev in data.get('devices', []) if dev.get('name') != device_name and dev.get('device_name') != device_name]
        with open(config_path, 'w') as f:
            yaml.safe_dump(data, f)

    @staticmethod
    def update_device(provider_name: str, device_name: str, updates: dict) -> None:
        """
        Update properties of an existing device configuration in the correct provider config file.
        """
        config_path = ConfigManager.resolve_device_config(provider_name)
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        for dev in data.get('devices', []):
            if dev.get('name') == device_name or dev.get('device_name') == device_name:
                dev.update(updates)
        with open(config_path, 'w') as f:
            yaml.safe_dump(data, f)

    @staticmethod
    def is_gate_supported(provider_name: str, device_name: str, gate: str) -> bool:
        """
        Check if a gate is natively supported by the device.
        """
        dev = DeviceAbstraction.get_device_info(provider_name, device_name)
        return gate in dev.get('native_gates', [])

    @staticmethod
    def get_native_gates(provider_name: str, device_name: str) -> List[str]:
        """
        Return the list of native gates for the device.
        """
        dev = DeviceAbstraction.get_device_info(provider_name, device_name)
        return dev.get('native_gates', [])

    @staticmethod
    def validate_circuit_for_device(circuit: dict, provider_name: str, device_name: str) -> bool:
        """
        Validate that a circuit is compatible with the device (native gates, connectivity, qubit count, etc.).
        """
        dev = DeviceAbstraction.get_device_info(provider_name, device_name)
        if len(circuit.get('qubits', [])) > dev.get('qubit_count', 0):
            return False
        native_gates = set(dev.get('native_gates', []))
        for gate in circuit.get('gates', []):
            if gate['name'] not in native_gates:
                return False
        # Optionally check connectivity here
        return True

    @staticmethod
    def get_current_provider_name():
        hw = ConfigManager.load_hardware_json()
        return hw.get('provider_name') 