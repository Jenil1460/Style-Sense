import asyncio
import logging

from app.ai.person_detector import PersonDetector
from app.ai.pose_detector import PoseDetector

logging.basicConfig(level=logging.INFO)

async def test():
    # Dancing full body photo
    url1 = "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?q=80&w=1000&auto=format&fit=crop"
    p1 = await PersonDetector.detect(url1)
    pose1 = await PoseDetector.detect(url1, p1)

    print("\n--- PHOTO 1 (Full Body) ---")
    print(f"Pose Type: {pose1.get('pose_type')}")
    print(f"Lower Body Visible: {pose1.get('lower_body_visible')}")
    print(f"Feet Visible: {pose1.get('feet_visible')}")
    print(f"Body Visibility %: {pose1.get('body_visibility_percentage')}%")

    # Portrait photo
    url2 = "https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=1000&auto=format&fit=crop"
    p2 = await PersonDetector.detect(url2)
    pose2 = await PoseDetector.detect(url2, p2)

    print("\n--- PHOTO 2 (Portrait) ---")
    print(f"Pose Type: {pose2.get('pose_type')}")
    print(f"Lower Body Visible: {pose2.get('lower_body_visible')}")
    print(f"Feet Visible: {pose2.get('feet_visible')}")
    print(f"Body Visibility %: {pose2.get('body_visibility_percentage')}%")

if __name__ == "__main__":
    asyncio.run(test())
