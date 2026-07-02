#!/bin/bash

echo "🚀 Trading Agent System - Setup Script"
echo "======================================="

# Check Docker
echo "✓ Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker Desktop."
    exit 1
fi

echo "✓ Docker found: $(docker --version)"

# Check Docker Compose
echo "✓ Checking Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️  Docker Compose not found. Using 'docker compose' instead."
fi

# Create environment file
echo "✓ Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  .env created from template. Please update with your credentials."
else
    echo "✓ .env already exists"
fi

# Create necessary directories
echo "✓ Creating directories..."
mkdir -p logs
mkdir -p data
mkdir -p data/models
mkdir -p data/backtest_results
mkdir -p notebooks

# Build images
echo "✓ Building Docker images..."
docker-compose build

echo ""
echo "======================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your API keys and credentials"
echo "2. Run: docker-compose up -d"
echo "3. Open: http://localhost:3000 (dashboard)"
echo "4. API Docs: http://localhost:8000/docs"
echo ""
echo "To stop: docker-compose down"
echo "To view logs: docker-compose logs -f backend"
echo ""
