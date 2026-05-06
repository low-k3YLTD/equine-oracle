"""
Equine Oracle v3.1 - Exotic Prediction API Endpoint
FastAPI router for conformal prediction sets
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Tuple
import numpy as np

from backend.ensemble.ensemble_service_v2 import MetaEnsembleV2
from backend.utils.auth import get_current_user
from backend.utils.cache import cache_prediction
from backend.monitoring.metrics import record_prediction_latency

router = APIRouter(prefix="/api/v1/predict", tags=["predictions"])

# Global ensemble instance (initialized in main.py)
ensemble: Optional[MetaEnsembleV2] = None

def get_ensemble() -> MetaEnsembleV2:
    if ensemble is None:
        raise HTTPException(status_code=503, detail="Ensemble not initialized")
    return ensemble


# ============================================================================
# Request/Response Models
# ============================================================================

class ExoticPredictionRequest(BaseModel):
    race_id: str = Field(..., description="Unique race identifier")
    bet_type: str = Field(default="trifecta", regex="^(exacta|trifecta|quartet)$")
    jurisdiction: Optional[str] = Field(default="NZ", regex="^(NZ|AU|UK|HK)$")
    max_combinations: int = Field(default=50, ge=1, le=200)
    include_raw_probabilities: bool = Field(default=False)
    
    class Config:
        schema_extra = {
            "example": {
                "race_id": "NZ_R20250419_R7",
                "bet_type": "trifecta",
                "jurisdiction": "NZ",
                "max_combinations": 50
            }
        }


class PredictionSet(BaseModel):
    horses: List[int] = Field(..., description="Horse indices in prediction set")
    scores: List[float] = Field(..., description="Calibrated probabilities")
    set_size: int = Field(..., description="Number of horses in set")
    quantile_threshold: float = Field(..., description="Non-conformity threshold used")


class ExoticPredictionResponse(BaseModel):
    race_id: str
    bet_type: str
    jurisdiction: str
    prediction_sets: Dict[str, PredictionSet]
    uncertainty_coefficient: Dict[str, float]
    valid_combinations: List[Tuple[int, ...]]
    coverage_guarantee: float = Field(0.90, description="Theoretical coverage guarantee")
    total_combinations: int
    high_uncertainty_warning: bool
    calibrated: bool
    timestamp: str
    
    class Config:
        schema_extra = {
            "example": {
                "race_id": "NZ_R20250419_R7",
                "bet_type": "trifecta",
                "jurisdiction": "NZ",
                "prediction_sets": {
                    "1st": {"horses": [3, 7, 12], "scores": [0.35, 0.28, 0.15], "set_size": 3, "quantile_threshold": 0.65},
                    "2nd": {"horses": [1, 3, 7, 12], "scores": [0.22, 0.20, 0.18, 0.12], "set_size": 4, "quantile_threshold": 0.78},
                    "3rd": {"horses": [1, 2, 3, 7, 12], "scores": [0.15, 0.14, 0.13, 0.12, 0.10], "set_size": 5, "quantile_threshold": 0.85}
                },
                "uncertainty_coefficient": {"1st": 0.25, "2nd": 0.33, "3rd": 0.42},
                "valid_combinations": [[3, 1, 2], [3, 7, 1], [7, 3, 1]],
                "coverage_guarantee": 0.90,
                "total_combinations": 60,
                "high_uncertainty_warning": True,
                "calibrated": True,
                "timestamp": "2026-04-19T20:09:00Z"
            }
        }


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/exotic", response_model=ExoticPredictionResponse)
async def predict_exotic(
    request: ExoticPredictionRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    ens: MetaEnsembleV2 = Depends(get_ensemble)
):
    """
    Generate conformal prediction sets for exotic bets.
    
    Returns prediction sets for each finishing position with 90% coverage
    guarantee, uncertainty coefficients, and valid exotic combinations.
    
    **Coverage Guarantee**: At least 90% of true outcomes will fall within
    the returned prediction sets (distribution-free guarantee).
    """
    import time
    start_time = time.time()
    
    try:
        # Update jurisdiction if different from default
        if request.jurisdiction != ens.jurisdiction:
            ens.jurisdiction = request.jurisdiction
            ens.jurisdiction_config = ens._get_jurisdiction_config(request.jurisdiction)
        
        # Fetch race features (implement based on your data source)
        race_features = await fetch_race_features(
            request.race_id, 
            request.jurisdiction
        )
        
        # Add metadata
        race_features['race_id'] = request.race_id
        race_features['total_horses'] = len(race_features.get('1st', []))
        
        # Get conformal prediction
        result = ens.predict_exotic_conformal(
            race_features,
            bet_type=request.bet_type
        )
        
        # Limit combinations
        result['valid_combinations'] = result['valid_combinations'][:request.max_combinations]
        result['calibrated'] = ens.calibration_fitted
        
        # Build response
        response = ExoticPredictionResponse(
            race_id=request.race_id,
            bet_type=request.bet_type,
            jurisdiction=request.jurisdiction,
            prediction_sets={
                pos: PredictionSet(**data) 
                for pos, data in result['prediction_sets'].items()
            },
            uncertainty_coefficient=result['uncertainty_coefficient'],
            valid_combinations=result['valid_combinations'],
            coverage_guarantee=result['coverage_guarantee'],
            total_combinations=result['total_combinations'],
            high_uncertainty_warning=result['high_uncertainty_warning'],
            calibrated=result['calibrated'],
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        
        # Background: cache and metrics
        background_tasks.add_task(
            cache_prediction, 
            request.race_id, 
            response.dict()
        )
        background_tasks.add_task(
            record_prediction_latency,
            "exotic_conformal",
            time.time() - start_time
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/calibrated")
async def predict_calibrated(
    race_id: str,
    jurisdiction: Optional[str] = "NZ",
    include_calibration_info: bool = False,
    current_user = Depends(get_current_user),
    ens: MetaEnsembleV2 = Depends(get_ensemble)
):
    """
    Standard win prediction with calibrated probabilities.
    
    Returns calibrated win probabilities using joint temperature scaling
    and CVXPY-optimized ensemble weights.
    """
    try:
        # Fetch features
        features = await fetch_race_features(race_id, jurisdiction)
        
        # Predict with calibration
        result = ens.predict(
            features, 
            race_id=race_id,
            return_raw=include_calibration_info
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Helper Functions (implement based on your infrastructure)
# ============================================================================

async def fetch_race_features(race_id: str, jurisdiction: str) -> Dict[str, Any]:
    """
    Fetch race features from database or external API.
    Implement based on your data source (TAB NZ, TAB AUS, etc.)
    """
    # Placeholder - replace with your actual implementation
    from backend.data.race_fetcher import RaceFetcher
    
    fetcher = RaceFetcher(jurisdiction=jurisdiction)
    return await fetcher.get_race_features(race_id)


# ============================================================================
# Initialization (call from main.py)
# ============================================================================

def initialize_ensemble(model_dir: str, jurisdiction: str = 'NZ'):
    """Initialize global ensemble instance."""
    global ensemble
    ensemble = MetaEnsembleV2(model_dir=model_dir, jurisdiction=jurisdiction)
    return ensemble
