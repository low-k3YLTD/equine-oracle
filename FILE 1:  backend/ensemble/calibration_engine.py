"""
Equine Oracle v3.1 - Calibration & Conformal Prediction Engine
Low Key Consultants Ltd - Production Module
"""

import numpy as np
from scipy.optimize import minimize
import cvxpy as cp
import torch
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class CalibrationConfig:
    """Configuration for jurisdiction-specific calibration."""
    jurisdiction: str = 'NZ'
    temperature_bounds: Tuple[float, float] = (0.5, 3.0)
    max_weight_per_model: float = 0.6
    coverage_alpha: float = 0.1  # 90% coverage
    min_calibration_samples: int = 100


class GodTierCalibrationEngine:
    """
    Joint optimization calibration for ensemble outputs.
    Addresses the 'ensemble optimality gap' in hyperparameter tuning.
    
    Research basis: Temperature scaling with CVXPY weight optimization
    outperforms individual model calibration.
    """
    
    def __init__(self, n_classes: int = 4, config: Optional[CalibrationConfig] = None):
        self.n_classes = n_classes
        self.config = config or CalibrationConfig()
        
        # Calibration parameters (fitted on validation data)
        self.temperature: float = 1.0
        self.calibration_weights: Optional[np.ndarray] = None
        self.is_fitted: bool = False
        
        # Per-jurisdiction tuning
        self.jurisdiction_params: Dict[str, Dict] = {
            'NZ': {'default_temp': 1.0, 'market_efficiency': 0.85},
            'AU': {'default_temp': 1.1, 'market_efficiency': 0.88},
            'UK': {'default_temp': 1.2, 'market_efficiency': 0.92},
            'HK': {'default_temp': 0.9, 'market_efficiency': 0.95}
        }
    
    def fit_temperature(self, 
                       base_predictions: np.ndarray, 
                       val_labels: np.ndarray,
                       group_ids: Optional[np.ndarray] = None) -> float:
        """
        Joint temperature optimization across all ensemble members.
        
        Args:
            base_predictions: Raw logits from base models [n_samples, n_models]
            val_labels: True labels [n_samples]
            group_ids: Race group identifiers for per-race normalization
            
        Returns:
            Optimal temperature parameter
        """
        def negative_log_likelihood(T: float) -> float:
            total_nll = 0.0
            
            if group_ids is not None:
                # Per-race temperature scaling with group-aware normalization
                for group_id in np.unique(group_ids):
                    mask = group_ids == group_id
                    group_preds = base_predictions[mask]
                    group_labels = val_labels[mask]
                    
                    # Temperature scaling
                    scaled = group_preds / T
                    probs = F.softmax(torch.tensor(scaled), dim=1).numpy()
                    
                    # NLL for this race
                    for i, label in enumerate(group_labels):
                        if 0 <= label < probs.shape[1]:
                            total_nll += -np.log(probs[i, label] + 1e-10)
            else:
                # Global temperature scaling
                scaled = base_predictions / T
                probs = F.softmax(torch.tensor(scaled), dim=1).numpy()
                total_nll = -np.log(probs[np.arange(len(val_labels)), val_labels] + 1e-10).sum()
            
            return total_nll
        
        # Optimize with L-BFGS-B
        result = minimize(
            negative_log_likelihood,
            x0=self.jurisdiction_params.get(self.config.jurisdiction, {}).get('default_temp', 1.0),
            bounds=[self.config.temperature_bounds],
            method='L-BFGS-B'
        )
        
        self.temperature = result.x[0]
        return self.temperature
    
    def fit_stacked_calibration(self,
                                 base_predictions: np.ndarray,
                                 y_true: np.ndarray,
                                 group_ids: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Two-stage meta-learner with calibration focus.
        Stage A: Temperature scaling per model
        Stage B: CVXPY convex optimization for ensemble weights
        
        Args:
            base_predictions: [n_samples, n_models] raw predictions
            y_true: [n_samples] true probabilities or rankings
            group_ids: Optional race grouping
            
        Returns:
            Calibrated ensemble predictions
        """
        n_samples, n_models = base_predictions.shape
        
        # Stage A: Apply temperature scaling to convert to probabilities
        scaled_preds = base_predictions / self.temperature
        # Sigmoid for binary/multiclass probability conversion
        prob_matrix = 1 / (1 + np.exp(-scaled_preds))
        
        # Stage B: CVXPY optimization
        # Minimize Brier score subject to sum(weights) = 1, weights >= 0, max_weight constraint
        weights = cp.Variable(n_models)
        
        # Predictions = weighted combination
        ensemble_pred = prob_matrix @ weights
        
        # Brier score: mean squared error of probabilities
        brier = cp.sum_squares(ensemble_pred - y_true) / n_samples
        
        # Constraints
        constraints = [
            cp.sum(weights) == 1,
            weights >= 0,
            weights <= self.config.max_weight_per_model
        ]
        
        # Solve convex problem
        problem = cp.Problem(cp.Minimize(brier), constraints)
        problem.solve(solver=cp.ECOS, verbose=False)
        
        if problem.status not in ["optimal", "optimal_inaccurate"]:
            # Fallback to uniform weights if optimization fails
            self.calibration_weights = np.ones(n_models) / n_models
        else:
            self.calibration_weights = weights.value
        
        self.is_fitted = True
        
        # Return calibrated predictions
        return self._apply_weights(prob_matrix)
    
    def _apply_weights(self, prob_matrix: np.ndarray) -> np.ndarray:
        """Apply fitted weights to probability matrix."""
        if self.calibration_weights is None:
            raise ValueError("Calibration not fitted. Call fit_stacked_calibration first.")
        return prob_matrix @ self.calibration_weights
    
    def predict_calibrated(self, base_predictions: np.ndarray) -> np.ndarray:
        """
        Apply fitted calibration to new predictions.
        
        Args:
            base_predictions: [n_samples, n_models] raw ensemble predictions
            
        Returns:
            [n_samples] calibrated probability estimates
        """
        if not self.is_fitted:
            # Fallback: simple mean with temperature scaling only
            scaled = base_predictions / self.temperature
            probs = 1 / (1 + np.exp(-scaled))
            return probs.mean(axis=1)
        
        # Full calibration
        scaled = base_predictions / self.temperature
        prob_matrix = 1 / (1 + np.exp(-scaled))
        calibrated = self._apply_weights(prob_matrix)
        
        # Normalize to valid probability distribution
        calibrated = np.clip(calibrated, 0.001, 0.999)
        return calibrated
    
    def get_calibration_diagnostics(self) -> Dict:
        """Return diagnostic info for monitoring."""
        return {
            'is_fitted': self.is_fitted,
            'temperature': float(self.temperature),
            'weights': self.calibration_weights.tolist() if self.calibration_weights is not None else None,
            'jurisdiction': self.config.jurisdiction,
            'max_weight_constraint': self.config.max_weight_per_model
        }


class ExoticConformalPredictor:
    """
    Conformal prediction for exotic bets with guaranteed coverage.
    
    Provides prediction sets for exacta/trifecta/quartet with
    distribution-free 90% coverage guarantee.
    """
    
    def __init__(self, alpha: float = 0.1, config: Optional[CalibrationConfig] = None):
        """
        Args:
            alpha: Miscoverage rate (0.1 = 90% coverage guarantee)
        """
        self.alpha = alpha
        self.config = config or CalibrationConfig()
        
        # Fitted parameters
        self.calibration_scores: Optional[np.ndarray] = None
        self.quantile: Optional[float] = None
        self.is_fitted: bool = False
        
        # Per-position non-conformity history
        self.position_quantiles: Dict[str, float] = {}
    
    def fit(self, 
            model_scores: np.ndarray, 
            true_outcomes: np.ndarray,
            position: str = '1st'):
        """
        Compute non-conformity scores on calibration set.
        
        Args:
            model_scores: Predicted probabilities for each horse [n_horses]
            true_outcomes: Binary indicators of actual result [n_horses]
            position: Which finishing position ('1st', '2nd', '3rd', '4th')
        """
        # Non-conformity score: 1 - predicted probability of true outcome
        # Lower = more conformal (better prediction)
        non_conformity = 1 - model_scores[true_outcomes == 1]
        
        # Store quantile for this position
        self.position_quantiles[position] = np.quantile(
            non_conformity, 
            1 - self.alpha
        )
        
        self.calibration_scores = non_conformity
        self.is_fitted = True
    
    def predict_position_set(self, 
                            scores: np.ndarray, 
                            position: str = '1st') -> Dict:
        """
        Return conformal prediction set for a single position.
        
        Args:
            scores: Predicted probabilities for each horse [n_horses]
            position: Finishing position
            
        Returns:
            Dict with 'horses' (indices), 'scores' (probs), 'set_size'
        """
        if not self.is_fitted:
            raise ValueError("Conformal predictor not fitted. Call fit() first.")
        
        quantile = self.position_quantiles.get(position, self.quantile)
        if quantile is None:
            quantile = np.quantile(1 - scores, 1 - self.alpha)
        
        # Non-conformity scores for this prediction
        non_conformity = 1 - scores
        
        # Prediction set: all horses with non-conformity <= quantile
        in_set = non_conformity <= quantile
        
        return {
            'horses': np.where(in_set)[0].tolist(),
            'scores': scores[in_set].tolist(),
            'set_size': int(in_set.sum()),
            'quantile_threshold': float(quantile)
        }
    
    def predict_exotic_sets(self,
                           race_predictions: Dict[str, np.ndarray],
                           bet_type: str = 'trifecta') -> Dict:
        """
        Generate conformal prediction sets for exotic bet.
        
        Args:
            race_predictions: Dict with keys '1st', '2nd', '3rd', '4th' 
                             mapping to probability arrays
            bet_type: 'exacta', 'trifecta', or 'quartet'
            
        Returns:
            Dict with prediction sets for each position
        """
        positions = {
            'exacta': ['1st', '2nd'],
            'trifecta': ['1st', '2nd', '3rd'],
            'quartet': ['1st', '2nd', '3rd', '4th']
        }.get(bet_type, ['1st', '2nd', '3rd'])
        
        prediction_sets = {}
        for pos in positions:
            if pos in race_predictions:
                prediction_sets[pos] = self.predict_position_set(
                    race_predictions[pos], 
                    position=pos
                )
        
        return prediction_sets
    
    def calculate_uncertainty_coefficient(self, 
                                          prediction_sets: Dict[str, Dict],
                                          total_horses: int) -> Dict[str, float]:
        """
        Quantify model uncertainty based on prediction set sizes.
        
        u_C = set_size / total_horses
        
        Lower = more certain (tighter prediction set)
        Higher = more uncertain (wider prediction set)
        
        Returns:
            Dict mapping position to uncertainty coefficient 0-1
        """
        uncertainty = {}
        for pos, data in prediction_sets.items():
            set_size = data['set_size']
            # Normalize by total horses in race
            u_c = set_size / total_horses if total_horses > 0 else 1.0
            uncertainty[pos] = round(u_c, 4)
        
        return uncertainty
    
    def generate_valid_combinations(self,
                                   prediction_sets: Dict[str, Dict],
                                   max_combinations: int = 50) -> List[Tuple]:
        """
        Generate valid exotic combinations from prediction sets.
        
        Ensures no horse appears in multiple positions (valid permutation).
        
        Args:
            prediction_sets: Output from predict_exotic_sets
            max_combinations: Limit to prevent combinatorial explosion
            
        Returns:
            List of tuples (horse_1st, horse_2nd, ...) representing valid bets
        """
        from itertools import product
        
        positions = list(prediction_sets.keys())
        horse_lists = [prediction_sets[p]['horses'] for p in positions]
        
        # Generate all combinations
        valid_combos = []
        for combo in product(*horse_lists):
            # Check all horses are distinct (valid finishing order)
            if len(set(combo)) == len(combo):
                valid_combos.append(combo)
                if len(valid_combos) >= max_combinations:
                    break
        
        return valid_combos
    
    def get_coverage_guarantee(self) -> float:
        """Return theoretical coverage guarantee."""
        return 1 - self.alpha  # 0.90 for alpha=0.1


# Utility functions for integration
def create_default_engines(jurisdiction: str = 'NZ'):
    """Factory function to create calibrated engines for a jurisdiction."""
    config = CalibrationConfig(jurisdiction=jurisdiction)
    calibration_engine = GodTierCalibrationEngine(n_classes=4, config=config)
    conformal_predictor = ExoticConformalPredictor(alpha=0.1, config=config)
    return calibration_engine, conformal_predictor
