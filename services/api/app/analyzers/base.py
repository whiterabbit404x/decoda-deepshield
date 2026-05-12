from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas import DetectionResult, EvidenceRecord


class EvidenceAnalyzer(ABC):
    """Extensible interface for evidence analyzers."""

    @property
    @abstractmethod
    def analyzer_name(self) -> str:
        ...

    @abstractmethod
    def analyze(self, evidence: EvidenceRecord) -> DetectionResult:
        """Analyze evidence and return decision-support output."""
        ...
