"""
T015: Contract validation tests for all MCP tools.

Loads each contract from specs/001-mcp-server/contracts/*.json and validates
that the corresponding tool's response conforms to the output schema.

This test MUST be written BEFORE tool implementation (TDD) and should FAIL
until the tools are implemented.
"""

import json
import pytest
from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch

try:
    from jsonschema import validate, ValidationError
except ImportError:
    pytest.skip("jsonschema not installed; run: pip install jsonschema", allow_module_level=True)

from finratioanalysis_mcp.server import mcp


# Discover all contract files
CONTRACTS_DIR = Path(__file__).parent.parent / "specs" / "001-mcp-server" / "contracts"
CONTRACT_FILES = sorted(CONTRACTS_DIR.glob("*.json"))


def load_contract(contract_path: Path) -> Dict[str, Any]:
    """Load a contract JSON file."""
    with open(contract_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.parametrize("contract_file", CONTRACT_FILES, ids=[f.stem for f in CONTRACT_FILES])
def test_tool_contract_compliance(contract_file: Path, mock_finratioanalysis):
    """
    Validate that each tool's response conforms to its contract output schema.
    
    This test:
    1. Loads the contract JSON
    2. Uses schema-backed mock from conftest.py
    3. Invokes the tool by name
    4. Validates the response against the output schema
    """
    contract = load_contract(contract_file)
    tool_name = contract["name"]
    output_schema = contract["output"]
    
    # Try to get the tool function from the global namespace
    # Tools are registered as @mcp.tool() decorators, which makes them
    # importable from finratioanalysis_mcp.tools
    # This will fail with ImportError until tools are implemented (expected for TDD)
    try:
        # Import the tools module to trigger registration
        import finratioanalysis_mcp.tools  # noqa: F401
    except (ImportError, ModuleNotFoundError):
        pytest.fail(
            f"Cannot import finratioanalysis_mcp.tools module. "
            f"Implement T016-T026 first."
        )
    
    # The tool should be registered in the mcp instance after import
    # FastMCP tools are accessible via the decorated functions
    # For now, we'll check if we can import and call it
    # The actual tool function names match the contract names
    tool_module = f"finratioanalysis_mcp.tools.{tool_name.replace('finratio_', '')}"
    
    try:
        __import__(tool_module)
    except (ImportError, ModuleNotFoundError):
        pytest.fail(
            f"Tool module {tool_module} not found. "
            f"Implement {tool_name} (T016-T025)."
        )
    
    # At this point, if the tool exists, it's been registered via @mcp.tool()
    # We need to find and call it
    # For testing purposes, we'll directly call the tool function
    # which should be the decorated function
    
    # Mock the library and call via the server's dispatcher
    with patch("finratioanalysis_mcp.server.FinRatioAnalysis") as MockClass:
        MockClass.return_value = mock_finratioanalysis
        
        # Import the specific tool module and get its tool function
        import importlib
        tool_mod = importlib.import_module(tool_module)
        
        # The tool function name is the same as the contract name
        if not hasattr(tool_mod, tool_name):
            pytest.fail(
                f"Module {tool_module} exists but doesn't export function {tool_name}"
            )
        
        tool_fn = getattr(tool_mod, tool_name)
        
        # Call the tool function directly
        response = tool_fn(ticker="AAPL", freq="yearly", response_format="json")
    
    # Validate response against contract output schema
    try:
        validate(instance=response, schema=output_schema)
    except ValidationError as e:
        pytest.fail(
            f"Tool {tool_name} response does not match contract schema.\n"
            f"Validation error: {e.message}\n"
            f"Response: {json.dumps(response, indent=2)}"
        )
    
    # Additional assertions for success responses
    if "data" in response:
        # Success response
        data = response["data"]
        
        # Period-rows tools should return a list
        if isinstance(data, list):
            assert len(data) > 0, f"{tool_name} returned empty data list"
            # Check date field in first row
            if data:
                assert "date" in data[0], f"{tool_name} period rows missing 'date' field"
        
        # Snapshot tools should return a dict
        elif isinstance(data, dict):
            assert "Symbol" in data, f"{tool_name} snapshot missing 'Symbol' field"
    
    elif "code" in response:
        # Error response - should not happen with mocked data
        pytest.fail(
            f"Tool {tool_name} returned error with mocked data: "
            f"{response['code']}: {response['message']}"
        )


def test_all_contracts_discovered():
    """Sanity check: verify we found the expected contract files."""
    expected_tools = [
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
        "finratio_company_snapshot",
    ]
    
    discovered = [f.stem for f in CONTRACT_FILES]
    
    for tool in expected_tools:
        assert tool in discovered, f"Missing contract file for {tool}"
    
    assert len(discovered) == len(expected_tools), (
        f"Expected {len(expected_tools)} contracts, found {len(discovered)}"
    )
