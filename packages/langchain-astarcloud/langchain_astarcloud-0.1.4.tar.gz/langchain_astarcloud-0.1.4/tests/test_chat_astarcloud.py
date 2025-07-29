"""Tests for ChatAstarCloud."""

import pytest
from unittest.mock import Mock, patch

from langchain_astarcloud import ChatAstarCloud
from langchain_core.messages import HumanMessage


def test_import():
    """Test that ChatAstarCloud can be imported."""
    assert ChatAstarCloud is not None


def test_init():
    """Test ChatAstarCloud initialization."""
    with patch('langchain_astarcloud.chat_astarcloud.AstarClient'), \
         patch('langchain_astarcloud.chat_astarcloud.AstarAsyncClient'):
        
        llm = ChatAstarCloud(model="gpt-4.1", api_key="test-key")
        
        assert llm.model == "gpt-4.1"
        assert llm._llm_type == "astarcloud"
        assert llm._identifying_params["model"] == "gpt-4.1"


def test_tool_model_validation():
    """Test that tool calling validation works correctly."""
    with patch('langchain_astarcloud.chat_astarcloud.AstarClient'), \
         patch('langchain_astarcloud.chat_astarcloud.AstarAsyncClient'):
        
        llm = ChatAstarCloud(model="unsupported-model")
        
        # Should raise ValueError for unsupported model with tools
        with pytest.raises(ValueError, match="does not support tool calling"):
            llm._build_payload([], tools=[{"type": "function"}])


def test_supported_tool_models():
    """Test that supported models don't raise errors with tools."""
    with patch('langchain_astarcloud.chat_astarcloud.AstarClient'), \
         patch('langchain_astarcloud.chat_astarcloud.AstarAsyncClient'):
        
        for model in ["gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "astar-gpt-4.1"]:
            llm = ChatAstarCloud(model=model)
            
            # Should not raise error
            payload = llm._build_payload([], tools=[{"type": "function"}])
            assert payload["model"] == model 