import unittest
import os
from scode.heuristic_layer.config_loader import ConfigLoader
from scode.heuristic_layer.heuristic_initialization_layer import HeuristicInitializationLayer
from hardware_abstraction.hardware_config_loader import HardwareConfigLoader
from scode.graph_transformer.graph_transformer import ConnectivityAwareGraphTransformer
try:
    from scode.rl_agent.rl_agent import ReinforcementLearningAgent
except ImportError:
    ReinforcementLearningAgent = None
from scode.rl_agent.environment import RLEnvironment
from scode.reward_engine.reward_engine import MultiObjectiveRewardEngine
from scode.multi_patch_mapper.multi_patch_mapper import MultiPatchMapper
from evaluation.evaluation_framework import EvaluationFramework
from scode.orchestrator import Orchestrator
from scode.heuristic_layer.surface_code import SurfaceCode
from scode.code_switcher.code_switcher import CodeSwitcher

class TestIntegrationPipeline(unittest.TestCase):
    def setUp(self):
        self.config_path = os.path.join(os.path.dirname(__file__), '../../configs/surface_code_config.yaml')
        self.switcher_config_path = os.path.join(os.path.dirname(__file__), '../../configs/switcher_config.yaml')
        self.config = ConfigLoader.load_yaml(self.config_path)
        self.device_config = {'qubit_count': 25, 'topology_type': 'grid', 'qubit_connectivity': {str(i): [str(i+1)] for i in range(24)}}
        self.mapping_constraints = {'patch_shapes': ['rectangular']}
        self.code_distance = 3
        self.layout_type = 'planar'
        self.hw_loader = HardwareConfigLoader(os.path.join(os.path.dirname(__file__), '../../configs'), self.config)
        self.device = self.hw_loader.load_device_config()
        self.h_layer = HeuristicInitializationLayer(self.config, self.device)
        self.transformer = ConnectivityAwareGraphTransformer(
            config=self.config,
            hardware_graph=self.device,
            native_gates=self.device['native_gates'],
            gate_error_rates=self.device['gate_error_rates'],
            qubit_error_rates={q: self.device['qubit_properties'][q]['readout_error'] for q in self.device['qubit_properties']}
        )
        self.reward_engine = MultiObjectiveRewardEngine(self.config)
        self.evaluator = EvaluationFramework(self.config)

    def test_full_pipeline(self):
        if ReinforcementLearningAgent is None:
            self.skipTest("ReinforcementLearningAgent not available (rl_agent.py missing)")
        # Heuristic layer
        code = self.h_layer.generate_surface_code(3, 'planar')
        self.assertTrue(len(code.qubit_layout) > 0)
        # Graph transformer
        transformed = self.transformer.transform(code)
        self.assertIn('transformed_layout', transformed)
        # RL environment
        env = RLEnvironment(
            transformed_layout=transformed,
            hardware_specs=self.device,
            error_profile=self.device['qubit_properties'],
            config=self.config
        )
        env.reset()
        agent = ReinforcementLearningAgent(self.config, env, self.reward_engine)
        policy_path = agent.train()
        provider = self.device.get('provider_name', 'provider').lower()
        device = self.device.get('device_name', 'device').lower()
        layout_type = self.config.get('surface_code', {}).get('layout_type', 'planar')
        code_distance = self.config.get('surface_code', {}).get('code_distance', 3)
        expected_policy_path = os.path.abspath(os.path.join(self.config.get('system', {}).get('output_dir', './outputs'), '../training_artifacts', f"{provider}_{device}_{layout_type}_d{code_distance}_sb3_ppo_surface_code.zip"))
        self.assertTrue(os.path.exists(expected_policy_path))
        agent.export_policy(policy_path)
        # Multi-patch mapping
        mapper = MultiPatchMapper(self.config, self.device)
        surface_codes = [self.h_layer.generate_surface_code(3, 'planar') for _ in range(2)]
        mapping_constraints = self.config.get('multi_patch', {'patch_shapes': ['rectangular', 'rectangular']})
        multi_patch_result = mapper.map_patches(surface_codes, mapping_constraints)
        self.assertIn('multi_patch_layout', multi_patch_result)
        # Evaluation
        ler = self.evaluator.evaluate_logical_error_rate(transformed['transformed_layout'], self.device, {})
        res_eff = self.evaluator.evaluate_resource_efficiency(transformed['transformed_layout'])
        learn_eff = self.evaluator.evaluate_learning_efficiency(agent.training_log)
        hw_adapt = self.evaluator.evaluate_hardware_adaptability({'hardware_compatibility': 1.0})
        self.assertIsInstance(ler, float)
        self.assertIsInstance(res_eff, dict)
        self.assertIsInstance(learn_eff, dict)
        self.assertIsInstance(hw_adapt, dict)

    def test_orchestrator_and_switcher(self):
        orchestrator = Orchestrator(self.config_path, self.device_config, self.switcher_config_path)
        code, mapping = orchestrator.initialize_code(self.code_distance, self.layout_type, self.mapping_constraints)
        self.assertIsNotNone(code)
        self.assertIsNotNone(mapping)
        # Simulate a SWAP operation
        operations = [{'type': 'SWAP', 'swap_pairs': [(0, 1)]}]
        orchestrator.run_operations(operations, self.mapping_constraints)
        # Test code switcher directly
        switcher = CodeSwitcher(self.switcher_config_path)
        result = switcher.switch(mapping, mapping, protocol='lattice_surgery')
        self.assertIn('protocol', result)
        self.assertEqual(result['protocol'], 'lattice_surgery')

if __name__ == '__main__':
    unittest.main() 