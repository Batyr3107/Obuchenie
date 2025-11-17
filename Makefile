.PHONY: help install dev run test lint format clean docker-up docker-down migrate backup restore

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "$(GREEN)CourseRate - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

# ============= Installation =============

install: ## Install all dependencies (backend + frontend)
	@echo "$(GREEN)Installing backend dependencies...$(NC)"
	cd backend && pip install -r requirements.txt
	@echo "$(GREEN)Installing frontend dependencies...$(NC)"
	cd frontend && npm install
	@echo "$(GREEN)Installing pre-commit hooks...$(NC)"
	pre-commit install

install-backend: ## Install backend dependencies only
	cd backend && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies only
	cd frontend && npm install

install-dev: ## Install development dependencies
	cd backend && pip install -r requirements.txt pytest pytest-cov black flake8 mypy
	pre-commit install

# ============= Development =============

dev: ## Run development servers (backend + frontend)
	@echo "$(GREEN)Starting development servers...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)Backend: http://localhost:8000$(NC)"
	@echo "$(GREEN)Frontend: http://localhost:5173$(NC)"
	@echo "$(GREEN)Docs: http://localhost:8000/docs$(NC)"

dev-backend: ## Run backend development server
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Run frontend development server
	cd frontend && npm run dev

# ============= Docker =============

docker-up: ## Start all services with Docker Compose
	@echo "$(GREEN)Starting Docker containers...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)Services started successfully!$(NC)"
	docker-compose ps

docker-down: ## Stop all Docker services
	@echo "$(YELLOW)Stopping Docker containers...$(NC)"
	docker-compose down

docker-logs: ## Show Docker logs
	docker-compose logs -f

docker-build: ## Build Docker images
	@echo "$(GREEN)Building Docker images...$(NC)"
	docker-compose build

docker-rebuild: ## Rebuild Docker images from scratch
	@echo "$(YELLOW)Rebuilding Docker images...$(NC)"
	docker-compose build --no-cache

docker-prod: ## Run production Docker setup
	@echo "$(GREEN)Starting production containers...$(NC)"
	docker-compose -f docker-compose.prod.yml up -d

docker-prod-build: ## Build production Docker images
	docker-compose -f docker-compose.prod.yml build

docker-clean: ## Remove all Docker containers and volumes
	@echo "$(RED)Cleaning Docker containers and volumes...$(NC)"
	docker-compose down -v
	docker system prune -f

# ============= Database =============

migrate: ## Run database migrations
	@echo "$(GREEN)Running database migrations...$(NC)"
	cd backend && alembic upgrade head

migrate-create: ## Create new migration (use MESSAGE="description")
	@if [ -z "$(MESSAGE)" ]; then \
		echo "$(RED)Error: MESSAGE is required$(NC)"; \
		echo "Usage: make migrate-create MESSAGE=\"Add user table\""; \
		exit 1; \
	fi
	cd backend && alembic revision --autogenerate -m "$(MESSAGE)"

migrate-down: ## Rollback last migration
	@echo "$(YELLOW)Rolling back last migration...$(NC)"
	cd backend && alembic downgrade -1

migrate-history: ## Show migration history
	cd backend && alembic history

db-shell: ## Open PostgreSQL shell
	docker-compose exec db psql -U courseuser -d courserate

backup: ## Create database backup
	@echo "$(GREEN)Creating database backup...$(NC)"
	@mkdir -p backups
	@docker-compose exec -T db pg_dump -U courseuser courserate > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "$(GREEN)Backup created in backups/$(NC)"

restore: ## Restore database from backup (use FILE=backup.sql)
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)Error: FILE is required$(NC)"; \
		echo "Usage: make restore FILE=backups/backup_20240101.sql"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Restoring database from $(FILE)...$(NC)"
	docker-compose exec -T db psql -U courseuser -d courserate < $(FILE)

# ============= Testing =============

test: ## Run all tests
	@echo "$(GREEN)Running tests...$(NC)"
	cd backend && pytest -v

test-cov: ## Run tests with coverage
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	cd backend && pytest --cov=app --cov-report=html --cov-report=term

test-backend: ## Run backend tests only
	cd backend && pytest tests/

test-frontend: ## Run frontend tests only
	cd frontend && npm test

test-watch: ## Run tests in watch mode
	cd backend && pytest-watch

# ============= Code Quality =============

lint: ## Run linting (backend + frontend)
	@echo "$(GREEN)Running linters...$(NC)"
	cd backend && flake8 app
	cd frontend && npm run lint

lint-backend: ## Run backend linting
	cd backend && flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics

lint-frontend: ## Run frontend linting
	cd frontend && npm run lint

format: ## Format code (backend + frontend)
	@echo "$(GREEN)Formatting code...$(NC)"
	cd backend && black app && isort app
	cd frontend && npm run format

format-check: ## Check code formatting
	cd backend && black --check app && isort --check app

type-check: ## Run type checking
	cd backend && mypy app --ignore-missing-imports

security-check: ## Run security checks
	@echo "$(GREEN)Running security checks...$(NC)"
	cd backend && bandit -r app
	cd backend && safety check
	cd frontend && npm audit

pre-commit: ## Run pre-commit hooks on all files
	pre-commit run --all-files

# ============= Build =============

build: ## Build frontend for production
	cd frontend && npm run build

build-backend: ## Build backend Docker image
	docker build -t courserate-backend:latest -f backend/Dockerfile.prod backend

build-frontend: ## Build frontend Docker image
	docker build -t courserate-frontend:latest -f frontend/Dockerfile.prod frontend

# ============= Cleanup =============

clean: ## Clean temporary files and caches
	@echo "$(YELLOW)Cleaning temporary files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/.coverage
	@echo "$(GREEN)Cleanup complete!$(NC)"

clean-logs: ## Clean log files
	rm -rf backend/logs/*.log

# ============= Deployment =============

deploy-staging: ## Deploy to staging environment
	@echo "$(GREEN)Deploying to staging...$(NC)"
	@echo "$(YELLOW)Not implemented yet$(NC)"

deploy-prod: ## Deploy to production environment
	@echo "$(RED)Deploying to production...$(NC)"
	@echo "$(YELLOW)Not implemented yet$(NC)"

# ============= Utilities =============

shell-backend: ## Open Python shell with app context
	cd backend && python -c "from app.db.base import *; from app.models import *; print('App context loaded')"

shell-db: ## Open database shell
	docker-compose exec db psql -U courseuser courserate

logs: ## Show application logs
	tail -f backend/logs/app.log

logs-error: ## Show error logs only
	tail -f backend/logs/error.log

status: ## Show service status
	@echo "$(GREEN)Service Status:$(NC)"
	@docker-compose ps

health: ## Check application health
	@echo "$(GREEN)Checking application health...$(NC)"
	@curl -f http://localhost:8000/health || echo "$(RED)Backend is down!$(NC)"

metrics: ## Show application metrics (if enabled)
	@curl -f http://localhost:9090/metrics || echo "$(YELLOW)Metrics not available$(NC)"

# ============= Documentation =============

docs: ## Generate and open API documentation
	@echo "$(GREEN)Opening API documentation...$(NC)"
	@open http://localhost:8000/docs || xdg-open http://localhost:8000/docs

docs-redoc: ## Open ReDoc documentation
	@open http://localhost:8000/redoc || xdg-open http://localhost:8000/redoc

# ============= Quick Start =============

quickstart: install docker-up migrate ## Quick start: install, docker up, migrate
	@echo "$(GREEN)=======================================$(NC)"
	@echo "$(GREEN)CourseRate is ready!$(NC)"
	@echo "$(GREEN)=======================================$(NC)"
	@echo "Backend:  http://localhost:8000"
	@echo "Frontend: http://localhost:5173"
	@echo "Docs:     http://localhost:8000/docs"
	@echo "$(GREEN)=======================================$(NC)"

# ============= Environment =============

env-create: ## Create .env files from examples
	@echo "$(GREEN)Creating .env files...$(NC)"
	cp backend/.env.example backend/.env
	cp frontend/.env.example frontend/.env
	@echo "$(YELLOW)Please edit .env files with your settings$(NC)"

env-check: ## Check if .env files exist
	@if [ ! -f backend/.env ]; then echo "$(RED)backend/.env not found!$(NC)"; exit 1; fi
	@if [ ! -f frontend/.env ]; then echo "$(RED)frontend/.env not found!$(NC)"; exit 1; fi
	@echo "$(GREEN)Environment files exist!$(NC)"

# ============= Performance =============

load-test: ## Run load testing (requires locust)
	@echo "$(GREEN)Starting load test...$(NC)"
	@echo "$(YELLOW)Not implemented yet - see scripts/load_test.py$(NC)"

benchmark: ## Run performance benchmarks
	@echo "$(GREEN)Running benchmarks...$(NC)"
	cd backend && pytest tests/performance/ -v

# ============= Git =============

git-hooks: ## Install git hooks
	pre-commit install
	@echo "$(GREEN)Git hooks installed!$(NC)"

git-check: ## Run all checks before commit
	pre-commit run --all-files
	make test

# ============= Info =============

info: ## Show project information
	@echo "$(GREEN)=======================================$(NC)"
	@echo "$(GREEN)CourseRate Project Information$(NC)"
	@echo "$(GREEN)=======================================$(NC)"
	@echo "Backend:  Python $(shell python --version 2>&1 | cut -d' ' -f2)"
	@echo "Frontend: Node $(shell node --version)"
	@echo "Docker:   $(shell docker --version | cut -d' ' -f3)"
	@echo "$(GREEN)=======================================$(NC)"
