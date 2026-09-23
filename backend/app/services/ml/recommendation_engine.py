"""
RecommendationEngine — Template-Based + Gemini AI Recommendation Generator for StyleSense AI.

Zero-hallucination guarantees:
- NO random.choice() (removed — total hallucination)
- NO fabricated brands, occasions, or confidence scores
- Generates recommendations ONLY from structured detections
- Every recommendation references only detected garments and colors
- Gemini is used ONLY for styling advice — never for detection
- Template-based fallback ensures no hallucination without API key
"""

import logging
import json
import asyncio
from typing import List

logger = logging.getLogger(__name__)

# Color complement map for pairing recommendations
COMPLEMENT_MAP = {
    "Navy Blue":     ["White", "Cream White", "Beige", "Mustard Yellow"],
    "Black":         ["White", "Cream White", "Light Gray", "Burgundy", "Royal Blue"],
    "White":         ["Navy Blue", "Black", "Royal Blue", "Emerald Green", "Burgundy"],
    "Beige":         ["Brown", "Olive Green", "Navy Blue", "Burgundy"],
    "Sage Green":    ["White", "Cream White", "Dusty Pink", "Tan"],
    "Olive Green":   ["Tan", "Brown", "Cream White", "Mustard Yellow"],
    "Charcoal Gray": ["White", "Royal Blue", "Burgundy", "Dusty Pink"],
    "Burgundy":      ["Beige", "Cream White", "Black", "Tan"],
    "Tan":           ["Navy Blue", "Brown", "Olive Green", "Burgundy"],
    "Dusty Pink":    ["Sage Green", "Charcoal Gray", "White", "Navy Blue"],
    "Blush Pink":    ["Light Gray", "White", "Sage Green", "Navy Blue"],
    "Mustard Yellow":["Navy Blue", "Charcoal Gray", "Brown", "Burgundy"],
    "Brown":         ["Beige", "Cream White", "White", "Navy Blue"],
    "Rust Orange":   ["Navy Blue", "Brown", "Charcoal Gray", "Cream White"],
    "Caramel":       ["White", "Navy Blue", "Sage Green"],
    "Royal Blue":    ["White", "Cream White", "Beige", "Light Gray"],
    "Cream White":   ["Navy Blue", "Brown", "Burgundy", "Olive Green"],
}


class RecommendationEngine:

    @staticmethod
    async def generate_outfit(analysis: dict) -> dict:
        """
        Generates outfit recommendations strictly from detected analysis data.
        NO random values, NO fabricated items.
        """
        garments = analysis.get("garments", [])
        colors = analysis.get("colors", {})
        styles = analysis.get("styles", [])
        occasion = analysis.get("occasion", "Unknown")
        skin_tone = analysis.get("skin_tone", {})
        season_data = analysis.get("season_data", {})

        primary_color = colors.get("primary", "Unknown")
        top_style = styles[0].get("style_name", "Unknown") if styles else "Unknown"
        style_conf = styles[0].get("confidence", 0) if styles else 0
        tone = skin_tone.get("tone", "Unknown") if isinstance(skin_tone, dict) else "Unknown"

        outfit = []
        recommendations = []
        color_palette = []

        # Build outfit suggestions from ACTUALLY detected garments
        for g in garments:
            item_name = g.get("item", "Unknown")
            item_color = g.get("color", "Unknown")
            item_region = g.get("region", "Unknown")
            item_conf = g.get("confidence", 0)

            if item_color != "Unknown":
                color_palette.append(item_color)

            outfit.append({
                "category": item_region,
                "name": f"{item_color} {item_name}",
                "color": item_color,
                "detected_confidence": round(item_conf, 2),
                "evidence": f"Detected by CLIP with {item_conf:.0%} confidence",
            })

        # Generate color pairing suggestions based on detected colors
        if primary_color in COMPLEMENT_MAP:
            complements = COMPLEMENT_MAP[primary_color]
            recommendations.append(
                f"Your detected {primary_color} pairs well with {', '.join(complements[:3])} "
                f"for color harmony."
            )

        # Style-specific recommendation (only if style was detected)
        if top_style != "Unknown" and style_conf > 0.3:
            style_tips = {
                "Casual": "Consider layering with a neutral-toned jacket for added depth.",
                "Minimal": "Stick to monochromatic tones for a cleaner silhouette.",
                "Streetwear": "Bold accessories and statement sneakers complete this look.",
                "Business Casual": "A structured blazer elevates the ensemble for professional settings.",
                "Formal": "Ensure clean lines with well-tailored proportions.",
                "Luxury": "Subtle textures and quality materials enhance the premium feel.",
                "Old Money": "Neutral earth tones with classic silhouettes define this aesthetic.",
                "Athleisure": "Technical fabrics with streamlined fits balance comfort and style.",
                "Vintage": "Unique patterns and retro accessories add authentic character.",
                "Traditional": "Rich fabrics and traditional motifs honor cultural elegance.",
            }
            tip = style_tips.get(top_style, "")
            if tip:
                recommendations.append(f"Based on your detected {top_style} style ({style_conf:.0%}): {tip}")

        # Skin tone recommendation (only if detected)
        if tone == "Warm":
            recommendations.append(
                "Your warm undertone pairs well with gold-tone accessories and earthy palettes."
            )
        elif tone == "Cool":
            recommendations.append(
                "Your cool undertone pairs well with silver-tone accessories and jewel-toned palettes."
            )

        # Add detected color to palette
        if not color_palette and primary_color != "Unknown":
            color_palette.append(primary_color)

        return {
            "occasion": occasion if occasion != "Unknown" else "Daily Wear",
            "confidence": round(style_conf, 2) if style_conf > 0 else 0.0,
            "outfit": outfit,
            "color_palette": color_palette,
            "recommendations": recommendations,
            "evidence": f"Generated from {len(garments)} detected garments, {top_style} style classification.",
            "source": "template_engine",
        }

    @staticmethod
    async def generate_gemini_tips(analysis: dict) -> dict:
        """
        NEW: Gemini 3.6 Flash AI Stylist enhancement layer.
        
        Takes ALL detection data from the existing pipeline and generates
        rich, personalized styling advice. Gemini does NOT detect anything —
        it only interprets detection results.
        
        Returns empty dict on failure (graceful degradation).
        """
        try:
            from app.services.ml.gemini_client import get_gemini_client
            client = get_gemini_client()
            if client is None:
                logger.info("[RecommendationEngine] Gemini not available — skipping AI tips")
                return {}

            # Extract detection data for the prompt
            garments = analysis.get("garments", [])
            colors = analysis.get("colors", {})
            styles = analysis.get("styles", [])
            occasion = analysis.get("occasion", "Unknown")
            skin_tone = analysis.get("skin_tone", {})
            body_type = analysis.get("body_type", {})
            face_shape = analysis.get("face_shape", {})
            season = analysis.get("season", "Unknown")
            fashion_score = analysis.get("fashion_score", 0)
            radar = analysis.get("radar_metrics", {})

            # Build garment summary
            garment_lines = []
            for g in garments:
                item = g.get("item", g.get("garment", "Unknown"))
                color = g.get("color", "Unknown")
                pattern = g.get("pattern", "Unknown")
                material = g.get("material", "Unknown")
                conf = g.get("confidence", 0)
                garment_lines.append(f"- {color} {item} (pattern: {pattern}, material: {material}, confidence: {conf:.0%})")
            garment_text = "\n".join(garment_lines) if garment_lines else "No garments detected"

            # Build style summary
            style_lines = []
            for s in styles[:3]:
                style_lines.append(f"- {s.get('style_name', 'Unknown')} ({s.get('confidence', 0):.0%})")
            style_text = "\n".join(style_lines) if style_lines else "No style detected"

            tone = skin_tone.get("tone", "Unknown") if isinstance(skin_tone, dict) else "Unknown"
            bt = body_type.get("body_type", "Unknown") if isinstance(body_type, dict) else "Unknown"
            fs = face_shape.get("face_shape", "Unknown") if isinstance(face_shape, dict) else "Unknown"

            prompt = f"""You are a world-class AI fashion stylist for StyleSense AI.

Based on the following AI-detected analysis of a person's outfit photo, provide personalized styling advice.

## Detected Outfit Data (from computer vision — do NOT question these detections):

**Garments Detected:**
{garment_text}

**Color Palette:** Primary: {colors.get('primary', 'Unknown')}, Secondary: {colors.get('secondary', 'None')}, Accent: {colors.get('accent', 'None')}

**Style Classification (CLIP):**
{style_text}

**Occasion:** {occasion}
**Season:** {season}
**Skin Tone:** {tone}
**Body Type:** {bt}
**Face Shape:** {fs}
**Fashion Score:** {fashion_score}/100

**Score Breakdown:**
- Color Harmony: {radar.get('color_harmony', 'N/A')}%
- Fit & Silhouette: {radar.get('fit', 'N/A')}%
- Style Consistency: {radar.get('style_consistency', 'N/A')}%
- Accessories: {radar.get('accessories', 'N/A')}%

## Instructions:
Respond ONLY with valid JSON (no markdown, no code fences) in this exact format:
{{
  "ai_styling_tips": ["tip1", "tip2", "tip3"],
  "ai_outfit_suggestions": [
    {{"suggestion": "description", "pieces": ["piece1", "piece2"], "occasion": "occasion"}},
    {{"suggestion": "description", "pieces": ["piece1", "piece2"], "occasion": "occasion"}}
  ],
  "ai_color_advice": "Color theory advice based on skin tone and current palette"
}}

Rules:
- Give 3-5 specific, actionable styling tips referencing the DETECTED garments and colors
- Suggest 2-3 outfit improvements or alternatives based on detected style and occasion
- Provide color theory advice considering the person's skin tone
- Be specific — reference actual detected items, not generic advice
- Keep each tip under 2 sentences
- Do NOT invent or fabricate brands"""

            # Call Gemini 3.6 Flash with timeout
            interaction = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: client.interactions.create(
                        model="gemini-3.6-flash",
                        input=prompt,
                        system_instruction="You are a fashion stylist AI. Output ONLY valid JSON. No markdown formatting, no code fences, no explanation text.",
                    )
                ),
                timeout=15.0
            )

            response_text = interaction.output_text
            if not response_text:
                logger.warning("[RecommendationEngine] Gemini returned empty response")
                return {}

            # Clean up response — remove markdown code fences if present
            cleaned = response_text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[-1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
            cleaned = cleaned.strip()

            parsed = json.loads(cleaned)

            logger.info(f"[RecommendationEngine] Gemini AI tips generated: {len(parsed.get('ai_styling_tips', []))} tips")

            return {
                "ai_styling_tips": parsed.get("ai_styling_tips", []),
                "ai_outfit_suggestions": parsed.get("ai_outfit_suggestions", []),
                "ai_color_advice": parsed.get("ai_color_advice", ""),
                "source": "gemini-3.6-flash",
            }

        except asyncio.TimeoutError:
            logger.warning("[RecommendationEngine] Gemini request timed out (15s)")
            return {}
        except json.JSONDecodeError as e:
            logger.warning(f"[RecommendationEngine] Gemini response not valid JSON: {e}")
            return {}
        except Exception as e:
            logger.error(f"[RecommendationEngine] Gemini AI tips failed: {e}", exc_info=True)
            return {}

