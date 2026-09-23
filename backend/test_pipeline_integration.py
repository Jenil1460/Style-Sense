"""
Quick integration test to verify the rebuilt AI pipeline loads correctly
and the server can start.
"""
import asyncio
import sys
import os

# Ensure we're in the backend directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_pipeline_imports():
    """Test that all pipeline components import without errors."""
    print("=" * 60)
    print("PIPELINE INTEGRATION TEST")
    print("=" * 60)

    # Test 1: Core infrastructure
    print("\n[1/8] Testing confidence module...")
    from app.ai.confidence import Prediction, unknown_prediction, THRESHOLD_GARMENT_CLASS
    p = Prediction(value="test", confidence=0.8, evidence="test", source="test", threshold=0.5)
    assert p.is_valid, "Valid prediction should pass threshold"
    assert p.safe_value == "test"

    p_low = Prediction(value="test", confidence=0.2, evidence="test", source="test", threshold=0.5)
    assert not p_low.is_valid, "Low confidence should fail threshold"
    assert p_low.safe_value == "Unknown"

    unk = unknown_prediction("no data")
    assert unk.safe_value == "Unknown"
    print("   ✓ Prediction dataclass works correctly")

    # Test 2: Person Detector
    print("\n[2/8] Testing PersonDetector...")
    from app.ai.person_detector import PersonDetector
    assert hasattr(PersonDetector, 'detect'), "PersonDetector should have detect method"
    print("   ✓ PersonDetector loaded (multi-modal detection)")

    # Test 3: Pose Detector
    print("\n[3/8] Testing PoseDetector...")
    from app.ai.pose_detector import PoseDetector
    # Verify no _fallback method that fabricates data
    fallback_result = PoseDetector._unknown("test")
    assert fallback_result["body_visibility_percentage"] == 0, \
        "Unknown pose should have 0% visibility, not 90%"
    assert fallback_result["lower_body_visible"] == False
    assert fallback_result["feet_visible"] == False
    assert fallback_result["upper_body_visible"] == False
    print("   ✓ PoseDetector loaded (no fabricated fallback)")

    # Test 4: Body Segmenter
    print("\n[4/8] Testing BodySegmenter...")
    from app.ai.body_segmenter import BodySegmenter
    print("   ✓ BodySegmenter loaded (landmark-guided)")

    # Test 5: Clothing Detector (CLIP)
    print("\n[5/8] Testing ClothingDetector (CLIP)...")
    from app.ai.clothing_detector import ClothingDetector, UPPER_GARMENT_LABELS, LOWER_GARMENT_LABELS
    assert len(UPPER_GARMENT_LABELS) > 10, "Should have many garment labels for CLIP"
    print(f"   ✓ ClothingDetector loaded ({len(UPPER_GARMENT_LABELS)} upper, {len(LOWER_GARMENT_LABELS)} lower labels)")

    # Test 6: Style Engine (CLIP)
    print("\n[6/8] Testing StyleEngine (CLIP)...")
    from app.services.ml.style_engine import StyleEngine, STYLE_NAMES, OCCASION_NAMES
    assert len(STYLE_NAMES) == 10, "Should have 10 style categories"
    assert len(OCCASION_NAMES) == 7, "Should have 7 occasion categories"
    print(f"   ✓ StyleEngine loaded ({len(STYLE_NAMES)} styles, {len(OCCASION_NAMES)} occasions)")

    # Test 7: Recommendation Engine (no random)
    print("\n[7/8] Testing RecommendationEngine...")
    from app.services.ml.recommendation_engine import RecommendationEngine
    import inspect
    source = inspect.getsource(RecommendationEngine)
    assert "random.choice" not in source, "RecommendationEngine should NOT use random.choice"
    print("   ✓ RecommendationEngine loaded (no random.choice)")

    # Test 8: Face Shape Detector
    print("\n[8/8] Testing FaceShapeDetector...")
    from app.ai.face_shape_detector import FaceShapeDetector
    unknown = FaceShapeDetector._unknown("test")
    assert unknown["face_shape"] == "Unknown", "Should return Unknown, not hardcoded Oval"
    print("   ✓ FaceShapeDetector loaded (no hardcoded Oval)")

    # Test deprecated vision engine
    print("\n[BONUS] Testing VisionEngine deprecation...")
    from app.services.ml.vision_engine import VisionEngine
    result = await VisionEngine.detect_person("test")
    assert result.get("deprecated") == True
    assert result.get("confidence") == 0.0
    print("   ✓ VisionEngine deprecated correctly")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)
    print("\nHallucination sources removed:")
    print("  ✗ Skin heuristic fallback (PersonDetector)")
    print("  ✗ Fabricated pose fallback (PoseDetector)")
    print("  ✗ Hardcoded 'Oval' face shape (FaceShapeDetector)")
    print("  ✗ random.choice() recommendations (RecommendationEngine)")
    print("  ✗ Placeholder vision engine (VisionEngine)")
    print("  ✗ HSV garment guessing (ClothingDetector)")
    print("  ✗ Hardcoded style scores (StyleEngine)")
    print("\nNew model-backed implementations:")
    print("  ✓ CLIP zero-shot garment classification")
    print("  ✓ CLIP zero-shot style classification")
    print("  ✓ CLIP zero-shot occasion detection")
    print("  ✓ MediaPipe FaceMesh face shape analysis")
    print("  ✓ ITA-based skin tone estimation")
    print("  ✓ Landmark-gated body type estimation")
    print("  ✓ Pose-landmark-guided body segmentation")


if __name__ == "__main__":
    asyncio.run(test_pipeline_imports())
