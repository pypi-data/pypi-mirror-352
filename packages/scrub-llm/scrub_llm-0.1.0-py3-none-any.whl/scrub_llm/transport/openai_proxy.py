from typing import Any, Dict, Iterator, Optional, Union
import httpx
from openai import OpenAI, AsyncOpenAI, Stream
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from dataclasses import dataclass
import json

from ..scrubber import Scrubber
from .httpx_hook import ScrubberHTTPXHook


@dataclass
class ScrubbedMessage:
    content: str
    flagged: bool = False
    secrets: list = None
    _mappings: Dict[str, str] = None
    
    def safe_text(self) -> str:
        return self.content
    
    def rehydrate(self) -> str:
        if self._mappings:
            result = self.content
            for placeholder, value in self._mappings.items():
                result = result.replace(placeholder, value)
            return result
        return self.content


class ScrubberStream:
    def __init__(self, stream: Stream, scrubber: Scrubber):
        self.stream = stream
        self.scrubber = scrubber
        self._buffer = ""
    
    def __iter__(self) -> Iterator[ScrubbedMessage]:
        for chunk in self.stream:
            if hasattr(chunk, 'choices') and chunk.choices:
                for choice in chunk.choices:
                    if hasattr(choice, 'delta') and hasattr(choice.delta, 'content'):
                        content = choice.delta.content
                        if content:
                            self._buffer += content
                            
                            scrubbed_content = self.scrubber.scrub_response(content)
                            has_secrets = scrubbed_content != content
                            
                            choice.delta.content = scrubbed_content
                            
                            yield ScrubbedMessage(
                                content=scrubbed_content,
                                flagged=has_secrets,
                                secrets=[] if not has_secrets else ["redacted"]
                            )
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        chunk = await self.stream.__anext__()
        if hasattr(chunk, 'choices') and chunk.choices:
            for choice in chunk.choices:
                if hasattr(choice, 'delta') and hasattr(choice.delta, 'content'):
                    content = choice.delta.content
                    if content:
                        self._buffer += content
                        
                        scrubbed_content = self.scrubber.scrub_response(content)
                        has_secrets = scrubbed_content != content
                        
                        choice.delta.content = scrubbed_content
                        
                        return ScrubberMessage(
                            content=scrubbed_content,
                            flagged=has_secrets,
                            secrets=[] if not has_secrets else ["redacted"]
                        )
        raise StopAsyncIteration


class OpenAIScrubber:
    def __init__(self, client: Optional[Union[OpenAI, type]] = None, scrubber: Optional[Scrubber] = None):
        self.scrubber = scrubber or Scrubber()
        self.hook = ScrubberHTTPXHook(self.scrubber)
        
        if client is None or client == OpenAI:
            self.client = OpenAI(http_client=self.hook.create_client())
        elif isinstance(client, OpenAI):
            http_client = self.hook.create_client()
            self.client = OpenAI(
                api_key=client.api_key,
                organization=client.organization,
                base_url=client.base_url,
                timeout=client.timeout,
                max_retries=client.max_retries,
                http_client=http_client
            )
        else:
            self.client = client
    
    @property
    def chat(self):
        return self
    
    @property
    def completions(self):
        return self
    
    def create(self, **kwargs) -> Union[ChatCompletion, ScrubberStream]:
        messages = kwargs.get('messages', [])
        scrubbed_messages = []
        
        for message in messages:
            if isinstance(message, dict) and 'content' in message:
                scrubbed_content, mappings = self.scrubber.scrub_prompt(message['content'])
                scrubbed_message = message.copy()
                scrubbed_message['content'] = scrubbed_content
                scrubbed_messages.append(scrubbed_message)
            else:
                scrubbed_messages.append(message)
        
        kwargs['messages'] = scrubbed_messages
        
        response = self.client.chat.completions.create(**kwargs)
        
        if kwargs.get('stream', False):
            return ScrubberStream(response, self.scrubber)
        else:
            if hasattr(response, 'choices'):
                for choice in response.choices:
                    if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                        choice.message.content = self.scrubber.scrub_response(choice.message.content)
            
            return response
    
    @property
    def ChatCompletion(self):
        class _ChatCompletion:
            @staticmethod
            def create(**kwargs):
                return self.create(**kwargs)
        return _ChatCompletion
    
    def __getattr__(self, name):
        return getattr(self.client, name)