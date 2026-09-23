import asyncio
import cv2
import numpy as np
import logging
import json
import io
import base64
from PIL import Image

from app.ai.person_detector import PersonDetector
from app.ai.pose_detector import PoseDetector
from app.ai.body_segmenter import BodySegmenter
from app.ai.clothing_detector import ClothingDetector
from app.ai.body_type_estimator import BodyTypeEstimator
from app.services.ml.style_engine import StyleEngine
from app.services.ml.scoring_engine import ScoringEngine

logging.basicConfig(level=logging.INFO)

# Test Photo URLs
PHOTO_1_URL = "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?q=80&w=1000&auto=format&fit=crop" # Dancing full body
PHOTO_2_URL = "https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=1000&auto=format&fit=crop" # Portrait / upper body

async def test_photo(url: str, label: str):
    print(f"\n====================================================")
    print(f"TESTING PIPELINE ON: {label}")
    print(f"URL: {url}")
    print(f"====================================================")

    # 1. Person Detection
    person = await PersonDetector.detect(url)
    print(f"1. Person Detected: {person.get('detected')} (Conf: {person.get('confidence')})")

    # 2. Pose & Visibility Detection (MediaPipe)
    pose = await PoseDetector.detect(url, person)
    vis = pose.get("body_visibility", {})
    print(f"2. Framing: {pose.get('pose_type')} | Visibility: {pose.get('body_visibility_percentage')}%")
    print(f"   UpperVisible: {vis.get('upper_body_visible')}, LowerVisible: {vis.get('lower_body_visible')}, FeetVisible: {vis.get('feet_visible')}")

    # 3. Garment Segmentation (Landmark-guided GrabCut)
    segmentation = await BodySegmenter.segment(url, person, pose)
    print(f"3. Segmentation: Mask Ready = {segmentation.get('mask_ready')}")

    # 4. Independent Garment Detection & Color Extraction
    colors = await StyleEngine.extract_colors(url, segmentation)
    clothing = await ClothingDetector.detect(url, person, pose, segmentation)
    garments = clothing.get("garments", [])

    print(f"4. Primary Color: {colors.get('primary')}")
    print(f"   Garments Detected ({len(garments)}):")
    for g in garments:
        print(f"   -> [{g.get('region')}] {g.get('garment')}: Color={g.get('color')}, Conf={g.get('confidence')}")

    if clothing.get("lower_body_status") != "Detected":
        print(f"   -> [Lower Body] {clothing.get('lower_body_status')}")
    if clothing.get("footwear_status") != "Detected":
        print(f"   -> [Footwear] {clothing.get('footwear_status')}")

    # 5. Body Type Estimation
    body_type = await BodyTypeEstimator.estimate(url, pose, person)
    print(f"5. Body Type: {body_type.get('body_type')} (Status: {body_type.get('status')})")

    # 6. Top-3 Style Taxonomy
    styles = await StyleEngine.classify_style(colors, garments, url, segmentation)
    print(f"6. Top-3 Styles:")
    for s in styles:
        print(f"   -> #{s.get('style_name')}: Conf={s.get('confidence')}")


async def main():
    await test_photo(PHOTO_1_URL, "Photo #1: Full-Body Photo")
    await test_photo(PHOTO_2_URL, "Photo #2: Upper-Body Photo")

if __name__ == "__main__":
    asyncio.run(main())
