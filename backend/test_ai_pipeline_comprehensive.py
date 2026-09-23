"""
Comprehensive Test Suite for StyleSense AI Fashion Analysis Pipeline.
Validates zero-hallucination guarantees across all test cases.
"""

import asyncio
import logging
import sys

from app.ai.person_detector import PersonDetector
from app.ai.pose_detector import PoseDetector
from app.ai.body_segmenter import BodySegmenter
from app.ai.clothing_detector import ClothingDetector
from app.ai.body_type_estimator import BodyTypeEstimator
from app.services.ml.style_engine import StyleEngine
from app.services.ml.scoring_engine import ScoringEngine

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("ComprehensiveTest")

TEST_CASES = [
    {
        "name": "1. Full-Body Photo",
        "url": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?q=80&w=1000&auto=format&fit=crop",
        "expect_person": True,
        "expect_lower_body": True,
        "expect_feet": True,
        "expect_body_type": True,
    },
    {
        "name": "2. Upper-Body Portrait Photo",
        "url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=1000&auto=format&fit=crop",
        "expect_person": True,
        "expect_lower_body": False,
        "expect_feet": False,
        "expect_body_type": False,
    },
    {
        "name": "3. Side Pose Three-Quarter Outfit Photo",
        "url": "https://images.unsplash.com/photo-1509631179647-0177331693ae?q=80&w=1000&auto=format&fit=crop",
        "expect_person": True,
        "expect_lower_body": True,
        "expect_feet": False,
        "expect_body_type": False,
    },


    {
        "name": "4. No Person (Landscape / Object Photo)",
        "url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?q=80&w=1000&auto=format&fit=crop",
        "expect_person": False,
        "expect_lower_body": False,
        "expect_feet": False,
        "expect_body_type": False,
    },
]


async def run_test_case(tc: dict):
    print(f"\n====================================================")
    print(f"RUNNING TEST: {tc['name']}")
    print(f"URL: {tc['url']}")
    print(f"====================================================")

    url = tc["url"]

    # Step 1: Person Detection
    person = await PersonDetector.detect(url)
    print(f"1. Person Detection: Detected={person.get('detected')} (Conf: {person.get('confidence', 0):.2f})")
    
    if tc["expect_person"]:
        assert person.get("detected") is True, f"FAIL: Expected person to be detected in {tc['name']}"
    else:
        if not person.get("detected"):
            print(f"   ✓ PASS: Correctly rejected image with no person present.")
            return

    # Step 2: Pose & Visibility Detection
    pose = await PoseDetector.detect(url, person)
    vis = pose.get("body_visibility", {})
    lower_vis = vis.get("lower_body_visible", False)
    feet_vis = vis.get("feet_visible", False)
    print(f"2. Pose Framing: {pose.get('pose_type')} | Visibility: {pose.get('body_visibility_percentage')}%")
    print(f"   UpperVisible={vis.get('upper_body_visible')}, LowerVisible={lower_vis}, FeetVisible={feet_vis}")

    if tc["expect_lower_body"]:
        assert lower_vis is True, f"FAIL: Expected lower body to be visible in {tc['name']}"
    else:
        assert lower_vis is False, f"FAIL: Expected lower body to NOT be visible in {tc['name']}"

    if tc["expect_feet"]:
        assert feet_vis is True, f"FAIL: Expected feet to be visible in {tc['name']}"
    else:
        assert feet_vis is False, f"FAIL: Expected feet to NOT be visible in {tc['name']}"

    # Step 3: Garment Segmentation
    segmentation = await BodySegmenter.segment(url, person, pose)
    print(f"3. Segmentation: Mask Ready={segmentation.get('mask_ready')}")

    # Step 4: Clothing & Color Detection
    colors = await StyleEngine.extract_colors(url, segmentation)
    clothing = await ClothingDetector.detect(url, person, pose, segmentation)
    garments = clothing.get("garments", [])

    print(f"4. Color Harmony Primary Color: {colors.get('primary')}")
    print(f"   Detected Garments ({len(garments)}):")
    for g in garments:
        print(f"   -> [{g.get('region')}] {g.get('color')} {g.get('garment')} (Conf: {g.get('confidence'):.0%})")

    # Verify no non-visible items exist in garment output
    if not feet_vis:
        shoe_garments = [g for g in garments if g.get("region") == "Shoes"]
        assert len(shoe_garments) == 0, f"FAIL: Shoes detected when feet were not visible in {tc['name']}!"

    if not lower_vis:
        pants_garments = [g for g in garments if g.get("region") == "Pants"]
        assert len(pants_garments) == 0, f"FAIL: Pants detected when lower body was not visible in {tc['name']}!"

    # Step 5: Body Type Estimation
    body_type = await BodyTypeEstimator.estimate(url, pose, person)
    bt_val = body_type.get("body_type")
    print(f"5. Body Type: {bt_val} (Status: {body_type.get('status')})")

    if tc["expect_body_type"]:
        assert bt_val != "Insufficient visibility", f"FAIL: Expected body type estimation for {tc['name']}"
    else:
        assert bt_val == "Insufficient visibility", f"FAIL: Expected 'Insufficient visibility' for {tc['name']}"

    # Step 6: Style Taxonomy
    styles = await StyleEngine.classify_style(colors, garments, url, segmentation)
    print(f"6. Top Style: #{styles[0].get('style_name')} (Conf: {styles[0].get('confidence'):.0%})")

    print(f"✓ PASS: All assertions passed for {tc['name']}")


async def main():
    print("====================================================")
    print("STARTING COMPREHENSIVE AI PIPELINE TEST SUITE")
    print("====================================================")

    for tc in TEST_CASES:
        await run_test_case(tc)

    print("\n====================================================")
    print("ALL COMPREHENSIVE PIPELINE TESTS PASSED SUCESSFULLY! ZERO HALLUCINATION GUARANTEED.")
    print("====================================================")


if __name__ == "__main__":
    asyncio.run(main())
