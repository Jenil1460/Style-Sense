"""
VisionEngine — DEPRECATED

This module was 100% placeholder code:
- segment_clothing() returned hardcoded 0.88
- detect_pose() returned hardcoded dict
- detect_person() is superseded by YOLO-based PersonDetector

All functionality has been replaced by real model-backed implementations:
- PersonDetector (YOLO) → app.ai.person_detector
- PoseDetector (MediaPipe) → app.ai.pose_detector
- BodySegmenter (Landmark-guided) → app.ai.body_segmenter
- ClothingDetector (CLIP) → app.ai.clothing_detector
"""

import logging

logger = logging.getLogger(__name__)


class VisionEngine:
    """DEPRECATED — Do not use. See module docstring for replacements."""

    @staticmethod
    async def detect_person(image_url: str) -> dict:
        logger.warning("[VisionEngine] DEPRECATED — use PersonDetector instead")
        return {"detected": False, "confidence": 0.0, "deprecated": True}

    @staticmethod
    async def segment_clothing(image_url: str, bounding_box: dict) -> float:
        logger.warning("[VisionEngine] DEPRECATED — use BodySegmenter instead")
        return 0.0

    @staticmethod
    async def detect_pose(image_url: str) -> dict:
        logger.warning("[VisionEngine] DEPRECATED — use PoseDetector instead")
        return {"overall_confidence": 0.0, "deprecated": True}
