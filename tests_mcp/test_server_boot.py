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
