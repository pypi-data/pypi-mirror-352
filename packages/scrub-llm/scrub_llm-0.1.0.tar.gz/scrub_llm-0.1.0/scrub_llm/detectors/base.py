from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Match:
    pattern_name: str
    value: str
    start: int
    end: int
    confidence: float = 1.0
    metadata: Optional[dict] = None


class Detector(ABC):
    @abstractmethod
    def scan(self, text: str) -> List[Match]:
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass