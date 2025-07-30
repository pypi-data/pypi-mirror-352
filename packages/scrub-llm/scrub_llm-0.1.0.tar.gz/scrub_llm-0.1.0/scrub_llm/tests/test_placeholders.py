import pytest
from scrub_llm.placeholders import PlaceholderManager
from scrub_llm.detectors.base import Match


class TestPlaceholderManager:
    def test_generate_placeholder(self):
        manager = PlaceholderManager()
        placeholder = manager.generate_placeholder("secret123")
        
        assert placeholder.startswith("<SECRET_")
        assert placeholder.endswith(">")
        assert manager.get_value(placeholder) == "secret123"
    
    def test_reuse_placeholder(self):
        manager = PlaceholderManager()
        placeholder1 = manager.generate_placeholder("secret123")
        placeholder2 = manager.generate_placeholder("secret123")
        
        assert placeholder1 == placeholder2
    
    def test_different_placeholders(self):
        manager = PlaceholderManager()
        placeholder1 = manager.generate_placeholder("secret123")
        placeholder2 = manager.generate_placeholder("secret456")
        
        assert placeholder1 != placeholder2
    
    def test_uuid_mode(self):
        manager = PlaceholderManager(use_uuid=True)
        placeholder = manager.generate_placeholder("secret")
        
        assert placeholder.startswith("<SECRET_")
        assert len(placeholder) > 10
    
    def test_custom_prefix(self):
        manager = PlaceholderManager(prefix="TOKEN")
        placeholder = manager.generate_placeholder("secret")
        
        assert placeholder.startswith("<TOKEN_")
    
    def test_replace_secrets(self):
        manager = PlaceholderManager()
        text = "My key is secret123 and token is secret456"
        secrets = [
            Match("key", "secret123", 10, 19),
            Match("token", "secret456", 34, 43)
        ]
        
        result, mappings = manager.replace_secrets(text, secrets)
        
        assert "secret123" not in result
        assert "secret456" not in result
        assert "<SECRET_" in result
        assert len(mappings) == 2
    
    def test_rehydrate(self):
        manager = PlaceholderManager()
        text = "My key is secret123"
        secrets = [Match("key", "secret123", 10, 19)]
        
        scrubbed, mappings = manager.replace_secrets(text, secrets)
        rehydrated = manager.rehydrate(scrubbed, mappings)
        
        assert rehydrated == text
    
    def test_clear(self):
        manager = PlaceholderManager()
        manager.generate_placeholder("secret")
        manager.clear()
        
        assert len(manager.get_all_mappings()) == 0