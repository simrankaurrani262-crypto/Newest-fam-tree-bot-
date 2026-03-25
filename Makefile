.PHONY: help install dev-install test lint format clean docker-build docker-up docker-down migrate shell

help:
	@echo "Fam Tree Bot - Available Commands:"
	@echo ""
	@echo "  make install      - Install production dependencies"
	@echo "  make dev-install  - Install development dependencies"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"
	@echo "  make clean        - Clean cache files"
	@echo "  make docker-build - Build Docker images"
	@echo "  make docker-up    - Start Docker containers"
	@echo "  make docker-down  - Stop Docker containers"
	@echo "  make migrate      - Run database migrations"
	@echo "  make shell        - Open Python shell"
	@echo ""

install:
	pip install -r requirements.txt

dev-install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v --cov=src --cov-report=term-missing

lint:
	flake8 src/ --max-line-length=100
	pylint src/ --disable=C,R
	mypy src/ --ignore-missing-imports

format:
	black src/ tests/ --line-length=100
	isort src/ tests/ --profile=black

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

migrate:
	alembic upgrade head

shell:
	python -c "from src.database.connection import init_database; import asyncio; asyncio.run(init_database()); print('Database initialized')"
