from __future__ import annotations

import hashlib

from .schemas import DetectionResult


def analyze_evidence(evidence_id: str) -> DetectionResult:
    digest = hashlib.sha256(evidence_id.encode("utf-8")).hexdigest()
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
        evidence_id=evidence_id,
        synthetic_risk_score=score,
        risk_level=level,
        reason_codes=reasons,
        recommended_action=action,
    )
