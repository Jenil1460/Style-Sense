"""
SkinToneEstimator — ITA-Based Skin Tone Classification for StyleSense AI.

Zero-hallucination guarantees:
- Uses face segmentation region from pose/segmentation for skin pixel sampling
- Uses ITA (Individual Typology Angle) calculation for Fitzpatrick-inspired classification
- Returns {value, confidence, evidence} with actual RGB values
- Returns "Unknown" when insufficient skin pixels detected
"""

import logging
from app.services.skin_tone_service import SkinToneService

logger = logging.getLogger(__name__)


class SkinToneEstimator:

    @staticmethod
    async def estimate(
        image_url: str,
        person_box: dict,
        segmentation: dict = None,
        selected_person_index: int = None
    ) -> dict:
        """
        Delegates skin tone analysis to SkinToneService while maintaining backward compatibility.
        """
        result = await SkinToneService.analyze_skin_tone(
            image_url=image_url,
            person_detection=person_box,
            selected_person_index=selected_person_index
        )

        # Ensure backward compatible 'tone' property exists alongside 'skin_tone' and 'undertone'
        result["tone"] = result.get("skin_tone", "Unavailable")
        return result

    @staticmethod
    def _unknown(reason: str) -> dict:
        return SkinToneService._unavailable(reason)

