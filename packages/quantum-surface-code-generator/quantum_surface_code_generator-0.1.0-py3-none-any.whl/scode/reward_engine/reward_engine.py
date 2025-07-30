from typing import Dict, Any
import numpy as np

class MultiObjectiveRewardEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.weights = config.get('reward_engine', {})
        self.normalization = self.weights.get('normalization', None)

    def compute_reward(self, hardware_graph: Any, circuit_metrics: Dict[str, Any], stabilizer_mapping: Dict[str, Any], reward_weights: Dict[str, float], baseline_metrics: Dict[str, Any] = None, phase: str = None) -> (float, Dict[str, float]):
        # Extract metrics with default values
        weighted_single_qubit_gate_error = circuit_metrics.get('weighted_single_qubit_gate_error', 0.0)
        weighted_two_qubit_gate_error = circuit_metrics.get('weighted_two_qubit_gate_error', 0.0)
        weighted_qubit_error = circuit_metrics.get('weighted_qubit_error', 0.0)
        total_swap_gates = circuit_metrics.get('total_swap_gates', 0)
        circuit_depth = circuit_metrics.get('circuit_depth', 0)
        logical_error_rate = circuit_metrics.get('logical_error_rate', 0.0)
        stabilizer_score = circuit_metrics.get('stabilizer_score', 0.0)
        
        # Weights (must be provided in reward_weights)
        alpha1 = reward_weights.get('alpha1', 1.0)
        alpha2 = reward_weights.get('alpha2', 1.0)
        beta = reward_weights.get('beta', 1.0)
        gamma = reward_weights.get('gamma', 1.0)
        delta = reward_weights.get('delta', 1.0)
        epsilon = reward_weights.get('epsilon', 1.0)
        zeta = reward_weights.get('zeta', 1.0)
        
        # Normalization if specified
        if self.normalization == 'running_mean_std' and baseline_metrics:
            weighted_single_qubit_gate_error = (weighted_single_qubit_gate_error - baseline_metrics.get('weighted_single_qubit_gate_error_mean', 0)) / (baseline_metrics.get('weighted_single_qubit_gate_error_std', 1) or 1)
            weighted_two_qubit_gate_error = (weighted_two_qubit_gate_error - baseline_metrics.get('weighted_two_qubit_gate_error_mean', 0)) / (baseline_metrics.get('weighted_two_qubit_gate_error_std', 1) or 1)
            weighted_qubit_error = (weighted_qubit_error - baseline_metrics.get('weighted_qubit_error_mean', 0)) / (baseline_metrics.get('weighted_qubit_error_std', 1) or 1)
            total_swap_gates = (total_swap_gates - baseline_metrics.get('total_swap_gates_mean', 0)) / (baseline_metrics.get('total_swap_gates_std', 1) or 1)
            circuit_depth = (circuit_depth - baseline_metrics.get('circuit_depth_mean', 0)) / (baseline_metrics.get('circuit_depth_std', 1) or 1)
            logical_error_rate = (logical_error_rate - baseline_metrics.get('logical_error_rate_mean', 0)) / (baseline_metrics.get('logical_error_rate_std', 1) or 1)
            stabilizer_score = (stabilizer_score - baseline_metrics.get('stabilizer_score_mean', 0)) / (baseline_metrics.get('stabilizer_score_std', 1) or 1)
        
        # Phase-specific reward shaping (now configurable)
        multipliers = self.config.get('reward_engine', {}).get('phase_multipliers', {})
        if phase == 'Structure Mastery':
            stabilizer_score *= multipliers.get('structure_mastery_stabilizer', 2.0)
        elif phase == 'Hardware Adaptation':
            total_swap_gates *= multipliers.get('hardware_adaptation_swap', 1.5)
            weighted_single_qubit_gate_error *= multipliers.get('hardware_adaptation_single_qubit_gate_error', 1.5)
            weighted_two_qubit_gate_error *= multipliers.get('hardware_adaptation_two_qubit_gate_error', 1.5)
        elif phase == 'Noise-Aware Optimization':
            logical_error_rate *= multipliers.get('noise_aware_logical_error', 2.0)
        
        # Reward formula
        reward = -(
            alpha1 * weighted_single_qubit_gate_error +
            alpha2 * weighted_two_qubit_gate_error +
            beta * total_swap_gates +
            gamma * circuit_depth +
            delta * logical_error_rate +
            epsilon * weighted_qubit_error -
            zeta * stabilizer_score
        )
        
        breakdown = {
            'weighted_single_qubit_gate_error': weighted_single_qubit_gate_error,
            'weighted_two_qubit_gate_error': weighted_two_qubit_gate_error,
            'weighted_qubit_error': weighted_qubit_error,
            'total_swap_gates': total_swap_gates,
            'circuit_depth': circuit_depth,
            'logical_error_rate': logical_error_rate,
            'stabilizer_score': stabilizer_score
        }
        return reward, breakdown 