import pytest
from unittest.mock import patch, MagicMock, mock_open
import os
from AstarCloud import AstarClient, ToolSpec
from AstarCloud._exceptions import AuthenticationError, APIError


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


class TestTranscription:
    """Test transcription functionality"""
    
    def test_transcribe_basic(self):
        """Test basic transcription"""
        client = AstarClient(api_key="test")
        
        # Mock file operations
        with patch('os.path.exists') as mock_exists, \
             patch('os.path.getsize') as mock_getsize, \
             patch('builtins.open', mock_open(read_data=b'fake audio data')), \
             patch.object(client._http, 'post_multipart') as mock_post:
            
            mock_exists.return_value = True
            mock_getsize.return_value = 1024 * 1024  # 1MB
            mock_post.return_value = {
                "text": "This is a test transcription",
                "language": "en",
                "duration": 10.5,
                "provider": "azure_openai",
                "model": "whisper-1",
                "response_ms": 1234
            }
            
            result = client.audio.transcribe(file_path="test.mp3")
            
            assert result.text == "This is a test transcription"
            assert result.language == "en"
            assert result.duration == 10.5
            assert result.model == "whisper-1"
            
            # Check the API call
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == '/v1/audio/transcriptions'
            assert 'file' in call_args[1]['files']
            assert call_args[1]['data']['model'] == 'whisper-1'
            assert call_args[1]['data']['response_format'] == 'json'
    
    def test_transcribe_text_format(self):
        """Test transcription with text format"""
        client = AstarClient(api_key="test")
        
        with patch('os.path.exists') as mock_exists, \
             patch('os.path.getsize') as mock_getsize, \
             patch('builtins.open', mock_open(read_data=b'fake audio data')), \
             patch.object(client._http, 'post_multipart') as mock_post:
            
            mock_exists.return_value = True
            mock_getsize.return_value = 1024 * 1024
            mock_post.return_value = {"text": "This is plain text transcription"}
            
            result = client.audio.transcribe(
                file_path="test.mp3",
                response_format="text"
            )
            
            # For text format, should return string directly
            assert result == "This is plain text transcription"
    
    def test_transcribe_verbose_json(self):
        """Test transcription with verbose JSON format"""
        client = AstarClient(api_key="test")
        
        with patch('os.path.exists') as mock_exists, \
             patch('os.path.getsize') as mock_getsize, \
             patch('builtins.open', mock_open(read_data=b'fake audio data')), \
             patch.object(client._http, 'post_multipart') as mock_post:
            
            mock_exists.return_value = True
            mock_getsize.return_value = 1024 * 1024
            mock_post.return_value = {
                "text": "Full transcription",
                "language": "en",
                "duration": 10.5,
                "segments": [
                    {"start": 0.0, "end": 5.2, "text": "Segment text"}
                ],
                "words": [
                    {"word": "Hello", "start": 0.0, "end": 0.5, "confidence": 0.99}
                ]
            }
            
            result = client.audio.transcribe(
                file_path="test.mp3",
                response_format="verbose_json"
            )
            
            assert result.text == "Full transcription"
            assert len(result.segments) == 1
            assert result.segments[0].text == "Segment text"
            assert len(result.words) == 1
            assert result.words[0].word == "Hello"
            assert result.words[0].confidence == 0.99
    
    def test_transcribe_file_not_found(self):
        """Test transcription with non-existent file"""
        client = AstarClient(api_key="test")
        
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            
            with pytest.raises(FileNotFoundError, match="Audio file not found"):
                client.audio.transcribe(file_path="nonexistent.mp3")
    
    def test_transcribe_file_too_large(self):
        """Test transcription with file exceeding size limit"""
        client = AstarClient(api_key="test")
        
        with patch('os.path.exists') as mock_exists, \
             patch('os.path.getsize') as mock_getsize:
            
            mock_exists.return_value = True
            mock_getsize.return_value = 26 * 1024 * 1024  # 26MB
            
            with pytest.raises(ValueError, match="exceeds 25MB limit"):
                client.audio.transcribe(file_path="large.mp3")
    
    def test_transcribe_with_options(self):
        """Test transcription with all options"""
        client = AstarClient(api_key="test")
        
        with patch('os.path.exists') as mock_exists, \
             patch('os.path.getsize') as mock_getsize, \
             patch('builtins.open', mock_open(read_data=b'fake audio data')), \
             patch.object(client._http, 'post_multipart') as mock_post:
            
            mock_exists.return_value = True
            mock_getsize.return_value = 1024 * 1024
            mock_post.return_value = {
                "text": "Transcription with context",
                "language": "en"
            }
            
            result = client.audio.transcribe(
                file_path="test.wav",
                model="gpt-4o-transcribe",
                prompt="This is about quantum physics",
                temperature=0.5
            )
            
            # Check the API call parameters
            call_args = mock_post.call_args
            data = call_args[1]['data']
            assert data['model'] == 'gpt-4o-transcribe'
            assert data['prompt'] == 'This is about quantum physics'
            assert data['temperature'] == '0.5'
    
    def test_transcribe_mime_type_detection(self):
        """Test MIME type detection for different audio formats"""
        client = AstarClient(api_key="test")
        
        test_cases = [
            ("test.mp3", "audio/mpeg"),
            ("test.wav", "audio/wav"),
            ("test.m4a", "audio/m4a"),
            ("test.webm", "audio/webm"),
        ]
        
        for filename, expected_mime in test_cases:
            with patch('os.path.exists') as mock_exists, \
                 patch('os.path.getsize') as mock_getsize, \
                 patch('builtins.open', mock_open(read_data=b'fake audio data')), \
                 patch.object(client._http, 'post_multipart') as mock_post:
                
                mock_exists.return_value = True
                mock_getsize.return_value = 1024 * 1024
                mock_post.return_value = {"text": "Test"}
                
                client.audio.transcribe(file_path=filename)
                
                # Check that correct MIME type was used
                call_args = mock_post.call_args
                files = call_args[1]['files']
                _, file_tuple = list(files.items())[0]
                assert file_tuple[2] == expected_mime
