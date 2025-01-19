"""Unit tests for utility functions."""
import json
import pytest
from playwright_mcp.browser_daemon.tools.handlers.utils import create_response
from mcp.types import TextContent


def test_create_response_with_string():
    """Test create_response with a string input."""
    result = create_response("test message")
    assert result["isError"] is False
    assert len(result["content"]) == 1
    assert isinstance(result["content"][0], TextContent)
    assert result["content"][0].type == "text"
    assert result["content"][0].text == "test message"


def test_create_response_with_dict():
    """Test create_response with a dictionary input."""
    test_dict = {"key": "value", "nested": {"inner": "data"}}
    result = create_response(test_dict)
    
    # Verify response structure
    assert result["isError"] is False
    assert len(result["content"]) == 1
    assert isinstance(result["content"][0], TextContent)
    assert result["content"][0].type == "text"
    
    # Convert single quotes to double quotes for JSON parsing
    json_str = result["content"][0].text.replace("'", '"')
    parsed = json.loads(json_str)

    # Verify the parsed dictionary matches the original
    assert parsed == test_dict
    assert parsed["key"] == "value"
    assert parsed["nested"]["inner"] == "data"


def test_create_response_with_error():
    """Test create_response with error flag set."""
    result = create_response("error message", is_error=True)
    assert result["isError"] is True
    assert len(result["content"]) == 1
    assert isinstance(result["content"][0], TextContent)
    assert result["content"][0].type == "text"
    assert result["content"][0].text == "error message"


def test_create_response_with_non_string_non_dict():
    """Test create_response with other types (should convert to string)."""
    result = create_response(123)
    assert result["isError"] is False
    assert len(result["content"]) == 1
    assert isinstance(result["content"][0], TextContent)
    assert result["content"][0].type == "text"
    assert result["content"][0].text == "123"


def test_create_response_with_empty_dict():
    """Test create_response with an empty dictionary."""
    result = create_response({})
    assert result["isError"] is False
    assert len(result["content"]) == 1
    assert isinstance(result["content"][0], TextContent)
    assert result["content"][0].type == "text"
    assert result["content"][0].text == "{}"


def test_create_response_with_none():
    """Test create_response with None input."""
    result = create_response(None)
    assert result["isError"] is False
    assert len(result["content"]) == 1
    assert isinstance(result["content"][0], TextContent)
    assert result["content"][0].type == "text"
    assert result["content"][0].text == "None" 