# 🏇 Equine Oracle — Production Repository Tree
## Lowkey Consultants Ltd | v3.1 | Consolidated Master Structure

```
equine-oracle/
│
├── README.md                          # Hero narrative + quickstart + architecture
├── ARCHITECTURE.md                    # Full V3.1 system map + gap analysis
├── CI_CD_BLUEPRINT.md                 # Complete GitHub Actions automation blueprint
├── CONTRIBUTING.md                    # Dev guidelines + PR standards
├── LICENSE                            # Proprietary — Lowkey Consultants Ltd
├── .gitignore                         # Python/Node/Kotlin/ML artifact exclusions
├── .env.example                       # Required environment variables template
├── docker-compose.yml                 # Full-stack local orchestration
├── Makefile                           # One-line dev commands
│
├── .github/
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── workflows/
│       ├── test.yml                   # Pipeline 1: Unit + integration tests
│       ├── train.yml                  # Pipeline 2: Automated model training
│       ├── deploy.yml                 # Pipeline 3: Zero-downtime deployment
│       ├── drift_monitor.yml          # Pipeline 4: Scheduled drift detection
│       └── evidence_export.yml        # Pipeline 5: RDTI evidence package export
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── setup.py
│   │
│   ├── core/                          # Precognition Engine V3.1 — Heart of the Oracle
│   │   ├── __init__.py
│   │   ├── precognition_engine.py     # PrecognitionEngineV3_1 master orchestrator
│   │   ├── temporal_sensor_grid.py    # TemporalStratifiedSensorGrid
│   │   ├── causal_engine.py           # HardenedCausalEngine + purged DML
│   │   ├── chaos_metrics.py           # Rosenstein Lyapunov + Takens embedding
│   │   ├── dark_pool_whisper.py       # Dark Pool Whisper (market microstructure)
│   │   ├── regime_memory.py           # RegimeMemoryArchitecture
│   │   └── counterfactual_engine.py   # CounterfactualFeedbackEngine
│   │
│   ├── models/                        # ML Model Zoo — 8 Parallel Estimators
│   │   ├── __init__.py
│   │   ├── base_model.py              # Abstract base class + typing contracts
│   │   ├── lgbm_ranker.py             # LightGBM LambdaRank
│   │   ├── lgbm_classifier.py         # LightGBM Binary Classifier
│   │   ├── xgboost_ranker.py          # XGBoost Rank:Pairwise
│   │   ├── catboost_ranker.py         # CatBoost YetiRank
│   │   ├── tabnet_ranker.py           # TabNet Attention Ranker (PyTorch)
│   │   ├── logistic_regression.py     # Logistic Regression (calibrated)
│   │   ├── random_forest.py           # Random Forest (sklearn 1.3+)
│   │   └── grok4_semantic.py          # Grok-4 API Semantic Scorer
│   │
│   ├── ensemble/                      # Two-Stage Meta-Learner
│   │   ├── __init__.py
│   │   ├── meta_ensemble.py           # MetaEnsembleV3_1 master class
│   │   ├── stage1_meta_features.py    # Stage 1: Base → Meta-feature extractor
│   │   ├── stage2a_logreg.py          # Stage 2A: Logistic meta-learner (L1)
│   │   ├── stage2b_lgbm.py            # Stage 2B: LightGBM final ranker
│   │   ├── dynamic_weighting.py       # DynamicWeightingEngine
│   │   └── calibration.py             # IsotonicRegression + Platt scaling
│   │
│   ├── rl/                            # Reinforcement Learning Layer
│   │   ├── __init__.py
│   │   ├── kelly_rl_agent.py          # KellyRLAgent with PPO
│   │   ├── position_sizer.py          # RobustPositionSizer + Cornish-Fisher CVaR
│   │   ├── reward_engine.py           # Reward shaping + Sharpe optimization
│   │   └── ppo_trainer.py             # PPO training loop
│   │
│   ├── features/                      # Feature Engineering Pipeline
│   │   ├── __init__.py
│   │   ├── feature_store.py           # FeatureStore (56 → 120 features)
│   │   ├── temporal_features.py       # L5/L10 rolling windows, form decay
│   │   ├── weather_features.py        # Track moisture, wind, temperature
│   │   ├── semantic_features.py       # Grok-4 extracted NLP features
│   │   ├── interaction_features.py    # Pace clusters, jockey×trainer synergy
│   │   ├── multicollinearity.py       # VIF reducer (threshold < 5.0)
│   │   └── preprocessing.py           # RobustScaler + SMOTE pipeline
│   │
│   ├── monitoring/                    # MLOps Observability
│   │   ├── __init__.py
│   │   ├── drift_detector.py          # Alibi-Detect KSDrift + TabularDrift
│   │   ├── calibration_monitor.py     # ECE tracker + recalibration trigger
│   │   ├── concept_drift.py           # ConceptDriftDetector
│   │   ├── uncertainty_estimator.py   # UncertaintyEstimator (conformal prediction)
│   │   ├── meta_monitor.py            # Meta-cognitive performance watchdog
│   │   └── prometheus_metrics.py      # Custom Prometheus metrics exporter
│   │
│   ├── training/                      # Training Orchestration
│   │   ├── __init__.py
│   │   ├── trainer.py                 # Master training orchestrator
│   │   ├── optuna_search.py           # Multi-objective Optuna HPO (200 trials)
│   │   ├── cross_validator.py         # TemporalStratifiedKFold (5-fold)
│   │   ├── mlflow_tracker.py          # MLflow experiment tracker
│   │   └── model_registry.py          # Champion/challenger registry
│   │
│   ├── api/                           # FastAPI Service
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app + lifespan handlers
│   │   ├── routes/
│   │   │   ├── predict.py             # POST /api/v2/predict
│   │   │   ├── explain.py             # POST /api/v2/explain (SHAP)
│   │   │   ├── health.py              # GET /api/v2/health
│   │   │   └── metrics.py             # GET /api/v2/metrics
│   │   ├── middleware/
│   │   │   ├── auth.py                # JWT + API key validation
│   │   │   ├── rate_limiter.py        # Redis token bucket
│   │   │   └── request_logger.py      # Prediction audit log → Postgres
│   │   ├── schemas/
│   │   │   ├── prediction.py          # Pydantic request/response schemas
│   │   │   └── race_card.py           # RaceCard input validation
│   │   └── dependencies.py            # Dependency injection (model loader)
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   ├── racing_api_client.py       # TheRacingAPI client
│   │   ├── weather_client.py          # OpenWeatherMap + WeatherAPI clients
│   │   ├── data_loader.py             # CSV/JSON/Parquet ingestion
│   │   └── validators.py              # Input schema validation
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logging.py                 # Structured JSON logging
│       ├── config.py                  # Settings (pydantic-settings)
│       └── crypto.py                  # AES-256 model artifact encryption
│
├── frontend/                          # React/TypeScript Cognitive Dashboard
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   │
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   │
│   │   ├── components/
│   │   │   ├── RaceDashboard/
│   │   │   │   ├── RaceCard.tsx       # Live race card renderer
│   │   │   │   ├── RunnerTable.tsx    # Horse rankings with confidence bars
│   │   │   │   └── OddsOverlay.tsx    # Real-time TAB odds integration
│   │   │   ├── UncertaintyViz/
│   │   │   │   ├── ConfidenceGauge.tsx   # Prediction confidence dial
│   │   │   │   ├── CalibrationCurve.tsx  # Live ECE calibration plot
│   │   │   │   └── FeatureHeatmap.tsx    # SHAP feature importance heatmap
│   │   │   ├── RegimePanel/
│   │   │   │   ├── RegimeIndicator.tsx   # Current market regime badge
│   │   │   │   └── RegimeHistory.tsx     # Regime transition timeline
│   │   │   ├── BettingPanel/
│   │   │   │   ├── KellyCalculator.tsx   # Kelly fraction + CVaR display
│   │   │   │   ├── PositionSizer.tsx     # Stake sizing recommendations
│   │   │   │   └── ExoticOptimizer.tsx   # Trifecta/exacta optimizer
│   │   │   └── shared/
│   │   │       ├── OracleHeader.tsx
│   │   │       ├── StatusBadge.tsx
│   │   │       └── LoadingOracle.tsx
│   │   │
│   │   ├── hooks/
│   │   │   ├── usePredictions.ts
│   │   │   ├── useWebSocket.ts        # Real-time prediction stream
│   │   │   └── useModelHealth.ts
│   │   │
│   │   ├── store/
│   │   │   ├── predictionSlice.ts     # Redux prediction state
│   │   │   └── raceSlice.ts
│   │   │
│   │   ├── api/
│   │   │   ├── client.ts              # Axios + auth interceptors
│   │   │   └── endpoints.ts
│   │   │
│   │   └── types/
│   │       ├── prediction.ts
│   │       └── race.ts
│   │
│   └── public/
│       └── oracle-logo.svg
│
├── android/                           # Kotlin Offline Predictor + Alerts
│   ├── app/
│   │   ├── build.gradle.kts
│   │   ├── src/main/
│   │   │   ├── java/com/lowkey/equineoracle/
│   │   │   │   ├── MainActivity.kt
│   │   │   │   ├── core/
│   │   │   │   │   ├── PrecognitionEngine.kt    # Offline TFLite inference
│   │   │   │   │   ├── ModelLoader.kt           # INT8 quantized model loader
│   │   │   │   │   └── FeatureExtractor.kt      # On-device feature pipeline
│   │   │   │   ├── ui/
│   │   │   │   │   ├── RaceDashboardScreen.kt   # Jetpack Compose UI
│   │   │   │   │   ├── PredictionCard.kt
│   │   │   │   │   └── AlertsScreen.kt
│   │   │   │   ├── alerts/
│   │   │   │   │   ├── AlertManager.kt          # Push notification + FCM
│   │   │   │   │   └── AlertTriggers.kt         # Drift + value bet triggers
│   │   │   │   ├── data/
│   │   │   │   │   ├── RaceRepository.kt
│   │   │   │   │   └── LocalDatabase.kt         # Room DB for offline cache
│   │   │   │   └── sync/
│   │   │   │       └── ModelSyncWorker.kt       # Background model update
│   │   │   └── assets/
│   │   │       └── models/
│   │   │           └── precognition_v3_int8.tflite
│   │   └── src/test/
│   └── build.gradle.kts
│
├── admin/                             # Model Management + Hyperparameter UI
│   ├── Dockerfile
│   ├── package.json
│   │
│   └── src/
│       ├── App.tsx
│       ├── pages/
│       │   ├── ModelRegistry.tsx      # Champion/challenger management
│       │   ├── HyperparamTuner.tsx    # Live Optuna trial viewer
│       │   ├── DriftAlerts.tsx        # Feature + prediction drift alerts
│       │   ├── CalibrationLab.tsx     # ECE curves + recalibration triggers
│       │   ├── FeatureImportance.tsx  # SHAP global importance dashboard
│       │   ├── TrainingJobs.tsx       # Active + historical training runs
│       │   └── AuditLog.tsx           # All predictions + API calls log
│       ├── components/
│       │   ├── MLflowRunTable.tsx
│       │   ├── OptunaProgressChart.tsx
│       │   └── ModelHealthMatrix.tsx
│       └── api/
│           └── adminClient.ts
│
├── standalone/                        # Jupyter Research Lab + Causal Tools
│   ├── requirements.txt
│   ├── environment.yml                # Conda environment
│   │
│   ├── notebooks/
│   │   ├── 01_EDA_and_Feature_Discovery.ipynb
│   │   ├── 02_Temporal_Sensor_Grid_Analysis.ipynb
│   │   ├── 03_Causal_Engine_Experiments.ipynb   # HardenedCausalEngine + DML
│   │   ├── 04_Lyapunov_Takens_Chaos.ipynb       # Rosenstein + embedding
│   │   ├── 05_Model_Zoo_Benchmarking.ipynb
│   │   ├── 06_Meta_Ensemble_Architecture.ipynb
│   │   ├── 07_Optuna_HPO_Analysis.ipynb
│   │   ├── 08_Calibration_Analysis.ipynb
│   │   ├── 09_KellyRL_Backtesting.ipynb
│   │   ├── 10_Counterfactual_Analysis.ipynb
│   │   ├── 11_RegimeMemory_Clustering.ipynb
│   │   ├── 12_Dark_Pool_Whisper_Analysis.ipynb
│   │   ├── 13_ROI_Simulation_Full.ipynb
│   │   └── 14_RDTI_Evidence_Generator.ipynb     # IRD evidence export
│   │
│   └── scripts/
│       ├── generate_calibration_plots.py
│       ├── generate_feature_importance_report.py
│       ├── backtest_kelly_strategy.py
│       └── export_evidence_package.py
│
├── docs/                              # Architecture + R&D + IRD Evidence
│   ├── architecture/
│   │   ├── SYSTEM_OVERVIEW.md
│   │   ├── V3_1_MODULE_SPECS.md       # All V3.1 module specs
│   │   ├── DATA_FLOW_DIAGRAM.md
│   │   └── API_SPECIFICATION.md
│   ├── rd_plans/
│   │   ├── PHASE1_FOUNDATION.md
│   │   ├── PHASE2_META_LEARNING.md
│   │   ├── PHASE3_MLOPS.md
│   │   ├── PHASE4_PRODUCTION.md
│   │   └── PHASE5_VALIDATION.md
│   ├── business/
│   │   ├── STRATEGIC_PLAN.md
│   │   ├── REVENUE_MODEL.md
│   │   └── COMPETITIVE_ANALYSIS.md
│   └── evidence/                      # RDTI / IR1240 Evidence Package
│       ├── RDTI_CLAIM_SUMMARY.md      # Master evidence index
│       ├── 400_HOUR_TIMELINE.md       # Development hour log (2019→2026)
│       ├── RD_WORKFLOW_LOG.md         # Hypothesis → experiment → outcome
│       ├── model_performance_report.pdf
│       ├── calibration_curves.pdf
│       ├── feature_importance_report.pdf
│       └── technical_uncertainty_log.md
│
├── infra/                             # Docker + CI/CD + Deployment
│   ├── docker/
│   │   ├── backend.Dockerfile
│   │   ├── frontend.Dockerfile
│   │   ├── admin.Dockerfile
│   │   └── nginx.conf
│   ├── k8s/                           # Kubernetes manifests (future)
│   │   ├── backend-deployment.yaml
│   │   ├── frontend-deployment.yaml
│   │   ├── ingress.yaml
│   │   └── hpa.yaml
│   ├── terraform/                     # AWS IaC (future)
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── scripts/
│       ├── bootstrap.sh               # One-command dev environment setup
│       ├── deploy_prod.sh             # Blue/green deployment
│       ├── rollback.sh                # Instant model rollback
│       └── health_check.sh
│
├── models/                            # Trained Artifacts + Version Registry
│   ├── registry/
│   │   ├── champion/                  # Production champion model
│   │   │   ├── meta_ensemble_v3.1.pkl
│   │   │   ├── lgbm_ranker_v3.1.pkl
│   │   │   ├── xgboost_ranker_v3.1.pkl
│   │   │   ├── catboost_ranker_v3.1.pkl
│   │   │   ├── tabnet_ranker_v3.1.pt
│   │   │   ├── feature_metadata.json
│   │   │   └── model_card.md
│   │   ├── challenger/                # Shadow deployment candidate
│   │   └── archive/                   # Historical model versions
│   ├── quantized/
│   │   ├── precognition_v3_int8.tflite   # Android deployment
│   │   └── tabnet_quantized.pt
│   └── .gitkeep                       # Models tracked via DVC/MLflow
│
└── tests/                             # Full Test Suite
    ├── conftest.py
    ├── unit/
    │   ├── test_precognition_engine.py
    │   ├── test_temporal_sensor_grid.py
    │   ├── test_causal_engine.py
    │   ├── test_chaos_metrics.py
    │   ├── test_meta_ensemble.py
    │   ├── test_kelly_rl_agent.py
    │   ├── test_position_sizer.py
    │   ├── test_counterfactual_engine.py
    │   ├── test_regime_memory.py
    │   ├── test_feature_store.py
    │   └── test_calibration.py
    ├── integration/
    │   ├── test_api_endpoints.py
    │   ├── test_full_prediction_pipeline.py
    │   ├── test_training_pipeline.py
    │   └── test_drift_detection.py
    ├── synthetic/
    │   ├── test_synthetic_races.py    # Synthetic race data stress tests
    │   ├── test_edge_cases.py         # Scratched horses, dead heats, etc.
    │   └── fixtures/
    │       ├── synthetic_race_cards.json
    │       └── historical_races_sample.csv
    └── performance/
        ├── test_latency.py            # p95 < 150ms assertion
        └── test_throughput.py         # 1000 req/min load test
```

**Total estimated files: ~180+ | Languages: Python, TypeScript, Kotlin, YAML, HCL**
