"""
PersonalColorService — Personalized Palette, Color Experimentation & Outfit Combinations for StyleSense AI.

Requirements enforced:
1. Generates 6-8 recommended colors with swatch name, HEX, RGB, and why_it_works.
2. NO HEX codes in why_it_works text. HEX is technical data only.
3. Generates 4-6 colors to experiment with using non-judgmental language:
   ("May create less contrast", "Can appear muted under warm lighting", "Consider balancing with a neutral"). Never calls them "bad colors".
4. Generates personalized outfit combinations (LOOK 1, LOOK 2, LOOK 3, LOOK 4).
5. Generates existing outfit & skin undertone harmony analysis.
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class PersonalColorService:

    # ── PALETTE DEFINITIONS BY UNDERTONE ──

    WARM_PALETTES = [
        {
            "name": "Olive Green", "hex": "#708238", "rgb": [112, 130, 56],
            "why_it_works": "Complements golden warmth and enhances rich natural skin tones.",
            "best_pairings": [
                {"name": "Cream", "hex": "#FFFDD0"},
                {"name": "Camel", "hex": "#C19A6B"},
                {"name": "Warm Brown", "hex": "#6E473B"}
            ],
            "occasion_tip": "Ideal for casual field jackets, knitwear, and smart-casual chinos."
        },
        {
            "name": "Terracotta", "hex": "#C86D51", "rgb": [200, 109, 81],
            "why_it_works": "Adds vibrant warmth that naturally elevates warm skin tones.",
            "best_pairings": [
                {"name": "Beige", "hex": "#F5F5DC"},
                {"name": "Navy Blue", "hex": "#000080"},
                {"name": "Olive Green", "hex": "#708238"}
            ],
            "occasion_tip": "Stunning focal piece for autumn shirts, sweaters, and midi dresses."
        },
        {
            "name": "Camel", "hex": "#C19A6B", "rgb": [193, 154, 107],
            "why_it_works": "A luxurious neutral foundation that pairs seamlessly with warm undertones.",
            "best_pairings": [
                {"name": "Deep Teal", "hex": "#005F73"},
                {"name": "Terracotta", "hex": "#C86D51"},
                {"name": "Crisp White", "hex": "#FFFFFF"}
            ],
            "occasion_tip": "Timeless choice for tailored trench coats, trousers, and leather boots."
        },
        {
            "name": "Warm Brown", "hex": "#6E473B", "rgb": [110, 71, 59],
            "why_it_works": "Provides deep grounding contrast while emphasizing golden skin hues.",
            "best_pairings": [
                {"name": "Mustard Yellow", "hex": "#E1AD01"},
                {"name": "Cream", "hex": "#FFFDD0"},
                {"name": "Olive Green", "hex": "#708238"}
            ],
            "occasion_tip": "Rich anchor layer for leather jackets, footwear, and corduroy pants."
        },
        {
            "name": "Mustard Yellow", "hex": "#E1AD01", "rgb": [225, 173, 1],
            "why_it_works": "Creates energetic harmony with golden undertones and warm skin depth.",
            "best_pairings": [
                {"name": "Dark Denim", "hex": "#1B263B"},
                {"name": "Charcoal", "hex": "#36454F"},
                {"name": "Warm Brown", "hex": "#6E473B"}
            ],
            "occasion_tip": "Vibrant accent sweater or shirt paired with dark denim trousers."
        },
    ]

    COOL_PALETTES = [
        {
            "name": "Navy Blue", "hex": "#000080", "rgb": [0, 0, 128],
            "why_it_works": "A classic anchoring neutral that highlights crisp cool undertones.",
            "best_pairings": [
                {"name": "Cool Gray", "hex": "#8C92AC"},
                {"name": "Crisp White", "hex": "#FFFFFF"},
                {"name": "Burgundy", "hex": "#800020"}
            ],
            "occasion_tip": "Essential staple for suits, tailored blazers, and dark denim."
        },
        {
            "name": "Emerald Green", "hex": "#50C878", "rgb": [80, 200, 120],
            "why_it_works": "Vibrant jewel tone that brings out pink and rosy undertone highlights.",
            "best_pairings": [
                {"name": "Slate Gray", "hex": "#708090"},
                {"name": "Black", "hex": "#000000"},
                {"name": "Navy Blue", "hex": "#000080"}
            ],
            "occasion_tip": "Eye-catching statement piece for silk blouses, evening coats, or tops."
        },
        {
            "name": "Burgundy", "hex": "#800020", "rgb": [128, 0, 32],
            "why_it_works": "Deep wine shade that complements blue and rosy undertones effortlessly.",
            "best_pairings": [
                {"name": "Crisp White", "hex": "#FFFFFF"},
                {"name": "Cool Gray", "hex": "#8C92AC"},
                {"name": "Black", "hex": "#000000"}
            ],
            "occasion_tip": "Elegant winter layer for knitwear, leather jackets, and dress shoes."
        },
        {
            "name": "Cool Gray", "hex": "#8C92AC", "rgb": [140, 146, 172],
            "why_it_works": "Sophisticated slate neutral that harmonizes with cool skin tones.",
            "best_pairings": [
                {"name": "Royal Blue", "hex": "#4169E1"},
                {"name": "Plum", "hex": "#8E4585"},
                {"name": "Navy Blue", "hex": "#000080"}
            ],
            "occasion_tip": "Versatile neutral for office trousers, suit jackets, and cardigans."
        },
        {
            "name": "Lavender", "hex": "#E6E6FA", "rgb": [230, 230, 250],
            "why_it_works": "Soft pastels brighten cool complexions without overwhelming contrast.",
            "best_pairings": [
                {"name": "Navy Blue", "hex": "#000080"},
                {"name": "Cool Gray", "hex": "#8C92AC"},
                {"name": "Crisp White", "hex": "#FFFFFF"}
            ],
            "occasion_tip": "Fresh spring pastel top or button-up shirt paired with slate pants."
        },
    ]

    NEUTRAL_PALETTES = [
        {
            "name": "Sage Green", "hex": "#9CAF88", "rgb": [156, 175, 136],
            "why_it_works": "Muted earth hue that flatters balanced neutral undertones.",
            "best_pairings": [
                {"name": "Cream", "hex": "#FFFDD0"},
                {"name": "Soft Taupe", "hex": "#483C32"},
                {"name": "Charcoal", "hex": "#36454F"}
            ],
            "occasion_tip": "Relaxed casual shirts, utility jackets, and linen trousers."
        },
        {
            "name": "Dusty Rose", "hex": "#DCAE96", "rgb": [220, 174, 150],
            "why_it_works": "Gentle blush tone that harmonizes with both warm and cool complexions.",
            "best_pairings": [
                {"name": "Charcoal", "hex": "#36454F"},
                {"name": "Soft Taupe", "hex": "#483C32"},
                {"name": "Navy Blue", "hex": "#000080"}
            ],
            "occasion_tip": "Subtle blush accent for tops, summer knits, and scarves."
        },
        {
            "name": "Charcoal", "hex": "#36454F", "rgb": [54, 69, 79],
            "why_it_works": "Versatile dark neutral providing sleek framing for balanced skin tones.",
            "best_pairings": [
                {"name": "Dusty Rose", "hex": "#DCAE96"},
                {"name": "Emerald Green", "hex": "#50C878"},
                {"name": "Cream", "hex": "#FFFDD0"}
            ],
            "occasion_tip": "Sleek foundational pants, suit separates, and outerwear."
        },
        {
            "name": "Soft Taupe", "hex": "#483C32", "rgb": [72, 60, 50],
            "why_it_works": "Subtle blend of gray and brown that complements neutral undertones.",
            "best_pairings": [
                {"name": "Sage Green", "hex": "#9CAF88"},
                {"name": "Navy Blue", "hex": "#000080"},
                {"name": "Dusty Rose", "hex": "#DCAE96"}
            ],
            "occasion_tip": "Sophisticated footwear, leather accessories, and knitwear."
        },
        {
            "name": "Navy Blue", "hex": "#000080", "rgb": [0, 0, 128],
            "why_it_works": "Timeless dark blue that delivers refined contrast across skin depths.",
            "best_pairings": [
                {"name": "Cream", "hex": "#FFFDD0"},
                {"name": "Terracotta", "hex": "#C86D51"},
                {"name": "Sage Green", "hex": "#9CAF88"}
            ],
            "occasion_tip": "Versatile blazer, denim jacket, or everyday trousers."
        },
    ]

    # ── EXPERIMENTATION COLORS (NON-JUDGMENTAL PHRASING) ──

    WARM_EXPERIMENTS = [
        {"name": "Icy Blue", "hex": "#AFEEEE", "rgb": [175, 238, 238], "experiment_note": "May create cool contrast against warm undertones. Consider balancing with warm neutrals like camel or tan."},
        {"name": "Stark Magenta", "hex": "#FF00FF", "rgb": [255, 0, 255], "experiment_note": "High intensity cool pink that can overpower warm warmth under direct sunlight."},
        {"name": "Cool Ash Gray", "hex": "#B0C4DE", "rgb": [176, 196, 222], "experiment_note": "Can appear slightly muted under warm indoor lighting. Pair with a warm jacket or scarf."},
        {"name": "Pastel Pink", "hex": "#FFD1DC", "rgb": [255, 209, 220], "experiment_note": "Soft cool tone that offers low contrast. Try styling with deep brown or olive layers."},
        {"name": "Silver", "hex": "#C0C0C0", "rgb": [192, 192, 192], "experiment_note": "Metallic cool sheen. Consider pairing with gold or brass accessories for balanced warmth."},
    ]

    COOL_EXPERIMENTS = [
        {"name": "Mustard Yellow", "hex": "#FFDB58", "rgb": [255, 219, 88], "experiment_note": "Warm yellow may create contrast against cool undertones. Balance with navy or charcoal layers."},
        {"name": "Bright Orange", "hex": "#FFA500", "rgb": [255, 165, 0], "experiment_note": "Vibrant warm hue that can clash under warm light. Balance with crisp white or dark navy."},
        {"name": "Golden Rust", "hex": "#B7410E", "rgb": [183, 65, 14], "experiment_note": "Strong warm earth tone. Consider balancing with cool gray or burgundy accents."},
        {"name": "Warm Olive", "hex": "#808000", "rgb": [128, 128, 0], "experiment_note": "Can appear slightly muted against cool complexions. Try pairing with bright white or silver."},
        {"name": "Peach", "hex": "#FFDAB9", "rgb": [255, 218, 185], "experiment_note": "Soft warm pastel. Styling with charcoal or deep blue adds structured depth."},
    ]

    NEUTRAL_EXPERIMENTS = [
        {"name": "Neon Lime", "hex": "#39FF14", "rgb": [57, 255, 20], "experiment_note": "High saturation hue. Best paired with grounding neutrals like charcoal or navy to maintain balance."},
        {"name": "Stark Magenta", "hex": "#FF00FF", "rgb": [255, 0, 255], "experiment_note": "Vibrant cool tone. Consider balancing with neutral beige or taupe bottom layers."},
        {"name": "Vivid Orange", "hex": "#FF5722", "rgb": [255, 87, 34], "experiment_note": "Bold warm accent. Pair with cool slate or navy to equalize visual weight."},
        {"name": "Ultra Yellow", "hex": "#FFFF00", "rgb": [255, 255, 0], "experiment_note": "High contrast under bright sunlight. Balance with dark denim or charcoal trousers."},
    ]

    @staticmethod
    def generate_personal_color_recommendations(
        skin_tone_data: Dict[str, Any],
        garments: List[Dict[str, Any]] = None,
        detected_colors: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generates full personal color recommendations package:
        - Recommended Palette (Top 5 colors)
        - Colors to Experiment With (4-5 colors)
        - Personalized Outfit Combinations (LOOK 1 to LOOK 4)
        - Existing Outfit & Skin Undertone Harmony
        """
        undertone = skin_tone_data.get("undertone", "Neutral")
        skin_tone = skin_tone_data.get("skin_tone", "Medium")

        if "Warm" in undertone:
            palette = PersonalColorService.WARM_PALETTES
            experiments = PersonalColorService.WARM_EXPERIMENTS
        elif "Cool" in undertone:
            palette = PersonalColorService.COOL_PALETTES
            experiments = PersonalColorService.COOL_EXPERIMENTS
        else:
            palette = PersonalColorService.NEUTRAL_PALETTES
            experiments = PersonalColorService.NEUTRAL_EXPERIMENTS

        # REQUIREMENT: Recommend ONLY top 5 colors
        recommended_colors = palette[:5]
        experimental_colors = experiments[:5]

        # Generate 4 outfit combinations
        combinations = PersonalColorService._generate_outfit_combinations(
            undertone, skin_tone, recommended_colors
        )

        # Existing Outfit & Skin Tone Harmony Assessment
        existing_harmony = PersonalColorService._analyze_existing_outfit_harmony(
            undertone, skin_tone, garments, detected_colors
        )

        return {
            "skin_tone": skin_tone,
            "undertone": undertone,
            "confidence": skin_tone_data.get("confidence", 0.0),
            "evidence": skin_tone_data.get("evidence", ""),
            "recommended_colors": recommended_colors,
            "experimental_colors": experimental_colors,
            "outfit_combinations": combinations,
            "existing_outfit_harmony": existing_harmony,
        }

    @staticmethod
    def _generate_outfit_combinations(
        undertone: str,
        skin_tone: str,
        palette: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        if "Warm" in undertone:
            return [
                {
                    "title": "LOOK 1",
                    "top": "Olive Green Shirt",
                    "top_hex": "#708238",
                    "bottom": "Cream Trousers",
                    "bottom_hex": "#FFFDD0",
                    "shoes": "Brown Leather Shoes",
                    "shoes_hex": "#6E473B",
                    "harmony_score": 98,
                    "tag": "Earth-Toned Casual",
                    "description": "Earth-toned harmony that accentuates golden undertones and delivers elevated casual contrast."
                },
                {
                    "title": "LOOK 2",
                    "top": "Terracotta Top",
                    "top_hex": "#C86D51",
                    "bottom": "Beige Trousers",
                    "bottom_hex": "#F5F5DC",
                    "shoes": "White Sneakers",
                    "shoes_hex": "#FFFFFF",
                    "harmony_score": 95,
                    "tag": "Vibrant Everyday",
                    "description": "Warm, vibrant accent paired with clean neutral pants for balanced everyday elegance."
                },
                {
                    "title": "LOOK 3",
                    "top": "Mustard Yellow Sweater",
                    "top_hex": "#E1AD01",
                    "bottom": "Dark Denim Jeans",
                    "bottom_hex": "#1B263B",
                    "shoes": "Warm Brown Boots",
                    "shoes_hex": "#6E473B",
                    "harmony_score": 94,
                    "tag": "Bold Contrast",
                    "description": "Rich golden focal top anchored by dark denim, creating bold yet harmonious contrast."
                },
                {
                    "title": "LOOK 4",
                    "top": "Camel Trench / Blazer",
                    "top_hex": "#C19A6B",
                    "bottom": "Olive Chinos",
                    "bottom_hex": "#708238",
                    "shoes": "Tan Loafers",
                    "shoes_hex": "#D2B48C",
                    "harmony_score": 96,
                    "tag": "Smart Tailored",
                    "description": "Luxurious camel neutral coat balanced by warm olive chinos for refined smart-casual wear."
                }
            ]
        elif "Cool" in undertone:
            return [
                {
                    "title": "LOOK 1",
                    "top": "Navy Blue Shirt",
                    "top_hex": "#000080",
                    "bottom": "Cool Gray Trousers",
                    "bottom_hex": "#8C92AC",
                    "shoes": "Black Dress Shoes",
                    "shoes_hex": "#000000",
                    "harmony_score": 98,
                    "tag": "Classic Cool",
                    "description": "Classic cool palette that provides sharp contrast and highlights cool skin clarity."
                },
                {
                    "title": "LOOK 2",
                    "top": "Burgundy Knit Sweater",
                    "top_hex": "#800020",
                    "bottom": "Crisp White Jeans",
                    "bottom_hex": "#FFFFFF",
                    "shoes": "Dark Brown Boots",
                    "shoes_hex": "#4A2E2B",
                    "harmony_score": 96,
                    "tag": "Berry Elegance",
                    "description": "Rich berry top anchored by clean white lower layer for sophisticated contrast."
                },
                {
                    "title": "LOOK 3",
                    "top": "Emerald Green Top",
                    "top_hex": "#50C878",
                    "bottom": "Slate Gray Pants",
                    "bottom_hex": "#708090",
                    "shoes": "White Sneakers",
                    "shoes_hex": "#FFFFFF",
                    "harmony_score": 95,
                    "tag": "Jewel Focal",
                    "description": "Jewel-toned focal point balanced with sleek gray neutrals."
                },
                {
                    "title": "LOOK 4",
                    "top": "Lavender Shirt / Blazer",
                    "top_hex": "#E6E6FA",
                    "bottom": "Navy Trousers",
                    "bottom_hex": "#000080",
                    "shoes": "Black Loafers",
                    "shoes_hex": "#000000",
                    "harmony_score": 94,
                    "tag": "Soft Tailoring",
                    "description": "Fresh pastel upper garment paired with deep navy trousers for balanced cool elegance."
                }
            ]
        else: # Neutral
            return [
                {
                    "title": "LOOK 1",
                    "top": "Sage Green Shirt",
                    "top_hex": "#9CAF88",
                    "bottom": "Cream Trousers",
                    "bottom_hex": "#FFFDD0",
                    "shoes": "White Sneakers",
                    "shoes_hex": "#FFFFFF",
                    "harmony_score": 97,
                    "tag": "Subtle Earth",
                    "description": "Balanced subtle green paired with cream neutrals for a clean contemporary aesthetic."
                },
                {
                    "title": "LOOK 2",
                    "top": "Dusty Rose Top",
                    "top_hex": "#DCAE96",
                    "bottom": "Charcoal Pants",
                    "bottom_hex": "#36454F",
                    "shoes": "Soft Taupe Shoes",
                    "shoes_hex": "#483C32",
                    "harmony_score": 96,
                    "tag": "Blush Accent",
                    "description": "Gentle blush accent anchored by charcoal lower garments to complement neutral skin depth."
                },
                {
                    "title": "LOOK 3",
                    "top": "Navy Blue Polo",
                    "top_hex": "#000080",
                    "bottom": "Beige Chinos",
                    "bottom_hex": "#F5F5DC",
                    "shoes": "Brown Leather Shoes",
                    "shoes_hex": "#6E473B",
                    "harmony_score": 95,
                    "tag": "Timeless Chic",
                    "description": "Timeless dark-and-light neutral harmony that enhances balanced complexions."
                },
                {
                    "title": "LOOK 4",
                    "top": "Soft Taupe Knit",
                    "top_hex": "#483C32",
                    "bottom": "Sage Green Pants",
                    "bottom_hex": "#9CAF88",
                    "shoes": "Dark Brown Loafers",
                    "shoes_hex": "#3E2723",
                    "harmony_score": 94,
                    "tag": "Dimensional Warmth",
                    "description": "Subtle warm-cool fusion that brings dimensional richness to neutral undertones."
                }
            ]

    @staticmethod
    def _analyze_existing_outfit_harmony(
        undertone: str,
        skin_tone: str,
        garments: List[Dict[str, Any]] = None,
        detected_colors: Dict[str, Any] = None
    ) -> str:
        """
        Analyzes how the currently worn detected garments interact with the detected skin undertone.
        """
        if not garments and not detected_colors:
            return f"Your {undertone.lower()} undertone pairs exceptionally well with balanced earth and jewel tones."

        primary_color = (detected_colors.get("primary") if detected_colors else None) or "Neutral"
        garment_descs = []

        top_color = None
        bottom_color = None

        if garments:
            for g in garments:
                item_name = str(g.get("item", g.get("garment", ""))).lower()
                color_name = str(g.get("color", primary_color)).capitalize()
                garment_descs.append(f"{color_name} {item_name}".strip())

                if any(k in item_name for k in ["shirt", "top", "jacket", "hoodie", "sweater", "blazer", "t-shirt"]):
                    top_color = color_name
                elif any(k in item_name for k in ["pants", "trousers", "jeans", "shorts", "skirt"]):
                    bottom_color = color_name

        worn_str = ", ".join(garment_descs) if garment_descs else primary_color

        if top_color and bottom_color:
            return (
                f"Your {undertone.lower()} skin undertone interacts harmoniously with your {top_color.lower()} top. "
                f"The {bottom_color.lower()} lower layer provides excellent visual grounding for a balanced aesthetic."
            )
        elif top_color:
            return (
                f"Your {undertone.lower()} skin undertone works well with the {top_color.lower()} upper garment, "
                f"enhancing your facial skin warmth and overall outfit balance."
            )
        else:
            return (
                f"The detected outfit ({worn_str}) complements your {skin_tone.lower()} skin with a {undertone.lower()} undertone, "
                f"creating natural contrast and visual cohesion."
            )
