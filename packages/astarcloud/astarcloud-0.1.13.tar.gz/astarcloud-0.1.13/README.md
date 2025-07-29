# AstarCloud SDK

Python SDK for the AstarCloud API with support for chat completions, tool calling, and audio transcription.

## Installation

```bash
pip install astarcloud-sdk
```

## Quick Start

```python
from AstarCloud import AstarClient

client = AstarClient(api_key="sk-...")

# Basic chat completion
response = client.create.completion(
    messages=[{"role": "user", "content": "Hello!"}],
    model="gpt-4.1"
)

print(response.choices[0].message.content)
```

## Tool Calling

The SDK supports tool calling for compatible models (`gpt-4.1`, `gpt-4.1-mini`, `gpt-4.1-nano`, `astar-gpt-4.1`).

### Basic Tool Usage

```python
from AstarCloud import AstarClient, ToolSpec

client = AstarClient(api_key="sk-...")

# Define a tool
weather_tool = ToolSpec(
    function={
        "name": "get_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                }
            },
            "required": ["location"]
        }
    }
)

# Use the tool in a completion
response = client.create.completion(
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    model="gpt-4.1",
    tools=[weather_tool],
    tool_choice="auto"
)

# Check if the model wants to call a tool
if response.choices[0].tool_calls:
    tool_call = response.choices[0].tool_calls[0]
    print(f"Tool called: {tool_call.function['name']}")
    print(f"Arguments: {tool_call.function['arguments']}")
```

### Bound Tools Client

For convenience, you can create a client with pre-bound tools:

```python
# Create a client with bound tools
bound_client = client.bind_tools([weather_tool])

# All completions will automatically include the bound tools
response = bound_client.create.completion(
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
    model="gpt-4.1"
)
```

## Streaming

The SDK supports streaming responses:

```python
for chunk in client.create.completion(
    messages=[{"role": "user", "content": "Write a story"}],
    model="gpt-4.1",
    stream=True
):
    if chunk.choices[0].message.content:
        print(chunk.choices[0].message.content, end="")
```

## Audio Transcription

The SDK supports audio transcription with various output formats:

### Basic Transcription

```python
# Transcribe an audio file
transcription = client.audio.transcribe(
    file_path="path/to/audio.mp3"
)

print(transcription.text)
print(f"Language: {transcription.language}")
print(f"Duration: {transcription.duration} seconds")
```

### Advanced Options

```python
# Transcribe with custom options
transcription = client.audio.transcribe(
    file_path="meeting.wav",
    model="gpt-4o-transcribe",  # or "whisper-1", "gpt-4o-mini-transcribe"
    prompt="This is a technical meeting about AI",
    temperature=0.2,
    response_format="verbose_json"  # Get detailed word-level timestamps
)

# Access segments and words (in verbose_json format)
for segment in transcription.segments:
    print(f"{segment.start}s - {segment.end}s: {segment.text}")

for word in transcription.words:
    print(f"{word.word} ({word.confidence:.2f})")
```

### Output Formats

```python
# Plain text output
text = client.audio.transcribe(
    file_path="audio.mp3",
    response_format="text"  # Returns string directly
)

# SRT subtitles
srt_content = client.audio.transcribe(
    file_path="video_audio.mp3",
    response_format="srt"
)

# WebVTT subtitles
vtt_content = client.audio.transcribe(
    file_path="video_audio.mp3",
    response_format="vtt"
)
```

### Supported Audio Formats
- MP3, MP4, MPEG, MPGA, M4A, WAV, WEBM
- Maximum file size: 25MB

### Available Transcription Models
- `whisper-1`: Standard Whisper model
- `gpt-4o-transcribe`: Latest GPT-4o transcription
- `gpt-4o-mini-transcribe`: Faster, cheaper option

## Error Handling

```python
from AstarCloud import AstarClient
from AstarCloud._exceptions import APIError, AuthenticationError

try:
    response = client.create.completion(
        messages=[{"role": "user", "content": "Hello"}],
        model="gpt-4.1"
    )
except AuthenticationError:
    print("Invalid API key")
except APIError as e:
    print(f"API error: {e}")
```

## Model Support

### Tool-Compatible Models
- `gpt-4.1`
- `gpt-4.1-mini`
- `gpt-4.1-nano`
- `astar-gpt-4.1`

Other models can be used for basic completions but do not support tool calling.