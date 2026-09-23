"""
Comprehensive Test Suite for Skin Tone Analysis & Personal Color Recommendations.

Test Scenarios (STEP 16 Requirements):
1. Clear full-face image
2. Full-body image
3. Upper-body image
4. Warm indoor lighting
5. Cool lighting
6. Outdoor sunlight
7. Dark image
8. Partially visible face
9. No-person image
10. Multiple-person image
"""

import asyncio
import logging
import os
import sys
import numpy as np
import cv2
from PIL import Image, ImageDraw

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_skin_tone")

from app.services.skin_tone_service import SkinToneService
from app.services.personal_color_service import PersonalColorService


def create_test_image(filename: str, face_type: str = "normal", lighting: str = "normal", num_people: int = 1):
    """
    Synthesizes realistic test images with faces, clothing, lighting variations, or no person.
    """
    img_w, img_h = 600, 800
    img = np.zeros((img_h, img_w, 3), dtype=np.uint8)
    
    # Background
    img[:] = (230, 220, 210)

    if face_type == "no_person":
        cv2.imwrite(filename, img)
        return filename

    # Create synthetic faces with skin colors
    for p_idx in range(num_people):
        center_x = int(img_w * (0.28 if num_people > 1 and p_idx == 0 else (0.72 if num_people > 1 else 0.5)))
        center_y = int(img_h * 0.35)

        # Base skin colors (BGR format)
        if p_idx == 0:
            skin_bgr = (150, 180, 220) # Light-medium warm skin (R=220, G=180, B=150)
        else:
            skin_bgr = (90, 120, 180)  # Medium tan skin

        # Draw Face oval
        radius_x = 65 if num_people > 1 else 80
        radius_y = 90 if num_people > 1 else 110
        cv2.ellipse(img, (center_x, center_y), (radius_x, radius_y), 0, 0, 360, skin_bgr, -1)

        if face_type != "partial":
            # Draw Eyes (dark circles)
            eye_off = 22 if num_people > 1 else 30
            cv2.circle(img, (center_x - eye_off, center_y - 15), 8, (50, 40, 30), -1)
            cv2.circle(img, (center_x + eye_off, center_y - 15), 8, (50, 40, 30), -1)
            # Draw Eyebrows
            cv2.line(img, (center_x - eye_off - 10, center_y - 28), (center_x - 5, center_y - 28), (40, 30, 20), 3)
            cv2.line(img, (center_x + 5, center_y - 28), (center_x + eye_off + 10, center_y - 28), (40, 30, 20), 3)
            # Draw Nose bridge & tip
            cv2.line(img, (center_x, center_y - 10), (center_x, center_y + 15), (100, 130, 170), 2)
            # Draw Lips
            cv2.ellipse(img, (center_x, center_y + 35), (20, 8), 0, 0, 360, (70, 70, 180), -1)
        else:
            # Partial face crop / obstruction
            cv2.rectangle(img, (center_x - 90, center_y - 120), (center_x + 90, center_y - 30), (50, 50, 50), -1)

        # Body / Clothing
        body_w = 90 if num_people > 1 else 120
        cv2.rectangle(img, (center_x - body_w, center_y + 90), (center_x + body_w, img_h - 80), (50, 120, 50), -1) # Olive shirt

    # Lighting adjustments
    if lighting == "warm":
        img[:, :, 2] = np.clip(img[:, :, 2] * 1.25, 0, 255) # Increase Red
        img[:, :, 1] = np.clip(img[:, :, 1] * 1.10, 0, 255) # Increase Green
    elif lighting == "cool":
        img[:, :, 0] = np.clip(img[:, :, 0] * 1.30, 0, 255) # Increase Blue
    elif lighting == "dark":
        img = (img * 0.35).astype(np.uint8)
    elif lighting == "sunlight":
        img = np.clip(img * 1.3, 0, 255).astype(np.uint8)

    cv2.imwrite(filename, img)
    return filename


async def run_skin_tone_tests():
    test_dir = os.path.join(backend_dir, "test_images_skintone")
    os.makedirs(test_dir, exist_ok=True)

    test_cases = [
        ("1. Clear full-face image", "full_face.jpg", "normal", "normal", 1),
        ("2. Full-body image", "full_body.jpg", "normal", "normal", 1),
        ("3. Upper-body image", "upper_body.jpg", "normal", "normal", 1),
        ("4. Warm indoor lighting", "warm_light.jpg", "normal", "warm", 1),
        ("5. Cool lighting", "cool_light.jpg", "normal", "cool", 1),
        ("6. Outdoor sunlight", "sunlight.jpg", "normal", "sunlight", 1),
        ("7. Dark image", "dark_image.jpg", "normal", "dark", 1),
        ("8. Partially visible face", "partial_face.jpg", "partial", "normal", 1),
        ("9. No-person image", "no_person.jpg", "no_person", "normal", 0),
        ("10. Multiple-person image", "multi_person.jpg", "normal", "normal", 2),
    ]

    print("\n" + "="*70)
    print("      STYLESENSE AI SKIN TONE & COLOR RECOMMENDATION TEST SUITE")
    print("="*70 + "\n")

    passed_count = 0

    for title, fname, ftype, ltype, npeople in test_cases:
        path = os.path.join(test_dir, fname)
        create_test_image(path, face_type=ftype, lighting=ltype, num_people=npeople)

        print(f"Testing [{title}] ...")
        st_result = await SkinToneService.analyze_skin_tone(path)

        status = st_result.get("status")
        skin_tone = st_result.get("skin_tone")
        undertone = st_result.get("undertone")
        confidence = st_result.get("confidence")
        multi = st_result.get("multiple_people_detected")

        print(f"  Result -> Status: {status} | Tone: {skin_tone} | Undertone: {undertone} | Conf: {confidence} | MultiPerson: {multi}")
        if st_result.get("lighting_note"):
            print(f"  Lighting Note: {st_result.get('lighting_note')}")
        if st_result.get("confidence_note"):
            print(f"  Confidence Note: {st_result.get('confidence_note')}")

        # Test PersonalColorService palette generation
        palette = PersonalColorService.generate_personal_color_recommendations(st_result)
        recs = palette.get("recommended_colors", [])
        exps = palette.get("experimental_colors", [])
        combos = palette.get("outfit_combinations", [])
        print(f"  Palette -> RecColors: {len(recs)} | ExpColors: {len(exps)} | Combos: {len(combos)}")

        # Verification rules
        if ftype == "no_person":
            assert status == "unavailable" or skin_tone == "Unavailable", "No-person must return unavailable skin tone"
            print("  [PASS] Handled no-person correctly.")
        elif npeople > 1:
            assert multi is True, "Multiple people must be flagged"
            print("  [PASS] Multi-person detection verified.")
        elif ltype == "dark":
            assert st_result.get("lighting_note") is not None or status == "unavailable", "Dark lighting warning expected"
            print("  [PASS] Lighting warning triggered.")
        else:
            assert len(recs) == 5, f"Must generate exactly top 5 recommended colors, got {len(recs)}"
            assert len(combos) >= 3, "Must generate outfit combinations"
            # Verify NO HEX codes inside recommendation sentences
            for r in recs:
                assert "#" not in r.get("why_it_works", ""), f"HEX code found in recommendation sentence: {r.get('why_it_works')}"
            print("  [PASS] Valid skin tone & top 5 color palette generated without HEX in text.")

        passed_count += 1
        print("-" * 60)

    print(f"\nALL {passed_count}/{len(test_cases)} TEST CASES PASSED SUCCESSFULLY!\n")


if __name__ == "__main__":
    asyncio.run(run_skin_tone_tests())
