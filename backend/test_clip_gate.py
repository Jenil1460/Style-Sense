"""Test CLIP gate specifically on images where YOLO might false-positive."""
import asyncio
import sys
sys.path.insert(0, ".")

async def test():
    from app.ai.person_detector import PersonDetector

    test_cases = [
        # Person photos (should PASS)
        ("https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400", "Portrait person", True),
        ("https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=400", "Fashion full body", True),
        ("https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400", "Female portrait", True),

        # Non-person photos (should be REJECTED)
        ("https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?w=400", "Laptop/machine", False),
        ("https://images.unsplash.com/photo-1518770660439-4636190af475?w=400", "Circuit board", False),
        ("https://images.unsplash.com/photo-1526738549149-8e07eca6c147?w=400", "Phone device", False),
        ("https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400", "Food plate", False),
        ("https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=400", "Dog animal", False),
    ]

    passed = 0
    failed = 0

    for url, label, expect_person in test_cases:
        print(f"\n{'='*60}")
        print(f"TEST: {label} | Expected: {'PERSON' if expect_person else 'REJECT'}")
        print(f"{'='*60}")

        result = await PersonDetector.detect(url)
        detected = result["detected"]
        conf = result.get("confidence", 0)
        reason = result.get("reason", "")
        clip = result.get("clip_verification", {})

        print(f"  Detected: {detected} (conf={conf})")
        print(f"  Reason: {reason}")
        if clip:
            print(f"  CLIP: {clip.get('evidence', '')}")

        if detected == expect_person:
            print(f"  >>> PASS")
            passed += 1
        else:
            print(f"  >>> FAIL (expected {'detected' if expect_person else 'rejected'})")
            failed += 1

    print(f"\n{'='*60}")
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)}")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(test())
