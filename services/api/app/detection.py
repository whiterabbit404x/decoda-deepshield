from __future__ import annotations

from app.analyzers.metadata import SIMULATED_ANALYZER_VERSION
from app.analyzers.simulated import SimulatedEvidenceAnalyzer
from app.schemas import DetectionResult, EvidenceRecord


def analyze_evidence(evidence_id: str) -> DetectionResult:
    return SimulatedEvidenceAnalyzer().analyze(EvidenceRecord(evidence_id=evidence_id, filename=evidence_id))
