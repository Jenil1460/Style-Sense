from datetime import datetime, timezone
from bson import ObjectId
from typing import List
import asyncio

from app.database.mongodb import get_database
from app.utils.exceptions import APIException
from app.services.ml.recommendation_engine import RecommendationEngine
from app.schemas.recommendation import FavoriteToggleRequest

import logging
logger = logging.getLogger(__name__)

class RecommendationService:
    
    @staticmethod
    def _format_response(doc: dict) -> dict:
        doc["id"] = str(doc["_id"])
        doc["analysis_id"] = str(doc["analysis_id"])
        return doc

    @staticmethod
    async def generate_for_analysis(user_id: str, analysis_id: str) -> dict:
        db = get_database()
        
        # 1. Fetch Analysis
        analysis = await db.analysis.find_one({
            "_id": ObjectId(analysis_id),
            "user_id": user_id
        })
        
        if not analysis:
            raise APIException(status_code=404, detail="Analysis not found")
            
        # 2. Call BOTH engines in parallel (template + Gemini)
        template_task = RecommendationEngine.generate_outfit(analysis)
        gemini_task = RecommendationEngine.generate_gemini_tips(analysis)
        
        generated_data, gemini_data = await asyncio.gather(
            template_task, gemini_task, return_exceptions=True
        )
        
        # Handle exceptions from gather
        if isinstance(generated_data, Exception):
            logger.error(f"Template recommendation failed: {generated_data}")
            raise APIException(status_code=500, detail="Recommendation generation failed")
        
        if isinstance(gemini_data, Exception):
            logger.warning(f"Gemini tips failed (non-blocking): {gemini_data}")
            gemini_data = {}
        
        # 3. Determine source
        source = "template_engine"
        if gemini_data and gemini_data.get("ai_styling_tips"):
            source = "template+gemini"
        
        # 4. Construct Document (template data + Gemini AI data merged)
        rec_doc = {
            "user_id": user_id,
            "analysis_id": ObjectId(analysis_id),
            "occasion": generated_data["occasion"],
            "confidence": generated_data["confidence"],
            "outfit": generated_data["outfit"],
            "color_palette": generated_data["color_palette"],
            # Gemini AI enhancement fields
            "ai_styling_tips": gemini_data.get("ai_styling_tips", []),
            "ai_outfit_suggestions": gemini_data.get("ai_outfit_suggestions", []),
            "ai_color_advice": gemini_data.get("ai_color_advice", ""),
            "source": source,
            "is_favorite": False,
            "created_at": datetime.now(timezone.utc)
        }
        
        # 5. Save to DB
        result = await db.recommendations.insert_one(rec_doc)
        rec_doc["_id"] = result.inserted_id
        
        logger.info(f"[RecommendationService] Generated recommendation (source: {source}) for analysis {analysis_id}")
        return RecommendationService._format_response(rec_doc)

    @staticmethod
    async def get_user_history(user_id: str) -> List[dict]:
        db = get_database()
        cursor = db.recommendations.find({"user_id": user_id}).sort("created_at", -1)
        recs = await cursor.to_list(length=100)
        return [RecommendationService._format_response(doc) for doc in recs]

    @staticmethod
    async def toggle_favorite(user_id: str, recommendation_id: str, data: FavoriteToggleRequest) -> dict:
        db = get_database()
        
        # First verify ownership
        rec = await db.recommendations.find_one({
            "_id": ObjectId(recommendation_id),
            "user_id": user_id
        })
        
        if not rec:
            raise APIException(status_code=404, detail="Recommendation not found")
            
        # Update flag
        await db.recommendations.update_one(
            {"_id": ObjectId(recommendation_id)},
            {"$set": {"is_favorite": data.is_favorite}}
        )
        
        rec["is_favorite"] = data.is_favorite
        return RecommendationService._format_response(rec)

    @staticmethod
    async def delete_recommendation(user_id: str, recommendation_id: str) -> bool:
        db = get_database()
        result = await db.recommendations.delete_one({
            "_id": ObjectId(recommendation_id),
            "user_id": user_id
        })
        
        if result.deleted_count == 0:
            raise APIException(status_code=404, detail="Recommendation not found or not authorized")
            
        return True
