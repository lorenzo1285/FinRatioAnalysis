"""Unit tests for adapters module."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from finratioanalysis_mcp.adapters import (
    df_to_period_rows,
    df_to_snapshot,
    to_markdown_table,
    to_markdown_kv,
)


class TestDfToPeriodRows:
    """Tests for df_to_period_rows function."""
    
    def test_basic_conversion(self):
        """Test basic DataFrame to period rows conversion."""
        dates = pd.to_datetime(['2023-01-01', '2024-01-01'])
        df = pd.DataFrame({'ROE': [0.15, 0.18], 'ROA': [0.08, 0.09]}, index=dates)
        
        result = df_to_period_rows(df)
        
        assert len(result) == 2
        assert result[0]['date'] == '2023-01-01'
        assert result[0]['ROE'] == 0.15
        assert result[0]['ROA'] == 0.08
        assert result[1]['date'] == '2024-01-01'
        assert result[1]['ROE'] == 0.18
        assert result[1]['ROA'] == 0.09
    
    def test_iso8601_date_format(self):
        """Test that dates are formatted as ISO-8601."""
        dates = pd.to_datetime(['2023-06-15', '2024-12-31'])
        df = pd.DataFrame({'value': [1.0, 2.0]}, index=dates)
        
        result = df_to_period_rows(df)
        
        assert result[0]['date'] == '2023-06-15'
        assert result[1]['date'] == '2024-12-31'
    
    def test_nan_to_none_conversion(self):
        """Test that NaN values are converted to None."""
        dates = pd.to_datetime(['2023-01-01', '2024-01-01'])
        df = pd.DataFrame({'metric': [0.15, np.nan]}, index=dates)
        
        result = df_to_period_rows(df)
        
        assert result[0]['metric'] == 0.15
        assert result[1]['metric'] is None
    
    def test_column_preservation(self):
        """Test that all columns are preserved."""
        dates = pd.to_datetime(['2023-01-01'])
        df = pd.DataFrame({
            'col1': [1.0],
            'col2': [2.0],
            'col3': [3.0],
        }, index=dates)
        
        result = df_to_period_rows(df)
        
        assert set(result[0].keys()) == {'date', 'col1', 'col2', 'col3'}


class TestDfToSnapshot:
    """Tests for df_to_snapshot function."""
    
    def test_basic_conversion(self):
        """Test basic single-row DataFrame to dict conversion."""
        df = pd.DataFrame({
            'Symbol': ['AAPL'],
            'PE_Ratio': [28.5],
            'Beta': [1.2],
        })
        
        result = df_to_snapshot(df)
        
        assert result['Symbol'] == 'AAPL'
        assert result['PE_Ratio'] == 28.5
        assert result['Beta'] == 1.2
    
    def test_nan_to_none_conversion(self):
        """Test that NaN values are converted to None."""
        df = pd.DataFrame({
            'Symbol': ['AAPL'],
            'PE_Ratio': [28.5],
            'DividendYield': [np.nan],
        })
        
        result = df_to_snapshot(df)
        
        assert result['Symbol'] == 'AAPL'
        assert result['PE_Ratio'] == 28.5
        assert result['DividendYield'] is None
    
    def test_takes_first_row(self):
        """Test that function requires exactly one row."""
        df = pd.DataFrame({
            'Symbol': ['AAPL', 'MSFT'],
            'PE': [28.5, 32.0],
        })
        
        # Should raise ValueError for multiple rows
        with pytest.raises(ValueError, match="exactly 1 row"):
            df_to_snapshot(df)
    
    def test_mixed_types(self):
        """Test handling of mixed data types."""
        df = pd.DataFrame({
            'Symbol': ['AAPL'],
            'PE_Ratio': [28.5],
            'Zone': ['Safe'],
            'Count': [100],
        })
        
        result = df_to_snapshot(df)
        
        assert isinstance(result['Symbol'], str)
        assert isinstance(result['Zone'], str)
        assert isinstance(result['Count'], (int, np.integer))


class TestToMarkdownTable:
    """Tests for to_markdown_table function."""
    
    def test_basic_table(self):
        """Test basic Markdown table generation."""
        rows = [
            {'date': '2023-01-01', 'ROE': 0.15},
            {'date': '2024-01-01', 'ROE': 0.18},
        ]
        
        result = to_markdown_table(rows)
        
        assert '| date' in result
        assert '| ROE' in result
        assert '2023-01-01' in result
        assert '2024-01-01' in result
        assert '0.15' in result or '0.1500' in result
    
    def test_none_rendered_as_null(self):
        """Test that None values are rendered as 'null'."""
        rows = [
            {'date': '2023-01-01', 'value': 0.15},
            {'date': '2024-01-01', 'value': None},
        ]
        
        result = to_markdown_table(rows)
        
        assert 'null' in result
    
    def test_empty_data(self):
        """Test handling of empty data."""
        result = to_markdown_table([])
        
        assert 'No data available' in result
    
    def test_well_formed_table(self):
        """Test that table structure is well-formed."""
        rows = [{'col1': 1, 'col2': 2}]
        
        result = to_markdown_table(rows)
        
        lines = result.split('\n')
        assert len(lines) >= 3  # Header, separator, at least one data row
        assert all('|' in line for line in lines)


class TestToMarkdownKv:
    """Tests for to_markdown_kv function."""
    
    def test_basic_kv_list(self):
        """Test basic key-value list generation."""
        snapshot = {
            'Symbol': 'AAPL',
            'PE_Ratio': 28.5,
            'Beta': 1.2,
        }
        
        result = to_markdown_kv(snapshot)
        
        assert '**Symbol**' in result
        assert 'AAPL' in result
        assert '**PE_Ratio**' in result
        assert '28.5' in result or '28.50' in result
    
    def test_none_rendered_as_null(self):
        """Test that None values are rendered as 'null'."""
        snapshot = {
            'Symbol': 'AAPL',
            'Value': None,
        }
        
        result = to_markdown_kv(snapshot)
        
        assert 'null' in result
    
    def test_empty_data(self):
        """Test handling of empty data."""
        result = to_markdown_kv({})
        
        assert 'No data available' in result
    
    def test_bulleted_format(self):
        """Test that output uses bullet points."""
        snapshot = {'key': 'value'}
        
        result = to_markdown_kv(snapshot)
        
        assert result.startswith('- ')
