import pytest
from scrub_llm.detectors import RegexDetector, EntropyDetector


class TestRegexDetector:
    def test_aws_keys(self):
        detector = RegexDetector()
        text = "My AWS key is AKIAIOSFODNN7EXAMPLE and secret is wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        matches = detector.scan(text)
        
        assert len(matches) >= 1
        assert any(m.pattern_name == "aws_access_key_id" for m in matches)
        assert any(m.value == "AKIAIOSFODNN7EXAMPLE" for m in matches)
    
    def test_github_token(self):
        detector = RegexDetector()
        text = "Use this token: ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        matches = detector.scan(text)
        
        assert len(matches) == 1
        assert matches[0].pattern_name == "github_token"
        assert matches[0].value == "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
    
    def test_openai_key(self):
        detector = RegexDetector()
        text = "OPENAI_API_KEY=sk-ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuv"
        matches = detector.scan(text)
        
        assert len(matches) == 1
        assert matches[0].pattern_name == "openai_api_key"
    
    def test_multiple_secrets(self):
        detector = RegexDetector()
        text = """
        AWS: AKIAIOSFODNN7EXAMPLE
        GitHub: ghp_1234567890abcdefghijklmnopqrstuvwxyz
        Slack: xoxb-1234567890-abcdefghijk
        """
        matches = detector.scan(text)
        
        assert len(matches) >= 3
        pattern_names = {m.pattern_name for m in matches}
        assert "aws_access_key_id" in pattern_names
        assert "github_token" in pattern_names
        assert "slack_token" in pattern_names
    
    def test_no_secrets(self):
        detector = RegexDetector()
        text = "This is just a normal text without any secrets."
        matches = detector.scan(text)
        
        assert len(matches) == 0


class TestEntropyDetector:
    def test_high_entropy_string(self):
        detector = EntropyDetector(min_length=20, min_entropy=3.5)
        text = "Random string: 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
        matches = detector.scan(text)
        
        assert len(matches) == 1
        assert matches[0].pattern_name == "high_entropy_string"
        assert matches[0].metadata["entropy"] > 3.5
    
    def test_low_entropy_string(self):
        detector = EntropyDetector(min_length=20, min_entropy=3.5)
        text = "Normal text: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        matches = detector.scan(text)
        
        assert len(matches) == 0
    
    def test_short_string_ignored(self):
        detector = EntropyDetector(min_length=20, min_entropy=3.5)
        text = "Short: Ab3$5^7*9"
        matches = detector.scan(text)
        
        assert len(matches) == 0
    
    def test_entropy_calculation(self):
        detector = EntropyDetector()
        
        entropy_low = detector._calculate_shannon_entropy("aaaaaaaaaa")
        entropy_med = detector._calculate_shannon_entropy("abcabcabca")
        entropy_high = detector._calculate_shannon_entropy("9f86d081884c7d659a2f")
        
        assert entropy_low < entropy_med < entropy_high
        assert entropy_low < 1.0
        assert entropy_high > 3.0