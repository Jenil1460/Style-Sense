import cv2
import numpy as np
import httpx
import asyncio
import io
from PIL import Image

from app.ai.person_detector import PersonDetector
from app.ai.pose_detector import _get_mp_pose

async def test_anatomical_ratio(url: str, label: str):
    person = await PersonDetector.detect(url)

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        resp = await client.get(url)
        raw_bytes = resp.content

    image = cv2.imdecode(np.frombuffer(raw_bytes, np.uint8), cv2.IMREAD_COLOR)
    h, w = image.shape[:2]

    # Person Bounding Box
    p_box = person["boxes"][0] if person.get("boxes") else {"x_min": 0.0, "y_min": 0.0, "x_max": 1.0, "y_max": 1.0}
    p_height = p_box["y_max"] - p_box["y_min"]

    # Run MediaPipe Pose for nose and shoulder landmarks
    pose = _get_mp_pose()
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark
        nose_y = lm[0].y
        shoulder_y = (lm[11].y + lm[12].y) / 2.0
        head_height = abs(shoulder_y - nose_y)
    else:
        head_height = 0.15

    ratio = p_height / max(0.04, head_height)

    print(f"\n====================================================")
    print(f"ANATOMICAL RATIO TEST: {label}")
    print(f"Person Height Ratio: {p_height:.3f} | Head-to-Shoulder Height: {head_height:.3f}")
    print(f"Anatomical Head-to-Body Ratio: {ratio:.2f} heads")

    if ratio >= 4.2:
        framing = "Full body"
        lower_visible = True
        feet_visible = True
    elif ratio >= 3.4:
        framing = "Three-Quarter"
        lower_visible = True
        feet_visible = False
    else:
        framing = "Upper body / Waist-up"
        lower_visible = False
        feet_visible = False

    print(f"Result: {framing} (LowerVisible={lower_visible}, FeetVisible={feet_visible})")

async def main():
    await test_anatomical_ratio(
        "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?q=80&w=1000&auto=format&fit=crop",
        "Photo 1: Dancing Woman (Full Body)"
    )
    await test_anatomical_ratio(
        "https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=1000&auto=format&fit=crop",
        "Photo 2: Upper-Body Portrait"
    )

if __name__ == "__main__":
    asyncio.run(main())
