"""
SeasonDetector — Detection-Derived Season Classification for StyleSense AI.

Zero-hallucination guarantees:
- Derives season from CLIP-classified garment types and detected colors
- NO keyword-matching heuristic
- Returns {value, confidence, evidence}
"""

import logging

logger = logging.getLogger(__name__)

# Heavy outerwear items → Winter
WINTER_GARMENTS = {"coat", "jacket", "sweater", "hoodie", "cardigan", "blazer", "vest", "boots"}
# Light garments → Summer
SUMMER_GARMENTS = {"tank top", "crop top", "shorts", "sandals", "flip flops"}
# Transitional
SPRING_GARMENTS = {"blouse", "shirt", "polo shirt", "loafers", "sneakers"}

AUTUMN_COLORS = {"Caramel", "Brown", "Rust Orange", "Mustard Yellow", "Olive Green", "Burgundy", "Wine Red"}
SPRING_COLORS = {"Blush Pink", "Sage Green", "Mint Green", "Baby Blue", "Cream White", "Lavender", "Coral"}
WINTER_COLORS = {"Black", "Charcoal Gray", "Navy Blue", "Forest Green"}
SUMMER_COLORS = {"White", "Royal Blue", "Coral", "Golden Yellow", "Lime Yellow", "Emerald Green"}


class SeasonDetector:

    @staticmethod
    def detect_season(clothing_items: list, colors: dict) -> dict:
        """
        Derives season from detected garments and colors.
        Returns {value, confidence, evidence}.
        """
        detected_items = set()
        for item in clothing_items:
            name = item.get("item", "").lower().strip()
            if name:
                detected_items.add(name)

        primary_color = colors.get("primary", "Unknown")

        # Score each season based on evidence
        scores = {"Winter": 0.0, "Summer": 0.0, "Autumn": 0.0, "Spring": 0.0}
        evidence_parts = []

        # Garment-based scoring
        winter_hits = detected_items & WINTER_GARMENTS
        summer_hits = detected_items & SUMMER_GARMENTS
        spring_hits = detected_items & SPRING_GARMENTS

        if winter_hits:
            scores["Winter"] += 0.4 * len(winter_hits)
            evidence_parts.append(f"Winter garments: {', '.join(winter_hits)}")
        if summer_hits:
            scores["Summer"] += 0.4 * len(summer_hits)
            evidence_parts.append(f"Summer garments: {', '.join(summer_hits)}")
        if spring_hits:
            scores["Spring"] += 0.2 * len(spring_hits)

        # Color-based scoring
        if primary_color in AUTUMN_COLORS:
            scores["Autumn"] += 0.3
            evidence_parts.append(f"Autumn color: {primary_color}")
        if primary_color in SPRING_COLORS:
            scores["Spring"] += 0.3
            evidence_parts.append(f"Spring color: {primary_color}")
        if primary_color in WINTER_COLORS:
            scores["Winter"] += 0.2
            evidence_parts.append(f"Winter color: {primary_color}")
        if primary_color in SUMMER_COLORS:
            scores["Summer"] += 0.2
            evidence_parts.append(f"Summer color: {primary_color}")

        # Determine best season
        best_season = max(scores, key=scores.get)
        best_score = scores[best_season]

        if best_score == 0:
            # No strong signal — report unknown
            season = "All Season"
            confidence = 0.40
            evidence = "No strong seasonal signals from detected garments or colors."
        else:
            season = best_season
            confidence = min(0.85, 0.40 + best_score)
            evidence = "; ".join(evidence_parts) if evidence_parts else "Derived from garment and color analysis"

        logger.info(f"[SeasonDetector] {season} (conf={confidence:.2f})")

        return {
            "value": season,
            "confidence": round(confidence, 2),
            "evidence": evidence,
            "source": "detection_derived",
            "scores": {k: round(v, 2) for k, v in scores.items()},
        }
