# Multi-stage Dockerfile for Equine Oracle v3.1
# Production-grade horse-race prediction system with ML ensemble and Kelly RL agent

# Stage 1: Build stage - Node.js dependencies and frontend build
FROM node:24-alpine AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache python3 make g++ cairo-dev jpeg-dev pango-dev giflib-dev pixman-dev

# Copy package files
COPY package*.json ./
COPY pnpm-lock.yaml* ./

# Install dependencies
RUN npm install -g pnpm && pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Build frontend
RUN pnpm run build:frontend || true

# Build backend TypeScript
RUN pnpm run build:backend || true

# Stage 2: Python ML environment - CatBoost, XGBoost, LightGBM ensemble
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for ML libraries and runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
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
    && rm -rf /var/lib/apt/lists/*

# Install Node.js in Python image
RUN curl -fsSL https://deb.nodesource.com/setup_24.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Copy built artifacts from builder stage
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/build ./build

# Copy source files
COPY . .

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
    sqlalchemy==2.0.21 \
    alembic==1.12.0 \
    pydantic-settings==2.0.3 \
    python-multipart==0.0.6 \
    uvicorn==0.23.2 \
    fastapi==0.103.1 \
    starlette==0.27.0 \
    pydantic-core==2.10.1

# Install Node.js dependencies with pnpm
RUN npm install -g pnpm && pnpm install --frozen-lockfile

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Expose ports
EXPOSE 3000 8000 5000

# Set environment variables
ENV NODE_ENV=production \
    PYTHONUNBUFFERED=1 \
    PORT=3000 \
    PYTHONPATH=/app

# Start application
CMD ["sh", "-c", "pnpm start:prod"]
