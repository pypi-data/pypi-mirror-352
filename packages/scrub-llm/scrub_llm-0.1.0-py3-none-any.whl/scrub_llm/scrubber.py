from typing import List, Tuple, Optional, Dict
from .detectors import RegexDetector, EntropyDetector, Detector
from .placeholders import PlaceholderManager


class Scrubber:
    def __init__(
        self,
        detectors: Optional[List[Detector]] = None,
        placeholder_manager: Optional[PlaceholderManager] = None,
        enable_regex: bool = True,
        enable_entropy: bool = True,
        min_entropy: float = 3.5,
        min_entropy_length: int = 20
    ):
        self.detectors = detectors or []
        
        if not detectors:
            if enable_regex:
                self.detectors.append(RegexDetector())
            if enable_entropy:
                self.detectors.append(EntropyDetector(
                    min_length=min_entropy_length,
                    min_entropy=min_entropy
                ))
        
        self.placeholder_manager = placeholder_manager or PlaceholderManager()
    
    def add_detector(self, detector: Detector) -> None:
        self.detectors.append(detector)
    
    def scan(self, text: str) -> List:
        all_matches = []
        seen_values = set()
        
        for detector in self.detectors:
            matches = detector.scan(text)
            for match in matches:
                if match.value not in seen_values:
                    all_matches.append(match)
                    seen_values.add(match.value)
        
        all_matches.sort(key=lambda x: (x.start, -x.confidence))
        
        filtered_matches = []
        last_end = -1
        
        for match in all_matches:
            if match.start >= last_end:
                filtered_matches.append(match)
                last_end = match.end
        
        return filtered_matches
    
    def scrub_prompt(self, text: str) -> Tuple[str, Dict[str, str]]:
        matches = self.scan(text)
        
        if not matches:
            return text, {}
        
        scrubbed_text, mappings = self.placeholder_manager.replace_secrets(text, matches)
        return scrubbed_text, mappings
    
    def scrub_response(self, text: str) -> str:
        matches = self.scan(text)
        
        if not matches:
            return text
        
        scrubbed_text = text
        for match in reversed(matches):
            scrubbed_text = (
                scrubbed_text[:match.start] +
                f"<REDACTED_{match.pattern_name.upper()}>" +
                scrubbed_text[match.end:]
            )
        
        return scrubbed_text
    
    def rehydrate(self, text: str, mappings: Optional[Dict[str, str]] = None) -> str:
        return self.placeholder_manager.rehydrate(text, mappings)


def scrub_prompt(text: str, **kwargs) -> Tuple[str, Dict[str, str]]:
    scrubber = Scrubber(**kwargs)
    return scrubber.scrub_prompt(text)


def scrub_response(text: str, **kwargs) -> str:
    scrubber = Scrubber(**kwargs)
    return scrubber.scrub_response(text)