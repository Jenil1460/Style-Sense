import asyncio
import logging
import os
import sys

# Set root log level
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("test_full_ai_pipeline")

from app.ai.person_detector import PersonDetector

async def run_pipeline_validation():
    print("\n====================================================")
    print("AI PIPELINE STEP-BY-STEP VERIFICATION & MODEL TEST")
    print("====================================================\n")

    test_cases = [
        {
            "name": "Full-Body Person Photo",
            "url": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?q=80&w=1000&auto=format&fit=crop",
            "expected_person": True
        },
        {
            "name": "Upper-Body / Portrait Person Photo",
            "url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=1000&auto=format&fit=crop",
            "expected_person": True
        },
        {
            "name": "No-Person Photo (Scenery / Landscape)",
            "url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?q=80&w=1000&auto=format&fit=crop",
            "expected_person": False
        }
    ]

    passed_count = 0

    for idx, test in enumerate(test_cases, 1):
        print(f"----------------------------------------------------")
        print(f"Test #{idx}: {test['name']}")
        print(f"URL: {test['url']}")
        print(f"Expected Person Detection: {test['expected_person']}")
        print(f"----------------------------------------------------")

        res = await PersonDetector.detect(test["url"])
        detected = res.get("detected", False)
        confidence = res.get("confidence", 0.0)
        num_dets = res.get("num_detections", 0)
        reason = res.get("reason", "")

        print(f"--> Result Detected: {detected}")
        print(f"--> Confidence: {confidence:.4f}")
        print(f"--> Total Person BBoxes: {num_dets}")
        if reason:
            print(f"--> Reason: {reason}")

        if detected == test["expected_person"]:
            print(f"✅ TEST #{idx} PASSED!")
            passed_count += 1
        else:
            print(f"❌ TEST #{idx} FAILED!")

    print("\n====================================================")
    print(f"VERIFICATION SUMMARY: {passed_count}/{len(test_cases)} TEST CASES PASSED")
    print("====================================================\n")

if __name__ == "__main__":
    asyncio.run(run_pipeline_validation())
