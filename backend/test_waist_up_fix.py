import cv2
import numpy as np
import httpx
import asyncio

# Comprehensive Human Color Dictionary (RGB)
COLORS_DICT = {
    "Black":            (0, 0, 0),
    "White":            (255, 255, 255),
    "Charcoal Gray":    (54, 69, 79),
    "Light Gray":       (169, 169, 169),
    "Navy Blue":        (0, 0, 128),
    "Royal Blue":       (65, 105, 225),
    "Sky Blue":         (135, 206, 235),
    "Lime Yellow":      (215, 230, 120),
    "Light Olive Green":(180, 195, 110),
    "Pistachio Green":  (190, 215, 130),
    "Mustard Yellow":   (235, 200, 70),
    "Golden Yellow":    (255, 215, 0),
    "Sage Green":       (156, 175, 136),
    "Olive Green":      (107, 142, 35),
    "Cream White":      (255, 253, 208),
    "Beige":            (245, 245, 220),
    "Tan":              (210, 180, 140),
    "Brown":            (139, 90, 43),
    "Burgundy":         (128, 0, 32),
    "Dusty Pink":       (214, 163, 169),
}

def closest_color(rgb_val):
    min_dist = float('inf')
    best_name = "Unknown"
    r, g, b = int(rgb_val[0]), int(rgb_val[1]), int(rgb_val[2])
    for name, (cr, cg, cb) in COLORS_DICT.items():
        dist = (r - cr)**2 + (g - cg)**2 + (b - cb)**2
        if dist < min_dist:
            min_dist = dist
            best_name = name
    return best_name

def test_garment_color_extraction(crop: np.ndarray):
    """
    Extracts garment color by masking out skin tone & background pixels.
    """
    if crop is None or crop.size == 0:
        return "Neutral"

    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)

    # 1. Skin tone mask (HSV: H=0-25, S=20-170, V=80-255)
    lower_skin = np.array([0, 20, 80], dtype=np.uint8)
    upper_skin = np.array([25, 170, 255], dtype=np.uint8)
    skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)

    # 2. Border background mask
    border_pixels = np.vstack([
        rgb[0, :, :], rgb[-1, :, :],
        rgb[:, 0, :], rgb[:, -1, :]
    ])
    bg_color = np.median(border_pixels, axis=0)
    bg_dists = np.linalg.norm(rgb.reshape((-1, 3)) - bg_color, axis=1).reshape((crop.shape[0], crop.shape[1]))
    bg_mask = (bg_dists < 35).astype(np.uint8) * 255

    # 3. Combined mask: exclude skin AND background
    exclude_mask = cv2.bitwise_or(skin_mask, bg_mask)
    garment_mask = cv2.bitwise_not(exclude_mask)

    # Extract garment pixels
    fg_pixels = rgb[garment_mask > 0]
    if len(fg_pixels) < 50:
        fg_pixels = rgb[skin_mask == 0] # fallback: exclude skin only
    if len(fg_pixels) < 50:
        fg_pixels = rgb.reshape((-1, 3))

    # K-Means clustering
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, label, center = cv2.kmeans(fg_pixels.astype(np.float32), min(3, len(fg_pixels)), None, criteria, 5, cv2.KMEANS_RANDOM_CENTERS)

    counts = np.bincount(label.flatten())
    dom_idx = np.argmax(counts)
    dom_rgb = center[dom_idx]

    return closest_color(dom_rgb)

if __name__ == "__main__":
    print("Testing skin & background masked color extraction...")
    # Create test image: Skin neck region + Lime Yellow Shirt + Wooden background
    crop = np.zeros((200, 200, 3), dtype=np.uint8)
    crop[:, :] = (40, 80, 120)  # Wooden background (BGR)
    crop[30:170, 30:170] = (120, 230, 215) # Lime Yellow Shirt (BGR)
    crop[30:80, 80:120] = (140, 170, 220)  # Skin tone neck (BGR)

    result_color = test_garment_color_extraction(crop)
    print(f"Extracted Garment Color: {result_color}")
