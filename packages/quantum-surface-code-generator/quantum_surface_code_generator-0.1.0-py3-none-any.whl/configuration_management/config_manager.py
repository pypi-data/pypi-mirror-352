import os
import yaml
import json
from .schema_validator import SchemaValidator

class ConfigManager:
    config_registry = {}
    env_path = '.env'
    _env_cache = None

    @classmethod
    def load_registry(cls, registry_path='configs/config_registry.yaml'):
        """Load the config registry mapping module names to config file paths."""
        with open(registry_path, 'r') as f:
            cls.config_registry = yaml.safe_load(f)['config_registry']

    @classmethod
    def load_config(cls, module_name, config_path=None):
        """Load a YAML or JSON config for a module."""
        if not config_path:
            config_path = cls.config_registry.get(module_name)
        if config_path.endswith('.yaml') or config_path.endswith('.yml'):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        elif config_path.endswith('.json'):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            raise ValueError("Unsupported config file format.")

    @classmethod
    def get_config(cls, module_name):
        """Get the current config for a module."""
        return cls.load_config(module_name)

    @classmethod
    def update_config(cls, module_name, updates):
        """Update a config for a module and save it. Notifies frontend if registered."""
        config = cls.get_config(module_name)
        config.update(updates)
        cls.save_config(module_name, config_path=None, config=config)
        cls._notify_config_change(module_name, config)

    @classmethod
    def save_config(cls, module_name, config_path=None, config=None):
        """Save a config for a module to file."""
        if not config_path:
            config_path = cls.config_registry.get(module_name)
        if config is None:
            config = cls.get_config(module_name)
        if config_path.endswith('.yaml') or config_path.endswith('.yml'):
            with open(config_path, 'w') as f:
                yaml.safe_dump(config, f)
        elif config_path.endswith('.json'):
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
        else:
            raise ValueError("Unsupported config file format.")

    @classmethod
    def list_configs(cls):
        """List all registered config modules/files."""
        return list(cls.config_registry.keys())

    @classmethod
    def load_hardware_json(cls, path=None):
        """Load hardware.json specifying provider_name and device_name."""
        if not path:
            path = cls.config_registry.get('hardware')
        with open(path, 'r') as f:
            return json.load(f)

    @classmethod
    def update_hardware_json(cls, updates):
        """Update hardware.json with new provider/device selection."""
        path = cls.config_registry.get('hardware')
        hardware = cls.load_hardware_json(path)
        hardware.update(updates)
        with open(path, 'w') as f:
            json.dump(hardware, f, indent=2)

    @classmethod
    def resolve_device_config(cls, provider_name):
        """Return the path to the provider-specific device config file."""
        key = f'{provider_name}_devices'
        return cls.config_registry.get(key)

    @classmethod
    def validate_config(cls, module_name, schema_path=None):
        """Validate a config against a schema."""
        config = cls.get_config(module_name)
        if not schema_path:
            schema_path = f'schemas/{module_name}.schema.yaml'
        return SchemaValidator.validate(config, schema_path)

    @classmethod
    def get_schema(cls, module_name):
        """Get the schema for a module's config."""
        schema_path = f'schemas/{module_name}.schema.yaml'
        with open(schema_path, 'r') as f:
            return yaml.safe_load(f) 

    @classmethod
    def get_outputs_dir(cls):
        """Return the absolute path to the outputs directory (for results, metrics, etc.)."""
        return os.path.abspath('outputs')

    @classmethod
    def get_training_artifacts_dir(cls):
        """Return the absolute path to the training_artifacts directory (for RL models, etc.)."""
        return os.path.abspath('training_artifacts')

    @classmethod
    def ensure_output_dirs(cls):
        """Ensure that outputs and training_artifacts directories exist."""
        os.makedirs(cls.get_outputs_dir(), exist_ok=True)
        os.makedirs(cls.get_training_artifacts_dir(), exist_ok=True)

    # --- PySide6/Frontend Integration ---
    _config_change_callbacks = []

    @classmethod
    def register_config_change_callback(cls, callback):
        """Register a callback to be called when any config is updated (for frontend live reload)."""
        if callback not in cls._config_change_callbacks:
            cls._config_change_callbacks.append(callback)

    @classmethod
    def _notify_config_change(cls, module_name, config):
        """Notify all registered callbacks of a config change."""
        for cb in cls._config_change_callbacks:
            try:
                cb(module_name, config)
            except Exception as e:
                print(f"ConfigManager callback error: {e}")

    @classmethod
    def hot_reload_config(cls, module_name):
        """Reload a config from disk (for frontend live reload)."""
        return cls.get_config(module_name)

    # --- .env API Key Management ---
    @classmethod
    def ensure_env_file(cls):
        if not os.path.exists(cls.env_path):
            with open(cls.env_path, 'w') as f:
                f.write('# Provider API keys\n')

    @classmethod
    def load_env(cls):
        cls.ensure_env_file()
        env = {}
        with open(cls.env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if ':' in line:
                    k, v = line.split(':', 1)
                    env[k.strip()] = v.strip()
        cls._env_cache = env
        return env

    @classmethod
    def get_api_key(cls, provider_name):
        env = cls._env_cache or cls.load_env()
        key = f'{provider_name}_api_key'
        return env.get(key)

    @classmethod
    def set_api_key(cls, provider_name, api_key):
        env = cls._env_cache or cls.load_env()
        key = f'{provider_name}_api_key'
        env[key] = api_key
        cls.save_env(env)

    @classmethod
    def save_env(cls, env):
        with open(cls.env_path, 'w') as f:
            f.write('# Provider API keys\n')
            for k, v in env.items():
                f.write(f'{k}: {v}\n')
        cls._env_cache = env 