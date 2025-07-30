# Makefile for chaturbate-events project

.PHONY: format check lint typecheck ty-check all clean help test test-cov install quality pre-commit ci-check security docs build dev-setup validate-env

# Default target
all: format check typecheck ty-check

# Validate environment setup
validate-env:
	@echo "Validating environment..."
	@command -v uv >/dev/null 2>&1 || { echo "ERROR: uv is not installed. Please install it first."; exit 1; }
	@echo "Environment validation passed"

# Format code with ruff
format: validate-env
	@echo "Formatting code..."
	uv run ruff format
	@echo "Code formatting completed"

# Check and fix code with ruff
check: validate-env
	@echo "Running ruff checks with auto-fix..."
	uv run ruff check --fix
	@echo "Ruff checks completed"

# Run mypy type checking
typecheck: validate-env
	@echo "Running mypy type checking..."
	uv run mypy ./
	@echo "Type checking completed"

# Run ty type checking
ty-check: validate-env
	@echo "Running ty type checking..."
	uv run ty check
	@echo "Ty type checking completed"

# Run linting only (without fixes)
lint: validate-env
	@echo "Running ruff lint check..."
	uv run ruff check

# Run all quality checks in sequence
quality: format check typecheck ty-check
	@echo "All quality checks completed successfully"

# CI-friendly check (no auto-fixes)
ci-check: validate-env
	@echo "Running CI checks..."
	@echo "Checking code formatting..."
	uv run ruff format --check
	@echo "Running linting..."
	uv run ruff check
	@echo "Running type checking..."
	uv run mypy ./
	@echo "Running ty checks..."
	uv run ty check
	@echo "Running tests..."
	uv run pytest
	@echo "All CI checks passed"

# Security scanning
security: validate-env
	@echo "Running security checks..."
	uv run pip-audit || echo "WARNING: pip-audit not available, skipping security scan"
	@echo "Checking for hardcoded secrets..."
	@grep -r "password\|secret\|key\|token" src/ examples/ tests/ --include="*.py" || echo "No obvious secrets found"

# Clean up cache files
clean:
	@echo "Cleaning up cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf htmlcov/ .coverage 2>/dev/null || true
	rm -rf dist/ build/ *.egg-info/ 2>/dev/null || true
	@echo "Cleanup completed"

# Run tests
test: validate-env
	@echo "Running tests..."
	uv run pytest

# Run tests with coverage
test-cov: validate-env
	@echo "Running tests with coverage..."
	uv run pytest --cov=src/chaturbate_events --cov-report=html --cov-report=term --cov-report=xml
	@echo "Coverage report generated in htmlcov/"

# Run specific test file
test-file: validate-env
	@if [ -z "$(FILE)" ]; then \
		echo "ERROR: Usage: make test-file FILE=test_filename.py"; \
		exit 1; \
	fi
	@echo "Running tests in $(FILE)..."
	uv run pytest tests/$(FILE) -v

# Run tests in watch mode (requires pytest-watch)
test-watch: validate-env
	@echo "Running tests in watch mode..."
	uv run ptw -- --cov=src/chaturbate_events

# Install dependencies
install: validate-env
	@echo "Installing dependencies..."
	uv sync
	@echo "Dependencies installed"

# Development setup
dev-setup: install
	@echo "Setting up development environment..."
	@echo "Installing pre-commit hooks..."
	@if command -v pre-commit >/dev/null 2>&1; then \
		pre-commit install; \
		echo "Pre-commit hooks installed"; \
	else \
		echo "WARNING: pre-commit not available, skipping hook installation"; \
	fi
	@echo "Development environment setup complete"

# Pre-commit hooks (if available)
pre-commit: validate-env
	@echo "Running pre-commit hooks..."
	@if command -v pre-commit >/dev/null 2>&1; then \
		pre-commit run --all-files; \
	else \
		echo "WARNING: pre-commit not installed, running manual checks..."; \
		$(MAKE) quality; \
	fi

# Build package
build: clean validate-env
	@echo "Building package..."
	uv build
	@echo "Package built successfully"

# Documentation generation (if docs exist)
docs: validate-env
	@echo "Generating documentation..."
	@if [ -d "docs" ]; then \
		uv run -m sphinx docs -T -E -a -j 1 -b html -D language=en docs/_build/html; \
		echo "Documentation generated in docs/_build/html"; \
		echo "Checking links in documentation..."; \
		uv run -m sphinx docs -b linkcheck docs/_build/linkcheck; \
		if [ -d "docs/_build/linkcheck" ]; then \
			echo "Link check completed, see docs/_build/linkcheck for results"; \
		else \
			echo "WARNING: Link check directory not found"; \
		fi; \
	else \
		echo "WARNING: No docs directory found, skipping documentation generation"; \
	fi
	
# Show help
help:
	@echo "Chaturbate Events - Available Makefile targets"
	@echo ""
	@echo "QUALITY & TESTING:"
	@echo "  all          - Run format, check, typecheck, and ty-check (default)"
	@echo "  quality      - Run all quality checks with status output"
	@echo "  ci-check     - Run CI-friendly checks (no auto-fixes)"
	@echo "  format       - Format code with ruff"
	@echo "  check        - Check and fix code with ruff"
	@echo "  lint         - Run ruff check without fixes"
	@echo "  typecheck    - Run mypy type checking"
	@echo "  ty-check     - Run ty type checking"
	@echo "  security     - Run security scans and checks"
	@echo ""
	@echo "TESTING:"
	@echo "  test         - Run tests with pytest"
	@echo "  test-cov     - Run tests with coverage report"
	@echo "  test-file    - Run specific test file (usage: make test-file FILE=test_file.py)"
	@echo "  test-watch   - Run tests in watch mode (requires pytest-watch)"
	@echo ""
	@echo "DEVELOPMENT:"
	@echo "  install      - Install dependencies with uv"
	@echo "  dev-setup    - Set up development environment with pre-commit hooks"
	@echo "  pre-commit   - Run pre-commit hooks on all files"
	@echo "  validate-env - Validate that required tools are installed"
	@echo ""
	@echo "BUILD:"
	@echo "  build        - Build the package"
	@echo "  docs         - Generate documentation"
	@echo ""
	@echo "MAINTENANCE:"
	@echo "  clean        - Remove cache files and build artifacts"
	@echo "  help         - Show this help message"
	@echo ""
	@echo "EXAMPLES:"
	@echo "  make quality                        # Run all quality checks"
	@echo "  make test-file FILE=test_client.py  # Test specific file"
