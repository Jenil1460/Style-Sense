import cv2
import numpy as np

def detect_face_or_upperbody(image: np.ndarray) -> list:
    boxes = []
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 1. Frontal Face Cascade
        face_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(face_path)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30))
        
        for (x, y, w, h) in faces:
            # Expand face box to full upper body estimate
            bx1 = max(0, int(x - w * 1.0))
            by1 = max(0, int(y - h * 0.2))
            bx2 = min(image.shape[1], int(x + w * 2.0))
            by2 = min(image.shape[0], int(y + h * 4.5))
            boxes.append({
                "confidence": 0.92,
                "x_min_px": bx1, "y_min_px": by1,
                "x_max_px": bx2, "y_max_px": by2,
                "source": "opencv_face"
            })

        # 2. Upper Body Cascade
        upper_path = cv2.data.haarcascades + 'haarcascade_upperbody.xml'
        upper_cascade = cv2.CascadeClassifier(upper_path)
        uppers = upper_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(60, 60))
        
        for (x, y, w, h) in uppers:
            boxes.append({
                "confidence": 0.85,
                "x_min_px": int(x), "y_min_px": int(y),
                "x_max_px": int(x + w), "y_max_px": int(y + h),
                "source": "opencv_upperbody"
            })

    except Exception as e:
        print("Cascade detection error:", e)

    return boxes

if __name__ == "__main__":
    # Test on a dummy black image with a drawn white circle
    dummy = np.zeros((600, 400, 3), dtype=np.uint8)
    boxes = detect_face_or_upperbody(dummy)
    print("Boxes detected on dummy:", len(boxes))
