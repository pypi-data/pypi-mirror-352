import os
from typing import List, Dict, Any, Optional
import importlib
import io
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
import json, yaml

# Device abstraction
from hardware_abstraction.hardware_config_loader import HardwareConfigLoader
# Surface code generation
from scode.heuristic_layer.heuristic_initialization_layer import HeuristicInitializationLayer
# RL agent management
# Evaluation
from evaluation.evaluation_framework import EvaluationFramework
# Visualization
import matplotlib.pyplot as plt
import networkx as nx

# Config paths (should be set via config management in real use)
CONFIG_DIR = os.path.join(os.path.dirname(__file__), '../configs')
SURFACE_CODE_CONFIG = os.path.join(CONFIG_DIR, 'surface_code_config.yaml')

from .orchestrator import Orchestrator
from .heuristic_layer.surface_code import SurfaceCode
from .code_switcher.code_switcher import CodeSwitcher

class SurfaceCodeAPI:
    def __init__(self, config_dir: str = CONFIG_DIR):
        self.config_dir = config_dir
        self.surface_code_config = SURFACE_CODE_CONFIG
        self.hw_loader = HardwareConfigLoader(self.config_dir, self._load_config())
        self.device_info = self.hw_loader.load_device_config()
        self.device = self.device_info['device_name']
        self.provider = self.device_info.get('provider_name', None)
        self.h_layer = HeuristicInitializationLayer(self._load_config(), self.device_info)
        self.evaluator = EvaluationFramework(self._load_config())

    def _load_config(self):
        # Lazy import to avoid circular import
        ConfigLoader = importlib.import_module('scode.heuristic_layer.config_loader').ConfigLoader
        return ConfigLoader.load_yaml(self.surface_code_config)

    # --- Device, Layout, and Agent Management ---
    def list_available_devices(self) -> List[str]:
        """Return all supported device names (from Device Abstraction module)."""
        return self.hw_loader.list_devices()

    def list_layout_types(self) -> List[str]:
        """Return all supported surface code layout types."""
        config = self._load_config()
        return config.get('surface_code', {}).get('supported_layout_types', ['planar', 'rotated'])

    def list_code_distances(self, device: str = None, layout_type: str = None) -> List[int]:
        """Return valid code distances for a given device and layout."""
        config = self._load_config()
        # Use device from config if not provided
        if device is None:
            device = self.device
        return config.get('surface_code', {}).get('supported_code_distances', [3, 5, 7, 9])

    def list_supported_logical_gates(self, layout_type: str = None, code_distance: int = None) -> List[str]:
        """Return the set of logical gates that are fault-tolerantly supported by the given code. Never include SWAP unless natively supported."""
        if layout_type is None:
            layout_type = self.list_layout_types()[0]
        # Only natively supported gates, never SWAP
        if layout_type == 'planar':
            return ['X', 'Z', 'CNOT', 'H']
        return ['X', 'Z', 'CNOT', 'H', 'S', 'T']

    def list_trained_agents(self) -> List[Dict[str, Any]]:
        """Return metadata for all available trained agents (device, layout, distance, path)."""
        agents_dir = os.path.abspath(os.path.join(self.config_dir, '../../training_artifacts'))
        agents = []
        if os.path.exists(agents_dir):
            for fname in os.listdir(agents_dir):
                if fname.endswith('.zip'):
                    parts = fname.split('_')
                    agents.append({
                        'device': parts[1] if len(parts) > 1 else '',
                        'layout': parts[2] if len(parts) > 2 else '',
                        'distance': parts[3][1:] if len(parts) > 3 and parts[3].startswith('d') else '',
                        'path': os.path.join(agents_dir, fname)
                    })
        return agents

    # --- Training ---
    def _get_artifacts_dir(self, config=None):
        if config is None:
            config = self._load_config()
        output_dir = config.get('system', {}).get('output_dir', './outputs')
        return os.path.abspath(os.path.join(output_dir, 'training_artifacts'))

    def train_surface_code_agent(self, provider: str, device: str, layout_type: str, code_distance: int, config_overrides: Optional[dict] = None, log_callback=None) -> str:
        """Train an RL agent for the specified parameters. Returns path to trained agent."""
        config = self._load_config()
        if device is None:
            device = self.device
        if provider is None:
            provider = self.provider
        if layout_type is None:
            layout_type = self.list_layout_types()[0]
        if code_distance is None:
            code_distance = self.list_code_distances(device, layout_type)[0]
        if config_overrides:
            config['surface_code'].update(config_overrides)
            if log_callback:
                log_callback(f"[INFO] Updated config with overrides: {config_overrides}", 0.0)
        if log_callback:
            log_callback(f"[INFO] Preparing training for provider={provider}, device={device}, layout_type={layout_type}, code_distance={code_distance}", 0.0)
        from scode.heuristic_layer.heuristic_initialization_layer import HeuristicInitializationLayer
        from scode.graph_transformer.graph_transformer import ConnectivityAwareGraphTransformer
        from scode.rl_agent.environment import RLEnvironment
        from scode.reward_engine.reward_engine import MultiObjectiveRewardEngine
        hw_loader = HardwareConfigLoader(self.config_dir, config)
        device_info = hw_loader.load_device_config()
        h_layer = HeuristicInitializationLayer(config, device_info)
        surface_code = h_layer.generate_surface_code(code_distance, layout_type, visualize=False)
        if log_callback:
            log_callback(f"[INFO] Generated surface code for layout_type={layout_type}, code_distance={code_distance}", 0.0)
        transformer = ConnectivityAwareGraphTransformer(
            config=config,
            hardware_graph=device_info,
            native_gates=device_info['native_gates'],
            gate_error_rates=device_info['gate_error_rates'],
            qubit_error_rates={q: device_info['qubit_properties'][q]['readout_error'] for q in device_info['qubit_properties']}
        )
        transformed = transformer.transform(surface_code)
        if log_callback:
            log_callback(f"[INFO] Transformed surface code for RL environment.", 0.0)
        def make_env():
            return RLEnvironment(
                transformed_layout=transformed,
                hardware_specs=device_info,
                error_profile=device_info['qubit_properties'],
                config=config
            )
        env = DummyVecEnv([make_env])
        total_timesteps = config['rl_agent'].get('num_episodes', 10000) * 200
        model = PPO('MlpPolicy', env, verbose=1, batch_size=config['rl_agent'].get('batch_size', 64), n_steps=2048)
        # Custom callback for progress/logging
        if log_callback:
            class ProgressCallback:
                def __init__(self, total):
                    self.total = total
                    self.last = 0
                def __call__(self, locals_, globals_):
                    n = locals_['self'].num_timesteps
                    progress = n / self.total
                    if n - self.last >= 200:
                        log_callback(f"[INFO] SB3 PPO Progress: {n}/{self.total}", progress)
                        self.last = n
                    return True
            model.learn(total_timesteps=total_timesteps, callback=ProgressCallback(total_timesteps))
        else:
            model.learn(total_timesteps=total_timesteps)
        artifacts_dir = self._get_artifacts_dir(config)
        os.makedirs(artifacts_dir, exist_ok=True)
        policy_path = os.path.join(artifacts_dir, f'{provider}_{device}_{layout_type}_d{code_distance}_sb3_ppo_surface_code.zip')
        model.save(policy_path)
        if log_callback:
            log_callback(f"[INFO] Training complete. Policy saved to {policy_path}", 1.0)
        return policy_path

    def get_training_status(self, agent_path: str) -> dict:
        """Return training progress, metrics, and status for a given agent."""
        status = {'status': 'not_found', 'path': agent_path}
        if not os.path.exists(agent_path):
            return status
        status['status'] = 'completed'
        # Try to find a metadata/log file with the same base name
        base, _ = os.path.splitext(agent_path)
        meta_json = base + '.json'
        meta_yaml = base + '.yaml'
        meta = None
        if os.path.exists(meta_json):
            with open(meta_json, 'r') as f:
                meta = json.load(f)
        elif os.path.exists(meta_yaml):
            with open(meta_yaml, 'r') as f:
                meta = yaml.safe_load(f)
        if meta:
            status.update(meta)
        else:
            # Fallback: try to get file size and mtime
            status['artifact_size'] = os.path.getsize(agent_path)
            status['last_modified'] = os.path.getmtime(agent_path)
        return status

    # --- Code Generation & Mapping ---
    def generate_surface_code_layout(self, layout_type: str = None, code_distance: int = None, device: str = None) -> dict:
        """Generate a surface code layout for the given parameters."""
        # Use config-driven device/layout if not provided
        if device is None:
            device = self.device
        if layout_type is None:
            layout_type = self.list_layout_types()[0]
        if code_distance is None:
            code_distance = self.list_code_distances(device, layout_type)[0]
        # Validate device
        available_devices = self.list_available_devices()
        if device not in available_devices:
            raise ValueError(f"Device '{device}' not found in available devices: {available_devices}")
        # Validate code distance
        code_distances = self.list_code_distances(device, layout_type)
        if code_distance not in code_distances:
            raise ValueError(f"Code distance '{code_distance}' not valid for device '{device}' and layout '{layout_type}'. Valid: {code_distances}")
        # Reload device info for the requested device
        device_info = self.hw_loader.load_device_config()
        h_layer = HeuristicInitializationLayer(self._load_config(), device_info)
        code = h_layer.generate_surface_code(code_distance, layout_type, visualize=False)
        return {
            'qubit_layout': code.qubit_layout,
            'stabilizer_map': code.stabilizer_map,
            'logical_operators': code.logical_operators,
            'adjacency_matrix': nx.to_dict_of_lists(code.adjacency_matrix),
            'code_distance': code.code_distance,
            'layout_type': code.layout_type,
            'grid_connectivity': code.grid_connectivity
        }

    def get_stabilizer_info(self, layout_type: str, code_distance: int) -> dict:
        """Return stabilizer information for the given code."""
        code = self.h_layer.generate_surface_code(code_distance, layout_type, visualize=False)
        return code.stabilizer_map

    def _find_agent_artifact(self, device, layout_type, code_distance, provider=None):
        """Find the correct trained agent artifact for the given parameters."""
        config = self._load_config()
        artifacts_dir = self._get_artifacts_dir(config)
        candidates = []
        for fname in os.listdir(artifacts_dir):
            if fname.endswith('.zip') and device in fname and layout_type in fname and f'd{code_distance}' in fname:
                if provider is None or provider in fname:
                    candidates.append(os.path.join(artifacts_dir, fname))
        if not candidates:
            raise FileNotFoundError(f"No trained agent artifact found for device={device}, layout_type={layout_type}, code_distance={code_distance}, provider={provider} in {artifacts_dir}")
        # If multiple, pick the most recent
        candidates.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        return candidates[0]

    # --- Evaluation & Utility ---
    def evaluate_logical_error_rate(self, mapped_circuit: dict, device: str, noise_model=None) -> float:
        """Estimate the logical error rate for a mapped circuit on a given device, using the noise model from the device config."""
        if not hasattr(self, 'evaluator') or self.evaluator is None:
            raise RuntimeError("EvaluationFramework is not available.")
        if not hasattr(self.evaluator, 'evaluate_logical_error_rate'):
            raise AttributeError("EvaluationFramework does not have 'evaluate_logical_error_rate'")
        # Always load noise_model from the device config file based on provider/device from hardware.json
        device_info = self.hw_loader.load_device_config()
        noise_model = device_info.get('noise_model', {})
        return self.evaluator.evaluate_logical_error_rate(mapped_circuit, device, noise_model)

    # --- Visualization ---
    def visualize_surface_code(self, layout: dict) -> bytes:
        """Return an image (as bytes) for the frontend to display."""
        G = nx.Graph()
        for q, pos in layout.get('qubit_layout', {}).items():
            G.add_node(q, **pos)
        pos = {q: (v['x'], v['y']) for q, v in layout.get('qubit_layout', {}).items()}
        plt.figure(figsize=(7, 7))
        nx.draw(G, pos, node_color='lightgray', edge_color='gray', node_size=400, alpha=0.3, with_labels=True)
        plt.title(f"Surface Code Layout: d={layout.get('code_distance', '?')}, {layout.get('layout_type', '?')}")
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        return buf.read()

    # --- Utility/Validation ---
    def validate_code_for_device(self, layout_type: str, code_distance: int, device: str) -> bool:
        """Check if a given code can be implemented on the selected device (qubit count, connectivity, etc)."""
        device_info = self.hw_loader.load_device_config()
        required_qubits = code_distance ** 2  # Simplified; real logic may differ
        return device_info.get('qubit_count', 0) >= required_qubits

    def orchestrate_code_and_mapping(self, code_distance: int, layout_type: str, mapping_constraints: dict, device_config: dict, switcher_config_path: str, config_path: str) -> dict:
        orchestrator = Orchestrator(config_path, device_config, switcher_config_path)
        code, mapping = orchestrator.initialize_code(code_distance, layout_type, mapping_constraints)
        return {'code': code, 'mapping': mapping}

    def switch_code_space(self, old_mapping: dict, new_mapping: dict, switcher_config_path: str, protocol: str = None, **kwargs) -> dict:
        switcher = CodeSwitcher(switcher_config_path)
        # Validate protocol
        import yaml
        with open(switcher_config_path, 'r') as f:
            config = yaml.safe_load(f)
        enabled_protocols = [p['name'] for p in config['switching_protocols'] if p['enabled']]
        if protocol and protocol not in enabled_protocols:
            raise ValueError(f"Protocol '{protocol}' is not enabled. Enabled protocols: {enabled_protocols}")
        return switcher.switch(old_mapping, new_mapping, protocol=protocol, **kwargs) 