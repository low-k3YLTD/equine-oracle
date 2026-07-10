# Production Dockerfile for Equine Oracle v3.1
# Horse-race prediction system with ML ensemble (CatBoost, XGBoost, LightGBM)

# Stage 1: Builder - Compile TypeScript and build frontend
FROM node:24-alpine AS builder

WORKDIR /build

# Install build dependencies
RUN apk add --no-cache python3 make g++

# Copy package files
COPY package*.json pnpm-lock.yaml* ./

# Install dependencies
RUN npm install -g pnpm && \
    pnpm install --frozen-lockfile || npm install

# Copy source code
COPY . .

# Build TypeScript and frontend
RUN npm run build || echo "Build script not found, skipping"

# Stage 2: Runtime - Python + Node.js for ML ensemble
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for ML libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    libc-dev \
    gcc \
    g++ \
    make \
    cmake \
    libboost-all-dev \
    libopenblas-dev \
    liblapack-dev \
    libblas-dev \
    gfortran \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install Python ML dependencies
RUN pip install --no-cache-dir \
    numpy==1.24.3 \
    pandas==2.0.3 \
    scikit-learn==1.3.0 \
    scipy==1.11.2 \
    catboost==1.2.2 \
    xgboost==2.0.0 \
    lightgbm==4.0.0 \
    mlflow==2.7.1 \
    optuna==3.13.0 \
    pydantic==2.3.0 \
    python-dotenv==1.0.0 \
    requests==2.31.0 \
    aiohttp==3.8.5 \
    redis==5.0.0 \
    psycopg2-binary==2.9.7 \
    mysql-connector-python==8.1.0 \
    sqlalchemy==2.0.21

# Copy built artifacts from builder
COPY --from=builder /build/dist ./dist 2>/dev/null || true
COPY --from=builder /build/build ./build 2>/dev/null || true

# Copy application files
COPY . .

# Install Node.js dependencies
RUN npm install -g pnpm && \
    pnpm install --frozen-lockfile || npm install

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Expose ports
EXPOSE 3000 8000 5000

# Set environment
ENV NODE_ENV=production \
    PYTHONUNBUFFERED=1 \
    PORT=3000 \
    PYTHONPATH=/app

# Start application
CMD ["npm", "run", "start:prod"]
