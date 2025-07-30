import os
from .config_loader import ConfigLoader
from .heuristic_initialization_layer import HeuristicInitializationLayer
from hardware_abstraction.hardware_config_loader import HardwareConfigLoader

CONFIG_DIR = os.path.join(os.path.dirname(__file__), '../configs')
SURFACE_CODE_CONFIG = os.path.join(CONFIG_DIR, 'surface_code_config.yaml')

def main():
    config = ConfigLoader.load_yaml(SURFACE_CODE_CONFIG)
    hw_loader = HardwareConfigLoader(CONFIG_DIR, config)
    device = hw_loader.load_device_config()
    h_layer = HeuristicInitializationLayer(config, device)
    params = config['surface_code']
    surface_code = h_layer.generate_surface_code(
        code_distance=params['code_distance'],
        layout_type=params['layout_type'],
        visualize=params['visualize']
    )
    print(f"Generated surface code: d={surface_code.code_distance}, layout={surface_code.layout_type}, connectivity={surface_code.grid_connectivity}")
    print(f"Qubits: {len(surface_code.qubit_layout)} | Stabilizers: {len(surface_code.stabilizer_map)} | Logical ops: {len(surface_code.logical_operators)}")

if __name__ == '__main__':
    main() 