from __future__ import annotations

import hashlib

from app.analyzers.base import EvidenceAnalyzer
from app.analyzers.metadata import MVP_DECISION_SUPPORT_DISCLAIMER, SIMULATED_ANALYZER_VERSION
from app.schemas import DetectionResult, EvidenceRecord


class SimulatedEvidenceAnalyzer(EvidenceAnalyzer):
    @property
    def analyzer_name(self) -> str:
        return "simulated"

    def analyze(self, evidence: EvidenceRecord) -> DetectionResult:
        digest = hashlib.sha256(evidence.evidence_id.encode("utf-8")).hexdigest()
        score = int(digest[:8], 16) % 101

        if score >= 70:
            level = "high"
            reasons = ["voice_clone_pattern", "lip_sync_artifact"]
            action = "Escalate immediately and freeze transaction workflow."
        elif score >= 40:
            level = "medium"
            reasons = ["metadata_inconsistency", "identity_velocity_spike"]
            action = "Require step-up verification and analyst review."
        else:
            level = "low"
            reasons = ["minor_signal_variance"]
            action = "Proceed with caution and monitor."

        return DetectionResult(
            evidence_id=evidence.evidence_id,
            synthetic_risk_score=score,
            risk_level=level,
            reason_codes=reasons,
            recommended_action=action,
            analyzer_version=SIMULATED_ANALYZER_VERSION,
            decision_support_disclaimer=MVP_DECISION_SUPPORT_DISCLAIMER,
        )
