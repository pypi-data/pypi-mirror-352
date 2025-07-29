import pytest
from unittest.mock import patch, MagicMock
from AstarCloud import AstarClient, ToolSpec
from AstarCloud._exceptions import AuthenticationError


def test_tool_capability_gate():
    """Test that tools are rejected for unsupported models"""
    client = AstarClient(api_key="test")
    
    tool = ToolSpec(function={"name": "test_tool", "parameters": {}})
    
    with pytest.raises(ValueError, 
                       match="Model 'unsupported-model' cannot accept tools"):
        client.create.completion(
            messages=[{"role": "user", "content": "hello"}],
            model="unsupported-model",
            tools=[tool]
        )


def test_bind_tools():
    """Test that bind_tools creates a client with bound tools"""
    client = AstarClient(api_key="test")
    tool = ToolSpec(function={"name": "test_tool", "parameters": {}})
    
    bound_client = client.bind_tools([tool])
    
    # Check that the bound client has the tools
    assert bound_client._tools == [tool]
    assert bound_client._tool_choice == "auto"


def test_supported_tool_models():
    """Test that supported models accept tools"""
    client = AstarClient(api_key="test")
    
    tool = ToolSpec(function={"name": "test_tool", "parameters": {}})
    
    # Mock the HTTP client to avoid actual network calls
    with patch.object(client._http, 'post') as mock_post:
        mock_post.return_value = {
            "id": "test-id",
            "created": 1234567890,
            "model": "gpt-4.1",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": "Hello"},
                "finish_reason": "stop"
            }]
        }
        
        # Should not raise an error for supported models
        client.create.completion(
            messages=[{"role": "user", "content": "hello"}],
            model="gpt-4.1",
            tools=[tool]
        )
        
        # Verify the request was made
        mock_post.assert_called_once()


@patch('httpx.Client')
def test_auth_failure(mock_client):
    """Test authentication failure"""
    # Set up the mock response
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    
    mock_client_instance = MagicMock()
    mock_client_instance.post.return_value = mock_response
    mock_client.return_value = mock_client_instance
    
    client = AstarClient(api_key="bad")
    
    with pytest.raises(AuthenticationError):
        client.create.completion(
            messages=[{"role": "user", "content": "hello"}], 
            model="gpt-4.1"
        )
