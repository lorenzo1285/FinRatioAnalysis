"""
Tests for momentum method (12-1 month cross-sectional price momentum factor).
"""
import pytest
import pandas as pd
import numpy as np


class TestMomentum:
    """Test 12-1 month price momentum calculation."""

    def test_momentum_returns_dataframe(self, analyzer):
        """momentum() must return a DataFrame."""
        result = analyzer.momentum()
        assert isinstance(result, pd.DataFrame)

    def test_momentum_has_expected_columns(self, analyzer):
        """Result must contain Symbol and momentum_12_1."""
        result = analyzer.momentum()
        assert 'Symbol' in result.columns
        assert 'momentum_12_1' in result.columns

    def test_momentum_is_single_row(self, analyzer):
        """Result must be a single-row summary (not a time series)."""
        result = analyzer.momentum()
        assert len(result) == 1

    def test_momentum_12_1_is_numeric(self, analyzer):
        """momentum_12_1 must be a finite float."""
        result = analyzer.momentum()
        value = result['momentum_12_1'].iloc[0]
        assert isinstance(value, float)
        assert np.isfinite(value)

    def test_momentum_symbol_matches_ticker(self, analyzer):
        """Symbol column must match the initialized ticker."""
        result = analyzer.momentum()
        assert result['Symbol'].iloc[0] == 'AAPL'

    def test_momentum_excludes_last_month(self, analyzer):
        """
        12-1 momentum skips the most recent 21 trading days.
        Verify the computed value equals (close[-22] / close[-273]) - 1.
        """
        result = analyzer.momentum()
        close = analyzer.close

        skip = 21
        lookback = 252
        expected = (float(close.iloc[-(skip + 1)]) / float(close.iloc[-(lookback + skip + 1)])) - 1

        assert abs(result['momentum_12_1'].iloc[0] - round(expected, 4)) < 1e-6

    def test_momentum_returns_nan_when_insufficient_history(self, analyzer):
        """Returns NaN when price history is shorter than 273 trading days."""
        # Replace the instance attribute directly with a short series
        analyzer.close = analyzer.close.iloc[-100:]

        result = analyzer.momentum()
        assert pd.isna(result['momentum_12_1'].iloc[0])
