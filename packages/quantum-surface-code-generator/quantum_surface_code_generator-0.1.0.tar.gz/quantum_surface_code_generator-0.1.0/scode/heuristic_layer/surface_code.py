from typing import Dict, Any
from scode.heuristic_layer.heuristic_initialization_layer import HeuristicInitializationLayer
from scode.heuristic_layer.config_loader import ConfigLoader
from scode.multi_patch_mapper.multi_patch_mapper import MultiPatchMapper

class SurfaceCode:
    def __init__(self, config_path: str, device_config: Dict[str, Any]):
        self.config = ConfigLoader.load_yaml(config_path)
        self.device_config = device_config
        self.h_layer = HeuristicInitializationLayer(self.config, self.device_config)
        self.mapper = MultiPatchMapper(self.config, self.device_config)
        self.current_code = None
        self.current_mapping = None

    def get_code(self, code_distance: int, layout_type: str):
        self.current_code = self.h_layer.generate_surface_code(code_distance, layout_type)
        return self.current_code

    def get_mapping(self, code_distance: int, layout_type: str, mapping_constraints: Dict[str, Any]):
        code = self.get_code(code_distance, layout_type)
        mapping = self.mapper.map_patches([code], mapping_constraints)
        self.current_mapping = mapping
        return mapping

    def request_new_mapping(self, swap_pairs: Any, code_distance: int, layout_type: str, mapping_constraints: Dict[str, Any]):
        # Use swap_pairs and mapping_constraints to generate a new mapping
        # All logic is config-driven
        mapping_constraints = dict(mapping_constraints)
        mapping_constraints['swap_pairs'] = swap_pairs
        return self.get_mapping(code_distance, layout_type, mapping_constraints) 