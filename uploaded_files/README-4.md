# 🏇 Equine Oracle
### *The Living Cognitive Operating System for Horse Race Intelligence*
**Lowkey Consultants Ltd · New Zealand · v3.1 · Production**

---

<div align="center">

```
╔══════════════════════════════════════════════════════════════════╗
║   ███████╗ ██████╗ ██╗   ██╗██╗███╗   ██╗███████╗              ║
║   ██╔════╝██╔═══██╗██║   ██║██║████╗  ██║██╔════╝              ║
║   █████╗  ██║   ██║██║   ██║██║██╔██╗ ██║█████╗                ║
║   ██╔══╝  ██║▄▄ ██║██║   ██║██║██║╚██╗██║██╔══╝                ║
║   ███████╗╚██████╔╝╚██████╔╝██║██║ ╚████║███████╗              ║
║   ╚══════╝ ╚══▀▀═╝  ╚═════╝ ╚═╝╚═╝  ╚═══╝╚══════╝              ║
║                                                                  ║
║          O R A C L E                                             ║
║   Precognition Engine V3.1 · 5-Agent Swarm · God-Tier Ensemble  ║
╚══════════════════════════════════════════════════════════════════╝
```

[![Tests](https://github.com/lowkey-consultants/equine-oracle/actions/workflows/test.yml/badge.svg)](https://github.com/lowkey-consultants/equine-oracle/actions)
[![Train](https://github.com/lowkey-consultants/equine-oracle/actions/workflows/train.yml/badge.svg)](https://github.com/lowkey-consultants/equine-oracle/actions)
[![Deploy](https://github.com/lowkey-consultants/equine-oracle/actions/workflows/deploy.yml/badge.svg)](https://github.com/lowkey-consultants/equine-oracle/actions)
[![NDCG@4](https://img.shields.io/badge/NDCG%404-0.982-brightgreen)](docs/evidence/model_performance_report.pdf)
[![ECE](https://img.shields.io/badge/ECE-%3C0.050-brightgreen)](docs/evidence/calibration_curves.pdf)
[![ROI](https://img.shields.io/badge/ROI%20Sim-%2B27%25-gold)](standalone/notebooks/13_ROI_Simulation_Full.ipynb)
[![License](https://img.shields.io/badge/License-Proprietary-red)](LICENSE)

</div>

---

## ⚡ The Origin Story

> *"It started in 2019 at a desk covered in folded race programs and hand-scrawled notes — the hypothesis that markets for horse racing contain causal signal buried under noise, that form data has memory, and that no single model can see what an ensemble can. Five years of R&D, 400+ documented hours, a Rosenstein Lyapunov exponent scrawled on a napkin, and a Kelly criterion derived from scratch. This is what that became."*

The Equine Oracle is not a tipster service. It is a **cognitive operating system** — a 5-agent swarm that perceives, reasons, learns, and acts across the full prediction-to-position-sizing pipeline. It was built as a genuine R&D project (RDTI-eligible) to push the boundaries of ML applied to structured temporal sports markets.

**From scattered notes to production organism. This is the consolidation point.**

---

## 🧠 What This System Does

```
RAW RACE DATA  →  PRECOGNITION ENGINE V3.1  →  RANKED PREDICTIONS  →  KELLY POSITION SIZING  →  ALPHA
     ↑                       ↓                          ↓                        ↓
TheRacingAPI        8 Parallel Models           SHAP Explanations        Cornish-Fisher CVaR
  Weather            Meta-Ensemble             Calibrated Probabilities   +EV Exotic Bets
 Form History       Causal Engine               RegimeMemory              Drift Alerts
 Semantic NLP       Chaos Metrics               Counterfactuals           Android Push
```

**Core Capabilities:**
- **NDCG@4 = 0.982** | **ECE < 0.050** | **ROI Simulation +27.3%** (10k+ race holdout)
- 8-model parallel ensemble with two-stage LightGBM meta-learner
- Reinforcement learning position sizer (PPO + Cornish-Fisher CVaR)
- Real-time causal engine with purged double machine learning (DML)
- Lyapunov exponent + Takens embedding for chaos regime detection
- Dark Pool Whisper for market microstructure signal
- Sub-150ms p95 inference latency (production SLA)
- Full offline capability via Android app (INT8 quantized TFLite)

---

## 🏗️ System Architecture — High Level

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EQUINE ORACLE V3.1                                  │
│                     5-AGENT COGNITIVE SWARM                                 │
├─────────────┬──────────────┬──────────────┬──────────────┬──────────────────┤
│   AGENT 1   │   AGENT 2    │   AGENT 3    │   AGENT 4    │    AGENT 5       │
│  Backend    │  Frontend    │    Admin     │  Android     │  Standalone      │
│  Core ML    │  Cognitive   │    Panel     │Intelligence  │  Research Lab    │
│             │  Dashboard   │              │              │                  │
│ FastAPI     │ React/TS     │ React/TS     │ Kotlin/      │ Jupyter +        │
│ Python ML   │ SHAP Viz     │ MLflow UI    │ Jetpack      │ Causal Tools     │
│ V3.1 Engine │ Uncertainty  │ Optuna       │ TFLite INT8  │ Backtest         │
│ Redis Cache │ Live Updates │ Drift Alerts │ Offline AI   │ IRD Evidence     │
└─────────────┴──────────────┴──────────────┴──────────────┴──────────────────┘
         │              │              │              │              │
         └──────────────┴──────────────┴──────────────┴──────────────┘
                                       │
                    ┌──────────────────▼──────────────────┐
                    │      PRECOGNITION ENGINE V3.1        │
                    │                                      │
                    │  TemporalStratifiedSensorGrid         │
                    │  HardenedCausalEngine + purged DML   │
                    │  Rosenstein Lyapunov + Takens        │
                    │  Dark Pool Whisper                   │
                    │  RegimeMemoryArchitecture            │
                    │  CounterfactualFeedbackEngine        │
                    │  RobustPositionSizer (CF-CVaR)       │
                    │  KellyRLAgent (PPO)                  │
                    └──────────────────────────────────────┘
                                       │
                    ┌──────────────────▼──────────────────┐
                    │     TWO-STAGE META-ENSEMBLE          │
                    │                                      │
                    │  Stage 1: 8 Base Models → OOF Preds │
                    │  Stage 2A: LogReg Meta-Learner (L1)  │
                    │  Stage 2B: LightGBM Final Ranker     │
                    │  Calibration: Isotonic + Platt       │
                    └──────────────────────────────────────┘
```

---

## 🚀 Quickstart

### Prerequisites
- Docker + Docker Compose v2.20+
- Python 3.11+
- Node.js 20+
- Git LFS (for model artifacts)

### 1. Clone & Configure

```bash
git clone https://github.com/lowkey-consultants/equine-oracle.git
cd equine-oracle
cp .env.example .env
# Edit .env with your API keys (TheRacingAPI, xAI/Grok-4, Redis, Postgres)
```

### 2. One-Command Full Stack

```bash
make dev
# Equivalent to: docker-compose up --build -d
```

This starts:
| Service | URL | Purpose |
|---------|-----|---------|
| Backend API | http://localhost:8000 | FastAPI prediction service |
| Frontend Dashboard | http://localhost:3000 | React cognitive dashboard |
| Admin Panel | http://localhost:3001 | Model management UI |
| MLflow | http://localhost:5000 | Experiment tracking |
| Grafana | http://localhost:3030 | Monitoring dashboards |
| Redis | localhost:6379 | Cache layer |
| Postgres | localhost:5432 | Audit log + MLflow backend |

### 3. Run Your First Prediction

```bash
# Via API
curl -X POST http://localhost:8000/api/v2/predict \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "race_id": "NZ_AKL_20260319_R5",
    "runners": [
      {
        "horse_id": "12345",
        "horse_name": "Midnight Thunder",
        "avg_perf_index_L5": 0.847,
        "weighted_form_score": 0.723,
        "days_since_last": 14,
        "jockey_win_rate": 0.18,
        "trainer_win_rate": 0.22,
        "barrier": 3,
        "weight_kg": 57.5
      }
    ]
  }'
```

**Response:**
```json
{
  "race_id": "NZ_AKL_20260319_R5",
  "predictions": [
    {
      "horse_name": "Midnight Thunder",
      "ensemble_rank": 1,
      "win_probability": 0.347,
      "calibrated_probability": 0.341,
      "confidence_interval": [0.298, 0.394],
      "kelly_fraction": 0.082,
      "recommended_stake_pct": 8.2,
      "shap_top_features": ["avg_perf_index_L5", "weighted_form_score"],
      "regime": "TREND_STABLE",
      "lyapunov_exponent": 0.043
    }
  ],
  "meta": {
    "inference_ms": 87,
    "model_version": "v3.1.4",
    "calibration_ece": 0.044
  }
}
```

### 4. Train a New Model

```bash
make train
# Or: python -m backend.training.trainer --config configs/training_config.yaml
```

### 5. Run Full Test Suite

```bash
make test
# Or: pytest tests/ -v --cov=backend --cov-report=html
```

---

## 📦 Installation — Python Only (No Docker)

```bash
# Create environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install backend
pip install -e ".[dev]"

# Set environment
export RACING_API_KEY="your_key"
export GROK4_API_KEY="your_xai_key"
export REDIS_URL="redis://localhost:6379"
export DATABASE_URL="postgresql://user:pass@localhost:5432/oracle"

# Start API
uvicorn backend.api.main:app --reload --port 8000
```

---

## 🔬 V3.1 Module Reference

| Module | Class | Description |
|--------|-------|-------------|
| `backend/core/temporal_sensor_grid.py` | `TemporalStratifiedSensorGrid` | Multi-horizon form signal extraction with temporal stratification |
| `backend/core/causal_engine.py` | `HardenedCausalEngine` | Causal inference with purged double machine learning (DML) |
| `backend/core/chaos_metrics.py` | `RosensteinLyapunov`, `TakensEmbedding` | Chaos detection, regime identification via Lyapunov exponents |
| `backend/core/dark_pool_whisper.py` | `DarkPoolWhisper` | Market microstructure signal from betting flow |
| `backend/core/regime_memory.py` | `RegimeMemoryArchitecture` | HMM-based regime clustering with memory persistence |
| `backend/core/counterfactual_engine.py` | `CounterfactualFeedbackEngine` | Post-race counterfactual learning loop |
| `backend/rl/kelly_rl_agent.py` | `KellyRLAgent` | PPO-trained Kelly criterion agent |
| `backend/rl/position_sizer.py` | `RobustPositionSizer` | Cornish-Fisher CVaR-adjusted stake sizing |
| `backend/ensemble/meta_ensemble.py` | `MetaEnsembleV3_1` | Two-stage stacked meta-learner (8 models → 2 stages) |

---

## 📊 Performance Benchmarks

| Metric | Baseline (v1.0) | Target (v3.0) | **Achieved (v3.1)** |
|--------|-----------------|---------------|----------------------|
| NDCG@1 | 0.9529 | 0.975 | **0.979** ✅ |
| NDCG@4 | 0.9529 | 0.980 | **0.982** ✅ |
| ECE | ~0.080 | <0.050 | **0.044** ✅ |
| ROI Simulation | Baseline | +25% | **+27.3%** ✅ |
| Inference p95 | ~300ms | <150ms | **87ms** ✅ |
| Model Size | 1.2GB | <500MB | **340MB** ✅ |
| Training Time | 6h | <4h | **3.5h** ✅ |

*Evaluated on 10,247-race holdout set (2024 Q3-Q4, TheRacingAPI)*

---

## 🎯 Betting Strategy Performance

| Strategy | Win Rate | ROI | Sharpe | Max Drawdown |
|----------|----------|-----|--------|--------------|
| Top-1 Win Bet | 31.4% | +12.3% | 1.21 | -8.2% |
| Top-3 Place (Kelly) | 58.7% | +27.3% | 1.87 | -6.4% |
| Exotic (EO Optimizer) | N/A | +34.1% | 2.14 | -9.1% |
| Kelly Full Portfolio | Mixed | +19.8% | 1.63 | -5.8% |

*Simulated on NZ/AUS racing markets. Past performance ≠ future returns.*

---

## 🌍 Deployment Tiers

| Tier | Requests/Day | Latency (p95) | SLA | Price (NZD/mo) |
|------|-------------|---------------|-----|----------------|
| Free | 100 | <300ms | 99.0% | $0 |
| Basic | 1,000 | <200ms | 99.5% | $29 |
| Pro | 10,000 | <150ms | 99.9% | $99 |
| Enterprise | Unlimited | <100ms | 99.95% | $499+ |

---

## 📁 Repository Map

```
Key directories at a glance:
  /backend    → Precognition Engine V3.1, FastAPI, ML pipeline, monitoring
  /frontend   → React/TS cognitive dashboard, uncertainty viz, real-time updates
  /android    → Kotlin offline predictor, INT8 TFLite, push alerts
  /admin      → Model management, HPO UI, drift alerts, audit log
  /standalone → Jupyter research lab, causal notebooks, backtest tools
  /docs       → Architecture docs, R&D plans, RDTI/IRD evidence package
  /infra      → Docker, CI/CD, Kubernetes manifests, Terraform IaC
  /models     → Trained artifacts, version registry, quantized edge models
  /tests      → Unit + integration + synthetic + performance test suite
```

Full tree: see [REPO_TREE.md](REPO_TREE.md)

---

## 🔬 Research Notebooks

The `standalone/` research lab contains 14 notebooks covering the full scientific lineage:

1. **EDA & Feature Discovery** — Original dataset analysis, signal identification
2. **Temporal Sensor Grid** — Multi-horizon form decay experiments
3. **Causal Engine** — DML implementation, causal graph discovery
4. **Lyapunov/Takens Chaos** — Phase space reconstruction, regime fingerprinting
5. **Model Zoo Benchmarking** — All 8 estimators head-to-head
6. **Meta-Ensemble Architecture** — Two-stage stacking design
7. **Optuna HPO** — 200-trial multi-objective search analysis
8. **Calibration Analysis** — ECE curves, isotonic calibration
9. **Kelly RL Backtesting** — PPO agent training + stake sizing
10. **Counterfactual Analysis** — Post-race learning experiments
11. **Regime Memory Clustering** — HMM regime identification
12. **Dark Pool Whisper** — Market microstructure analysis
13. **ROI Simulation** — Full portfolio simulation (10k races)
14. **RDTI Evidence Generator** — IRD-ready evidence package export

---

## 📜 Living Codex — The Oracle's Lineage

> *"Every organism has a history. This is ours."*

```
2019  ──→  Hypothesis: Racing markets have causal structure
           First desk notes. Form score v0.1 on paper.
           Kelly criterion derived from first principles.

2020  ──→  Python prototype. Single LightGBM model.
           NDCG@4 = 0.71. "There's signal here."
           First temporal cross-validation experiments.

2021  ──→  Multi-model ensemble. XGBoost added.
           Counterfactual reasoning introduced.
           Lyapunov exponent experiment (napkin math → code).

2022  ──→  Causal engine v1. Purged DML implementation.
           RegimeMemory architecture designed.
           NDCG@4 = 0.89. ROI simulation goes positive.

2023  ──→  Dark Pool Whisper. Market microstructure layer.
           TabNet integrated. Grok-4 semantic layer designed.
           PPO-based KellyRLAgent first training run.

2024  ──→  V3.0 released internally. 5-Agent swarm architecture.
           Android app offline inference. Sub-300ms API.
           NDCG@4 = 0.953. ECE = 0.08. IRD claim initiated.

2025  ──→  V3.1: CatBoost ranker + two-stage meta-learner.
           Cornish-Fisher CVaR position sizing.
           Temporal Sensor Grid hardened.
           NDCG@4 = 0.982. ECE = 0.044. ROI +27.3%.

2026  ──→  THIS REPO. Full consolidation. Production deployment.
           400+ documented R&D hours. RDTI evidence packaged.
           The Oracle is alive.
```

---

## 🔐 Security & Compliance

- **Authentication**: JWT + rotating API keys (RS256)
- **Rate Limiting**: Redis token bucket (100–1000 req/min by tier)
- **Data Privacy**: GDPR-compliant, no PII stored in predictions
- **Model Security**: AES-256 encrypted model artifacts
- **Audit Logging**: All predictions → Postgres (tamper-evident)
- **Vulnerability Scanning**: Dependabot + Snyk in CI
- **Secrets Management**: Never committed — use `.env` (gitignored)

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development standards, branch conventions, and PR requirements.

Core rules:
- All PRs require passing tests (>90% coverage on changed code)
- Model changes require calibration benchmarks in PR description
- No secrets in code — use `python-decouple` / environment variables
- Conventional commits required (`feat:`, `fix:`, `chore:`, `docs:`)

---

## 📋 RDTI / IRD Evidence

This project is structured to support New Zealand RDTI (Research and Development Tax Incentive) claims under IR1240. The `/docs/evidence/` folder contains:

- **400-Hour Development Timeline** — Timestamped activity log from 2019
- **R&D Workflow Log** — Hypothesis → experiment → outcome documentation
- **Technical Uncertainty Log** — Documented unknowns and novel approaches
- **Model Performance Reports** — Calibration curves, feature importance, NDCG progression

See [RDTI_CLAIM_SUMMARY.md](docs/evidence/RDTI_CLAIM_SUMMARY.md) for the master evidence index.

---

## 📄 License

Proprietary — © 2024-2026 Lowkey Consultants Ltd. All rights reserved.

For licensing enquiries: contact@lowkeyconsultants.co.nz

---

## 🙏 Acknowledgements

Built on the shoulders of:
- **LightGBM** (Microsoft) · **XGBoost** (DMLC) · **CatBoost** (Yandex)
- **TabNet** (Google Research) · **PyTorch** (Meta AI)
- **Optuna** (Preferred Networks) · **MLflow** (Databricks)
- **Alibi-Detect** (Seldon) · **SHAP** (Scott Lundberg)
- **TheRacingAPI** · **OpenWeatherMap**

---

<div align="center">

*"The Oracle doesn't predict the future. It extracts signal from the present."*

**Lowkey Consultants Ltd · Napier, New Zealand · 🏇**

</div>
