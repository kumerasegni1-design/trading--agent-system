.PHONY: help setup build up down logs clean test install

help:
	@echo "Trading Agent System - Commands"
	@echo "================================"
	@echo "make setup      - Initial setup (download deps, create dirs)"
	@echo "make build      - Build Docker images"
	@echo "make up         - Start all services"
	@echo "make down       - Stop all services"
	@echo "make logs       - View backend logs"
	@echo "make test       - Run tests"
	@echo "make clean      - Clean up containers and volumes"
	@echo "make install    - Install Python dependencies"

 setup:
	@chmod +x setup.sh
	@./setup.sh

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "✓ Services starting..."
	@echo "  Dashboard: http://localhost:3000"
	@echo "  API: http://localhost:8000/docs"

down:
	docker-compose down
	@echo "✓ Services stopped"

logs:
	docker-compose logs -f backend

test:
	docker-compose exec backend pytest tests/ -v --cov

clean:
	docker-compose down -v
	@echo "✓ All containers and volumes removed"

install:
	pip install -r requirements.txt
