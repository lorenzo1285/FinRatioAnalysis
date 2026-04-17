# Testing Guide for FinRatioAnalysis

This project supports **two types of tests**:

## 🚀 Quick Start

### Run ALL tests (fast unit tests ONLY):
```bash
pytest
```

### Run integration tests (with REAL yfinance data):
```bash
pytest -m integration
```

### Run unit tests ONLY (skip integration):
```bash
pytest -m "not integration"
```

---

## 📋 Test Types

### 1. **Unit Tests** (Fast, No Network Required)
- Use **mocked/dummy data**
- Run in milliseconds
- No API rate limits
- Always consistent results
- **Files**: `test_initialization.py`, `test_return_ratios.py`, etc.

**Command**:
```bash
pytest -m "not integration"
```

### 2. **Integration Tests** (Real Data, Requires Network)
- Use **actual yfinance API calls**
- Validate against real market data
- Takes longer (30-60 seconds)
- Requires internet connection
- May fail if Yahoo Finance is down
- **File**: `test_integration_real_data.py`

**Command**:
```bash
pytest -m integration
```

---

## 🎯 Common Test Commands

```bash
# Run all tests (unit tests only by default)
pytest

# Run specific test file
pytest tests/test_return_ratios.py

# Run specific test function
pytest tests/test_integration_real_data.py::TestRealDataIntegration::test_real_return_ratios

# Run with verbose output
pytest -v

# Run with print statements visible
pytest -s

# Run and show detailed output for real data tests
pytest -m integration -v -s

# Run fast tests only (skip slow integration tests)
pytest -m "not slow"

# Generate coverage report
pytest --cov=FinRatioAnalysis --cov-report=html

# Run tests in parallel (requires pytest-xdist)
pytest -n auto
```

---

## 📊 Test Coverage

### Unit Tests Coverage:
- ✅ Initialization & validation
- ✅ Return ratios (ROE, ROA, ROCE, Margins)
- ✅ Leverage ratios
- ✅ Efficiency ratios
- ✅ Liquidity ratios
- ✅ Cash Conversion Cycle
- ✅ Altman Z-Score
- ✅ CAPM
- ✅ WACC

### Integration Tests Coverage:
- ✅ Real API initialization
- ✅ All ratio calculations with real data
- ✅ Multiple tickers (AAPL, MSFT, GOOGL, JPM)
- ✅ Quarterly vs Yearly frequency
- ✅ Error handling with invalid tickers

---

## 🔧 Writing New Tests

### For Unit Tests (Fast):
```python
def test_my_feature(analyzer):  # Uses mock_yfinance fixture
    """Test with mocked data."""
    result = analyzer.return_ratios()
    assert not result.empty
```

### For Integration Tests (Real Data):
```python
@pytest.mark.integration
@pytest.mark.slow
def test_my_feature_real(real_analyzer):  # Uses real yfinance
    """Test with real API data."""
    result = real_analyzer.return_ratios()
    assert not result.empty
    print(f"Real ROE: {result['ROE'].iloc[0]}")
```

---

## 🏃 CI/CD Recommendations

### Development Workflow:
```bash
# During development - fast feedback
pytest -m "not integration"

# Before committing - full validation
pytest -m integration
```

### CI Pipeline:
```yaml
# Fast CI (every commit)
- Run: pytest -m "not integration"

# Slow CI (nightly/weekly)
- Run: pytest -m integration
```

---

## 📦 Required Test Dependencies

Install with:
```bash
pip install pytest pytest-mock pytest-cov
```

Or if using the project:
```bash
pip install -e .[dev]  # If you add dev dependencies to setup.py
```

---

## 🐛 Troubleshooting

### Tests are too slow:
```bash
# Skip integration tests
pytest -m "not integration"
```

### Integration tests failing:
- Check internet connection
- Verify Yahoo Finance is accessible
- Try with a different ticker
- Check for API rate limiting

### Want to test a specific ticker:
```python
@pytest.mark.integration
def test_custom_ticker():
    from FinRatioAnalysis import FinRatioAnalysis
    analyzer = FinRatioAnalysis('YOUR_TICKER', 'yearly')
    result = analyzer.return_ratios()
    print(result)
```

---

## 💡 Best Practices

1. **Run unit tests frequently** during development (fast feedback)
2. **Run integration tests** before releases (validates real-world behavior)
3. **Use `-s` flag** when debugging to see print statements
4. **Use `-v` flag** for verbose output
5. **Mark slow tests** with `@pytest.mark.slow`
6. **Mark integration tests** with `@pytest.mark.integration`

---

## 📈 Example Output

### Unit Tests (Fast):
```
$ pytest -m "not integration"
===== test session starts =====
tests/test_return_ratios.py ✓✓✓✓        [100%]
===== 52 passed in 0.85s =====
```

### Integration Tests (Real Data):
```
$ pytest -m integration -s
===== test session starts =====
tests/test_integration_real_data.py::test_real_return_ratios
✓ Initialized AAPL - Market Cap: $3,456,789,012,345
✓ Return Ratios Retrieved:
                    2023-09-30  2022-09-30  2021-09-30
ROE                   1.5621      1.9698      1.5000
✓ PASSED
===== 12 passed in 45.32s =====
```
