"""
Equine Oracle v3.1 - Meta Ensemble Service with Calibration
Modified integration points - merge with your existing file
"""

import numpy as np
from typing import Dict, List, Optional, Any
from .calibration_engine import (
    GodTierCalibrationEngine, 
    ExoticConformalPredictor,
    CalibrationConfig,
    create_default_engines
)


class MetaEnsembleV2:
    """
    Production ensemble with v3.1 calibration and conformal prediction.
    """
    
    def __init__(self, model_dir: str, jurisdiction: str = 'NZ'):
        self.model_dir = model_dir
        self.jurisdiction = jurisdiction
        
        # Load your existing 5 models
        self.models = self._load_base_models(model_dir)
        
        # v3.1: Initialize calibration engines
        config = CalibrationConfig(jurisdiction=jurisdiction)
        self.calibration_engine = GodTierCalibrationEngine(n_classes=4, config=config)
        self.conformal_predictor = ExoticConformalPredictor(alpha=0.1, config=config)
        
        # Fitting status
        self.calibration_fitted = False
        self.conformal_fitted = False
        
        # Jurisdiction-specific parameters
        self.jurisdiction_config = self._get_jurisdiction_config(jurisdiction)
    
    def _load_base_models(self, model_dir: str) -> Dict[str, Any]:
        """Your existing model loading logic."""
        # Keep your current implementation:
        # - LightGBM Ranker
        # - XGBoost Ranker  
        # - CatBoost Ranker
        # - TabNet Ranker
        # - Grok-4 Semantic Scorer
        pass  # Your existing code here
    
    def _get_jurisdiction_config(self, jurisdiction: str) -> Dict:
        """Market-specific configuration."""
        configs = {
            'NZ': {'takeout': 0.25, 'currency': 'NZD', 'data_source': 'tab_nz'},
            'AU': {'takeout': 0.22, 'currency': 'AUD', 'data_source': 'tab_aus'},
            'UK': {'takeout': 0.20, 'currency': 'GBP', 'data_source': 'betfair_uk'},
            'HK': {'takeout': 0.25, 'currency': 'HKD', 'data_source': 'hkjc'}
        }
        return configs.get(jurisdiction, configs['NZ'])
    
    # =====================================================================
    # v3.1 MODIFIED PREDICTION METHOD - REPLACE YOUR EXISTING predict()
    # =====================================================================
    def predict(self, features: np.ndarray, race_id: str, return_raw: bool = False) -> Dict:
        """
        Main prediction method with calibrated probabilities.
        
        Args:
            features: Input features [n_horses, n_features]
            race_id: Unique race identifier
            return_raw: If True, also return uncalibrated probabilities
            
        Returns:
            Dict with calibrated win probabilities and metadata
        """
        # Get raw predictions from all 5 base models
        base_predictions = []
        model_names = []
        
        for name, model in self.models.items():
            try:
                pred = model.predict(features)
                base_predictions.append(pred)
                model_names.append(name)
            except Exception as e:
                # Log error but continue with other models
                print(f"Model {name} failed: {e}")
                continue
        
        if not base_predictions:
            raise ValueError("All base models failed")
        
        # Stack to [n_horses, n_models]
        base_matrix = np.column_stack(base_predictions)
        
        # v3.1: Apply calibration if fitted
        if self.calibration_fitted:
            calibrated_probs = self.calibration_engine.predict_calibrated(base_matrix)
        else:
            # Fallback: simple mean with temperature=1.0
            calibrated_probs = base_matrix.mean(axis=1)
            calibrated_probs = np.clip(calibrated_probs, 0.001, 0.999)
            calibrated_probs = calibrated_probs / calibrated_probs.sum()
        
        # Build result
        result = {
            'race_id': race_id,
            'win_probabilities': calibrated_probs.tolist(),
            'calibrated': self.calibration_fitted,
            'jurisdiction': self.jurisdiction,
            'models_used': model_names,
            'takeout_rate': self.jurisdiction_config['takeout']
        }
        
        if return_raw:
            result['raw_probabilities'] = base_matrix.mean(axis=1).tolist()
            result['temperature'] = self.calibration_engine.temperature if self.calibration_fitted else 1.0
        
        return result
    
    # =====================================================================
    # v3.1 NEW METHOD - Add to your class
    # =====================================================================
    def predict_exotic_conformal(self,
                                  race_features: Dict[str, Any],
                                  bet_type: str = 'trifecta') -> Dict:
        """
        Conformal prediction for exotic bets with uncertainty quantification.
        
        Args:
            race_features: Dict with keys '1st', '2nd', '3rd', '4th' 
                          containing probability arrays, plus 'total_horses'
            bet_type: 'exacta', 'trifecta', or 'quartet'
            
        Returns:
            Dict with prediction sets, uncertainty coefficients, valid combinations
        """
        if not self.conformal_fitted:
            # Use default quantiles if not fitted
            pass
        
        # Get position-specific probabilities
        position_probs = {}
        for pos in ['1st', '2nd', '3rd', '4th']:
            if pos in race_features:
                # Ensure using calibrated probabilities
                position_probs[pos] = np.array(race_features[pos])
        
        # Generate conformal prediction sets
        prediction_sets = self.conformal_predictor.predict_exotic_sets(
            position_probs, 
            bet_type=bet_type
        )
        
        # Calculate uncertainty coefficients
        total_horses = race_features.get('total_horses', len(position_probs.get('1st', [])))
        uncertainty = self.conformal_predictor.calculate_uncertainty_coefficient(
            prediction_sets, 
            total_horses
        )
        
        # Generate valid combinations
        combinations = self.conformal_predictor.generate_valid_combinations(
            prediction_sets,
            max_combinations=50
        )
        
        return {
            'race_id': race_features.get('race_id', 'unknown'),
            'bet_type': bet_type,
            'jurisdiction': self.jurisdiction,
            'prediction_sets': prediction_sets,
            'uncertainty_coefficient': uncertainty,
            'valid_combinations': combinations,
            'coverage_guarantee': self.conformal_predictor.get_coverage_guarantee(),
            'total_combinations': len(combinations),
            'high_uncertainty_warning': any(u > 0.4 for u in uncertainty.values())
        }
    
    # =====================================================================
    # v3.1 FITTING METHODS - Call these during training/retraining
    # =====================================================================
    def fit_calibration(self, 
                       validation_data: List[Dict],
                       optimize_temperature: bool = True) -> Dict:
        """
        Fit calibration engine on validation set.
        
        Args:
            validation_data: List of dicts with 'features', 'true_winner', 'race_id'
            
        Returns:
            Diagnostics dict
        """
        X_val = np.array([d['features'] for d in validation_data])
        y_val = np.array([d['true_winner'] for d in validation_data])
        group_ids = np.array([d['race_id'] for d in validation_data])
        
        # Get base predictions
        base_preds = []
        for model in self.models.values():
            base_preds.append(model.predict(X_val))
        
        base_matrix = np.column_stack(base_preds)
        
        # Fit temperature scaling
        if optimize_temperature:
            temp = self.calibration_engine.fit_temperature(base_matrix, y_val, group_ids)
            print(f"Optimal temperature: {temp:.3f}")
        
        # Fit stacked calibration
        calibrated = self.calibration_engine.fit_stacked_calibration(
            base_matrix, y_val, group_ids
        )
        
        self.calibration_fitted = True
        
        return {
            'temperature': self.calibration_engine.temperature,
            'weights': self.calibration_engine.calibration_weights.tolist(),
            'n_samples': len(validation_data),
            'calibration_error': float(np.mean((calibrated - y_val) ** 2))
        }
    
    def fit_conformal(self, calibration_data: List[Dict]) -> None:
        """
        Fit conformal predictor on calibration set.
        
        Args:
            calibration_data: List of dicts with 'position', 'scores', 'true_outcome'
        """
        for item in calibration_data:
            position = item.get('position', '1st')
            scores = np.array(item['scores'])
            true_outcome = np.array(item['true_outcome'])
            
            self.conformal_predictor.fit(scores, true_outcome, position=position)
        
        self.conformal_fitted = True
        print(f"Conformal predictor fitted with {self.conformal_predictor.get_coverage_guarantee():.0%} coverage")

