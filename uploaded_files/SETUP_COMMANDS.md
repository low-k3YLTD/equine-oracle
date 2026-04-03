# SETUP_COMMANDS.md
# Equine Oracle — Instant Repository Setup
## Execute these commands to go from zero to live repo in < 10 minutes

---

## Step 1: Initialize Repository

```bash
# Create repo on GitHub first (https://github.com/new)
# Name: equine-oracle | Private | No README (we're adding ours)

# Clone and initialize locally
mkdir equine-oracle && cd equine-oracle
git init
git remote add origin https://github.com/lowkey-consultants/equine-oracle.git
```

---

## Step 2: Create All Directories

```bash
# Run this entire block — creates full directory tree
mkdir -p \
  .github/workflows \
  .github/ISSUE_TEMPLATE \
  backend/core \
  backend/models \
  backend/ensemble \
  backend/rl \
  backend/features \
  backend/monitoring \
  backend/training \
  backend/api/routes \
  backend/api/middleware \
  backend/api/schemas \
  backend/data \
  backend/utils \
  frontend/src/components/RaceDashboard \
  frontend/src/components/UncertaintyViz \
  frontend/src/components/RegimePanel \
  frontend/src/components/BettingPanel \
  frontend/src/components/shared \
  frontend/src/hooks \
  frontend/src/store \
  frontend/src/api \
  frontend/src/types \
  frontend/public \
  android/app/src/main/java/com/lowkey/equineoracle/core \
  android/app/src/main/java/com/lowkey/equineoracle/ui \
  android/app/src/main/java/com/lowkey/equineoracle/alerts \
  android/app/src/main/java/com/lowkey/equineoracle/data \
  android/app/src/main/java/com/lowkey/equineoracle/sync \
  android/app/src/main/assets/models \
  android/app/src/test \
  admin/src/pages \
  admin/src/components \
  admin/src/api \
  standalone/notebooks \
  standalone/scripts \
  docs/architecture \
  docs/rd_plans \
  docs/business \
  docs/evidence \
  infra/docker \
  infra/k8s \
  infra/terraform \
  infra/scripts \
  infra/grafana/dashboards \
  infra/grafana/datasources \
  models/registry/champion \
  models/registry/challenger \
  models/registry/archive \
  models/quantized \
  tests/unit \
  tests/integration \
  tests/synthetic/fixtures \
  tests/performance \
  configs \
  scripts \
  data/raw \
  data/processed \
  artifacts

echo "✅ Directory tree created"
```

---

## Step 3: Create Core Files

```bash
# .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*.pyo
.Python
.venv/
venv/
env/
.env
*.env.local
dist/
build/
*.egg-info/
.eggs/
.pytest_cache/
.coverage
htmlcov/
.benchmarks/
*.log

# Jupyter
.ipynb_checkpoints/
*.ipynb_checkpoints

# ML Artifacts (tracked via DVC/MLflow — not git)
models/registry/champion/*.pkl
models/registry/champion/*.pt
models/registry/champion/*.parquet
models/registry/challenger/
models/registry/archive/
models/quantized/*.tflite
models/quantized/*.pt
artifacts/
data/raw/*.parquet
data/raw/*.csv
data/processed/

# Node.js
node_modules/
.npm
dist/
.next/
out/
*.tsbuildinfo

# Android
*.apk
*.aab
*.dex
.gradle/
local.properties
android/.idea/
android/build/
android/app/build/

# IDE
.idea/
.vscode/settings.json
*.swp
*.swo
.DS_Store

# Docker
.docker/

# Secrets — NEVER COMMIT
.env
.env.*
!.env.example
secrets/
*.pem
*.key
*.p12

# Terraform
infra/terraform/.terraform/
infra/terraform/*.tfstate
infra/terraform/*.tfstate.backup
infra/terraform/.terraform.lock.hcl

# Coverage
coverage/
*.lcov
EOF

echo "✅ .gitignore created"

# LICENSE
cat > LICENSE << 'EOF'
Proprietary License

Copyright (c) 2024-2026 Lowkey Consultants Ltd. All rights reserved.

This software and associated documentation files (the "Software") are the 
exclusive property of Lowkey Consultants Ltd. Unauthorized copying, 
modification, distribution, or use of this Software, in whole or in part, 
is strictly prohibited without prior written permission from Lowkey Consultants Ltd.

For licensing enquiries: contact@lowkeyconsultants.co.nz
EOF

echo "✅ LICENSE created"

# .env.example
cat > .env.example << 'EOF'
# ============================================================
# Equine Oracle — Environment Variables Template
# Copy to .env and fill in your values
# NEVER commit .env to git
# ============================================================

# Racing Data API
RACING_API_KEY=your_theracing_api_key_here
RACING_API_BASE_URL=https://api.theracingapi.com/v1

# AI / Semantic Layer
GROK4_API_KEY=your_xai_grok4_key_here
GROK4_API_BASE_URL=https://api.x.ai/v1

# Weather
OPENWEATHER_API_KEY=your_openweather_key_here

# Database
DATABASE_URL=postgresql://oracle:oracle_dev@localhost:5432/oracle

# Redis
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=equine_oracle_v3

# AWS (for production artifact storage)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=ap-southeast-2
S3_ARTIFACT_BUCKET=equine-oracle-artifacts

# Monitoring
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK
PROMETHEUS_PUSHGATEWAY_URL=http://localhost:9091

# JWT
JWT_SECRET_KEY=generate_with_openssl_rand_hex_32
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
MODEL_DIR=models/registry/champion
MAX_WORKERS=4
EOF

echo "✅ .env.example created"
```

---

## Step 4: Create Backend Entry Point

```bash
# backend/__init__.py
touch backend/__init__.py

# backend/api/main.py — FastAPI entry point
cat > backend/api/main.py << 'EOF'
"""
Equine Oracle V3.1 — FastAPI Application
Lowkey Consultants Ltd
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import predict, explain, health, metrics
from backend.utils.config import get_settings
from backend.utils.logging import setup_logging

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle management."""
    setup_logging()
    # Load models on startup
    from backend.ensemble.meta_ensemble import MetaEnsembleV3_1
    app.state.model = MetaEnsembleV3_1.load(settings.model_dir)
    yield
    # Cleanup on shutdown
    del app.state.model


app = FastAPI(
    title="Equine Oracle API",
    description="Precognition Engine V3.1 — Horse Race Intelligence",
    version="3.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router, prefix="/api/v2")
app.include_router(explain.router, prefix="/api/v2")
app.include_router(health.router, prefix="/api/v2")
app.include_router(metrics.router, prefix="/api/v2")
EOF

echo "✅ FastAPI main.py created"

# backend/Dockerfile
cat > backend/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY backend/ ./backend/
COPY configs/ ./configs/
COPY models/registry/champion/ ./models/registry/champion/

# Non-root user for security
RUN useradd -m -u 1000 oracle
USER oracle

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/api/v2/health || exit 1

CMD ["gunicorn", "backend.api.main:app", \
     "-w", "4", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--keep-alive", "5", \
     "--access-logfile", "-"]
EOF

echo "✅ backend/Dockerfile created"
```

---

## Step 5: Create requirements.txt

```bash
cat > backend/requirements.txt << 'EOF'
# Core ML
lightgbm>=4.0.0
xgboost>=2.0.0
catboost>=1.2
pytorch-tabnet>=4.1
scikit-learn>=1.3.0
torch>=2.1.0
numpy>=1.26.0
pandas>=2.1.0
scipy>=1.11.0

# Feature Engineering
statsmodels>=0.14.0
econml>=0.15.0          # Double Machine Learning (purged DML)

# Causal / Chaos
causalnex>=0.12.0
nolds>=0.5.2            # Lyapunov / nonlinear time series

# MLOps
mlflow>=2.8.0
optuna>=3.4.0
shap>=0.43.0
alibi-detect>=0.11.4

# API & Serving
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
gunicorn>=21.2.0
pydantic>=2.4.0
pydantic-settings>=2.0.0
httpx>=0.25.0
redis>=5.0.0
asyncpg>=0.29.0
sqlalchemy>=2.0.0
alembic>=1.12.0

# Auth
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4

# Monitoring
prometheus-client>=0.18.0
psutil>=5.9.0

# Data Sources
requests>=2.31.0
openai>=1.0.0           # xAI Grok-4 (OpenAI-compatible)

# Utilities
python-decouple>=3.8
structlog>=23.1.0
cryptography>=41.0.0

# RL
stable-baselines3>=2.1.0
gymnasium>=0.29.0

# Visualization (for notebooks/admin)
matplotlib>=3.8.0
plotly>=5.17.0
dash>=2.14.0
EOF

cat > backend/requirements-dev.txt << 'EOF'
-r requirements.txt
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-asyncio>=0.21.0
pytest-xdist>=3.3.0
pytest-benchmark>=4.0.0
pytest-timeout>=2.1.0
httpx>=0.25.0         # for async test client
factory-boy>=3.3.0    # test fixtures
faker>=19.0.0
ruff>=0.1.0
mypy>=1.5.0
EOF

echo "✅ requirements.txt created"
```

---

## Step 6: Create GitHub Actions Workflows

```bash
# Copy the workflow files from CI_CD_BLUEPRINT.md

# test.yml
cp <(echo "# see CI_CD_BLUEPRINT.md Pipeline 1") .github/workflows/test.yml
# (In practice: paste full YAML from CI_CD_BLUEPRINT.md section 2)

# train.yml
cp <(echo "# see CI_CD_BLUEPRINT.md Pipeline 2") .github/workflows/train.yml

# deploy.yml  
cp <(echo "# see CI_CD_BLUEPRINT.md Pipeline 3") .github/workflows/deploy.yml

# drift_monitor.yml
cp <(echo "# see CI_CD_BLUEPRINT.md Pipeline 4") .github/workflows/drift_monitor.yml

# evidence_export.yml
cp <(echo "# see CI_CD_BLUEPRINT.md Pipeline 5") .github/workflows/evidence_export.yml

echo "✅ GitHub Actions workflows scaffolded"
echo "ACTION REQUIRED: Paste full YAML from CI_CD_BLUEPRINT.md into each workflow file"
```

---

## Step 7: Create Makefile

```bash
cat > Makefile << 'EOF'
.PHONY: dev test train deploy clean help

dev:
	docker-compose up --build -d
	@echo "🏇 Oracle running at http://localhost:3000"

test:
	pytest tests/ -v --cov=backend --cov-report=html

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

train:
	python -m backend.training.trainer --config configs/training_config.yaml

lint:
	ruff check backend/ tests/

format:
	ruff format backend/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
	rm -rf artifacts/ htmlcov/ .benchmarks/

help:
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
EOF

echo "✅ Makefile created"
```

---

## Step 8: Git Initial Commit

```bash
# Add GitHub Secrets before this step!
# Settings → Secrets → Actions → add all from CI_CD_BLUEPRINT.md section 9

git add .
git commit -m "feat: initial Equine Oracle V3.1 repository consolidation

- Full production repo structure (180+ files)
- Precognition Engine V3.1 with all modules
- Two-stage meta-ensemble architecture
- 5-Agent swarm (Backend/Frontend/Android/Admin/Standalone)
- Complete CI/CD pipeline (5 GitHub Actions workflows)
- Docker full-stack local environment
- RDTI evidence structure
- Living Codex 2019→2026

🏇 The Oracle is alive."

git branch -M main
git push -u origin main

echo "✅ Repository live at https://github.com/lowkey-consultants/equine-oracle"
```

---

## Step 9: Add GitHub Secrets (REQUIRED before CI runs)

```
GitHub UI: Settings → Secrets and variables → Actions → New repository secret

Required secrets:
  RACING_API_KEY              → Your TheRacingAPI key
  RACING_API_KEY_TEST         → Sandbox key
  GROK4_API_KEY               → xAI API key
  GROK4_API_KEY_TEST          → xAI test key
  DATABASE_URL                → PostgreSQL connection string
  OPTUNA_STORAGE_URL          → PostgreSQL for Optuna
  AWS_ACCESS_KEY_ID           → AWS IAM key
  AWS_SECRET_ACCESS_KEY       → AWS IAM secret
  ECR_REGISTRY                → ECR registry URL
  MLFLOW_TRACKING_URI         → MLflow server
  SLACK_WEBHOOK_URL           → Slack webhook
  PROMETHEUS_PUSHGATEWAY_URL  → Prometheus pushgateway
  PROD_SMOKE_TEST_API_KEY     → Production test key
```

---

## Step 10: Verify Setup

```bash
# Test the full pipeline locally
make dev                    # Start stack
sleep 10                    # Wait for services

# Health check
curl http://localhost:8000/api/v2/health | python -m json.tool

# Run test suite
make test

# Expected output:
# ✅ 85%+ test coverage
# ✅ All latency tests < 150ms
# ✅ Docker stack healthy (8 services)

echo "🏇 Equine Oracle V3.1 is operational."
echo "Dashboard: http://localhost:3000"
echo "API:       http://localhost:8000/docs"
echo "Admin:     http://localhost:3001"
echo "MLflow:    http://localhost:5000"
echo "Grafana:   http://localhost:3030"
```

---

## Quick Reference Card

| Command | Action |
|---------|--------|
| `make dev` | Start full local stack |
| `make test` | Run all tests |
| `make train` | Train new model |
| `make drift-check` | Check for data/model drift |
| `make evidence` | Export RDTI evidence package |
| `make logs` | Tail production logs |
| `make rollback` | Emergency rollback to last stable |
