# CI_CD_BLUEPRINT.md
# Equine Oracle — Complete CI/CD Automation Blueprint
## GitHub Actions + Model Registry + Drift Detection + Zero-Downtime Deploy

---

## Table of Contents

1. [Pipeline Overview](#1-pipeline-overview)
2. [Pipeline 1: Test (test.yml)](#2-pipeline-1-test-testyml)
3. [Pipeline 2: Train (train.yml)](#3-pipeline-2-train-trainyml)
4. [Pipeline 3: Deploy (deploy.yml)](#4-pipeline-3-deploy-deployyml)
5. [Pipeline 4: Drift Monitor (drift_monitor.yml)](#5-pipeline-4-drift-monitor-drift_monitoryml)
6. [Pipeline 5: Evidence Export (evidence_export.yml)](#6-pipeline-5-evidence-export-evidence_exportyml)
7. [Model Registry Strategy](#7-model-registry-strategy)
8. [Zero-Downtime Deployment](#8-zero-downtime-deployment)
9. [Secrets Management](#9-secrets-management)
10. [Rollback Procedures](#10-rollback-procedures)

---

## 1. Pipeline Overview

```
┌──────────────────────────────────────────────────────────────┐
│                   CI/CD PIPELINE MAP                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  CODE PUSH/PR                                                │
│       │                                                      │
│       ▼                                                      │
│  ┌─────────────┐                                             │
│  │  test.yml   │ ← Runs on: every push + PR to main/develop  │
│  │             │   Tests: unit + integration + performance    │
│  │             │   Coverage: >90% required on changed files   │
│  └──────┬──────┘                                             │
│         │ PASS                                               │
│         ▼                                                    │
│  ┌─────────────┐                                             │
│  │  train.yml  │ ← Triggered: merge to main OR manual        │
│  │             │   OR scheduled (weekly Sunday 02:00 NZT)    │
│  │             │   Runs: full training + HPO + evaluation     │
│  │             │   Output: challenger model artifact          │
│  └──────┬──────┘                                             │
│         │ NDCG@4 ≥ current champion                          │
│         ▼                                                    │
│  ┌─────────────┐                                             │
│  │  deploy.yml │ ← Triggered: successful train + approval    │
│  │             │   Strategy: blue/green zero-downtime         │
│  │             │   Smoke test → promote → archive old         │
│  └─────────────┘                                             │
│                                                              │
│  SCHEDULED (independent)                                     │
│  ┌──────────────────┐   ┌────────────────────┐              │
│  │ drift_monitor.yml│   │evidence_export.yml │              │
│  │ Every 6 hours    │   │ Monthly / on-demand│              │
│  └──────────────────┘   └────────────────────┘              │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Pipeline 1: Test (test.yml)

```yaml
# .github/workflows/test.yml
name: 🧪 Test Suite

on:
  push:
    branches: [main, develop, 'feature/**', 'fix/**']
  pull_request:
    branches: [main, develop]

env:
  PYTHON_VERSION: '3.11'
  NODE_VERSION: '20'

jobs:
  # ─── PYTHON BACKEND TESTS ───────────────────────────────────
  backend-unit-tests:
    name: Backend Unit Tests
    runs-on: ubuntu-latest
    timeout-minutes: 20

    services:
      redis:
        image: redis:7-alpine
        ports: ['6379:6379']
        options: --health-cmd "redis-cli ping" --health-interval 10s
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: oracle_test
        ports: ['5432:5432']
        options: --health-cmd pg_isready --health-interval 10s

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip

      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -e ".[dev,test]"

      - name: Run unit tests with coverage
        env:
          DATABASE_URL: postgresql://postgres:test_password@localhost:5432/oracle_test
          REDIS_URL: redis://localhost:6379
          RACING_API_KEY: ${{ secrets.RACING_API_KEY_TEST }}
          GROK4_API_KEY: ${{ secrets.GROK4_API_KEY_TEST }}
          TESTING: true
        run: |
          pytest tests/unit/ \
            -v \
            --cov=backend \
            --cov-report=xml \
            --cov-report=html \
            --cov-fail-under=85 \
            --junit-xml=test-results/unit.xml \
            -n auto \
            --timeout=60

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          files: coverage.xml
          flags: unit-tests

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: unit-test-results
          path: test-results/

  # ─── INTEGRATION TESTS ──────────────────────────────────────
  backend-integration-tests:
    name: Backend Integration Tests
    runs-on: ubuntu-latest
    needs: backend-unit-tests
    timeout-minutes: 30

    services:
      redis:
        image: redis:7-alpine
        ports: ['6379:6379']
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: oracle_test
        ports: ['5432:5432']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip

      - name: Install dependencies
        run: pip install -e ".[dev,test]"

      - name: Download test model artifacts
        run: |
          python scripts/download_test_models.py
          # Downloads minimal test-size model fixtures

      - name: Run integration tests
        env:
          DATABASE_URL: postgresql://postgres:test_password@localhost:5432/oracle_test
          REDIS_URL: redis://localhost:6379
          TESTING: true
        run: |
          pytest tests/integration/ \
            -v \
            --junit-xml=test-results/integration.xml \
            --timeout=120 \
            -n 2

      - name: Run API endpoint tests
        run: |
          # Start API in background
          uvicorn backend.api.main:app --port 8001 &
          sleep 5
          # Run endpoint tests
          pytest tests/integration/test_api_endpoints.py \
            --base-url=http://localhost:8001 \
            -v

  # ─── PERFORMANCE / LATENCY TESTS ────────────────────────────
  performance-tests:
    name: Performance / Latency Tests
    runs-on: ubuntu-latest
    needs: backend-unit-tests
    timeout-minutes: 20

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip

      - run: pip install -e ".[dev,test]"

      - name: Run latency tests
        run: |
          pytest tests/performance/test_latency.py \
            -v \
            --benchmark-autosave \
            --benchmark-compare-fail=mean:10% \
            --junit-xml=test-results/performance.xml

      - name: Assert p95 < 150ms
        run: |
          python tests/performance/assert_sla.py \
            --p95-threshold-ms=150 \
            --results=.benchmarks/

  # ─── FRONTEND TESTS ─────────────────────────────────────────
  frontend-tests:
    name: Frontend Tests (React/TS)
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm
          cache-dependency-path: frontend/package-lock.json

      - name: Install deps
        working-directory: frontend
        run: npm ci

      - name: TypeScript type check
        working-directory: frontend
        run: npm run type-check

      - name: Run tests
        working-directory: frontend
        run: npm run test -- --coverage --watchAll=false

      - name: Build check
        working-directory: frontend
        run: npm run build

  # ─── SECURITY SCAN ──────────────────────────────────────────
  security-scan:
    name: Security Scan
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: fs
          scan-ref: .
          format: table
          exit-code: 1
          severity: CRITICAL,HIGH

      - name: Run Bandit (Python security)
        run: |
          pip install bandit[toml]
          bandit -r backend/ -c pyproject.toml --severity-level medium

  # ─── SYNTHETIC DATA TESTS ───────────────────────────────────
  synthetic-tests:
    name: Synthetic Race Tests
    runs-on: ubuntu-latest
    needs: backend-unit-tests

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip

      - run: pip install -e ".[dev,test]"

      - name: Run synthetic race stress tests
        run: |
          pytest tests/synthetic/ \
            -v \
            --junit-xml=test-results/synthetic.xml \
            --timeout=60

  # ─── ALL TESTS GATE ─────────────────────────────────────────
  all-tests-pass:
    name: ✅ All Tests Pass Gate
    runs-on: ubuntu-latest
    needs:
      - backend-unit-tests
      - backend-integration-tests
      - performance-tests
      - frontend-tests
      - security-scan
      - synthetic-tests
    steps:
      - run: echo "All test suites passed ✅"
```

---

## 3. Pipeline 2: Train (train.yml)

```yaml
# .github/workflows/train.yml
name: 🏋️ Model Training

on:
  workflow_run:
    workflows: ["🧪 Test Suite"]
    types: [completed]
    branches: [main]
  schedule:
    - cron: '0 14 * * 0'   # Sunday 02:00 NZT (UTC+12 → 14:00 UTC Saturday)
  workflow_dispatch:
    inputs:
      force_full_retrain:
        description: 'Force full retrain (skip incremental check)'
        required: false
        default: 'false'
        type: boolean
      n_optuna_trials:
        description: 'Number of Optuna trials'
        required: false
        default: '200'
        type: string

jobs:
  check-trigger:
    name: Check Training Trigger
    runs-on: ubuntu-latest
    if: |
      github.event_name == 'schedule' ||
      github.event_name == 'workflow_dispatch' ||
      (github.event_name == 'workflow_run' && github.event.workflow_run.conclusion == 'success')
    outputs:
      should_train: ${{ steps.check.outputs.should_train }}
    steps:
      - uses: actions/checkout@v4

      - name: Check if new data available
        id: check
        run: |
          python scripts/check_new_race_data.py \
            --last-training-date=$(cat models/registry/champion/.last_trained) \
            --min-new-races=100 \
            --output=should_train.txt
          echo "should_train=$(cat should_train.txt)" >> $GITHUB_OUTPUT

  train-challenger:
    name: Train Challenger Model
    runs-on: ubuntu-latest  # Use self-hosted GPU runner in production
    needs: check-trigger
    if: needs.check-trigger.outputs.should_train == 'true' || github.event.inputs.force_full_retrain == 'true'
    timeout-minutes: 360   # 6 hours max

    env:
      MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
      AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
      AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      RACING_API_KEY: ${{ secrets.RACING_API_KEY }}
      GROK4_API_KEY: ${{ secrets.GROK4_API_KEY }}

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: pip

      - name: Install training dependencies
        run: pip install -e ".[training]"

      - name: Download latest race data
        run: |
          python -m backend.data.racing_api_client \
            --fetch-since=$(cat models/registry/champion/.last_trained) \
            --output=data/raw/latest_races.parquet
          echo "Downloaded $(python -c "import pandas as pd; print(len(pd.read_parquet('data/raw/latest_races.parquet')))" ) races"

      - name: Feature engineering
        run: |
          python -m backend.features.feature_store \
            --input=data/raw/latest_races.parquet \
            --output=data/processed/features_v3.parquet \
            --config=configs/feature_config.yaml

      - name: Optuna hyperparameter search
        run: |
          python -m backend.training.optuna_search \
            --n-trials=${{ github.event.inputs.n_optuna_trials || '200' }} \
            --study-name=equine_oracle_v3_$(date +%Y%m%d) \
            --storage=${{ secrets.OPTUNA_STORAGE_URL }} \
            --output=artifacts/best_params.json
          echo "Best params saved to artifacts/best_params.json"

      - name: Train full ensemble
        run: |
          python -m backend.training.trainer \
            --config=configs/training_config.yaml \
            --hyperparams=artifacts/best_params.json \
            --data=data/processed/features_v3.parquet \
            --output-dir=artifacts/challenger/ \
            --run-name=challenger_$(date +%Y%m%d_%H%M%S)

      - name: Evaluate challenger vs champion
        id: evaluate
        run: |
          python -m backend.training.model_registry \
            evaluate-challenger \
            --challenger-dir=artifacts/challenger/ \
            --champion-dir=models/registry/champion/ \
            --test-data=data/processed/holdout_2024_q3q4.parquet \
            --output=artifacts/evaluation_report.json

          # Parse results
          python -c "
          import json
          with open('artifacts/evaluation_report.json') as f:
              r = json.load(f)
          print(f'Challenger NDCG@4: {r[\"challenger\"][\"ndcg4\"]:.4f}')
          print(f'Champion  NDCG@4: {r[\"champion\"][\"ndcg4\"]:.4f}')
          print(f'Challenger ECE:    {r[\"challenger\"][\"ece\"]:.4f}')
          print(f'Is better: {r[\"challenger_is_better\"]}')
          import os
          os.environ['CHALLENGER_NDCG4'] = str(r['challenger']['ndcg4'])
          os.environ['IS_BETTER'] = str(r['challenger_is_better']).lower()
          " >> $GITHUB_ENV

          # Set output
          IS_BETTER=$(python -c "import json; r=json.load(open('artifacts/evaluation_report.json')); print(str(r['challenger_is_better']).lower())")
          echo "challenger_is_better=${IS_BETTER}" >> $GITHUB_OUTPUT

      - name: Calibrate challenger
        if: steps.evaluate.outputs.challenger_is_better == 'true'
        run: |
          python -m backend.ensemble.calibration \
            --model-dir=artifacts/challenger/ \
            --calibration-data=data/processed/calibration_set.parquet \
            --method=isotonic

      - name: Generate model card
        run: |
          python scripts/generate_model_card.py \
            --evaluation=artifacts/evaluation_report.json \
            --model-dir=artifacts/challenger/ \
            --output=artifacts/challenger/model_card.md

      - name: Log to MLflow
        run: |
          python -m backend.training.mlflow_tracker \
            --run-name=challenger_$(date +%Y%m%d) \
            --artifacts-dir=artifacts/challenger/ \
            --evaluation=artifacts/evaluation_report.json

      - name: Upload challenger artifact
        uses: actions/upload-artifact@v4
        with:
          name: challenger-model-${{ github.run_number }}
          path: artifacts/challenger/
          retention-days: 30

      - name: Notify Slack — Training complete
        uses: slackapi/slack-github-action@v1.25.0
        with:
          payload: |
            {
              "text": "🏋️ Training complete | Challenger NDCG@4: ${{ env.CHALLENGER_NDCG4 }} | Better than champion: ${{ env.IS_BETTER }}",
              "channel": "#oracle-mlops"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}

      - name: Fail if challenger is worse
        if: steps.evaluate.outputs.challenger_is_better == 'false'
        run: |
          echo "❌ Challenger did not beat champion. Blocking deployment."
          echo "Review evaluation report in artifacts."
          exit 1
```

---

## 4. Pipeline 3: Deploy (deploy.yml)

```yaml
# .github/workflows/deploy.yml
name: 🚀 Deploy to Production

on:
  workflow_run:
    workflows: ["🏋️ Model Training"]
    types: [completed]
    branches: [main]
  workflow_dispatch:
    inputs:
      model_run_number:
        description: 'GitHub run number of training artifact to deploy'
        required: true
        type: string
      environment:
        description: 'Deployment environment'
        required: true
        default: 'production'
        type: choice
        options: [staging, production]

concurrency:
  group: production-deploy
  cancel-in-progress: false   # Never cancel a deployment mid-flight

jobs:
  pre-deploy-validation:
    name: Pre-Deploy Validation
    runs-on: ubuntu-latest
    if: |
      github.event_name == 'workflow_dispatch' ||
      (github.event_name == 'workflow_run' && github.event.workflow_run.conclusion == 'success')
    outputs:
      deploy_approved: ${{ steps.validate.outputs.approved }}

    steps:
      - uses: actions/checkout@v4

      - name: Download model artifact
        uses: actions/download-artifact@v4
        with:
          name: challenger-model-${{ github.event.inputs.model_run_number || github.event.workflow_run.run_number }}
          path: artifacts/challenger/

      - name: Validate model artifact integrity
        id: validate
        run: |
          python scripts/validate_model_artifact.py \
            --model-dir=artifacts/challenger/ \
            --required-files="meta_ensemble_v3.1.pkl,lgbm_ranker_v3.1.pkl,feature_metadata.json,model_card.md" \
            --min-ndcg4=0.97 \
            --max-ece=0.06
          echo "approved=true" >> $GITHUB_OUTPUT

      - name: Smoke test against staging
        run: |
          python scripts/smoke_test.py \
            --model-dir=artifacts/challenger/ \
            --test-cases=tests/synthetic/fixtures/synthetic_race_cards.json \
            --expected-latency-ms=200 \
            --expected-ndcg4=0.97

  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: pre-deploy-validation
    if: needs.pre-deploy-validation.outputs.deploy_approved == 'true'
    environment:
      name: staging
      url: https://staging.equineoracle.co.nz

    steps:
      - uses: actions/checkout@v4

      - name: Download model artifact
        uses: actions/download-artifact@v4
        with:
          name: challenger-model-${{ github.event.inputs.model_run_number || github.event.workflow_run.run_number }}
          path: artifacts/challenger/

      - name: Build Docker image
        run: |
          docker build \
            -f backend/Dockerfile \
            -t equine-oracle-backend:staging-${{ github.run_number }} \
            --build-arg MODEL_VERSION=${{ github.run_number }} \
            .

      - name: Push to ECR
        run: |
          aws ecr get-login-password --region ap-southeast-2 | \
            docker login --username AWS --password-stdin ${{ secrets.ECR_REGISTRY }}
          docker tag equine-oracle-backend:staging-${{ github.run_number }} \
            ${{ secrets.ECR_REGISTRY }}/equine-oracle:staging-${{ github.run_number }}
          docker push ${{ secrets.ECR_REGISTRY }}/equine-oracle:staging-${{ github.run_number }}

      - name: Deploy to staging ECS
        run: |
          aws ecs update-service \
            --cluster equine-oracle-staging \
            --service backend-service \
            --force-new-deployment \
            --region ap-southeast-2

      - name: Wait for staging to be healthy
        run: |
          python scripts/wait_for_deployment.py \
            --url=https://staging-api.equineoracle.co.nz/api/v2/health \
            --timeout=180

      - name: Run staging integration tests
        run: |
          pytest tests/integration/ \
            --base-url=https://staging-api.equineoracle.co.nz \
            -v \
            --timeout=30

  deploy-production:
    name: Deploy to Production (Blue/Green)
    runs-on: ubuntu-latest
    needs: deploy-staging
    environment:
      name: production
      url: https://api.equineoracle.co.nz

    steps:
      - uses: actions/checkout@v4

      - name: Archive current champion
        run: |
          python -m backend.training.model_registry \
            archive-champion \
            --destination=models/registry/archive/v$(date +%Y%m%d_%H%M%S)/

      - name: Tag image as production
        run: |
          docker tag \
            ${{ secrets.ECR_REGISTRY }}/equine-oracle:staging-${{ github.run_number }} \
            ${{ secrets.ECR_REGISTRY }}/equine-oracle:production-${{ github.run_number }}
          docker tag \
            ${{ secrets.ECR_REGISTRY }}/equine-oracle:staging-${{ github.run_number }} \
            ${{ secrets.ECR_REGISTRY }}/equine-oracle:latest
          docker push ${{ secrets.ECR_REGISTRY }}/equine-oracle:production-${{ github.run_number }}
          docker push ${{ secrets.ECR_REGISTRY }}/equine-oracle:latest

      - name: Blue/Green deployment — launch Green
        run: |
          # Launch new (green) task definition
          aws ecs register-task-definition \
            --family equine-oracle-backend \
            --container-definitions "[{
              \"name\": \"backend\",
              \"image\": \"${{ secrets.ECR_REGISTRY }}/equine-oracle:production-${{ github.run_number }}\",
              \"environment\": [{\"name\": \"MODEL_VERSION\", \"value\": \"${{ github.run_number }}\"}]
            }]"

          # Update service to use new task definition
          aws ecs update-service \
            --cluster equine-oracle-prod \
            --service backend-service \
            --task-definition equine-oracle-backend \
            --deployment-configuration '{"maximumPercent": 200, "minimumHealthyPercent": 100}' \
            --region ap-southeast-2

      - name: Wait for production health
        run: |
          python scripts/wait_for_deployment.py \
            --url=https://api.equineoracle.co.nz/api/v2/health \
            --timeout=300 \
            --expected-model-version=${{ github.run_number }}

      - name: Production smoke test
        run: |
          python scripts/smoke_test.py \
            --base-url=https://api.equineoracle.co.nz \
            --api-key=${{ secrets.PROD_SMOKE_TEST_API_KEY }} \
            --test-cases=tests/synthetic/fixtures/synthetic_race_cards.json \
            --expected-latency-ms=150

      - name: Promote challenger to champion in registry
        run: |
          python -m backend.training.model_registry \
            promote-challenger \
            --challenger-dir=artifacts/challenger/ \
            --champion-dir=models/registry/champion/ \
            --version=${{ github.run_number }}
          date +%Y-%m-%d > models/registry/champion/.last_trained

      - name: Update drift baseline
        run: |
          python -m backend.monitoring.drift_detector \
            update-baseline \
            --new-model-version=${{ github.run_number }}

      - name: Notify Slack — Deployment successful
        uses: slackapi/slack-github-action@v1.25.0
        with:
          payload: |
            {
              "text": "🚀 Production deployment successful! Model v${{ github.run_number }} is live at https://api.equineoracle.co.nz",
              "channel": "#oracle-mlops"
            }
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}

      - name: Rollback on failure
        if: failure()
        run: |
          echo "❌ Deployment failed — initiating automatic rollback"
          bash infra/scripts/rollback.sh \
            --cluster=equine-oracle-prod \
            --service=backend-service \
            --previous-version=$(cat models/registry/archive/.latest_archived_version)
```

---

## 5. Pipeline 4: Drift Monitor (drift_monitor.yml)

```yaml
# .github/workflows/drift_monitor.yml
name: 📡 Drift Monitoring

on:
  schedule:
    - cron: '0 */6 * * *'   # Every 6 hours
  workflow_dispatch:

jobs:
  detect-drift:
    name: Feature + Prediction Drift Detection
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: pip

      - run: pip install -e ".[monitoring]"

      - name: Run feature drift detection
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
        run: |
          python -m backend.monitoring.drift_detector \
            detect \
            --window=last_500_predictions \
            --reference=models/registry/champion/drift_baseline.parquet \
            --output=artifacts/drift_report.json \
            --features=avg_perf_index_L5,weighted_form_score,track_moisture_pct

      - name: Run calibration drift detection
        run: |
          python -m backend.monitoring.calibration_monitor \
            check \
            --window=last_200_predictions \
            --ece-threshold=0.065 \
            --output=artifacts/calibration_report.json

      - name: Run concept drift detection
        run: |
          python -m backend.monitoring.concept_drift \
            detect \
            --ndcg4-threshold=0.94 \
            --window=last_7_days \
            --output=artifacts/concept_drift_report.json

      - name: Parse drift results and alert
        id: parse_drift
        run: |
          python scripts/parse_drift_and_alert.py \
            --feature-drift=artifacts/drift_report.json \
            --calibration=artifacts/calibration_report.json \
            --concept-drift=artifacts/concept_drift_report.json \
            --slack-webhook=${{ secrets.SLACK_WEBHOOK_URL }} \
            --output=artifacts/drift_summary.txt

          DRIFT_SEVERITY=$(cat artifacts/drift_summary.txt | grep "SEVERITY:" | cut -d: -f2 | tr -d ' ')
          echo "drift_severity=${DRIFT_SEVERITY}" >> $GITHUB_OUTPUT

      - name: Trigger retrain if critical drift
        if: steps.parse_drift.outputs.drift_severity == 'CRITICAL'
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.actions.createWorkflowDispatch({
              owner: context.repo.owner,
              repo: context.repo.repo,
              workflow_id: 'train.yml',
              ref: 'main',
              inputs: {
                force_full_retrain: 'true',
                n_optuna_trials: '100'
              }
            });
            console.log('🚨 Critical drift detected — triggered emergency retrain');

      - name: Upload drift reports
        uses: actions/upload-artifact@v4
        with:
          name: drift-report-${{ github.run_number }}
          path: artifacts/drift_report.json
          retention-days: 90

      - name: Post drift summary to Grafana
        run: |
          python scripts/push_drift_metrics_to_prometheus.py \
            --pushgateway-url=${{ secrets.PROMETHEUS_PUSHGATEWAY_URL }} \
            --drift-report=artifacts/drift_report.json
```

---

## 6. Pipeline 5: Evidence Export (evidence_export.yml)

```yaml
# .github/workflows/evidence_export.yml
name: 📋 RDTI Evidence Export

on:
  schedule:
    - cron: '0 0 1 * *'   # First day of each month
  workflow_dispatch:
    inputs:
      tax_year:
        description: 'Tax year for evidence (e.g., 2025-2026)'
        required: true
        type: string

jobs:
  export-evidence:
    name: Generate RDTI Evidence Package
    runs-on: ubuntu-latest
    timeout-minutes: 60

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: pip

      - run: pip install -e ".[standalone]"

      - name: Generate calibration curves PDF
        run: |
          jupyter nbconvert \
            --to script standalone/notebooks/08_Calibration_Analysis.ipynb
          python standalone/scripts/generate_calibration_plots.py \
            --output=docs/evidence/calibration_curves.pdf

      - name: Generate feature importance report
        run: |
          python standalone/scripts/generate_feature_importance_report.py \
            --model-dir=models/registry/champion/ \
            --output=docs/evidence/feature_importance_report.pdf

      - name: Generate model performance report
        run: |
          python standalone/scripts/generate_model_card.py \
            --evaluation=models/registry/champion/evaluation.json \
            --output=docs/evidence/model_performance_report.pdf

      - name: Export full RDTI package
        run: |
          python standalone/scripts/export_evidence_package.py \
            --tax-year=${{ github.event.inputs.tax_year || '2025-2026' }} \
            --output-dir=artifacts/rdti_evidence/ \
            --include-timeline \
            --include-hypothesis-log \
            --include-technical-uncertainty

      - name: Upload evidence package
        uses: actions/upload-artifact@v4
        with:
          name: rdti-evidence-${{ github.event.inputs.tax_year || github.run_number }}
          path: artifacts/rdti_evidence/
          retention-days: 365   # Keep for full tax year
```

---

## 7. Model Registry Strategy

```
MODEL LIFECYCLE
────────────────
  CHALLENGER → (evaluation) → CHAMPION → (deprecation) → ARCHIVE

Registry structure:
  models/registry/
    champion/           ← Always serving 100% of production traffic
      meta_ensemble_v3.1.pkl
      feature_metadata.json
      model_card.md
      evaluation.json
      drift_baseline.parquet
      .last_trained      ← date string "2026-03-01"
    challenger/         ← Shadow deployment (5% traffic, A/B)
      [same structure]
    archive/
      v20260201_120000/  ← Timestamped archives
      v20260115_090000/
      .latest_archived_version  ← pointer for rollback

Version numbering: MAJOR.MINOR.PATCH
  - MAJOR: Architecture change (new model type)
  - MINOR: Significant NDCG improvement (>1%)
  - PATCH: Calibration update, minor retrain

PROMOTION CRITERIA (challenger → champion)
───────────────────────────────────────────
  Required:
    ✅ NDCG@4 ≥ current_champion.ndcg4  (strict improvement)
    ✅ ECE ≤ current_champion.ece + 0.005  (calibration not degraded)
    ✅ p95 latency ≤ 150ms
    ✅ All integration tests pass
  
  Recommended (soft check, warning not blocker):
    ⚠️  ROI simulation ≥ current_champion.roi
    ⚠️  No significant distribution shift in top features
```

---

## 8. Zero-Downtime Deployment

```
BLUE/GREEN STRATEGY
────────────────────

Before:
  NGINX → [BLUE] Current champion (100% traffic)
              └── ECS Task: equine-oracle-backend:v3.1.3

Deployment:
  Step 1: Launch GREEN (new version) alongside BLUE
    NGINX → [BLUE] 100% | [GREEN] 0%

  Step 2: Health check GREEN
    Wait for ECS health: /api/v2/health → 200
    Smoke test: 3 synthetic race predictions pass

  Step 3: Gradual traffic shift (optional for high-risk deploys)
    NGINX → [BLUE] 50% | [GREEN] 50%
    Monitor: error rate, latency (5 minutes)

  Step 4: Full cutover
    NGINX → [BLUE] 0% | [GREEN] 100%
    Rename: GREEN → BLUE (for next deploy cycle)

  Step 5: Drain and stop old BLUE
    Wait 30s for in-flight requests
    Stop old ECS tasks

ROLLBACK (< 60 seconds):
  Step 1: Shift traffic back to BLUE immediately
  Step 2: Stop GREEN tasks
  Step 3: Alert on-call engineer via PagerDuty

ECS Deployment Configuration:
  maximumPercent: 200          # Allow double capacity during deploy
  minimumHealthyPercent: 100   # Never drop below current capacity
  deploymentCircuitBreaker:
    enable: true
    rollback: true             # Auto-rollback if health checks fail
```

---

## 9. Secrets Management

```
GitHub Secrets Required (Settings → Secrets → Actions)
──────────────────────────────────────────────────────
# API Keys
RACING_API_KEY              TheRacingAPI production key
RACING_API_KEY_TEST         TheRacingAPI test/sandbox key
GROK4_API_KEY               xAI Grok-4 API key
GROK4_API_KEY_TEST          xAI test key (low quota)

# Database
DATABASE_URL                postgresql://user:pass@host:5432/oracle
OPTUNA_STORAGE_URL          postgresql://user:pass@host:5432/optuna

# Cloud Infrastructure
AWS_ACCESS_KEY_ID           AWS IAM access key
AWS_SECRET_ACCESS_KEY       AWS IAM secret key
ECR_REGISTRY                AWS ECR registry URL

# MLflow
MLFLOW_TRACKING_URI         MLflow tracking server URL

# Monitoring
SLACK_WEBHOOK_URL           Slack #oracle-mlops channel
PROMETHEUS_PUSHGATEWAY_URL  Prometheus pushgateway URL
PAGERDUTY_API_KEY           PagerDuty integration key

# Production API
PROD_SMOKE_TEST_API_KEY     Dedicated key for smoke tests

NEVER COMMIT:
  ✗ Any key starting with sk- or xai-
  ✗ Database passwords
  ✗ .env files
  ✗ Any file in /models/ (use Git LFS + DVC)

Local development: copy .env.example → .env and fill values
```

---

## 10. Rollback Procedures

### Automatic Rollback (ECS Circuit Breaker)
Triggered automatically if >50% of ECS health checks fail during deployment.

### Manual Rollback (< 5 minutes)

```bash
# 1. Identify the last stable version
cat models/registry/archive/.latest_archived_version
# → v20260201_120000

# 2. Execute rollback script
bash infra/scripts/rollback.sh \
  --cluster=equine-oracle-prod \
  --service=backend-service \
  --previous-version=v20260201_120000

# 3. Verify health
curl https://api.equineoracle.co.nz/api/v2/health | jq .

# 4. Confirm traffic restored
bash infra/scripts/health_check.sh --env=production

# 5. Notify team
python scripts/notify_rollback.py \
  --reason="Manual rollback - $(git log -1 --oneline)" \
  --channel="#oracle-mlops"
```

### Model-Only Rollback (without code change)

```bash
# Restore previous champion model files
python -m backend.training.model_registry \
  restore-archive \
  --version=v20260201_120000 \
  --destination=models/registry/champion/

# Restart API workers to reload models (no downtime)
aws ecs update-service \
  --cluster equine-oracle-prod \
  --service backend-service \
  --force-new-deployment \
  --region ap-southeast-2
```

### Drift-Triggered Emergency Retrain Checklist

```
When drift_severity == CRITICAL:
  1. ✅ Automatic retrain triggered by drift_monitor.yml
  2. ✅ Slack alert sent to #oracle-mlops
  3. Manual review: check drift_report.json for affected features
  4. If data quality issue: pause predictions until resolved
     → POST /api/v2/admin/maintenance-mode (Admin panel)
  5. If model quality issue: let retrain complete, then deploy
  6. Post-incident: update drift_baseline.parquet
```

---

## Makefile Reference

```makefile
# Full Makefile — run `make help` to see all commands

.PHONY: dev test train deploy clean help

dev:                  ## Start full local stack (Docker Compose)
	docker-compose up --build -d
	@echo "🏇 Oracle is running at http://localhost:3000"

test:                 ## Run full test suite
	pytest tests/ -v --cov=backend --cov-report=html

test-unit:            ## Run unit tests only
	pytest tests/unit/ -v

test-integration:     ## Run integration tests only
	pytest tests/integration/ -v

test-perf:            ## Run performance / latency tests
	pytest tests/performance/ -v --benchmark-autosave

train:                ## Trigger local training run
	python -m backend.training.trainer --config configs/training_config.yaml

train-fast:           ## Quick training run (50 Optuna trials)
	python -m backend.training.trainer \
		--config configs/training_config.yaml \
		--n-optuna-trials=50 \
		--skip-grok4

train-with-hpo:       ## Full training + 200-trial Optuna search
	python -m backend.training.trainer \
		--config configs/training_config.yaml \
		--n-optuna-trials=200

evaluate:             ## Evaluate current champion on holdout set
	python -m backend.training.model_registry evaluate-champion

deploy-staging:       ## Deploy to staging manually
	gh workflow run deploy.yml \
		-f environment=staging

deploy-prod:          ## Deploy to production manually
	gh workflow run deploy.yml \
		-f environment=production

drift-check:          ## Run manual drift detection
	python -m backend.monitoring.drift_detector detect

evidence:             ## Generate RDTI evidence package
	python standalone/scripts/export_evidence_package.py

lint:                 ## Lint Python + TypeScript
	ruff check backend/ tests/
	cd frontend && npm run lint

format:               ## Auto-format code
	ruff format backend/ tests/
	cd frontend && npm run format

clean:                ## Clean generated files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
	rm -rf artifacts/ .benchmarks/ htmlcov/

logs:                 ## Tail production API logs
	aws logs tail /ecs/equine-oracle-prod --follow

help:                 ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
```

---

*CI/CD Blueprint Version: 3.1.0 | Last Updated: 2026-03-19*  
*Owner: Lowkey Consultants Ltd | Review cycle: per major release*
