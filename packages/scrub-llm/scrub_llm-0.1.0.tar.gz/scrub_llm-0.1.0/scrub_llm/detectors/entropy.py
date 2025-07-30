import math
import re
from typing import List
from .base import Detector, Match


class EntropyDetector(Detector):
    def __init__(self, min_length: int = 20, min_entropy: float = 3.5):
        self.min_length = min_length
        self.min_entropy = min_entropy
        self.token_pattern = re.compile(r'[0-9a-zA-Z_\-+=/.]{20,}')
    
    @property
    def name(self) -> str:
        return "entropy_detector"
    
    def _calculate_shannon_entropy(self, text: str) -> float:
        if not text:
            return 0.0
        
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        entropy = 0.0
        text_len = len(text)
        
        for count in char_counts.values():
            probability = count / text_len
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    def scan(self, text: str) -> List[Match]:
        matches = []
        
        for token_match in self.token_pattern.finditer(text):
            token = token_match.group(0)
            
            if len(token) < self.min_length:
                continue
            
            entropy = self._calculate_shannon_entropy(token)
            
            if entropy >= self.min_entropy:
                matches.append(Match(
                    pattern_name="high_entropy_string",
                    value=token,
                    start=token_match.start(),
                    end=token_match.end(),
                    confidence=min(1.0, entropy / 5.0),
                    metadata={"entropy": entropy}
                ))
        
        return matches