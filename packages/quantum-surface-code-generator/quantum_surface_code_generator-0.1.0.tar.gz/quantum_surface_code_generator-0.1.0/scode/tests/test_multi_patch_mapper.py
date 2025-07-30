import unittest
from scode.heuristic_layer.heuristic_initialization_layer import HeuristicInitializationLayer
from scode.heuristic_layer.config_loader import ConfigLoader
from hardware_abstraction.hardware_config_loader import HardwareConfigLoader
from scode.multi_patch_mapper.multi_patch_mapper import MultiPatchMapper
import os

class TestMultiPatchMapper(unittest.TestCase):
    def setUp(self):
        config_path = os.path.join(os.path.dirname(__file__), '../../configs/surface_code_config.yaml')
        self.config = ConfigLoader.load_yaml(config_path)
        self.hw_loader = HardwareConfigLoader(os.path.join(os.path.dirname(__file__), '../../configs'), self.config)
        self.device = self.hw_loader.load_device_config()
        self.h_layer = HeuristicInitializationLayer(self.config, self.device)

    def test_map_patches(self):
        num_patches = 2
        surface_codes = [
            self.h_layer.generate_surface_code(3, 'planar')
            for _ in range(num_patches)
        ]
        mapping_constraints = {'patch_shapes': ['rectangular', 'rectangular']}
        mapper = MultiPatchMapper(self.config, self.device)
        result = mapper.map_patches(surface_codes, mapping_constraints)
        self.assertIn('multi_patch_layout', result)
        self.assertIn('inter_patch_connectivity', result)
        self.assertIn('resource_allocation', result)
        self.assertIn('optimization_metrics', result)

if __name__ == '__main__':
    unittest.main() 