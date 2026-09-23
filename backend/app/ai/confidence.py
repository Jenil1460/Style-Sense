"""
Prediction — Structured prediction container for zero-hallucination AI.

Every AI prediction in the pipeline MUST use this structure.
Nothing is returned without a confidence score and evidence trail.
"""

from dataclasses import dataclass, field, asdict
from typing import Any, Optional


# ──────────────────────────────────────────────────────────────
# Confidence Thresholds — strict minimums per prediction type
# ──────────────────────────────────────────────────────────────
THRESHOLD_PERSON_DETECTION   = 0.25
THRESHOLD_POSE_LANDMARK      = 0.20
THRESHOLD_GARMENT_CLASS      = 0.25
THRESHOLD_MATERIAL           = 0.70
THRESHOLD_COLOR              = 0.40
THRESHOLD_STYLE              = 0.15
THRESHOLD_FACE_SHAPE         = 0.40
THRESHOLD_BODY_TYPE          = 0.60
THRESHOLD_BODY_VISIBILITY    = 0.80   # 80% body must be visible for body-type estimation



@dataclass
class Prediction:
    """
    Every AI output in the pipeline is wrapped in this container.
    Predictions below their confidence threshold are either hidden
    or returned with value="Unknown".
    """
    value: Any
    confidence: float
    evidence: str
    source: str = ""          # which model produced this (e.g., "CLIP", "YOLOv8", "MediaPipe")
    threshold: float = 0.0    # minimum confidence for this prediction type

    @property
    def is_valid(self) -> bool:
        """True if confidence meets or exceeds the threshold."""
        return self.confidence >= self.threshold

    @property
    def safe_value(self) -> Any:
        """Returns the value if valid, otherwise 'Unknown'."""
        return self.value if self.is_valid else "Unknown"

    def to_dict(self) -> dict:
        return {
            "value": self.safe_value,
            "confidence": round(self.confidence, 4),
            "evidence": self.evidence,
            "source": self.source,
        }


def unknown_prediction(reason: str = "Insufficient data", source: str = "") -> Prediction:
    """Factory for explicit 'Unknown' predictions — used instead of guessing."""
    return Prediction(
        value="Unknown",
        confidence=0.0,
        evidence=reason,
        source=source,
        threshold=1.0,  # will never pass is_valid
    )
