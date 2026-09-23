"""
BodyTypeEstimator — Pose-Landmark-Gated Body Silhouette Estimator for StyleSense AI.

Guarantees:
- Estimates ONLY if:
  1. Full body is visible (head to feet/ankles)
  2. Standing pose
  3. Enough landmarks (shoulders 11,12 & hips 23,24)
- Otherwise returns "Insufficient visibility"
- NEVER guesses
"""

import logging

logger = logging.getLogger(__name__)


class BodyTypeEstimator:

    @staticmethod
    async def estimate(image_url: str, pose: dict = None, person_box: dict = None) -> dict:
        try:
            pose = pose or {}
            framing = pose.get("framing", "Unknown")
            orientation = pose.get("orientation", "Unknown")
            body_visibility = pose.get("body_visibility_percentage", 0)
            landmarks = pose.get("landmarks", {})

            # 1. GATE: Must be Full body framing and standing pose
            if framing != "Full body":
                return BodyTypeEstimator._insufficient_visibility(
                    f"Photo framing is '{framing}' (requires 'Full body'). Body type estimation withheld."
                )

            if orientation not in ["Front", "Side"]:
                return BodyTypeEstimator._insufficient_visibility(
                    f"Pose orientation is '{orientation}' (requires standing 'Front' or 'Side' view)."
                )

            if body_visibility < 75:
                return BodyTypeEstimator._insufficient_visibility(
                    f"Only {body_visibility}% body visible (minimum 75% required)."
                )

            # 2. GATE: Check key shoulder and hip landmarks
            has_shoulders = (
                "11" in landmarks and "12" in landmarks and
                landmarks["11"].get("visibility", 0) >= 0.20 and
                landmarks["12"].get("visibility", 0) >= 0.20
            )
            has_hips = (
                "23" in landmarks and "24" in landmarks and
                landmarks["23"].get("visibility", 0) >= 0.20 and
                landmarks["24"].get("visibility", 0) >= 0.20
            )

            if not has_shoulders or not has_hips:
                return BodyTypeEstimator._insufficient_visibility(
                    "Insufficient landmark visibility for shoulder/hip measurement."
                )

            # Calculate actual shoulder and hip widths
            left_shoulder_x = landmarks["11"]["x"]
            right_shoulder_x = landmarks["12"]["x"]
            left_hip_x = landmarks["23"]["x"]
            right_hip_x = landmarks["24"]["x"]

            shoulder_width = abs(right_shoulder_x - left_shoulder_x)
            hip_width = abs(right_hip_x - left_hip_x)

            if hip_width < 0.01:
                return BodyTypeEstimator._insufficient_visibility("Hip landmarks too close to calculate width.")

            shr = shoulder_width / hip_width

            # Classify body type from measurements
            if shr > 1.25:
                body_type = "Athletic"
                confidence = min(0.90, 0.70 + (shr - 1.25) * 0.5)
                fit_tip = "Structured tops with clean shoulders pair well with straight-leg bottoms."
            elif shr < 0.88:
                body_type = "Pear"
                confidence = min(0.85, 0.65 + (0.88 - shr) * 0.5)
                fit_tip = "A-line silhouettes and upper-body focus create a balanced line."
            elif 0.88 <= shr <= 1.15:
                body_type = "Average / Rectangle"
                confidence = 0.78
                fit_tip = "Fitted cuts with defined waistlines define the silhouette."
            else:
                body_type = "Inverted Triangle"
                confidence = 0.75
                fit_tip = "Relaxed upper garments with wider bottoms balance proportion."

            evidence = f"MediaPipe Landmark ratio (Shoulder/Hip={shr:.2f}). {body_visibility}% visible body keypoints."

            logger.info(f"[BodyTypeEstimator] Body Type={body_type} (SHR={shr:.2f})")

            return {
                "body_type": body_type,
                "status": "Estimated",
                "confidence": round(confidence, 2),
                "evidence": evidence,
                "fit_recommendation": fit_tip,
                "source": "mediapipe_pose",
            }

        except Exception as e:
            logger.error(f"[BodyTypeEstimator] Error: {e}")
            return BodyTypeEstimator._insufficient_visibility(f"Body type calculation error: {str(e)}")

    @staticmethod
    def _insufficient_visibility(reason: str) -> dict:
        return {
            "body_type": "Insufficient visibility",
            "status": "Insufficient visibility",
            "confidence": 0.0,
            "evidence": reason,
            "fit_recommendation": "Body type analysis requires a full-length standing photo.",
            "source": "mediapipe_pose",
        }

