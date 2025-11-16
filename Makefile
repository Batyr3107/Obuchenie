.PHONY: help install run stop clean test migrate

help:
	@echo "CourseRate - Available commands:"
	@echo "  make install  - Install dependencies"
	@echo "  make run      - Run the application with Docker Compose"
	@echo "  make stop     - Stop all services"
	@echo "  make clean    - Clean up containers and volumes"
	@echo "  make logs     - View logs"
	@echo "  make test     - Run tests"
	@echo "  make migrate  - Run database migrations"

install:
	cd backend && pip install -r requirements.txt
	cp .env.example .env
	@echo "✅ Dependencies installed. Please edit .env file with your settings."

run:
	docker-compose up -d
	@echo "✅ Application is running!"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

stop:
	docker-compose down

clean:
	docker-compose down -v
	@echo "✅ Cleaned up containers and volumes"

logs:
	docker-compose logs -f

test:
	cd backend && pytest

migrate:
	cd backend && alembic upgrade head

backend-shell:
	docker-compose exec backend /bin/bash

db-shell:
	docker-compose exec db psql -U courseuser -d courserate
