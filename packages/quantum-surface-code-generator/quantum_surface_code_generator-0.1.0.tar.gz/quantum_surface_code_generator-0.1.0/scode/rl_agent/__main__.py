import os
from scode.heuristic_layer.config_loader import ConfigLoader
from scode.heuristic_layer.heuristic_initialization_layer import HeuristicInitializationLayer
from hardware_abstraction.hardware_config_loader import HardwareConfigLoader
from scode.graph_transformer.graph_transformer import ConnectivityAwareGraphTransformer
from .environment import RLEnvironment
from scode.reward_engine.reward_engine import MultiObjectiveRewardEngine
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
import time
from stable_baselines3.common.callbacks import BaseCallback
import sys

CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../configs'))
SURFACE_CODE_CONFIG = os.path.join(CONFIG_DIR, 'surface_code_config.yaml')
TRAINING_ARTIFACTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../training_artifacts'))
os.makedirs(TRAINING_ARTIFACTS_DIR, exist_ok=True)

def make_env(config, device, reward_engine):
    from scode.heuristic_layer.heuristic_initialization_layer import HeuristicInitializationLayer
    from scode.graph_transformer.graph_transformer import ConnectivityAwareGraphTransformer
    from .environment import RLEnvironment
    h_layer = HeuristicInitializationLayer(config, device)
    params = config['surface_code']
    surface_code = h_layer.generate_surface_code(
        code_distance=params['code_distance'],
        layout_type=params['layout_type'],
        visualize=params.get('visualize', False)
    )
    transformer = ConnectivityAwareGraphTransformer(
        config=config,
        hardware_graph=device,
        native_gates=device['native_gates'],
        gate_error_rates=device['gate_error_rates'],
        qubit_error_rates={q: device['qubit_properties'][q]['readout_error'] for q in device['qubit_properties']}
    )
    transformed = transformer.transform(surface_code)
    return lambda: RLEnvironment(
        transformed_layout=transformed,
        hardware_specs=device,
        error_profile=device['qubit_properties'],
        config=config
    )

# True terminal progress bar callback (no tqdm)
class TerminalProgressBarCallback(BaseCallback):
    def __init__(self, total_timesteps, bar_length=40, print_freq=5, verbose=0):
        super().__init__(verbose)
        self.total_timesteps = total_timesteps
        self.bar_length = bar_length
        self.print_freq = print_freq
        self.start_time = None
        self.last_print = 0
        self.last_reward = None
        self.last_ler = None

    def _on_training_start(self):
        self.start_time = time.time()
        self.last_print = self.num_timesteps

    def _on_step(self):
        now = time.time()
        # Only update every print_freq seconds
        if now - self.start_time > 0 and (now - self.last_print > self.print_freq):
            elapsed = now - self.start_time
            progress = self.num_timesteps / self.total_timesteps
            filled_len = int(self.bar_length * progress)
            bar = '=' * filled_len + '>' + ' ' * (self.bar_length - filled_len - 1)
            if progress > 0:
                eta = elapsed * (1 - progress) / progress
                eta_str = time.strftime('%H:%M:%S', time.gmtime(eta))
            else:
                eta_str = 'N/A'
            elapsed_str = time.strftime('%H:%M:%S', time.gmtime(elapsed))

            # Get reward and LER from infos if available
            infos = self.locals.get('infos', [])
            rewards = self.locals.get('rewards', [])
            if rewards is not None and len(rewards) > 0:
                self.last_reward = sum(rewards) / len(rewards)
            if infos and isinstance(infos, (list, tuple)):
                # Try to extract LER from info dicts
                lers = [info.get('ler', None) or info.get('logical_error_rate', None)
                        for info in infos if isinstance(info, dict)]
                lers = [ler for ler in lers if ler is not None]
                if lers:
                    self.last_ler = sum(lers) / len(lers)

            reward_str = f'Reward: {self.last_reward:.3f}' if self.last_reward is not None else ''
            ler_str = f'LER: {self.last_ler:.3e}' if self.last_ler is not None else ''

            sys.stdout.write(
                f'\r[{bar}] {progress*100:6.2f}% | Elapsed: {elapsed_str} | ETA: {eta_str} | {reward_str} {ler_str}   '
            )
            sys.stdout.flush()
            self.last_print = now
        return True

    def _on_training_end(self):
        sys.stdout.write('\n')
        sys.stdout.flush()

def main_sb3():
    config = ConfigLoader.load_yaml(SURFACE_CODE_CONFIG)
    hw_loader = HardwareConfigLoader(CONFIG_DIR, config)
    device = hw_loader.load_device_config()
    reward_engine = MultiObjectiveRewardEngine(config)
    n_envs = config.get('rl_agent', {}).get('n_envs', 4)
    env_fns = [make_env(config, device, reward_engine) for _ in range(n_envs)]
    vec_env = DummyVecEnv(env_fns) if n_envs == 1 else SubprocVecEnv(env_fns)
    total_timesteps = config['rl_agent'].get('num_episodes', 10000) * 200
    callback = TerminalProgressBarCallback(total_timesteps)
    model = PPO('MlpPolicy', vec_env, verbose=1, batch_size=config['rl_agent'].get('batch_size', 64), n_steps=2048)
    model.learn(total_timesteps=total_timesteps, callback=callback)
    model.save('sb3_ppo_surface_code')

if __name__ == '__main__':
    main_sb3()  # New SB3 PPO vectorized training 