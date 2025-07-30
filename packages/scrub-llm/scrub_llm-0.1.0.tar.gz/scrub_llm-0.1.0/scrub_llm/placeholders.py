import contextvars
import uuid
from typing import Dict, Optional, Tuple
from threading import Lock


_placeholder_store: contextvars.ContextVar[Dict[str, str]] = contextvars.ContextVar(
    'placeholder_store', default={}
)
_global_lock = Lock()


class PlaceholderManager:
    def __init__(self, prefix: str = "SECRET", use_uuid: bool = False):
        self.prefix = prefix
        self.use_uuid = use_uuid
        self._counter = 0
        self._local_lock = Lock()
    
    def generate_placeholder(self, value: str) -> str:
        store = _placeholder_store.get()
        
        for placeholder, stored_value in store.items():
            if stored_value == value:
                return placeholder
        
        if self.use_uuid:
            placeholder = f"<{self.prefix}_{uuid.uuid4().hex[:8].upper()}>"
        else:
            with self._local_lock:
                self._counter += 1
                placeholder = f"<{self.prefix}_{self._counter}>"
        
        new_store = store.copy()
        new_store[placeholder] = value
        _placeholder_store.set(new_store)
        
        return placeholder
    
    def store_mapping(self, placeholder: str, value: str) -> None:
        store = _placeholder_store.get()
        new_store = store.copy()
        new_store[placeholder] = value
        _placeholder_store.set(new_store)
    
    def get_value(self, placeholder: str) -> Optional[str]:
        store = _placeholder_store.get()
        return store.get(placeholder)
    
    def get_all_mappings(self) -> Dict[str, str]:
        return _placeholder_store.get().copy()
    
    def clear(self) -> None:
        _placeholder_store.set({})
    
    def replace_secrets(self, text: str, secrets: list) -> Tuple[str, Dict[str, str]]:
        result = text
        mappings = {}
        
        sorted_secrets = sorted(secrets, key=lambda x: x.start, reverse=True)
        
        for secret in sorted_secrets:
            placeholder = self.generate_placeholder(secret.value)
            result = result[:secret.start] + placeholder + result[secret.end:]
            mappings[placeholder] = secret.value
        
        return result, mappings
    
    def rehydrate(self, text: str, mappings: Optional[Dict[str, str]] = None) -> str:
        if mappings is None:
            mappings = self.get_all_mappings()
        
        result = text
        for placeholder, value in mappings.items():
            result = result.replace(placeholder, value)
        
        return result