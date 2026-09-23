import cv2
import numpy as np
import httpx
import asyncio

# Human color lookup
COLORS_DICT = {
    "Black":         (0, 0, 0),
    "White":         (255, 255, 255),
    "Charcoal Gray": (54, 69, 79),
    "Light Gray":    (169, 169, 169),
    "Navy Blue":     (0, 0, 128),
    "Royal Blue":    (65, 105, 225),
    "Sage Green":    (156, 175, 136),
    "Cream White":   (255, 253, 208),
    "Beige":         (245, 245, 220),
    "Tan":           (210, 180, 140),
    "Brown":         (139, 90, 43),
    "Mauve / Brown": (120, 80, 85),
    "Burgundy":      (128, 0, 32),
    "Wine Red":      (114, 47, 55),
    "Mustard Yellow":(255, 219, 88),
    "Golden Yellow": (255, 215, 0),
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

def test_background_subtracted_color(crop: np.ndarray):
    """
    Extracts garment color while filtering out dominant background colors.
    """
    if crop is None or crop.size == 0:
        return "Neutral"
    
    # Convert BGR to RGB
    rgb_crop = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
    h, w = crop.shape[:2]
    
    # 1. Estimate background color from outer border pixels
    border_pixels = np.vstack([
        rgb_crop[0, :, :], rgb_crop[-1, :, :],
        rgb_crop[:, 0, :], rgb_crop[:, -1, :]
    ])
    bg_color = np.median(border_pixels, axis=0)

    # 2. Filter out pixels close to background color
    pixels = rgb_crop.reshape((-1, 3)).astype(np.float32)
    bg_dists = np.linalg.norm(pixels - bg_color, axis=1)
    
    # Keep foreground pixels (distance > 40 from background color)
    fg_pixels = pixels[bg_dists > 40]
    if len(fg_pixels) < 50:
        fg_pixels = pixels  # fallback if all filtered

    # 3. K-Means clustering on foreground garment pixels
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, label, center = cv2.kmeans(fg_pixels, min(3, len(fg_pixels)), None, criteria, 5, cv2.KMEANS_RANDOM_CENTERS)
    
    counts = np.bincount(label.flatten())
    dom_idx = np.argmax(counts)
    dom_rgb = center[dom_idx]
    
    return closest_color(dom_rgb)

if __name__ == "__main__":
    print("Testing background subtracted color extraction logic...")
    # Create dummy crop: Yellow studio background with Burgundy central garment rectangle
    crop = np.zeros((200, 200, 3), dtype=np.uint8)
    crop[:, :] = (0, 215, 255) # Yellow background (BGR)
    crop[40:160, 40:160] = (32, 0, 128) # Burgundy shirt (BGR)
    
    color_without_subtraction = closest_color(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB).reshape((-1, 3)).mean(axis=0))
    color_with_subtraction = test_background_subtracted_color(crop)
    
    print(f"Without background subtraction: {color_without_subtraction}")
    print(f"WITH background subtraction: {color_with_subtraction}")
