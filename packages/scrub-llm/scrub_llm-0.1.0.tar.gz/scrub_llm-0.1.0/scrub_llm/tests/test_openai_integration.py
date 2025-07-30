import pytest
import respx
import httpx
from openai import OpenAI
from scrub_llm import OpenAIScrubber


@pytest.fixture
def mock_openai_response():
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "gpt-3.5-turbo",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Here's your API key: sk-FAKE1234567890abcdefghijklmnopqrstuvwxyz"
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 12,
            "total_tokens": 21
        }
    }


@respx.mock
def test_openai_scrubber_basic(mock_openai_response):
    respx.post("https://api.openai.com/v1/chat/completions").mock(
        return_value=httpx.Response(200, json=mock_openai_response)
    )
    
    client = OpenAI(api_key="test-key")
    scrubbed = OpenAIScrubber(client)
    
    response = scrubbed.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": "My AWS key is AKIAIOSFODNN7EXAMPLE"
        }]
    )
    
    assert "sk-FAKE1234567890" not in response.choices[0].message.content
    assert "REDACTED" in response.choices[0].message.content


@respx.mock
def test_openai_scrubber_prompt_cleaning(mock_openai_response):
    request_capture = []
    
    def capture_request(request):
        request_capture.append(request.json())
        return httpx.Response(200, json=mock_openai_response)
    
    respx.post("https://api.openai.com/v1/chat/completions").mock(
        side_effect=capture_request
    )
    
    client = OpenAI(api_key="test-key")
    scrubbed = OpenAIScrubber(client)
    
    scrubbed.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": "My secret key is ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        }]
    )
    
    assert len(request_capture) == 1
    sent_content = request_capture[0]["messages"][0]["content"]
    assert "ghp_1234567890" not in sent_content
    assert "<SECRET_" in sent_content


@respx.mock
def test_openai_scrubber_streaming():
    chunks = [
        {
            "id": "chatcmpl-123",
            "object": "chat.completion.chunk",
            "created": 1677652288,
            "model": "gpt-3.5-turbo",
            "choices": [{
                "index": 0,
                "delta": {"content": "Here's your key: "},
                "finish_reason": None
            }]
        },
        {
            "id": "chatcmpl-123",
            "object": "chat.completion.chunk",
            "created": 1677652288,
            "model": "gpt-3.5-turbo",
            "choices": [{
                "index": 0,
                "delta": {"content": "sk-FAKE1234567890abcdefghijklmnopqrstuvwxyz"},
                "finish_reason": None
            }]
        },
        {
            "id": "chatcmpl-123",
            "object": "chat.completion.chunk",
            "created": 1677652288,
            "model": "gpt-3.5-turbo",
            "choices": [{
                "index": 0,
                "delta": {},
                "finish_reason": "stop"
            }]
        }
    ]
    
    import json
    stream_data = "\n".join(f"data: {json.dumps(chunk)}" for chunk in chunks)
    stream_data += "\n\ndata: [DONE]\n\n"
    
    respx.post("https://api.openai.com/v1/chat/completions").mock(
        return_value=httpx.Response(
            200,
            content=stream_data.encode(),
            headers={"content-type": "text/event-stream"}
        )
    )
    
    client = OpenAI(api_key="test-key")
    scrubbed = OpenAIScrubber(client)
    
    stream = scrubbed.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Test"}],
        stream=True
    )
    
    collected = []
    for chunk in stream:
        if hasattr(chunk, 'content'):
            collected.append(chunk.content)
    
    full_response = "".join(collected)
    assert "sk-FAKE1234567890" not in full_response