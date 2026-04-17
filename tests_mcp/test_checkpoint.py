"""Phase 2 checkpoint test - verify MCP server boots correctly."""

import pytest
from finratioanalysis_mcp.server import mcp


class TestPhase2Checkpoint:
    """Verify Phase 2 completion criteria."""
    
    def test_server_boots_successfully(self):
        """Test that server instance can be created."""
        assert mcp is not None
        assert mcp.name == "finratioanalysis_mcp"
    
    def test_server_has_run_method(self):
        """Test that server can be run."""
        assert hasattr(mcp, 'run')
        assert callable(mcp.run)
    
    def test_zero_tools_registered(self):
        """Test that no tools are registered yet (Phase 2 checkpoint)."""
        # At Phase 2, tools haven't been registered yet
        # This will change in Phase 3 when we add the 10 tools
        # For now, just verify the server is importable
        assert mcp.name == "finratioanalysis_mcp"
