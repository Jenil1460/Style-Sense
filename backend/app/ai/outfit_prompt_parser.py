"""
OutfitPromptParser — Normalizes outfit text prompts and extracts structured garment attributes for StyleSense AI.

Normalize user's text:
"wear black suit" -> garment: "formal suit", color: "black", style: "formal", target: "upper_body"
"wear blue denim jacket" -> garment: "denim jacket", color: "blue", style: "casual", target: "upper_body"
"wear white hoodie" -> garment: "hoodie", color: "white", style: "casual", target: "upper_body"
"wear beige formal blazer" -> garment: "formal blazer", color: "beige", style: "formal", target: "upper_body"

Fixes common spelling mistakes: "suite" -> "suit", "jaket" -> "jacket", etc.
"""

import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Common typo corrections
TYPO_CORRECTIONS = {
    r"\bsuite\b": "suit",
    r"\bjaket\b": "jacket",
    r"\bhody\b": "hoodie",
    r"\btshirt\b": "t-shirt",
    r"\btee shirt\b": "t-shirt",
    r"\bkurti\b": "kurta",
    r"\bblaser\b": "blazer",
    r"\bdenim-jacket\b": "denim jacket",
}

# Color keywords
COLORS = [
    "black", "white", "blue", "navy", "beige", "grey", "gray", "red",
    "green", "yellow", "pink", "purple", "brown", "maroon", "gold", "silver"
]

# Garment types & target region mapping
GARMENT_TYPES = [
    ("denim jacket", "denim jacket", "casual", "upper_body"),
    ("formal blazer", "formal blazer", "formal", "upper_body"),
    ("suit", "formal suit", "formal", "upper_body"),
    ("tuxedo", "tuxedo", "formal", "upper_body"),
    ("blazer", "blazer", "formal", "upper_body"),
    ("hoodie", "hoodie", "casual", "upper_body"),
    ("jacket", "jacket", "casual", "upper_body"),
    ("sweater", "sweater", "casual", "upper_body"),
    ("shirt", "shirt", "casual", "upper_body"),
    ("t-shirt", "t-shirt", "casual", "upper_body"),
    ("kurta", "kurta", "traditional", "upper_body"),
    ("coat", "coat", "formal", "upper_body"),
    ("overcoat", "overcoat", "formal", "upper_body"),
    ("dress", "dress", "formal", "dress"),
    ("gown", "gown", "formal", "dress"),
    ("saree", "saree", "traditional", "full_body"),
    ("jeans", "jeans", "casual", "lower_body"),
    ("trousers", "trousers", "formal", "lower_body"),
    ("pants", "pants", "casual", "lower_body"),
]

# Style keywords override
STYLES = {
    "formal": "formal",
    "business": "formal",
    "tailored": "formal",
    "casual": "casual",
    "oversized": "casual",
    "traditional": "traditional",
    "ethnic": "traditional",
    "streetwear": "streetwear",
    "sporty": "sporty"
}


class OutfitPromptParser:
    @staticmethod
    def parse(prompt: str) -> Dict[str, Any]:
        """
        Parses and normalizes a text outfit prompt into structured attributes:
        garment, color, style, target
        """
        if not prompt or not isinstance(prompt, str):
            return {
                "rawPrompt": "",
                "cleanDescription": "black formal suit",
                "garment": "formal suit",
                "color": "black",
                "style": "formal",
                "target": "upper_body"
            }

        text = prompt.lower().strip()

        # 1. Apply typo corrections
        for pattern, replacement in TYPO_CORRECTIONS.items():
            text = re.sub(pattern, replacement, text)

        # 2. Extract color
        extracted_color = "black"
        for c in COLORS:
            if c in text:
                extracted_color = c if c != "gray" else "grey"
                break

        # 3. Extract garment & default style/target
        extracted_garment = "formal suit"
        extracted_style = "formal"
        extracted_target = "upper_body"

        for key, g_name, default_style, default_target in GARMENT_TYPES:
            if key in text:
                extracted_garment = g_name
                extracted_style = default_style
                extracted_target = default_target
                break

        # 4. Extract explicit style override if present
        for key, style_val in STYLES.items():
            if key in text:
                extracted_style = style_val
                break

        # Special combinations
        if "denim jacket" in text:
            extracted_garment = "denim jacket"
            extracted_style = "casual"
        elif "blazer" in text and "formal" in text:
            extracted_garment = "formal blazer"
            extracted_style = "formal"

        parts = [p for p in [extracted_color, extracted_style, extracted_garment] if p]
        clean_description = " ".join(dict.fromkeys(" ".join(parts).split()))

        result = {
            "rawPrompt": prompt,
            "normalizedPrompt": f"wear {clean_description}",
            "cleanDescription": clean_description,
            "garment": extracted_garment,
            "color": extracted_color,
            "style": extracted_style,
            "target": extracted_target,
            # Backwards compatibility fields if needed elsewhere
            "garmentType": extracted_garment,
            "targetRegion": extracted_target
        }

        logger.info(f"[OutfitPromptParser] Parsed '{prompt}' -> {result}")
        return result
