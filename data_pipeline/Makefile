.PHONY: help setup install clean test lint format run init

# Default Python interpreter
PYTHON := python3
PIP := $(PYTHON) -m pip
VENV := venv

help:
	@echo "Financial Data ELT Pipeline - Make Commands"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make setup      - Create virtual environment and install dependencies"
	@echo "  make install    - Install dependencies only"
	@echo ""
	@echo "Database Commands:"
	@echo "  make init-db    - Initialize database tables"
	@echo ""
	@echo "Pipeline Commands:"
	@echo "  make run        - Run full ELT pipeline"
	@echo "  make run-qb     - Run QuickBooks pipeline only"
	@echo "  make run-rf     - Run Rootfi pipeline only"
	@echo ""
	@echo "Testing Commands:"
	@echo "  make test       - Run all tests"
	@echo "  make test-unit  - Run unit tests only"
	@echo "  make coverage   - Run tests with coverage report"
	@echo ""
	@echo "Code Quality Commands:"
	@echo "  make lint       - Run linters (flake8, mypy)"
	@echo "  make format     - Format code with black and isort"
	@echo "  make check      - Run format check without modifying files"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make clean      - Remove generated files and cache"
	@echo "  make logs       - View pipeline logs"

setup:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	@echo "Installing dependencies..."
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt
	@echo ""
	@echo "✓ Setup complete!"
	@echo "Activate virtual environment: source $(VENV)/bin/activate"
	@echo "Configure database: cp .env.example .env (then edit .env)"

install:
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "✓ Dependencies installed"

init-db:
	@echo "Initializing database..."
	$(PYTHON) main.py init
	@echo "✓ Database initialized"

run:
	@echo "Running full ELT pipeline..."
	$(PYTHON) main.py run

run-qb:
	@echo "Running QuickBooks pipeline..."
	$(PYTHON) main.py run --source quickbooks

run-rf:
	@echo "Running Rootfi pipeline..."
	$(PYTHON) main.py run --source rootfi

test:
	@echo "Running all tests..."
	$(PYTHON) -m pytest tests/ -v

test-unit:
	@echo "Running unit tests..."
	$(PYTHON) -m pytest tests/unit/ -v

coverage:
	@echo "Running tests with coverage..."
	$(PYTHON) -m pytest tests/ --cov=src --cov-report=html --cov-report=term
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	@echo "Running flake8..."
	$(PYTHON) -m flake8 src/ tests/ --max-line-length=100 --extend-ignore=E203,W503
	@echo "Running mypy..."
	$(PYTHON) -m mypy src/ --ignore-missing-imports

format:
	@echo "Formatting code with black..."
	$(PYTHON) -m black src/ tests/ main.py
	@echo "Sorting imports with isort..."
	$(PYTHON) -m isort src/ tests/ main.py
	@echo "✓ Code formatted"

check:
	@echo "Checking code format..."
	$(PYTHON) -m black --check src/ tests/ main.py
	$(PYTHON) -m isort --check-only src/ tests/ main.py

clean:
	@echo "Cleaning generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	rm -rf .dlt/
	@echo "✓ Cleanup complete"

logs:
	@echo "Recent pipeline logs:"
	@tail -n 50 logs/pipeline.log 2>/dev/null || echo "No logs found. Run the pipeline first."

.DEFAULT_GOAL := help
