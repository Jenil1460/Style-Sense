import asyncio
import cv2
import numpy as np
import httpx
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_user_image")

def test_multimodal_person_detection(image: np.ndarray):
    img_h, img_w = image.shape[:2]
    print(f"Image Resolution: {img_w}x{img_h} px")

    # 1. Test YOLO
    yolo_detected = False
    yolo_conf = 0.0
    try:
        from ultralytics import YOLO
        model = YOLO("yolov8n.pt")
        results = model.predict(source=image, conf=0.20, verbose=False)
        boxes = results[0].boxes
        names = results[0].names
        for box in boxes:
            cls_id = int(box.cls[0].item())
            conf = float(box.conf[0].item())
            if cls_id == 0:
                yolo_detected = True
                yolo_conf = max(yolo_conf, conf)
        print(f"[YOLO] Detected: {yolo_detected}, Conf: {yolo_conf:.4f}")
    except Exception as e:
        print(f"[YOLO] Exception: {e}")

    # 2. Test MediaPipe Pose (Shoulders / Face keypoints)
    mp_detected = False
    mp_conf = 0.0
    try:
        import mediapipe as mp
        mp_pose = mp.solutions.pose.Pose(static_image_mode=True, min_detection_confidence=0.4)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        res = mp_pose.process(rgb)
        if res.pose_landmarks:
            lm = res.pose_landmarks.landmark
            # Check shoulder visibility (11=left_shoulder, 12=right_shoulder) or nose (0)
            shoulder_vis = (lm[11].visibility + lm[12].visibility) / 2
            nose_vis = lm[0].visibility
            if shoulder_vis > 0.3 or nose_vis > 0.3:
                mp_detected = True
                mp_conf = max(shoulder_vis, nose_vis)
        print(f"[MediaPipe Pose] Detected: {mp_detected}, Conf: {mp_conf:.4f}")
    except Exception as e:
        print(f"[MediaPipe Pose] Exception: {e}")

    # 3. Test OpenCV Haar / DNN Face Detection
    face_detected = False
    face_conf = 0.0
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)
        if len(faces) > 0:
            face_detected = True
            face_conf = 0.90
        print(f"[OpenCV Face] Detected: {face_detected}, Count: {len(faces)}")
    except Exception as e:
        print(f"[OpenCV Face] Exception: {e}")

    final_decision = yolo_detected or mp_detected or face_detected
    print(f"\n===> FINAL MULTI-MODAL PERSON DECISION: {'PERSON DETECTED' if final_decision else 'NO PERSON DETECTED'}")

if __name__ == "__main__":
    # Test on unsplash portrait image
    url = "https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=1000&auto=format&fit=crop"
    async def run():
        async with httpx.AsyncClient(timeout=10.0) as c:
            r = await c.get(url)
            raw = np.frombuffer(r.content, np.uint8)
            img = cv2.imdecode(raw, cv2.IMREAD_COLOR)
            test_multimodal_person_detection(img)
    asyncio.run(run())
