import asyncio
import cv2
import numpy as np
import httpx
import logging
import os
import sys

# Configure root logger to output to stdout
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("test_pipeline_debug")

async def test_debug():
    # Sample public image URL of a person
    test_urls = [
        "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?q=80&w=1000&auto=format&fit=crop", # Fashion model photo
        "https://res.cloudinary.com/demo/image/upload/v1312461204/sample.jpg" # Sample image
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print("====================================================")
    print("STEP 1: Testing Model Loading")
    print("====================================================")
    try:
        from ultralytics import YOLO
        print("[1.1] Importing ultralytics: SUCCESS")
        model = YOLO("yolov8n.pt")
        print("[1.2] YOLO('yolov8n.pt') loaded: SUCCESS")
    except Exception as e:
        print(f"[1.1/1.2] FAILED loading model: {e}")
        return

    for url in test_urls:
        print("\n====================================================")
        print(f"STEP 2: Testing Image Fetch & Decode for URL: {url}")
        print("====================================================")
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True, headers=headers) as client:
                resp = await client.get(url)
                print(f"[2.1] HTTP status: {resp.status_code}")
                resp.raise_for_status()
                raw_bytes = np.frombuffer(resp.content, np.uint8)
                print(f"[2.2] Downloaded bytes size: {len(raw_bytes)} bytes")
        except Exception as e:
            print(f"[2.1] Image download FAILED: {e}")
            continue

        image = cv2.imdecode(raw_bytes, cv2.IMREAD_COLOR)
        if image is None:
            print("[2.3] cv2.imdecode FAILED: Returned None")
            continue
        
        img_h, img_w = image.shape[:2]
        print(f"[2.3] Image decode SUCCESS: {img_w}x{img_h} px, channels={image.shape[2]}")

        print("====================================================")
        print("STEP 3: Testing YOLO Inference")
        print("====================================================")
        try:
            # Predict all classes first to inspect what YOLO sees
            results = model.predict(source=image, conf=0.25, verbose=False)
            boxes = results[0].boxes
            names = results[0].names
            print(f"[3.1] Raw detections count: {len(boxes)}")
            
            for i, box in enumerate(boxes):
                cls_id = int(box.cls[0].item())
                cls_name = names.get(cls_id, "unknown")
                conf = float(box.conf[0].item())
                xyxy = [round(v) for v in box.xyxy[0].tolist()]
                print(f"   Detection #{i+1}: Class ID={cls_id} ({cls_name}), Confidence={conf:.4f}, BBox={xyxy}")

            # Specifically filter for Person class (class 0)
            person_boxes = [b for b in boxes if int(b.cls[0].item()) == 0]
            print(f"[3.2] Person class (0) detections count: {len(person_boxes)}")
            if len(person_boxes) > 0:
                best_person = max(person_boxes, key=lambda b: float(b.conf[0].item()))
                print(f"   BEST PERSON: Confidence={float(best_person.conf[0].item()):.4f}")
            else:
                print("   NO PERSON DETECTED AT CONF 0.25!")

        except Exception as e:
            print(f"[3.1] Inference FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_debug())
