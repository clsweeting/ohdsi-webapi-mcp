.PHONY: help install test lint format type-check debug-search test-integration clean build publish docker-build docker-run docker-test

# Default target
help:
	@echo "Available commands:"
	@echo "  install           Install dependencies with Poetry"
	@echo "  test             Run all tests"
	@echo "  test-unit        Run unit tests only (fast)"
	@echo "  test-integration Run integration tests only" 
	@echo "  test-cov         Run tests with coverage reporting"
	@echo "  test-all         Run all tests with coverage"
	@echo "  test-mcp-inspector  Start MCP Inspector for interactive testing"
	@echo "  lint             Run linting with ruff and mypy"
	@echo "  format           Format code with ruff"
	@echo "  format-check     Check code formatting with ruff"
	@echo "  type-check       Run type checking with mypy"
	@echo "  debug-search     Debug concept search functionality"
	@echo "  check-all        Run all checks (lint, format, type-check, test)"
	@echo "  clean            Clean build artifacts"
	@echo "  build            Build package"
	@echo "  publish          Publish to PyPI"
	@echo "  run              Start HTTP MCP server (default)"
	@echo "  run-stdio        Start stdio MCP server"
	@echo "  docker-build     Build Docker image"
	@echo "  docker-run       Run MCP server in Docker"
	@echo "  docker-test      Test Docker image"
	@echo "  docker-clean     Clean Docker images"

# Development setup
install:
	poetry install
	poetry run pre-commit install

# Testing
test:
	poetry run pytest

test-unit:
	poetry run pytest tests/unit/ -v

test-integration:
	poetry run pytest tests/integration/ -v

test-cov:
	poetry run pytest --cov=src --cov-report=html --cov-report=term-missing

test-all:
	poetry run pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

test-mcp-inspector:
	@echo "Starting MCP Inspector for interactive testing..."
	@echo "This will open a web interface for testing the MCP server"
	WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI WEBAPI_SOURCE_KEY=EUNOMIA mcp-inspector poetry run ohdsi-webapi-mcp

# Code quality
lint:
	poetry run ruff check src tests scripts
# 	poetry run mypy src --show-error-codes

format:
	poetry run ruff format src tests scripts
	poetry run ruff check --fix src tests scripts

format-check:
	poetry run ruff format --check src tests scripts
	poetry run ruff check src tests scripts

type-check:
	poetry run mypy src

# Debug helpers
debug-search:
	poetry run python scripts/debug_search.py

# Combined checks
check-all: lint format-check type-check test

# MCP Server
run:
	@echo "Starting HTTP MCP server..."
	@echo "Configure settings in .env file or set environment variables"
	poetry run python -m ohdsi_webapi_mcp.http_server

run-stdio:
	@echo "Starting stdio MCP server..."
	@echo "Configure settings in .env file or set environment variables"
	poetry run python -m ohdsi_webapi_mcp.server

# Build and publish
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

build: clean
	poetry build

publish: build
	poetry publish

# Development helpers
fix:
	poetry run ruff format src tests scripts
	poetry run ruff check --fix src tests scripts

# Install in development mode
dev-install:
	poetry install
	poetry run pip install -e .

# Pre-commit setup
pre-commit-install:
	poetry run pre-commit install

pre-commit-run:
	poetry run pre-commit run --all-files

# Docker commands
docker-build:
	./docker.sh build

docker-run:
	./docker.sh run

docker-test:
	./docker.sh test

docker-clean:
	./docker.sh clean

docker-compose:
	./docker.sh compose
