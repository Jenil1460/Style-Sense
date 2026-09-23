"""
OutfitParser — Parses outfit prompts into structured garment metadata for Virtual Try-On.

Supports:
- Categories: upper_body, lower_body, dress, full_body, footwear, accessory
- Color extraction: black, white, blue, navy, red, green, beige, grey, pink, purple, yellow, brown, etc.
- Garment extraction: suit, blazer, jacket, hoodie, shirt, t-shirt, kurta, trousers, jeans, dress, etc.
- Style extraction: formal, casual, athleisure, traditional, luxury, streetwear, etc.
"""

import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

COLOR_KEYWORDS = [
    "black", "white", "blue", "navy", "dark blue", "light blue", "red", "maroon",
    "green", "olive", "emerald", "beige", "khaki", "tan", "brown", "grey", "gray",
    "charcoal", "pink", "purple", "yellow", "cream", "ivory", "caramel", "gold", "silver"
]

CATEGORY_MAP = {
    "upper_body": [
        "suit", "blazer", "jacket", "hoodie", "shirt", "t-shirt", "tshirt", "top",
        "sweater", "cardigan", "kurta", "sherwani", "coat", "trench", "vest", "overcoat"
    ],
    "lower_body": [
        "trousers", "pants", "jeans", "slacks", "shorts", "skirt", "chinos", "cargo", "leggings"
    ],
    "dress": [
        "dress", "gown", "saree", "anarkali", "frock", "jumpsuit"
    ],
    "full_body": [
        "tuxedo", "suit set", "tracksuit", "overalls"
    ],
    "footwear": [
        "shoes", "sneakers", "boots", "loafers", "heels", "sandals"
    ]
}

GARMENT_TYPE_DESCRIPTIONS = {
    "suit": "black formal tailored single-breasted suit jacket",
    "blazer": "tailored formal suit blazer",
    "tuxedo": "black formal luxury tuxedo jacket with satin lapels",
    "hoodie": "oversized casual hooded sweatshirt",
    "jacket": "stylish outerwear jacket",
    "denim jacket": "classic denim trucker jacket",
    "leather jacket": "sleek leather jacket",
    "kurta": "traditional mandarin collar kurta shirt",
    "shirt": "button-down collared dress shirt",
    "t-shirt": "crewneck plain cotton t-shirt",
    "sweater": "knit pullover sweater",
    "trousers": "tailored formal dress trousers",
    "jeans": "classic denim jeans",
    "dress": "elegant formal dress"
}


class OutfitParser:
    @staticmethod
    def parse(prompt: str) -> Dict[str, Any]:
        """
        Parses outfit prompt string into structured dict:
        {
            "category": "upper_body",
            "garment": "formal suit",
            "color": "black",
            "style": "formal",
            "description": "black tailored formal suit"
        }
        """
        if not prompt or not prompt.strip():
            return {
                "category": "upper_body",
                "garment": "garment",
                "color": "black",
                "style": "casual",
                "description": "black clothing"
            }

        p_lower = prompt.lower().strip()

        # 1. Color extraction
        detected_color = "black" # default
        for color in COLOR_KEYWORDS:
            if re.search(r'\b' + re.escape(color) + r'\b', p_lower):
                detected_color = color
                break

        # 2. Garment & Category extraction
        detected_garment = "garment"
        detected_category = "upper_body" # default for try-on

        for category, keywords in CATEGORY_MAP.items():
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', p_lower):
                    detected_garment = kw
                    detected_category = category
                    break
            if detected_garment != "garment":
                break

        # Compound garment names
        if "denim jacket" in p_lower:
            detected_garment = "denim jacket"
            detected_category = "upper_body"
        elif "leather jacket" in p_lower:
            detected_garment = "leather jacket"
            detected_category = "upper_body"
        elif "black suit" in p_lower or "formal suit" in p_lower:
            detected_garment = "suit"
            detected_category = "upper_body"
        elif "tuxedo" in p_lower:
            detected_garment = "tuxedo"
            detected_category = "upper_body"

        # 3. Style extraction
        detected_style = "formal" if any(w in p_lower for w in ["formal", "suit", "blazer", "tuxedo", "kurta", "business"]) else "casual"

        # 4. Clean description generation for Garment Reference Generator
        base_desc = GARMENT_TYPE_DESCRIPTIONS.get(detected_garment, f"{detected_garment}")
        clean_description = f"{detected_color} {base_desc}".strip()

        logger.info(f"[OutfitParser] Parsed '{prompt}' -> Category: {detected_category} | Garment: {detected_garment} | Color: {detected_color} | Desc: {clean_description}")

        return {
            "category": detected_category,
            "garment": detected_garment,
            "color": detected_color,
            "style": detected_style,
            "description": clean_description,
            "original_prompt": prompt
        }
