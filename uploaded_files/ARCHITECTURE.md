# ARCHITECTURE.md
# Equine Oracle V3.1 — Complete System Architecture
## Lowkey Consultants Ltd | Master Architecture Document

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Precognition Engine V3.1 — Core Modules](#2-precognition-engine-v31--core-modules)
3. [Model Zoo — 8 Parallel Estimators](#3-model-zoo--8-parallel-estimators)
4. [Two-Stage Meta-Ensemble Architecture](#4-two-stage-meta-ensemble-architecture)
5. [Feature Engineering Pipeline (56→120)](#5-feature-engineering-pipeline-56120)
6. [Reinforcement Learning Layer](#6-reinforcement-learning-layer)
7. [API Service Architecture](#7-api-service-architecture)
8. [5-Agent Swarm Design](#8-5-agent-swarm-design)
9. [MLOps Infrastructure](#9-mlops-infrastructure)
10. [Data Flow — End to End](#10-data-flow--end-to-end)
11. [Gap Analysis & V4.0 Roadmap](#11-gap-analysis--v40-roadmap)

---

## 1. System Overview

The Equine Oracle is a **multi-layer cognitive prediction system** for thoroughbred horse racing markets. It is designed around five architectural principles:

1. **Causal over correlational** — All signal extraction uses causal methods where possible (purged DML, counterfactuals)
2. **Uncertainty-aware** — Every prediction carries a calibrated confidence interval; the system knows what it doesn't know
3. **Regime-aware** — The system identifies market regimes and adapts its weighting accordingly
4. **Production-hardened** — Sub-150ms latency, drift detection, zero-downtime deployment
5. **Evidence-auditable** — Every decision can be traced from input features through SHAP values to final ranking

### Version History

| Version | NDCG@4 | ECE | Key Additions |
|---------|--------|-----|---------------|
| v1.0 | 0.710 | ~0.15 | Single LightGBM, basic features |
| v2.0 | 0.890 | ~0.10 | XGBoost ensemble, causal engine v1 |
| v2.5 | 0.930 | ~0.09 | RegimeMemory, DML, Dark Pool Whisper |
| v3.0 | 0.953 | ~0.08 | 5-model ensemble, Android app, API |
| **v3.1** | **0.982** | **0.044** | **CatBoost + TabNet + 2-stage meta-learner + CF-CVaR** |

---

## 2. Precognition Engine V3.1 — Core Modules

### 2.1 TemporalStratifiedSensorGrid

**File:** `backend/core/temporal_sensor_grid.py`  
**Class:** `TemporalStratifiedSensorGrid`

The grid is the perceptual layer — it extracts multi-horizon form signals from raw race history without temporal leakage.

```
SENSOR GRID DESIGN
──────────────────
Horizon L1  (last 1 race):   Immediate form signal
Horizon L3  (last 3 races):  Short-term trend
Horizon L5  (last 5 races):  Medium-term form curve
Horizon L10 (last 10 races): Long-term baseline
Season      (current season): Class/track affinity

For each horizon, extract:
  - avg_position_Lk          (weighted, recency decay λ=0.85)
  - avg_speed_rating_Lk      (normalized by distance/track)
  - consistency_score_Lk     (std deviation of positions)
  - win_rate_Lk              (binary hit rate)
  - form_momentum_Lk         (Lk vs Lk+1 delta)

Stratification prevents:
  - Data leakage across race dates
  - Future peek in cross-validation
  - Distribution shift between train/test windows
```

**Key Methods:**
- `extract(horse_id, race_date, k_horizons)` → `Dict[str, float]`
- `compute_form_decay(positions, λ=0.85)` → `np.ndarray`
- `stratify_by_date(df, n_folds)` → `List[Tuple[pd.DataFrame, pd.DataFrame]]`

### 2.2 HardenedCausalEngine

**File:** `backend/core/causal_engine.py`  
**Class:** `HardenedCausalEngine`

Standard ML captures correlation. The CausalEngine captures **why** a horse wins — separating genuine causal factors (distance fitness, going preference) from confounders (field quality, draw bias).

```
CAUSAL IDENTIFICATION STRATEGY
────────────────────────────────
Method: Purged Double Machine Learning (DML)
        as per Chernozhukov et al. (2018)

Step 1: Nuisance models
  g_hat(X) = E[Y|X]     (outcome nuisance — LightGBM)
  m_hat(X) = E[D|X]     (treatment nuisance — LightGBM)

Step 2: Partial out confounders
  Ỹ = Y - g_hat(X)      (residualized outcome)
  D̃ = D - m_hat(X)      (residualized treatment)

Step 3: Causal effect estimate
  θ = E[Ỹ·D̃] / E[D̃²]   (Frisch-Waugh-Lovell)

Purging: K-fold cross-fitting with 20-race gap
         between nuisance training and DML estimation
         (prevents overfitting-induced bias)

Treatments estimated:
  - distance_fitness (causal effect of distance match)
  - going_preference (causal effect of track condition)
  - jockey_lift      (causal effect of jockey assignment)
  - class_drop       (causal effect of downgrading class)
  - draw_bias        (causal effect of barrier position)
```

**Key Methods:**
- `estimate_causal_effects(df, treatment_vars, outcome_var)` → `CausalEstimates`
- `cross_fit_nuisance(df, k=5, purge_gap=20)` → `Tuple[np.ndarray, np.ndarray]`
- `compute_ate(residual_Y, residual_D)` → `float`

### 2.3 Chaos Metrics — Rosenstein Lyapunov + Takens Embedding

**File:** `backend/core/chaos_metrics.py`  
**Classes:** `RosensteinLyapunov`, `TakensEmbedding`

The racing market is a nonlinear dynamical system. The Lyapunov exponent measures the **degree of chaos** (predictability horizon) and Takens embedding reconstructs the system's phase space from a single observable time series.

```
LYAPUNOV EXPONENT (Rosenstein Algorithm)
──────────────────────────────────────────
Input: Time series of odds movements or form scores
       x_t (length N ≥ 500 observations)

Step 1: Delay embedding via Takens theorem
  Dimension m estimated via FNN (False Nearest Neighbors)
  Delay τ estimated via mutual information minimum

Step 2: Phase space reconstruction
  X_i = [x_i, x_{i+τ}, x_{i+2τ}, ..., x_{i+(m-1)τ}]

Step 3: Nearest neighbor search
  For each X_i, find nearest neighbor X_j (j ≠ i±w)
  where w = Theiler window (prevents temporal autocorrelation)

Step 4: Divergence estimation
  d_j(t) = |X_{i+t} - X_{j+t}|
  λ_max = slope of mean(ln d_j(t)) vs t

Interpretation:
  λ > 0.1  → Chaotic regime (high uncertainty, reduce position size)
  λ ≈ 0.0  → Periodic regime (structured, model highly reliable)
  λ < 0.0  → Stable attractor (extreme predictability, rare)

Current regime flags: CHAOTIC | TRANSITIONAL | STABLE | PERIODIC
```

### 2.4 Dark Pool Whisper

**File:** `backend/core/dark_pool_whisper.py`  
**Class:** `DarkPoolWhisper`

Racing markets have a "dark pool" analog — informed money that moves before it shows in the displayed market. The Whisper detects early sharp money signals.

```
SIGNAL DETECTION PIPELINE
──────────────────────────
Input: TAB odds time series (t₀ to race_start)

1. Baseline computation
   Fair_odds = 1 / (win_probability_from_model)
   Market_odds = TAB_displayed_odds

2. Sharp money signal
   Value_drift = (Market_odds - Fair_odds) / Fair_odds
   Early_drift = drift in T-60min window before T-5min

3. Volume proxy (where available)
   Bet_velocity = d(pool_size)/dt
   Abnormal_velocity = velocity > μ + 2σ (rolling 30-day)

4. Whisper score (0→1)
   whisper_score = σ(β₁ · early_drift + β₂ · velocity_flag)
   β coefficients trained on historical sharp bettor outcomes

Output: whisper_score, drift_direction, confidence
```

### 2.5 RegimeMemoryArchitecture

**File:** `backend/core/regime_memory.py`  
**Class:** `RegimeMemoryArchitecture`

Markets move through regimes: form horses win consistently (trending), then upsets cluster (mean-reverting), then chaos (exogenous shock). The RegimeMemory identifies which regime we're in and adjusts ensemble weights accordingly.

```
REGIME IDENTIFICATION
──────────────────────
Method: Hidden Markov Model (HMM) + K-Means

Features for regime detection:
  - 7-day rolling upset rate (% favourites beaten)
  - Market efficiency score (ECE of market-implied probs)
  - Lyapunov exponent (from ChaosMetrics)
  - Meeting-type distribution (flat/hurdle/chase ratio)
  - Track going distribution

HMM States (K=4):
  State 0: TREND_STABLE    — Form horses dominating, model weights: [0.4, 0.3, 0.2, 0.1]
  State 1: MEAN_REVERTING  — Upsets frequent, increase RF/RL weight
  State 2: CHAOTIC         — High Lyapunov, reduce all weights, widen CIs
  State 3: SEASONAL_SHIFT  — Track/weather structural break

Memory mechanism:
  - Regime posterior stored as Dirichlet prior
  - 30-race rolling window for regime state estimation
  - Exponential smoothing α=0.7 for regime weight adjustment
```

### 2.6 CounterfactualFeedbackEngine

**File:** `backend/core/counterfactual_engine.py`  
**Class:** `CounterfactualFeedbackEngine`

After every race, the engine asks: "What would have needed to be different for Horse X to win?" This generates synthetic training examples and corrects systematic model errors.

```
COUNTERFACTUAL GENERATION (DiCE-style)
────────────────────────────────────────
For each race outcome:
  1. Take actual winner (rank_actual=1)
  2. Take model's predicted top-3 (ensemble_rank ≤ 3)
  3. If model was wrong (predicted ≠ actual):
     a. Generate counterfactual: minimum feature change
        that flips the prediction to the actual winner
     b. Constraint: features must be physically plausible
        (no barrier → 1 for every horse, no weight < 50kg)
  4. Store (counterfactual_input, actual_outcome) as
     synthetic training example

Online learning:
  - Batch counterfactuals weekly (50+ races minimum)
  - Fine-tune ensemble meta-learner on augmented set
  - Weight counterfactual examples at 0.3× real examples
  - Track ECE improvement per batch

Key insight: Systematic model errors cluster by:
  - Track type (soft going underweighted)
  - Race class (maiden vs open weight difference)
  - Jockey form (recent winning streak ignored)
```

---

## 3. Model Zoo — 8 Parallel Estimators

```
┌──────────────────────────────────────────────────────────────────────┐
│  LAYER: BASE MODELS (Parallel Inference, Output → OOF Predictions)  │
├──────────────┬──────────────────────────────────────────────────────┤
│  Model       │  Specification                                        │
├──────────────┼──────────────────────────────────────────────────────┤
│ 1. LightGBM  │  LambdaRank · 200 est · lr=0.05 · max_depth=8       │
│    Ranker    │  num_leaves=63 · Feature importance: perf_L5 (23.4%) │
│              │  Primary ranking model, NDCG@4 optimized             │
├──────────────┼──────────────────────────────────────────────────────┤
│ 2. LightGBM  │  Binary classifier · balanced classes                │
│    Classifier│  100 est · max_depth=6 · Calibrated w/ isotonic      │
│              │  Provides calibrated win probabilities                │
├──────────────┼──────────────────────────────────────────────────────┤
│ 3. XGBoost   │  rank:pairwise · 150 est · eta=0.03 · max_depth=7   │
│    Ranker    │  GPU acceleration · subsample=0.8                    │
│              │  Captures high-order feature interactions            │
├──────────────┼──────────────────────────────────────────────────────┤
│ 4. CatBoost  │  YetiRank · 300 iter · auto-depth · GPU support     │
│    Ranker    │  Native categorical features · L2_leaf_reg=3         │
│              │  Best for track/race_type categoricals               │
├──────────────┼──────────────────────────────────────────────────────┤
│ 5. TabNet    │  Attention ranker · 8 decision steps · n_d=64        │
│    Ranker    │  Sparse feature selection · CUDA optimized           │
│              │  Captures non-linear interaction patterns            │
├──────────────┼──────────────────────────────────────────────────────┤
│ 6. Logistic  │  L2 reg · C=0.5 · RobustScaler input                │
│    Regression│  Isotonic calibration · Platt scaling                │
│              │  Interpretable baseline, well-calibrated             │
├──────────────┼──────────────────────────────────────────────────────┤
│ 7. Random    │  200 est · max_depth=10 · min_samples_split=5        │
│    Forest    │  sklearn 1.3+ · joblib protocol=5                    │
│              │  Ensemble diversity via bagging                      │
├──────────────┼──────────────────────────────────────────────────────┤
│ 8. Grok-4    │  xAI API · Redis cache TTL=24h                      │
│    Semantic  │  Input: jockey bio + trainer record + pedigree       │
│              │  Output: confidence_score (0-1) + explanation text   │
│              │  Fallback: distilbert local model (offline)          │
└──────────────┴──────────────────────────────────────────────────────┘
```

### OOF Prediction Strategy

All base models use **Out-of-Fold (OOF)** predictions for meta-learner training:

```python
# TemporalStratifiedKFold — prevents look-ahead bias
cv = TemporalStratifiedKFold(n_splits=5, gap_races=20)

for fold_idx, (train_idx, val_idx) in enumerate(cv.split(df)):
    # Train base model on train split
    model.fit(df.iloc[train_idx])
    # Generate OOF predictions on val split
    oof_preds[val_idx] = model.predict(df.iloc[val_idx])

# oof_preds used as meta-features → no temporal leakage
```

---

## 4. Two-Stage Meta-Ensemble Architecture

```
STAGE 1: BASE MODEL → OOF META-FEATURES
─────────────────────────────────────────
Input:  X (120 features per runner)
Output: Meta-features M (18 columns)

  M = [pred_lgbm_ranker,   # 0-1 win probability
       pred_lgbm_clf,      # calibrated probability
       pred_xgboost,       # pairwise ranking score
       pred_catboost,      # YetiRank score
       pred_tabnet,        # attention output
       pred_logreg,        # calibrated probability
       pred_rf,            # vote-based probability
       pred_grok4,         # semantic confidence
       + top_10_original_features (selected by Optuna)]

STAGE 2A: LOGISTIC META-LEARNER
─────────────────────────────────
Input:  M (18 meta-features)
Method: Logistic Regression, penalty='l1', C=1.0
        → Learns optimal sparse weights for base models
        → Isotonic recalibration post-prediction
Output: calibrated_proba_2a (0-1, well-calibrated)

Key property: L1 penalty drives weak models to zero weight
              → Automatic base model selection

STAGE 2B: LIGHTGBM FINAL RANKER
─────────────────────────────────
Input:  M + [calibrated_proba_2a] (19 features)
Method: LightGBM · lambdarank · NDCG@4 optimization
        100 est · lr=0.01 · early_stopping=20
Output: final_ensemble_score (ranking scores per race)

POST-PROCESSING
────────────────
Group by race_id → rank by final_ensemble_score (desc)
Clip 99th percentile outliers
Normalize scores to sum=1.0 per race (probability simplex)
Output: ensemble_rank, win_probability, confidence_interval
```

### Ensemble Weight Analysis (Current Champion v3.1)

| Model | Learned Weight (Stage 2A) | Direction |
|-------|--------------------------|-----------|
| LightGBM Ranker | 0.31 | ↑ Primary |
| XGBoost Ranker | 0.22 | ↑ |
| CatBoost Ranker | 0.19 | ↑ |
| TabNet | 0.14 | ↑ |
| Logistic Regression | 0.07 | → |
| Random Forest | 0.05 | → |
| Grok-4 Semantic | 0.02 | ↓ Low without good API data |
| LightGBM Classifier | 0.00 | ✗ Pruned by L1 |

---

## 5. Feature Engineering Pipeline (56→120)

```
INPUT: Raw race card data
OUTPUT: 120 engineered features per runner

GROUP 1: Historical Performance (56 features — v1.0 core)
──────────────────────────────────────────────────────────
  • avg_perf_index_L5         (weighted form index, L5)  [TOP FEATURE: 23.4%]
  • weighted_form_score       (decay-weighted composite)  [2nd: 18.7%]
  • days_since_last_race      (freshness signal)
  • avg_position_L3/L5/L10   (multi-horizon position avg)
  • win_rate_L10              (binary win rate, 10 races)
  • place_rate_L10            (top-3 rate)
  • speed_rating_L3           (speed figure average)
  • consistency_score_L5      (std dev of positions)
  • distance_win_rate         (win rate at this distance ±100m)
  • track_win_rate            (venue-specific win rate)
  • going_win_rate_soft       (performance on soft going)
  • going_win_rate_firm       (performance on firm going)
  • jockey_win_rate_L50       (jockey recent form)
  • trainer_win_rate_L50      (trainer recent form)
  • jockey_trainer_combo_rate (combination win rate)
  ... (42 more historical features)

GROUP 2: Weather/Track Features (12 features — V3.0 addition)
──────────────────────────────────────────────────────────────
  • track_moisture_pct        (going measurement %)
  • wind_speed_mph            (headwind effect)
  • temperature_f             (performance temperature correlation)
  • precipitation_last_24h    (track saturation proxy)
  • going_soft_indicator      (binary flag)
  • going_code                (encoded: F/G/S/H/AW)
  • track_rail_position       (inside/outside advantage)
  • humidity_pct
  • barometric_pressure       (weather system proxy)
  • uv_index                  (afternoon glare)
  • wind_direction_deg        (track-specific headwind)
  • dew_point_f               (turf hardness proxy)

GROUP 3: Semantic Features (24 features — V3.1 Grok-4)
────────────────────────────────────────────────────────
  • grok4_jockey_form_score   (0-1 NLP confidence)
  • grok4_trainer_momentum    (sentiment: improving/declining)
  • grok4_horse_fitness       (vet/trainer comment analysis)
  • grok4_market_confidence   (analyst consensus score)
  • grok4_weight_concern      (weight/class concern flag)
  • grok4_distance_confidence (reported distance preference)
  ... (18 more Grok-4 extracted semantic features)

GROUP 4: Interaction Features (28 features — V3.1 new)
────────────────────────────────────────────────────────
  • track_x_distance_fit      (venue × distance match score)
  • jockey_x_trainer_synergy  (combination lift factor)
  • pace_scenario_cluster     (K-means pace profile: 0-4)
  • barrier_x_distance_adj    (draw × distance adjustment)
  • weight_x_class_ratio      (weight carried vs class avg)
  • form_x_going_interaction  (form × conditions interaction)
  ... (22 more interaction features)

PREPROCESSING PIPELINE
────────────────────────
1. MulticollinearityReducer (VIF < 5.0, r-threshold < 0.75)
   → Removes redundant features, typically reduces 120 → ~95
2. RobustScaler (IQR-based, outlier-resistant)
3. SMOTE (class balancing for rare winners in classifier)
4. FeatureSelector (SelectKBest + RFE hybrid, Optuna-tuned k)
```

---

## 6. Reinforcement Learning Layer

### 6.1 KellyRLAgent (PPO)

**File:** `backend/rl/kelly_rl_agent.py`

```
ENVIRONMENT DESIGN
───────────────────
State space S:
  - current_bankroll (normalized 0-1)
  - win_probabilities (n_runners × 1)
  - market_odds (n_runners × 1)
  - regime_state (one-hot, 4 regimes)
  - lyapunov_exponent (scalar)
  - recent_roi_7day (scalar)

Action space A:
  - Continuous: stake_fraction ∈ [0, max_kelly]
  - Discrete head: bet_type ∈ {WIN, PLACE, EACH_WAY, PASS}
  - Multi-horse: portfolio of up to 3 simultaneous bets

Reward function R:
  r_t = realized_roi_t
       + λ₁ · sharpe_bonus_t       (Sharpe > 1.5 reward)
       - λ₂ · drawdown_penalty_t   (max drawdown > 15% penalty)
       - λ₃ · overbet_penalty_t    (Kelly fraction > 0.25 penalty)

PPO Hyperparameters:
  - n_steps=2048 · batch_size=256 · n_epochs=10
  - clip_range=0.2 · ent_coef=0.01 · vf_coef=0.5
  - learning_rate=3e-4 · gamma=0.99 · gae_lambda=0.95
```

### 6.2 RobustPositionSizer (Cornish-Fisher CVaR)

**File:** `backend/rl/position_sizer.py`

```
POSITION SIZING ALGORITHM
──────────────────────────
Input:  win_probability p, market_odds o, bankroll B

Step 1: Kelly fraction
  f* = (p·o - 1) / (o - 1)   [standard Kelly]
  f_half = f* / 2              [half-Kelly for conservatism]

Step 2: Cornish-Fisher CVaR adjustment
  # Adjust for tail risk using higher-order moments
  z_α = z_95 + (z_95² - 1)·γ₁/6 + (z_95³ - 3z_95)·γ₂/24
        - (2z_95³ - 5z_95)·γ₁²/36
  
  where:
    γ₁ = skewness of recent P&L distribution
    γ₂ = excess kurtosis of recent P&L distribution
    z_95 = 1.645 (95% confidence level)
  
  CVaR_adjusted = μ_pnl - σ_pnl · z_α
  
  # Scale down Kelly if CVaR > threshold
  if CVaR_adjusted < -max_acceptable_loss:
    f_adjusted = f_half * (max_acceptable_loss / abs(CVaR_adjusted))
  else:
    f_adjusted = f_half

Step 3: Regime scaling
  f_final = f_adjusted * regime_confidence_multiplier
  # Regime multipliers: STABLE→1.0, TREND→0.9, MEAN_REV→0.7, CHAOTIC→0.4

Output: stake = B * min(f_final, 0.10)  [hard cap: 10% of bankroll per bet]
```

---

## 7. API Service Architecture

```
NGINX (Load Balancer + SSL)
│  Rate limit: 100/min (free) | 1000/min (premium)
│  WAF: SQL injection, XSS protection
│  SSL termination (Let's Encrypt / ACM)
│
├──▶ FastAPI Application (Gunicorn + 4 workers)
│    │
│    ├── POST /api/v2/predict
│    │   1. Validate RaceCard (Pydantic)
│    │   2. Load features from FeatureStore
│    │   3. Run 8 base models (parallel thread pool)
│    │   4. Run meta-ensemble
│    │   5. Apply calibration
│    │   6. Run KellyRLAgent for stake sizing
│    │   7. Log to Postgres (async)
│    │   8. Return PredictionResponse
│    │
│    ├── POST /api/v2/explain
│    │   1. Run prediction (if not cached)
│    │   2. Load SHAP explainer (precomputed)
│    │   3. Compute waterfall values for top-3 horses
│    │   4. Return SHAP values + force plot data
│    │
│    ├── GET /api/v2/health
│    │   → liveness: process alive
│    │   → readiness: all models loaded, Redis connected
│    │   → metrics: ECE (last 100 races), drift_status
│    │
│    └── GET /api/v2/metrics (Prometheus format)
│
├──▶ Redis (Cache Layer)
│    - Grok-4 API responses (TTL: 24h)
│    - Race card feature cache (TTL: 30min)
│    - Rate limiting token buckets
│
└──▶ PostgreSQL (Persistence)
     - All predictions + outcomes (audit trail)
     - MLflow backend
     - User + API key management

LATENCY BUDGET (p95 < 150ms)
──────────────────────────────
  Feature extraction:    ~20ms
  8 base model inference: ~45ms (parallel)
  Meta-learner:          ~10ms
  Kelly RL agent:         ~5ms
  Serialization:          ~7ms
  ─────────────────────
  Total:                 ~87ms  ✅ (well under budget)
```

---

## 8. 5-Agent Swarm Design

```
AGENT 1: Backend Core ML (Python/FastAPI)
──────────────────────────────────────────
Responsibilities: ML inference, training, monitoring
Key components:   PrecognitionEngineV3_1, MetaEnsembleV3_1,
                  KellyRLAgent, DriftDetector, API endpoints
Communication:    REST API, Redis pub/sub, Postgres

AGENT 2: Frontend Cognitive Dashboard (React/TypeScript)
─────────────────────────────────────────────────────────
Responsibilities: Real-time race visualization, SHAP display,
                  uncertainty visualization, betting panel
Key components:   RaceDashboard, UncertaintyViz, KellyCalculator,
                  RegimePanel, WebSocket live updates
Communication:    REST API calls, WebSocket subscription

AGENT 3: Admin Panel (React/TypeScript)
────────────────────────────────────────
Responsibilities: Model lifecycle management, HPO monitoring,
                  drift alert management, audit log review
Key components:   ModelRegistry, HyperparamTuner, DriftAlerts,
                  CalibrationLab, TrainingJobs
Communication:    Admin REST API (separate auth scope)

AGENT 4: Android Intelligence (Kotlin/Jetpack Compose)
────────────────────────────────────────────────────────
Responsibilities: Offline prediction, push alerts, mobile UX
Key components:   PrecognitionEngine (TFLite INT8),
                  ModelSyncWorker, AlertManager, RaceRepository
Communication:    Background sync with backend API,
                  FCM push notifications

AGENT 5: Standalone Research Lab (Python/Jupyter)
──────────────────────────────────────────────────
Responsibilities: Research, experimentation, evidence generation
Key components:   14 notebooks, causal tools, backtest engine,
                  RDTI evidence exporter
Communication:    Direct database access, MLflow API, file export
```

---

## 9. MLOps Infrastructure

### Hyperparameter Optimization (Optuna)

```yaml
optuna_config:
  n_trials: 200
  timeout_hours: 48
  directions:
    - maximize  # NDCG@4
    - minimize  # ECE
    - minimize  # inference_latency_ms
  sampler: TPESampler (n_startup_trials=20)
  pruner: HyperbandPruner

search_space:
  lgbm_n_estimators: [50, 300]
  lgbm_learning_rate: [0.01, 0.1]  # log-uniform
  lgbm_max_depth: [4, 12]
  lgbm_num_leaves: [20, 100]
  catboost_iterations: [100, 500]
  catboost_depth: [4, 10]
  tabnet_n_steps: [3, 10]
  tabnet_n_d: [8, 64]
  meta_logreg_C: [0.01, 10]  # log-uniform
  meta_lgbm_n_estimators: [50, 200]
  weight_lgbm_ranker: [0.10, 0.40]
  weight_catboost: [0.10, 0.30]
  weight_tabnet: [0.05, 0.20]
  weight_grok4: [0.00, 0.15]
```

### Experiment Tracking (MLflow)

```yaml
mlflow_config:
  tracking_uri: postgresql://mlflow:***@localhost:5432/mlflow_db
  artifact_root: s3://equine-oracle-artifacts/

  logged_metrics:
    - ndcg@1, ndcg@3, ndcg@4, ndcg@10
    - expected_calibration_error (ECE)
    - brier_score
    - roi_simulation (sharpe_ratio, kelly_criterion)
    - inference_latency_p50/p95/p99
    - feature_importance_top10
    - drift_score

  logged_artifacts:
    - trained_models/*.pkl / *.pt
    - shap_explainer.pkl
    - feature_metadata.json
    - calibration_curves.png
    - confusion_matrix.png
    - optuna_study.pkl
```

### Drift Detection (Alibi-Detect)

```yaml
drift_config:
  feature_drift:
    method: TabularDrift (Alibi-Detect)
    reference: last_10k_predictions.parquet
    p_val: 0.05
    correction: bonferroni
    monitored_features:
      - avg_perf_index_L5
      - weighted_form_score
      - track_moisture_pct

  prediction_drift:
    method: KSDrift
    statistic: kolmogorov_smirnov
    threshold: 0.05
    window: 500 predictions

  performance_drift:
    metric: ndcg@4
    threshold_pct: -5.0
    window: 7_days
    action: alert_and_trigger_retrain

  alerting:
    channels: [slack, email, pagerduty]
    severity_levels: [WARNING, CRITICAL, RETRAIN_REQUIRED]
```

---

## 10. Data Flow — End to End

```
ONLINE PREDICTION FLOW
──────────────────────
Race Card Input
     │
     ▼
FeatureStore.extract(race_card)         ~5ms
     │
     ▼
TemporalSensorGrid.extract(horse_ids)   ~10ms
     │
     ▼
ChaosMetrics.compute_regime()           ~3ms
     │
     ▼
DarkPoolWhisper.compute_whisper()       ~2ms
     │
     ▼
BaseModels.predict_parallel(features)   ~45ms
[LightGBM, XGB, CatBoost, TabNet,
 LogReg, RF, Grok4(cached)]
     │
     ▼
MetaEnsemble.predict(oof_preds)         ~10ms
     │
     ▼
Calibration.apply(raw_probs)            ~1ms
     │
     ▼
KellyRLAgent.size_position(probs, odds) ~5ms
     │
     ▼
PredictionResponse (ranked + stakes)
     │
     ├── → API Response (JSON)
     ├── → Postgres audit log (async)
     ├── → Prometheus metrics
     └── → WebSocket push → Frontend

TRAINING FLOW
──────────────
Historical data (racebase_processed_final_large.csv)
+ TheRacingAPI live data
     │
     ▼
FeatureStore.build(full_history)
     │
     ▼
TemporalStratifiedKFold(n_splits=5, gap=20)
     │
     ▼
BaseModels.fit_oof(train_folds) → OOF predictions
     │
     ▼
HardenedCausalEngine.estimate() → Causal features
     │
     ▼
MetaEnsemble.fit(oof_preds + causal_features)
     │
     ▼
Calibration.fit(val_predictions)
     │
     ▼
KellyRLAgent.train(simulation_env, n_steps=100k)
     │
     ▼
ModelRegistry.register(champion_or_challenger)
     │
     ▼
MLflow.log_all(metrics, artifacts, params)
     │
     ▼
DriftBaseline.update(new_reference_data)
```

---

## 11. Gap Analysis & V4.0 Roadmap

### Current Gaps (V3.1 → V4.0)

| Gap | Priority | Effort | Impact |
|-----|----------|--------|--------|
| Video gait analysis integration | HIGH | HIGH | +3-5% NDCG |
| Continual learning (no full retrain) | HIGH | MEDIUM | -40% training time |
| Multi-market support (AU/UK/IRE) | HIGH | MEDIUM | 3× data volume |
| White-label API packaging | MEDIUM | LOW | Revenue unlock |
| iOS app (SwiftUI) | MEDIUM | MEDIUM | Market expansion |
| Transformer-based sequence model | MEDIUM | HIGH | Captures long-range form |
| Track-specific micro-models | LOW | MEDIUM | +1-2% venue accuracy |
| Raspberry Pi edge kiosk | LOW | LOW | On-track deployment |

### V4.0 Architecture Changes (Planned)

```
V4.0 ADDITIONS
──────────────
1. VideoIntelligenceLayer
   - Gait analysis via computer vision (OpenCV + ResNet)
   - Paddock condition assessment
   - Sweat/coat condition detection

2. ContinualLearningArchitecture
   - Online LightGBM updates (no full retrain)
   - StreamingDML for real-time causal updates
   - Elastic weight consolidation (prevent catastrophic forgetting)

3. TransformerFormModel
   - Self-attention over race history sequence
   - Token: (race_date, distance, going, position, speed_rating)
   - Pre-trained on 50k+ races, fine-tuned per horse

4. MultiMarketAdapter
   - Market-specific feature normalization
   - Cross-market transfer learning
   - Currency-adjusted Kelly criterion
```

### Known Technical Debt

1. **Grok-4 fallback** — Local distilbert fallback not yet trained; currently uses rule-based heuristic
2. **iOS app** — Only Android implemented; SwiftUI version pending
3. **Kubernetes** — Manifests exist but not battle-tested in production
4. **Terraform** — IaC scaffolded but not fully parameterized
5. **Counterfactual online learning** — Implemented but not yet scheduled in CI/CD

---

*Document Version: 3.1.0 | Last Updated: 2026-03-19 | Author: Equine Oracle Architecture Team*  
*Status: Production | Next Review: Q2 2026*
