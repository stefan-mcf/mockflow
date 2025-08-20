# Contributing to MockFlow

Thank you for your interest in contributing to MockFlow! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git

### Setting up the development environment

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/mockflow.git
   cd mockflow
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

### Running Tests

Run the full test suite:
```bash
pytest tests/
```

Run tests with coverage:
```bash
pytest tests/ --cov=mockflow --cov-report=html
```

Run specific test categories:
```bash
pytest tests/ -m "contract"      # API contract tests
pytest tests/ -m "integration"   # Integration tests
pytest tests/ -m "not slow"      # Skip slow tests
```

### Code Quality

We use several tools to maintain code quality:

#### Linting
```bash
ruff check .                    # Check for issues
ruff check . --fix             # Fix auto-fixable issues
```

#### Code Formatting
```bash
ruff format .                   # Format code
ruff format . --check          # Check if formatting is needed
```

#### Type Checking
```bash
mypy mockflow                   # Type check the package
```

#### Run All Quality Checks
```bash
# Run all checks at once
ruff check . && ruff format . --check && mypy mockflow && pytest tests/
```

## Code Style Guidelines

### Python Code Style

- Follow PEP 8 style guidelines
- Use type hints for all function signatures
- Maximum line length: 88 characters
- Use descriptive variable and function names
- Add docstrings for all public functions and classes

### Example Function
```python
def generate_mock_data(
    symbol: str,
    timeframe: str,
    days: Optional[int] = None,
    scenario: str = "auto"
) -> pd.DataFrame:
    """Generate financial time series mock data.
    
    Args:
        symbol: Trading pair symbol identifier
        timeframe: Candle/bar timeframe for data generation
        days: Number of days of data to generate
        scenario: Market scenario pattern
        
    Returns:
        DataFrame with OHLCV columns and datetime index
        
    Raises:
        ValueError: If parameters are invalid
    """
    # Implementation here
```

### Documentation Style

- Use clear, concise language
- Provide examples for complex functions
- Update README.md for user-facing changes
- Update API_REFERENCE.md for API changes

## Testing Guidelines

### Test Structure

Tests are organized in the `tests/` directory:
- `test_api_contract.py` - API contract validation
- `test_core_functionality.py` - Core feature tests
- `test_volatility_validation.py` - Volatility model tests
- `test_drift_validation.py` - Trend/drift tests
- `test_anomaly_validation.py` - Edge case tests

### Writing Tests

- Use descriptive test names: `test_generate_data_with_bull_scenario`
- Test both happy path and error cases
- Use parametrized tests for multiple input combinations
- Mock external dependencies if needed

### Test Categories

Use pytest markers to categorize tests:
```python
import pytest

@pytest.mark.contract
def test_api_contract():
    """Test API contract compliance."""
    pass

@pytest.mark.integration
def test_integration_with_pandas():
    """Test integration with pandas."""
    pass

@pytest.mark.slow
def test_large_dataset_generation():
    """Test generation of large datasets."""
    pass
```

## Submitting Changes

### Pull Request Process

1. Create a feature branch from main:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them:
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

3. Run all quality checks:
   ```bash
   ruff check . && ruff format . --check && mypy mockflow && pytest tests/
   ```

4. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

5. Create a Pull Request on GitHub

### Commit Message Format

Use conventional commit format:
- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `test:` - Test additions/updates
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `chore:` - Maintenance tasks

Examples:
```
feat: add support for custom volatility models
fix: resolve OHLC validation edge case
docs: update API reference for new parameters
test: add integration tests for scenario generation
```

### Pull Request Guidelines

- Provide a clear description of changes
- Reference related issues if applicable
- Include tests for new functionality
- Update documentation as needed
- Ensure all CI checks pass

## Release Process

Releases are managed by maintainers:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create a GitHub release
4. Automated CI will publish to PyPI

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow GitHub's community guidelines

## Getting Help

- Open an issue for bug reports or feature requests
- Join discussions in GitHub Discussions
- Check existing issues and documentation first

## Recognition

Contributors will be recognized in:
- GitHub contributors list
- CHANGELOG.md for significant contributions
- Package metadata for major contributions

Thank you for contributing to MockFlow!