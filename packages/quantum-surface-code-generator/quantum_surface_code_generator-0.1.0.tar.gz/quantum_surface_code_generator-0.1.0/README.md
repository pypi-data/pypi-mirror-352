# Quantum Surface Code Generator Using Reinforcement Learning

## Introduction
Quantum error correction is a cornerstone of scalable quantum computing. Surface codes, with their topological protection and hardware compatibility, are a leading candidate for fault-tolerant quantum computation. This project presents a modular, configuration-driven framework for generating, mapping, and optimizing quantum surface codes on real hardware using reinforcement learning (RL). The system supports curriculum learning, multi-patch mapping, and a variety of code/grid types, and is designed for extensibility, reproducibility, and hardware-awareness.

## Methodology
The framework is composed of the following modular components:
- **HeuristicInitializationLayer**: Generates valid surface code layouts (planar, toric, rotated, color) for arbitrary code distances and grid connectivities, ensuring only valid codes are used for training.
- **ConnectivityAwareGraphTransformer**: Maps ideal surface code layouts to hardware-aware graphs, respecting native coupling maps and minimizing non-native operations.
- **ReinforcementLearningAgent**: Refines hardware-mapped layouts using curriculum learning and dynamic reward shaping. Supports continuous learning, checkpointing, and config-driven policy networks.
- **MultiObjectiveRewardEngine**: Computes reward using a multi-objective formula, with all weights and normalization strategies specified in YAML config files.
- **MultiPatchMapper**: Maps multiple logical qubits (surface code patches) onto a single hardware device, supporting adjacent, separated, and shared-boundary layouts, as well as constraints like minimum distance and patch shapes.
- **EvaluationFramework**: Systematically assesses logical error rate, resource efficiency, learning efficiency, and hardware adaptability.

All parameters, including RL agent settings, curriculum phases, reward weights, and hardware profiles, are specified in YAML/JSON config files. No hardcoded values are present in the codebase.

## Reward
The reward function is fully modular, config-driven, and supports both normalization and curriculum phase shaping. The general formula is:

```
reward = -(
    α * weighted_gate_error +
    β * total_swap_gates +
    γ * circuit_depth +
    δ * logical_error_rate +
    ε * weighted_qubit_error -
    ζ * stabilizer_score
)
```

- **Normalization:** If enabled in the config and provided with baseline metrics, each component can be normalized (e.g., using running mean/std).
- **Curriculum phase shaping:** During training, reward components are dynamically scaled depending on the current curriculum phase:
    - *Structure Mastery*: stabilizer_score is boosted
    - *Hardware Adaptation*: swaps and gate errors are penalized more
    - *Noise-Aware Optimization*: logical error rate is penalized more
- **Tunable weights:** All weights (α, β, γ, δ, ε, ζ) are provided via config and can be updated dynamically.

All weights and normalization strategies are specified in the config. Reward shaping and phase progression are handled automatically by the RL agent according to curriculum criteria.

## Configuration Parameters Explained

### RL Agent (`rl_agent`)
- `algorithm`: RL algorithm to use (e.g., PPO, DQN).
- `learning_rate`: Learning rate for the optimizer.
- `gamma`: Discount factor for future rewards.
- `batch_size`: Number of samples per training batch.
- `num_episodes`: Total number of training episodes.
- `max_steps_per_episode`: Maximum steps per episode.
- `ler_frequency`: How often (in episodes) to compute logical error rate (LER).
- `ler_num_trials`: Number of Monte Carlo trials per LER estimate.
- `ler_noise_prob`: Noise probability for LER estimation.
- `ppo_epochs`: Number of PPO update epochs per batch.
- `ppo_clip_eps`: PPO clipping epsilon for policy updates.
- `invalid_action_penalty`: Penalty value for invalid actions in action masking.
- `policy_network`/`value_network`: Structure and activation of policy/value networks.
- `optimizer`: Optimizer type (Adam, SGD, etc.).
- `device`: Device for training (auto, cpu, cuda).
- `checkpoint_interval`: Save policy every N episodes.
- `n_envs`: Number of parallel environments for data collection.

### Reward Engine (`reward_engine`)
- `normalization`: Reward normalization strategy (e.g., running_mean_std).
- `low_latency`: Optimize for low-latency reward computation.
- `dynamic_weights`: Allow dynamic reward weights.
- `phase_multipliers`: Multipliers for reward components in different curriculum phases:
    - `structure_mastery_stabilizer`: Multiplier for stabilizer score in Structure Mastery phase.
    - `hardware_adaptation_swap`: Multiplier for swap penalty in Hardware Adaptation phase.
    - `hardware_adaptation_gate_error`: Multiplier for gate error penalty in Hardware Adaptation phase.
    - `noise_aware_logical_error`: Multiplier for logical error rate in Noise-Aware Optimization phase.

### Curriculum (`curriculum`)
- `enabled`: Whether curriculum learning is enabled.
- `phases`: List of curriculum phases, each with:
    - `name`: Phase name.
    - `reward_weights`: Dict of weights (see below).
    - `criteria`: Dict of criteria for phase progression (e.g., valid_layouts, stabilizer_score, reward_variance, mean_swap, gate_errors, hardware_compatibility, logical_error_rate_improvement, reward_convergence, validation_performance).

#### Reward Weights (`reward_weights`)
- `alpha`: Weight for weighted gate error (sum of error rates for all gates used in the code).
- `beta`: Weight for total swap gates (SWAP overhead).
- `gamma`: Weight for circuit depth (latency/resource usage).
- `delta`: Weight for logical error rate (LER, code performance).
- `epsilon`: Weight for weighted qubit error (sum of error rates for all qubits used in the code, data + ancilla).
- `zeta`: Weight for stabilizer score (code quality/validity).

**Implications and Impact:**
- Increasing `alpha`, `beta`, `gamma`, `delta`, or `epsilon` penalizes the corresponding metric, making the RL agent avoid high error, swaps, depth, LER, or qubit count.
- Increasing `zeta` rewards higher stabilizer score, encouraging valid and robust code layouts.
- Adjusting these weights in curriculum phases allows staged learning: e.g., first focus on code validity, then hardware adaptation, then noise resilience.

### Evaluation (`evaluation`)
- `default_logical_error_rate`: Default LER if not computed.
- `default_training_time`: Default training time if not measured.
- `reward_variance_threshold`: Threshold for reward variance to determine convergence.

### Actions (`actions`)
- `enabled_types`: List of allowed action types (swap, rewire, assign_gate).
- `max_swaps_per_episode`: Maximum number of swaps allowed per episode.

### Multi-Patch (`multi_patch`)
- `num_patches`: Number of surface code patches to map.
- `patch_shapes`: Shape of each patch.
- `min_distance_between_patches`: Minimum distance between patches.
- `layout_type`: Patch layout type (adjacent, custom).

### System (`system`)
- `random_seed`: Random seed for reproducibility.
- `log_level`: Logging level.
- `output_dir`: Directory for outputs, logs, checkpoints.
- `device_preference`: Device for training (auto, cpu, cuda).

### Surface Code (`surface_code`)
- `code_distance`: Code distance for surface code.
- `layout_type`: Code layout (planar, rotated, toric, color).
- `visualize`: Whether to visualize the generated code.

## Opportunities for Improvement (Clarified & Expanded)
- **Advanced RL Algorithms:** Currently, PPO (Proximal Policy Optimization) is implemented as the main RL algorithm. Future work could add DQN, A3C, distributed actor-critic, or meta-RL approaches for broader benchmarking and performance.
- **LER Estimation & Noise Models:** The framework already uses Stim and PyMatching for accurate, research-grade logical error rate estimation. Further improvements could include more realistic noise models (e.g., correlated, biased, or hardware-calibrated noise), adaptive LER estimation, or integration with additional simulators (Qiskit, Cirq) for non-Clifford circuits.
- **Curriculum Learning:** Explore more advanced curriculum strategies, such as automatic phase progression, adaptive reward shaping, or meta-curriculum learning.
- **Visualization:** Add advanced visualization tools for code layouts, training progress, evaluation metrics, and hardware mapping.
- **User Interface:** Develop a web-based or CLI dashboard for experiment management, hyperparameter tuning, and result analysis.
- **Plugin System:** Expand the plugin architecture for easy addition of new hardware backends, reward functions, RL agents, and curriculum strategies.
- **Community Contributions:** Encourage open-source contributions, benchmarking, collaborative research, and shared datasets.
- **Automated Hyperparameter Tuning:** Integrate tools for automated hyperparameter search (e.g., Optuna, Ray Tune).
- **Benchmarking Suite:** Develop a benchmarking suite for comparing different code layouts, hardware profiles, and RL strategies.
- **Hardware-in-the-Loop:** Support for running experiments on real quantum hardware or high-fidelity simulators.
- **Documentation & Tutorials:** Expand documentation, add example configs, and provide step-by-step tutorials for new users.
- **Logging & Monitoring:** Improve logging, monitoring, and experiment tracking (e.g., with MLflow, Weights & Biases).
- **Robust Error Handling:** Add more robust error handling and diagnostics for all pipeline stages.
- **Test Coverage:** Increase unit and integration test coverage, including edge cases and hardware-specific scenarios.

## Installation
1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd quantum-surface-code-generator-using-reinforcement-learning
   ```
2. Install dependencies:
   ```bash
   pip install --break-system-packages -r requirements.txt
   ```
3. (Optional) For GPU support, ensure CUDA and PyTorch with CUDA are installed.

## Quickstart
1. Edit `configs/surface_code_config.yaml` to set your desired parameters (see the Configuration Parameters Explained section above).
2. Edit `configs/hardware.json` to select your provider and device. The provider should match the prefix of a devices YAML file (e.g., `ibm` for `ibm_devices.yaml`).
3. (Optional) Edit or select a hardware/device YAML file in `configs/`.
4. Edit `configs/gates.yaml` to define the set of quantum gates available in the circuit designer and backend modules. This file is required for the GUI and backend to function correctly.
5. Run the RL agent training pipeline:
   ```bash
   python3 -m scode.rl_agent.__main__
   ```
6. Monitor training progress with TensorBoard:
     ```bash
     tensorboard --logdir ./outputs/runs
     ```
7. Evaluate results:
   ```bash
   python3 -m evaluation.__main__
   ```

**Example minimal config:**
```

# Packaging and Distribution

## Packaging the Project

This project is structured for modular development and can be packaged as a Python package for distribution or installation. The backend and GUI are decoupled, and the RL agent, environment, and reward engine are all modular and compatible with the callback/logging mechanism for progress reporting.

### Key Features
- Modular backend with clear API boundaries
- PySide6 GUI with thread-safe progress/logging integration
- RL agent training supports log/progress callbacks for CLI, GUI, and test integration
- Flexible device/provider config handling
- Automatic checkpointing and policy saving

### Packaging Steps

1. **Ensure all dependencies are listed in `requirements.txt`**
2. **Add a `setup.py` and/or `pyproject.toml` for setuptools/PEP 517 packaging**
3. **Organize modules under a top-level package (e.g., `scode`, `circuit_designer`, etc.)**
4. **Include entry points for CLI and GUI (e.g., `gui_main.py`, `__main__.py`)**
5. **Add MANIFEST.in to include non-Python files (YAML configs, etc.)**
6. **Test install with `pip install .` and run both CLI and GUI**

### Example `setup.py`
```python
from setuptools import setup, find_packages

setup(
    name='quantum_surface_code_generator',
    version='0.1.0',
    description='Quantum Surface Code Generator using RL with GUI',
    author='Your Name',
    packages=find_packages(),
    install_requires=[
        'PySide6',
        'stable-baselines3',
        'gymnasium',
        'numpy',
        'matplotlib',
        'networkx',
        'pymatching',
        'stim',
        # ... add others from requirements.txt
    ],
    entry_points={
        'console_scripts': [
            'quantum-gui = circuit_designer.gui_main:main',
            'quantum-train = scode.rl_agent.__main__:main_sb3',
        ],
    },
    include_package_data=True,
)
```

### Example `MANIFEST.in`
```
include requirements.txt
recursive-include configs *.yaml *.json
recursive-include circuit_designer *.ui
recursive-include scode *.yaml *.json
```

### Callback/Logging Mechanism
- All RL training and backend APIs accept a `log_callback` or `progress_callback` argument.
- The GUI passes a callback that emits Qt signals for thread-safe UI updates.
- CLI and tests pass a simple print or logging function.
- Progress is reported as a float in [0,1], and log messages are human-readable.

### Testing
- Run `pytest scode/tests` to verify backend and RL agent logic.
- Run the GUI and start a training session to verify log/progress integration.