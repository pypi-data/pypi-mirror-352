# Contributing to CSV CDC

Thank you for your interest in contributing to CSV CDC! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Release Process](#release-process)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

### Our Standards

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Development Setup

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/maurohkcba/csv-cdc.git
   cd csv-cdc
   ```

2. **Set up development environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install in development mode
   make install-dev
   
   # Or manually:
   pip install -r requirements.txt
   pip install pytest pytest-cov flake8 black isort mypy pre-commit
   python setup.py develop
   ```

3. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

4. **Verify setup**
   ```bash
   # Run tests
   make test
   
   # Run linting
   make lint
   
   # Run examples
   make run-examples
   ```

## Making Changes

### Branching Strategy

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/feature-name`: New features
- `bugfix/issue-description`: Bug fixes
- `hotfix/critical-fix`: Critical production fixes

### Creating a Feature Branch

```bash
# Update your fork
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
```

### Coding Standards

1. **Code Style**
   - Use Black for code formatting
   - Follow PEP 8 guidelines
   - Use type hints where possible
   - Maximum line length: 88 characters

2. **Code Quality**
   ```bash
   # Format code
   make format
   
   # Check formatting
   make format-check
   
   # Run linting
   make lint
   ```

3. **Documentation**
   - Add docstrings to all public functions and classes
   - Update README.md if adding new features
   - Add examples for new functionality

### Commit Messages

Use conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(api): add support for custom separators
fix(parser): handle malformed CSV files gracefully
docs(readme): add performance benchmarks section
test(core): add tests for composite primary keys
```

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run specific test file
pytest tests/test_csvcdc.py -v

# Run specific test
pytest tests/test_csvcdc.py::TestCSVCDC::test_basic_comparison -v
```

### Writing Tests

1. **Test Structure**
   ```python
   def test_feature_name(self):
       """Test description"""
       # Arrange
       setup_data()
       
       # Act
       result = perform_action()
       
       # Assert
       assert expected_result == result
   ```

2. **Test Categories**
   - Unit tests: Test individual functions/methods
   - Integration tests: Test component interactions
   - Performance tests: Test speed and memory usage
   - Error handling tests: Test edge cases and errors

3. **Test Data**
   - Use fixtures for reusable test data
   - Create minimal test cases that focus on specific functionality
   - Test with various file sizes and formats

### Performance Testing

```bash
# Run performance tests
make perf-test

# Manual performance testing
python -c "
import time
from csvcdc import CSVCDC
# Your performance test code here
"
```

## Documentation

### API Documentation

- Add comprehensive docstrings to all public methods
- Include parameter types and return types
- Provide usage examples

```python
def compare(self, base_file: str, delta_file: str) -> CSVCDCResult:
    """Compare two CSV files and return differences.
    
    Args:
        base_file: Path to the base CSV file
        delta_file: Path to the delta CSV file
        
    Returns:
        CSVCDCResult containing additions, modifications, and deletions
        
    Raises:
        FileNotFoundError: If input files don't exist
        ValueError: If files have incompatible structures
        
    Example:
        >>> cdc = CSVCDC(primary_key=[0])
        >>> result = cdc.compare('old.csv', 'new.csv')
        >>> print(f"Found {len(result.additions)} additions")
    """
```

### User Documentation

- Update README.md for new features
- Add examples to docs/EXAMPLES.md
- Update API documentation in docs/API.md

## Submitting Changes

### Pull Request Process

1. **Prepare your changes**
   ```bash
   # Ensure tests pass
   make test
   
   # Ensure code quality
   make lint
   make format-check
   
   # Update documentation
   # Add/update tests
   ```

2. **Create Pull Request**
   - Use the pull request template
   - Provide clear description of changes
   - Link related issues
   - Add screenshots/examples if applicable

3. **Review Process**
   - Address reviewer feedback
   - Keep discussions constructive
   - Update code as needed

### Pull Request Checklist

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] New tests added for new functionality
- [ ] No breaking changes (or clearly documented)
- [ ] Performance impact considered
- [ ] Security implications reviewed

## Release Process

### Version Numbering

We use Semantic Versioning (SemVer):
- `MAJOR.MINOR.PATCH`
- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes (backward compatible)

### Creating a Release

1. **Prepare release**
   ```bash
   # Update version in setup.py
   # Update CHANGELOG.md
   # Ensure all tests pass
   make test-all
   ```

2. **Create release branch**
   ```bash
   git checkout -b release/v1.1.0
   # Make final adjustments
   git commit -m "chore: prepare release v1.1.0"
   ```

3. **Merge and tag**
   ```bash
   # Create PR to main
   # After merge, create tag
   git tag -a v1.1.0 -m "Release version 1.1.0"
   git push origin v1.1.0
   ```

## Issue Reporting

### Bug Reports

Use the bug report template and include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Sample data (if possible)
- Environment details
- Error messages

### Feature Requests

Use the feature request template and include:
- Clear description of the desired feature
- Use case and motivation
- Possible implementation approaches
- Examples of how it would be used

## Development Tips

### Performance Considerations

- Profile code changes with large datasets
- Consider memory usage impact
- Use appropriate data structures
- Leverage vectorized operations

### Debugging

```bash
# Debug with verbose output
python csvcdc.py file1.csv file2.csv --progressbar 1

# Profile performance
python -m cProfile -o profile.stats csvcdc.py file1.csv file2.csv
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(10)"
```

### Testing with Large Files

```bash
# Generate large test files
python -c "
import csv
with open('large_test.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'name', 'value'])
    for i in range(100000):
        writer.writerow([i, f'Item_{i}', i * 10])
"
```

## Getting Help

- 📖 Read the documentation thoroughly
- 🐛 Search existing issues before creating new ones
- 💬 Use GitHub Discussions for questions
- 📧 Contact maintainers for sensitive issues

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- GitHub contributor graphs

Thank you for contributing to CSV CDC! 🎉