import httpx
from typing import Optional, Dict, Any
import json
from ..scrubber import Scrubber


class ScrubberHTTPXHook:
    def __init__(self, scrubber: Optional[Scrubber] = None):
        self.scrubber = scrubber or Scrubber()
    
    async def async_request_hook(self, request: httpx.Request) -> None:
        if request.content:
            try:
                content = request.content.decode('utf-8')
                if request.headers.get('content-type', '').startswith('application/json'):
                    data = json.loads(content)
                    scrubbed_data = self._scrub_json(data)
                    request.content = json.dumps(scrubbed_data).encode('utf-8')
                else:
                    scrubbed_content, _ = self.scrubber.scrub_prompt(content)
                    request.content = scrubbed_content.encode('utf-8')
            except Exception:
                pass
    
    async def async_response_hook(self, response: httpx.Response) -> None:
        if response.status_code == 200 and response.content:
            try:
                content = response.content.decode('utf-8')
                if response.headers.get('content-type', '').startswith('application/json'):
                    data = json.loads(content)
                    scrubbed_data = self._scrub_json(data)
                    response._content = json.dumps(scrubbed_data).encode('utf-8')
                else:
                    scrubbed_content = self.scrubber.scrub_response(content)
                    response._content = scrubbed_content.encode('utf-8')
            except Exception:
                pass
    
    def sync_request_hook(self, request: httpx.Request) -> None:
        if request.content:
            try:
                content = request.content.decode('utf-8')
                if request.headers.get('content-type', '').startswith('application/json'):
                    data = json.loads(content)
                    scrubbed_data = self._scrub_json(data)
                    request.content = json.dumps(scrubbed_data).encode('utf-8')
                else:
                    scrubbed_content, _ = self.scrubber.scrub_prompt(content)
                    request.content = scrubbed_content.encode('utf-8')
            except Exception:
                pass
    
    def sync_response_hook(self, response: httpx.Response) -> None:
        if response.status_code == 200 and response.content:
            try:
                content = response.content.decode('utf-8')
                if response.headers.get('content-type', '').startswith('application/json'):
                    data = json.loads(content)
                    scrubbed_data = self._scrub_json(data)
                    response._content = json.dumps(scrubbed_data).encode('utf-8')
                else:
                    scrubbed_content = self.scrubber.scrub_response(content)
                    response._content = scrubbed_content.encode('utf-8')
            except Exception:
                pass
    
    def _scrub_json(self, data: Any) -> Any:
        if isinstance(data, str):
            scrubbed, _ = self.scrubber.scrub_prompt(data)
            return scrubbed
        elif isinstance(data, dict):
            return {k: self._scrub_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._scrub_json(item) for item in data]
        else:
            return data
    
    def create_client(self, **kwargs) -> httpx.Client:
        event_hooks = kwargs.get('event_hooks', {})
        event_hooks['request'] = event_hooks.get('request', []) + [self.sync_request_hook]
        event_hooks['response'] = event_hooks.get('response', []) + [self.sync_response_hook]
        kwargs['event_hooks'] = event_hooks
        return httpx.Client(**kwargs)
    
    def create_async_client(self, **kwargs) -> httpx.AsyncClient:
        event_hooks = kwargs.get('event_hooks', {})
        event_hooks['request'] = event_hooks.get('request', []) + [self.async_request_hook]
        event_hooks['response'] = event_hooks.get('response', []) + [self.async_response_hook]
        kwargs['event_hooks'] = event_hooks
        return httpx.AsyncClient(**kwargs)