import pytest
from scrub_llm import Scrubber, scrub_prompt, scrub_response


class TestScrubber:
    def test_scrub_prompt(self):
        scrubber = Scrubber()
        text = "My AWS key is AKIAIOSFODNN7EXAMPLE"
        scrubbed, mappings = scrubber.scrub_prompt(text)
        
        assert "AKIAIOSFODNN7EXAMPLE" not in scrubbed
        assert "<SECRET_" in scrubbed
        assert len(mappings) == 1
        
        placeholder = list(mappings.keys())[0]
        assert mappings[placeholder] == "AKIAIOSFODNN7EXAMPLE"
    
    def test_scrub_response(self):
        scrubber = Scrubber()
        text = "Generated key: sk-ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuv"
        scrubbed = scrubber.scrub_response(text)
        
        assert "sk-ABCDEFGHIJKLMNOPQRSTUVWXYZ" not in scrubbed
        assert "<REDACTED_" in scrubbed
    
    def test_multiple_secrets(self):
        scrubber = Scrubber()
        text = """
        AWS: AKIAIOSFODNN7EXAMPLE
        OpenAI: sk-ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuv
        Random: 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
        """
        
        scrubbed, mappings = scrubber.scrub_prompt(text)
        
        assert "AKIAIOSFODNN7EXAMPLE" not in scrubbed
        assert "sk-ABCDEFGHIJKLMNOPQRSTUVWXYZ" not in scrubbed
        assert "9f86d081884c7d659a2feaa0c55ad015" not in scrubbed
        assert len(mappings) >= 3
    
    def test_rehydrate(self):
        scrubber = Scrubber()
        original = "My key is AKIAIOSFODNN7EXAMPLE"
        scrubbed, mappings = scrubber.scrub_prompt(original)
        rehydrated = scrubber.rehydrate(scrubbed, mappings)
        
        assert rehydrated == original
    
    def test_no_secrets(self):
        scrubber = Scrubber()
        text = "This is just normal text without secrets"
        scrubbed, mappings = scrubber.scrub_prompt(text)
        
        assert scrubbed == text
        assert len(mappings) == 0
    
    def test_overlapping_secrets(self):
        scrubber = Scrubber()
        text = "Key: AKIAIOSFODNN7EXAMPLEAKIAIOSFODNN7EXAMPLE"
        scrubbed, mappings = scrubber.scrub_prompt(text)
        
        assert "AKIAIOSFODNN7EXAMPLE" not in scrubbed
    
    def test_disable_detectors(self):
        scrubber = Scrubber(enable_regex=False, enable_entropy=True)
        text = "AWS: AKIAIOSFODNN7EXAMPLE"
        scrubbed, mappings = scrubber.scrub_prompt(text)
        
        assert scrubbed == text
    
    def test_custom_entropy_settings(self):
        scrubber = Scrubber(
            enable_regex=False,
            enable_entropy=True,
            min_entropy=2.0,
            min_entropy_length=10
        )
        text = "Short high entropy: Ab3$5^7*9!Qw2"
        matches = scrubber.scan(text)
        
        assert len(matches) > 0


class TestConvenienceFunctions:
    def test_scrub_prompt_function(self):
        text = "API key: sk-ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuv"
        scrubbed, mappings = scrub_prompt(text)
        
        assert "sk-ABCDEFGHIJKLMNOPQRSTUVWXYZ" not in scrubbed
        assert len(mappings) == 1
    
    def test_scrub_response_function(self):
        text = "Generated: ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        scrubbed = scrub_response(text)
        
        assert "ghp_" not in scrubbed or "REDACTED" in scrubbed