.PHONY: install test clean lint format docs build upload

# Variables
PYTHON := python3
PIP := pip3
PACKAGE_NAME := csv-cdc

# Installation
install:
	$(PIP) install -r requirements.txt
	$(PYTHON) setup.py install

install-dev:
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-cov flake8 black isort mypy
	$(PYTHON) setup.py develop

# Testing
test:
	pytest tests/ -v

test-coverage:
	pytest tests/ --cov=csvcdc --cov-report=html --cov-report=term

test-all:
	pytest tests/ -v --tb=long

# Code Quality
lint:
	flake8 csvcdc.py tests/ examples/
	mypy csvcdc.py

format:
	black csvcdc.py tests/ examples/
	isort csvcdc.py tests/ examples/

format-check:
	black --check csvcdc.py tests/ examples/
	isort --check-only csvcdc.py tests/ examples/

# Documentation
docs:
	@echo "Generating documentation..."
	@echo "API documentation: docs/API.md"
	@echo "Examples: docs/EXAMPLES.md"

# Building
build:
	$(PYTHON) setup.py sdist bdist_wheel

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# Upload to PyPI (requires proper credentials)
upload-test:
	twine upload --repository testpypi dist/*

upload:
	twine upload dist/*

# Development helpers
run-examples:
	cd examples && $(PYTHON) basic_example.py
	cd examples && $(PYTHON) advanced_example.py

check-deps:
	$(PIP) list --outdated

security-check:
	safety check

# CI/CD helpers
ci-install:
	$(PIP) install -r requirements.txt
	$(PIP) install pytest pytest-cov

ci-test:
	pytest tests/ --cov=csvcdc --cov-report=xml

# Performance testing
perf-test:
	@echo "Running performance tests..."
	$(PYTHON) -c "
import time
import tempfile
import os
from csvcdc import CSVCDC

# Generate test data
with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f1, \
     tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f2:
    
    # Write 10k rows
    f1.write('id,name,value\n')
    f2.write('id,name,value\n')
    
    for i in range(10000):
        f1.write(f'{i},Item_{i},{i*10}\n')
        f2.write(f'{i},Item_{i},{i*11}\n')  # Different values
    
    f1.flush()
    f2.flush()
    
    # Test performance
    start = time.time()
    cdc = CSVCDC(primary_key=[0], progressbar=0)
    result = cdc.compare(f1.name, f2.name)
    end = time.time()
    
    print(f'Processed 10k rows in {end-start:.2f} seconds')
    print(f'Found {len(result.modifications)} modifications')
    
    # Cleanup
    os.unlink(f1.name)
    os.unlink(f2.name)
"

# Help
help:
	@echo "Available targets:"
	@echo "  install        - Install the package"
	@echo "  install-dev    - Install in development mode with dev dependencies"
	@echo "  test          - Run tests"
	@echo "  test-coverage - Run tests with coverage report"
	@echo "  lint          - Run code linting"
	@echo "  format        - Format code with black and isort"
	@echo "  build         - Build distribution packages"
	@echo "  clean         - Clean build artifacts"
	@echo "  run-examples  - Run example scripts"
	@echo "  perf-test     - Run performance test"
	@echo "  help          - Show this help message"