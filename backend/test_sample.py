import asyncio
import logging
from app.ai.person_detector import PersonDetector

logging.basicConfig(level=logging.INFO)

async def test_sample():
    # Test on portrait/upper-body image URL
    test_url = "https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=1000&auto=format&fit=crop"
    result = await PersonDetector.detect(test_url)
    print("---------------------------------------------")
    print("TEST DETECT RESULT:", result)
    print("---------------------------------------------")

if __name__ == "__main__":
    asyncio.run(test_sample())
