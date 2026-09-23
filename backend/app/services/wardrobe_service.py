import asyncio
import logging
from datetime import datetime, timezone
from bson import ObjectId
from typing import List

from app.database.mongodb import get_database
from app.utils.exceptions import APIException

logger = logging.getLogger(__name__)

def _safe_id(doc: dict) -> dict:
    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)
    return doc

class WardrobeService:
    @staticmethod
    async def add_item(user_id: str, item_data: dict) -> dict:
        db = get_database()
        doc = {
            "user_id": user_id,
            "category": item_data.get("category", "General"),
            "clothing_type": item_data.get("clothing_type", "Garment"),
            "color_name": item_data.get("color_name", "Neutral"),
            "image_url": item_data.get("image_url", ""),
            "tags": item_data.get("tags", []),
            "created_at": datetime.now(timezone.utc),
        }
        res = await db.wardrobe.insert_one(doc)
        doc["_id"] = res.inserted_id
        return _safe_id(doc)

    @staticmethod
    async def get_user_wardrobe(user_id: str) -> List[dict]:
        db = get_database()
        cursor = db.wardrobe.find({"user_id": user_id}).sort("created_at", -1)
        docs = await cursor.to_list(length=100)
        return [_safe_id(doc) for doc in docs]

    @staticmethod
    async def delete_item(user_id: str, item_id: str) -> bool:
        db = get_database()
        res = await db.wardrobe.delete_one({"_id": ObjectId(item_id), "user_id": user_id})
        if res.deleted_count == 0:
            raise APIException(status_code=404, detail="Wardrobe item not found.")
        return True

    @staticmethod
    async def generate_combinations(user_id: str) -> dict:
        db = get_database()
        cursor = db.wardrobe.find({"user_id": user_id})
        items = await cursor.to_list(length=100)

        uppers = [i for i in items if i.get("category") in ["Upper", "Shirt", "T-Shirt", "Jacket", "Blazer", "Top"]]
        lowers = [i for i in items if i.get("category") in ["Lower", "Pants", "Jeans", "Shorts", "Skirt"]]
        shoes = [i for i in items if i.get("category") in ["Shoes", "Footwear", "Sneakers"]]

        combinations = []
        if uppers and lowers:
            for u in uppers[:3]:
                for l in lowers[:3]:
                    s = shoes[0] if shoes else None
                    comb_name = f"{u.get('color_name', '')} {u.get('clothing_type', 'Top')} paired with {l.get('color_name', '')} {l.get('clothing_type', 'Bottom')}"
                    combinations.append({
                        "title": comb_name,
                        "upper": _safe_id(u),
                        "lower": _safe_id(l),
                        "shoes": _safe_id(s) if s else None,
                        "occasion": "Casual / Everyday",
                        "match_score": 92
                    })
        elif items:
            combinations.append({
                "title": f"Monochrome {items[0].get('color_name', 'Neutral')} Ensemble",
                "upper": _safe_id(items[0]),
                "lower": None,
                "shoes": None,
                "occasion": "Everyday Wear",
                "match_score": 88
            })

        return {
            "total_items": len(items),
            "combinations": combinations
        }
