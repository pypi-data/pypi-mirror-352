import unittest
from scode.heuristic_layer.heuristic_initialization_layer import HeuristicInitializationLayer
from scode.heuristic_layer.config_loader import ConfigLoader
import os
from hardware_abstraction.hardware_config_loader import HardwareConfigLoader

class TestHeuristicInitializationLayer(unittest.TestCase):
    def setUp(self):
        config_path = os.path.join(os.path.dirname(__file__), '../../configs/surface_code_config.yaml')
        self.config = ConfigLoader.load_yaml(config_path)
        self.hw_loader = HardwareConfigLoader(os.path.join(os.path.dirname(__file__), '../../configs'), self.config)
        self.device = self.hw_loader.load_device_config()
        self.h_layer = HeuristicInitializationLayer(self.config, self.device)

    def test_planar_nearest_neighbour(self):
        code = self.h_layer.generate_surface_code(3, 'planar')
        self.assertTrue(len(code.qubit_layout) > 0)
        self.assertTrue(len(code.stabilizer_map) > 0)
        self.assertTrue(len(code.logical_operators) > 0)

    def test_rotated_all_to_all(self):
        code = self.h_layer.generate_surface_code(3, 'rotated')
        self.assertTrue(len(code.qubit_layout) > 0)
        self.assertTrue(len(code.stabilizer_map) > 0)
        self.assertTrue(len(code.logical_operators) > 0)

if __name__ == '__main__':
    unittest.main() 