# Contributing to FinRatioAnalysis

Thank you for your interest in contributing to FinRatioAnalysis! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Running Tests](#running-tests)
- [Submitting Changes](#submitting-changes)
- [Style Guidelines](#style-guidelines)

## Code of Conduct

This project follows standard open-source community guidelines. Please be respectful and constructive in all interactions.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- A clear, descriptive title
- Detailed steps to reproduce the issue
- Expected vs. actual behavior
- Your environment (Python version, OS, package version)
- Sample code that demonstrates the problem

**Example:**
```markdown
**Bug**: Historical valuation metrics returns empty DataFrame for ticker XYZ

**Steps to reproduce:**
1. Install FinRatioAnalysis 0.2.1
2. Run: `analyzer = FinRatioAnalysis('XYZ', freq='yearly')`
3. Run: `analyzer.historical_valuation_metrics()`

**Expected**: DataFrame with P/E, EV/EBITDA, FCF Yield
**Actual**: Empty DataFrame

**Environment**: Python 3.11, Windows 11, FinRatioAnalysis 0.2.1
```

### Suggesting Features

Feature suggestions are welcome! Please provide:

- Clear use case and benefit
- Example of how the feature would work
- Any relevant research or references

### Contributing Code

We welcome pull requests for:

- Bug fixes
- New financial ratios or metrics
- Performance improvements
- Documentation improvements
- Test coverage expansion
- MCP server enhancements

## Development Setup

### Prerequisites

- Python 3.10 or higher
- Git
- Virtual environment tool (venv, virtualenv, or uv)

### Setup Instructions

1. **Fork and clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/FinRatioAnalysis.git
cd FinRatioAnalysis
```

2. **Create a virtual environment**

```bash
# Using venv
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Or using uv (faster)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**

```bash
# Install in editable mode with MCP extras
pip install -e ".[mcp]"

# Or using uv
uv pip install -e ".[mcp]"

# Install development dependencies
pip install pytest pytest-mock jsonschema build twine
```

4. **Verify installation**

```bash
# Test the library
python -c "from FinRatioAnalysis import FinRatioAnalysis; print('Library OK')"

# Test the MCP server
python -m finratioanalysis_mcp --help
```

## Running Tests

### Run All Tests

```bash
# Full test suite (library + MCP server)
pytest

# With verbose output
pytest -v

# With coverage report
pytest --cov=FinRatioAnalysis --cov=finratioanalysis_mcp
```

### Run Specific Test Suites

```bash
# Library tests only
pytest tests/

# MCP server tests only
pytest tests_mcp/

# Specific test file
pytest tests/test_return_ratios.py

# Integration tests (uses real Yahoo Finance data)
pytest -m integration

# Specific test function
pytest tests/test_return_ratios.py::test_roic_calculation
```

### Test Guidelines

- All new features should include tests
- Aim for >80% code coverage
- Use fixtures from `tests/fixtures/` and `tests_mcp/fixtures/`
- Mock external API calls in unit tests
- Mark integration tests with `@pytest.mark.integration`

## Submitting Changes

### Pull Request Process

1. **Create a feature branch**

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-number-description
```

2. **Make your changes**

- Write clear, documented code
- Follow the existing code style
- Add tests for new functionality
- Update documentation if needed

3. **Test your changes**

```bash
# Run all tests
pytest

# Check code style (if using linters)
flake8 FinRatioAnalysis/ finratioanalysis_mcp/
```

4. **Commit your changes**

```bash
git add .
git commit -m "feat: add new liquidity ratio XYZ"
# or
git commit -m "fix: correct ROIC calculation for banks"
```

Use conventional commit messages:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions/changes
- `refactor:` - Code refactoring
- `perf:` - Performance improvements

5. **Push and create PR**

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title describing the change
- Description of what changed and why
- Reference any related issues (`Fixes #123`)
- Screenshots/examples if applicable

6. **Wait for review**

- Maintainers will review your PR
- Address any requested changes
- Once approved, your PR will be merged!

## Style Guidelines

### Python Code Style

- Follow PEP 8 conventions
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use docstrings for public methods

**Example:**

```python
def calculate_roic(self, net_income: float, invested_capital: float) -> float:
    """
    Calculate Return on Invested Capital.
    
    Args:
        net_income: Net income from operations
        invested_capital: Total invested capital (debt + equity - cash)
    
    Returns:
        ROIC as a percentage
    
    Raises:
        ValueError: If invested_capital is zero
    """
    if invested_capital == 0:
        raise ValueError("Invested capital cannot be zero")
    return (net_income / invested_capital) * 100
```

### Documentation Style

- Use clear, concise language
- Include code examples for new features
- Update README.md if adding major features
- Keep CHANGELOG.md up to date

### MCP Server Guidelines

If contributing to the MCP server (`finratioanalysis_mcp/`):

- All tools must return structured data (Pydantic models)
- Support both JSON and Markdown output formats
- Include error handling (no stack traces to clients)
- Add contract tests in `tests_mcp/test_tool_contracts.py`
- Update schema snapshots if needed

## Project Structure

```
FinRatioAnalysis/
├── FinRatioAnalysis/          # Core library
│   ├── __init__.py
│   └── FinRatioAnalysis.py    # Main analyzer class
├── finratioanalysis_mcp/      # MCP server
│   ├── __init__.py
│   ├── server.py              # MCP server implementation
│   ├── models.py              # Pydantic models
│   ├── adapters.py            # Library-to-MCP adapters
│   └── tools/                 # Individual MCP tools
├── tests/                     # Library tests
├── tests_mcp/                 # MCP server tests
├── example/                   # Example notebooks
├── specs/                     # Specifications and docs
└── pyproject.toml             # Package configuration
```

## Questions?

- **General questions**: Open a [GitHub Discussion](https://github.com/lorenzo1285/FinRatioAnalysis/discussions)
- **Bugs**: Open an [Issue](https://github.com/lorenzo1285/FinRatioAnalysis/issues)
- **Security issues**: Email lorenzo_cardenas@msn.com

## License

By contributing to FinRatioAnalysis, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
