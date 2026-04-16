"""Unit tests for server boot and basic functionality."""

import pytest
from finratioanalysis_mcp.server import mcp, main


class TestServerBoot:
    """Tests for server initialization and boot."""
    
    def test_mcp_instance_exists(self):
        """Test that FastMCP instance is created."""
        assert mcp is not None
    
    def test_mcp_instance_name(self):
        """Test that FastMCP instance has correct name."""
        assert mcp.name == "finratioanalysis_mcp"
    
    def test_main_function_exists(self):
        """Test that main() function is callable."""
        assert callable(main)
    
    def test_main_function_signature(self):
        """Test that main() has correct signature."""
        import inspect
        sig = inspect.signature(main)
        
        # main() should have no required parameters
        assert len(sig.parameters) == 0
    
    def test_server_import_succeeds(self):
        """Test that server module can be imported without errors."""
        # This test passes if the import at the top succeeded
        from finratioanalysis_mcp import server
        assert hasattr(server, 'mcp')
        assert hasattr(server, 'main')
        assert hasattr(server, '_call_library')

    def test_tools_registered_on_server_import(self):
        """Importing only the server module must register all 10 US1 tools.

        Guards against a regression where tool registration depended on a
        side-effect import in test files instead of the server boot path —
        which would leave MCP Inspector showing zero tools in production.
        """
        import asyncio

        tools = asyncio.run(mcp.list_tools())
        names = {t.name for t in tools}

        expected = {
            "finratio_return_ratios",
            "finratio_efficiency_ratios",
            "finratio_leverage_ratios",
            "finratio_liquidity_ratios",
            "finratio_ccc",
            "finratio_historical_valuation_metrics",
            "finratio_valuation_growth_metrics",
            "finratio_z_score",
            "finratio_capm",
            "finratio_wacc",
        }
        assert names == expected, f"Tool registry mismatch: {names ^ expected}"
