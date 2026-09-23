"""
Comprehensive Test Suite for StyleSense AI Virtual Try-On Pipeline.
Validates real VTON pipeline, input validation, multi-provider execution (HF + Gemini fallback),
and output validation.
"""

import asyncio
import logging
import sys
import os

# Ensure backend root is in sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.ml.tryon_engine import TryonEngine
from app.ai.person_detector import PersonDetector

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("VTONTest")

TEST_CASES = [
    {
        "name": "1. Person + black suit",
        "url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=1000&auto=format&fit=crop",
        "outfit": "wear black suit",
        "expect_success": True
    },
    {
        "name": "2. Person + white oversized hoodie",
        "url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=1000&auto=format&fit=crop",
        "outfit": "wear white oversized hoodie",
        "expect_success": True
    },
    {
        "name": "3. Person + blue denim jacket",
        "url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?q=80&w=1000&auto=format&fit=crop",
        "outfit": "wear blue denim jacket",
        "expect_success": True
    },
    {
        "name": "4. Person + beige formal blazer",
        "url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?q=80&w=1000&auto=format&fit=crop",
        "outfit": "wear beige formal blazer",
        "expect_success": True
    },
    {
        "name": "5. Person + traditional black kurta",
        "url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=1000&auto=format&fit=crop",
        "outfit": "wear traditional black kurta",
        "expect_success": True
    },
    {
        "name": "6. Person + garment reference image",
        "url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=1000&auto=format&fit=crop",
        "outfit": "wear black leather jacket",
        "garment_url": "https://images.unsplash.com/photo-1551028719-00167b16eac5?q=80&w=1000&auto=format&fit=crop",
        "expect_success": True
    },
    {
        "name": "7. Upper-body image",
        "url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=1000&auto=format&fit=crop",
        "outfit": "wear red velvet blazer",
        "expect_success": True
    },
    {
        "name": "8. Full-body image",
        "url": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?q=80&w=1000&auto=format&fit=crop",
        "outfit": "wear navy blue business suit",
        "expect_success": True
    },
    {
        "name": "9. Image without person (Landscape)",
        "url": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?q=80&w=1000&auto=format&fit=crop",
        "outfit": "wear black suit",
        "expect_success": False,
        "expected_message": "Virtual try-on requires a clear image of a person."
    },
    {
        "name": "10. Invalid image URL",
        "url": "https://invalid-domain-stylesense-test-12345.com/nonexistent.jpg",
        "outfit": "wear black suit",
        "expect_success": False,
        "expected_message": "Virtual try-on requires a clear image of a person."
    }
]


async def run_vton_test(tc: dict):
    print(f"\n====================================================")
    print(f"RUNNING VTON TEST: {tc['name']}")
    print(f"URL: {tc['url']}")
    print(f"Outfit: {tc['outfit']}")
    if tc.get("garment_url"):
        print(f"Garment Ref: {tc['garment_url']}")
    print(f"====================================================")

    res = await TryonEngine.generate(
        source_image_url=tc["url"],
        outfit_description=tc["outfit"],
        garment_image_url=tc.get("garment_url")
    )

    print(f"Result Success: {res.get('success')}")
    print(f"Result Status: {res.get('status')}")
    print(f"Provider: {res.get('provider')}")
    print(f"Model: {res.get('model')}")
    print(f"Fallback Used: {res.get('fallback_used')}")
    print(f"Generation Time: {res.get('generation_time')}")
    print(f"Message: {res.get('message')}")
    print(f"Generated Image URL: {res.get('generated_image_url')}")

    if tc["expect_success"]:
        assert res.get("success") is True, f"FAIL: Expected success for {tc['name']}. Got: {res.get('message')}"
        assert res.get("generated_image_url") is not None, f"FAIL: Expected generated_image_url for {tc['name']}"
        print(f"✓ PASS: {tc['name']} generated try-on result via {res.get('provider')} ({res.get('model')})")
    else:
        assert res.get("success") is False, f"FAIL: Expected failure for {tc['name']}"
        if tc.get("expected_message"):
            assert tc["expected_message"] in res.get("message", ""), f"FAIL: Expected '{tc['expected_message']}' in message. Got: '{res.get('message')}'"
        print(f"✓ PASS: {tc['name']} correctly rejected with message: '{res.get('message')}'")


async def main():
    print("====================================================")
    print("STARTING VIRTUAL TRY-ON PIPELINE INTEGRATION TEST SUITE")
    print("====================================================")

    for tc in TEST_CASES:
        await run_vton_test(tc)

    print("\n====================================================")
    print("ALL VIRTUAL TRY-ON PIPELINE INTEGRATION TESTS PASSED SUCCESSFULLY!")
    print("====================================================")


if __name__ == "__main__":
    asyncio.run(main())
