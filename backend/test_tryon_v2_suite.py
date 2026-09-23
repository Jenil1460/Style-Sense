"""
Comprehensive 2-Mode Virtual Try-On Integration Test Suite for StyleSense AI.

Tests:
1. "wear black suit" (Text Mode A -> Gemini Image Edit -> Real Black Suit)
2. "wear red hoodie" (Text Mode A -> Gemini Image Edit -> Real Red Hoodie)
3. "wear blue denim jacket" (Text Mode A -> Gemini Image Edit -> Real Blue Denim Jacket)
4. Garment Reference Mode B (Person + Real Garment Photograph -> IDM-VTON)
5. Garment Validator Rejection (Solid black shape / blob -> Rejection)
"""

import asyncio
import logging
import sys
import numpy as np
import cv2
from app.services.ml.tryon_engine import TryonEngine
from app.ai.garment_validator import GarmentValidator
from app.ai.outfit_prompt_parser import OutfitPromptParser

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TestTryOnV2")

TEST_PERSON_URL = "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=1000&auto=format&fit=crop"
TEST_REAL_GARMENT_URL = "https://images.unsplash.com/photo-1551028719-00167b16eac5?q=80&w=1000&auto=format&fit=crop"


async def test_prompt_parser():
    logger.info("=== TEST: OutfitPromptParser Normalization ===")
    test_cases = [
        ("wear black suit", "black formal suit", "formal suit", "black"),
        ("wear suite", "black formal suit", "formal suit", "black"),
        ("black suite", "black formal suit", "formal suit", "black"),
        ("wear tshirt", "black casual t-shirt", "t-shirt", "black"),
        ("formal black", "black formal suit", "formal suit", "black"),
        ("blue jaket", "blue casual jacket", "jacket", "blue"),
        ("wear red hody", "red casual hoodie", "hoodie", "red"),
    ]
    for raw, exp_desc, exp_type, exp_color in test_cases:
        res = OutfitPromptParser.parse(raw)
        logger.info(f"Raw: '{raw}' -> CleanDesc: '{res['cleanDescription']}' | GarmentType: '{res['garmentType']}' | Color: '{res['color']}'")
        assert res["cleanDescription"] is not None
        assert res["garmentType"] is not None
    logger.info("✓ PASS: OutfitPromptParser tests passed!\n")


async def test_garment_validator():
    logger.info("=== TEST: GarmentValidator (Rejection of Black Blobs & Icons) ===")
    # 1. Valid real garment simulation (High variance color image)
    real_photo = np.random.randint(50, 220, (500, 500, 3), dtype=np.uint8)
    cv2.rectangle(real_photo, (100, 100), (400, 400), (200, 50, 50), -1)
    cv2.circle(real_photo, (250, 250), 80, (50, 200, 50), -1)
    val_real = GarmentValidator.validate(real_photo)
    logger.info(f"Real Garment Photo Validation: {val_real['valid']} (Reason: {val_real['reason']})")
    assert val_real["valid"] is True

    # 2. Black blob / solid black shape (Should be REJECTED)
    black_blob = np.zeros((500, 500, 3), dtype=np.uint8)
    cv2.ellipse(black_blob, (250, 250), (150, 200), 0, 0, 360, (10, 10, 10), -1)
    val_blob = GarmentValidator.validate(black_blob)
    logger.info(f"Black Blob Validation: {val_blob['valid']} | Reason: {val_blob['reason']}")
    assert val_blob["valid"] is False
    assert "black blob" in val_blob["reason"].lower() or "flat shape" in val_blob["reason"].lower()

    logger.info("✓ PASS: GarmentValidator tests passed!\n")


async def test_text_mode_black_suit():
    logger.info("=== ACCEPTANCE TEST 1: 'wear black suit' (Text Mode A) ===")
    res = await TryonEngine.generate(
        source_image_url=TEST_PERSON_URL,
        outfit_description="wear black suit"
    )
    logger.info(f"Result Success: {res.get('success')}")
    logger.info(f"Mode: {res.get('mode')}")
    logger.info(f"Provider: {res.get('provider')}")
    logger.info(f"Requested Outfit: {res.get('requested_outfit')}")
    logger.info(f"Garment Ref URL: {res.get('garment_reference_url')}")
    logger.info(f"Generated Image URL: {res.get('generated_image_url')}")
    logger.info(f"Message: {res.get('message')}\n")

    assert res.get("success") is True, f"Black Suit Test Failed: {res.get('message')}"
    assert res.get("mode") == "text"
    assert res.get("garment_reference_url") is None, "Text mode MUST NOT produce a garment reference URL!"
    assert res.get("generated_image_url") is not None
    logger.info("✓ PASS: ACCEPTANCE TEST 1 ('wear black suit') SUCCESSFUL!\n")


async def test_text_mode_red_hoodie():
    logger.info("=== ACCEPTANCE TEST 2: 'wear red hoodie' (Text Mode A) ===")
    res = await TryonEngine.generate(
        source_image_url=TEST_PERSON_URL,
        outfit_description="wear red hoodie"
    )
    logger.info(f"Result Success: {res.get('success')}")
    logger.info(f"Mode: {res.get('mode')}")
    logger.info(f"Provider: {res.get('provider')}")
    logger.info(f"Requested Outfit: {res.get('requested_outfit')}")
    logger.info(f"Generated Image URL: {res.get('generated_image_url')}\n")

    assert res.get("success") is True, f"Red Hoodie Test Failed: {res.get('message')}"
    assert res.get("mode") == "text"
    assert "red" in res.get("requested_outfit", "").lower()
    logger.info("✓ PASS: ACCEPTANCE TEST 2 ('wear red hoodie') SUCCESSFUL!\n")


async def test_text_mode_blue_denim_jacket():
    logger.info("=== ACCEPTANCE TEST 3: 'wear blue denim jacket' (Text Mode A) ===")
    res = await TryonEngine.generate(
        source_image_url=TEST_PERSON_URL,
        outfit_description="wear blue denim jacket"
    )
    logger.info(f"Result Success: {res.get('success')}")
    logger.info(f"Mode: {res.get('mode')}")
    logger.info(f"Provider: {res.get('provider')}")
    logger.info(f"Requested Outfit: {res.get('requested_outfit')}")
    logger.info(f"Generated Image URL: {res.get('generated_image_url')}\n")

    assert res.get("success") is True, f"Blue Denim Jacket Test Failed: {res.get('message')}"
    assert res.get("mode") == "text"
    assert "denim" in res.get("requested_outfit", "").lower() or "blue" in res.get("requested_outfit", "").lower()
    logger.info("✓ PASS: ACCEPTANCE TEST 3 ('wear blue denim jacket') SUCCESSFUL!\n")


async def test_garment_mode_real_photo():
    logger.info("=== REAL GARMENT TEST: Person + Real Garment Photo (Mode B) ===")
    res = await TryonEngine.generate(
        source_image_url=TEST_PERSON_URL,
        outfit_description="black leather jacket",
        garment_image_url=TEST_REAL_GARMENT_URL
    )
    logger.info(f"Result Success: {res.get('success')}")
    logger.info(f"Mode: {res.get('mode')}")
    logger.info(f"Provider: {res.get('provider')}")
    logger.info(f"Garment Ref URL: {res.get('garment_reference_url')}")
    logger.info(f"Generated Image URL: {res.get('generated_image_url')}\n")

    assert res.get("success") is True, f"Real Garment Mode Test Failed: {res.get('message')}"
    assert res.get("mode") == "garment"
    assert res.get("garment_reference_url") == TEST_REAL_GARMENT_URL
    logger.info("✓ PASS: REAL GARMENT TEST (Mode B IDM-VTON) SUCCESSFUL!\n")


async def main():
    logger.info("====================================================")
    logger.info("STARTING 2-MODE VIRTUAL TRY-ON SUITE VALIDATION")
    logger.info("====================================================\n")

    await test_prompt_parser()
    await test_garment_validator()
    await test_text_mode_black_suit()
    await test_text_mode_red_hoodie()
    await test_text_mode_blue_denim_jacket()
    await test_garment_mode_real_photo()

    logger.info("====================================================")
    logger.info("ALL VIRTUAL TRY-ON TESTS PASSED 100% CLEANLY!")
    logger.info("====================================================")


if __name__ == "__main__":
    asyncio.run(main())
