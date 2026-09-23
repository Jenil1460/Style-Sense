from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import math

from app.database.mongodb import get_database
from app.utils.exceptions import APIException

class HistoryService:
    
    @staticmethod
    def _format_id(doc: dict) -> dict:
        if "_id" in doc:
            doc["id"] = str(doc.pop("_id"))
        return doc

    @staticmethod
    async def get_unified_history(
        user_id: str, 
        item_type: Optional[str] = None,
        sort: str = "desc",
        page: int = 1,
        limit: int = 20,
        favorites_only: bool = False
    ) -> dict:
        """
        Dynamically aggregates Uploads, Recommendations, and Try-Ons into a unified timeline using $unionWith.
        """
        db = get_database()
        
        # Build the dynamic union pipeline
        pipeline = []
        
        # 1. Base query starts from 'uploads' mapped to standard history schema
        base_match = {"user_id": user_id}
        if favorites_only:
            # Uploads don't have favorites, so they are excluded if favorites_only is True
            base_match["is_favorite"] = True
            
        pipeline.append({"$match": base_match})
        pipeline.append({
            "$project": {
                "_id": 1,
                "user_id": 1,
                "item_type": {"$literal": "upload"},
                "item_id": "$_id",
                "created_at": 1,
                "is_deleted": {"$ifNull": ["$is_deleted", False]},
                "data": "$$ROOT" # Embed the whole document
            }
        })
        
        # 2. Union with Recommendations
        rec_match = {"user_id": user_id}
        if favorites_only:
            rec_match["is_favorite"] = True
            
        pipeline.append({
            "$unionWith": {
                "coll": "recommendations",
                "pipeline": [
                    {"$match": rec_match},
                    {"$project": {
                        "_id": 1,
                        "user_id": 1,
                        "item_type": {"$literal": "recommendation"},
                        "item_id": "$_id",
                        "created_at": 1,
                        "is_deleted": {"$ifNull": ["$is_deleted", False]},
                        "data": "$$ROOT"
                    }}
                ]
            }
        })
        
        # 3. Union with Virtual Try-Ons
        tryon_match = {"user_id": user_id}
        if favorites_only:
            tryon_match["is_favorite"] = True
            
        pipeline.append({
            "$unionWith": {
                "coll": "virtual_tryon",
                "pipeline": [
                    {"$match": tryon_match},
                    {"$project": {
                        "_id": 1,
                        "user_id": 1,
                        "item_type": {"$literal": "virtual_tryon"},
                        "item_id": "$_id",
                        "created_at": 1,
                        "is_deleted": {"$ifNull": ["$is_deleted", False]},
                        "data": "$$ROOT"
                    }}
                ]
            }
        })

        # 4. Global Filters applied after union
        global_match = {"is_deleted": False}
        if item_type:
            global_match["item_type"] = item_type
            
        pipeline.append({"$match": global_match})
        
        # 5. Global Sort
        sort_dir = -1 if sort == "desc" else 1
        pipeline.append({"$sort": {"created_at": sort_dir}})
        
        # 6. Pagination using $facet
        skip = (page - 1) * limit
        pipeline.append({
            "$facet": {
                "metadata": [{"$count": "total"}],
                "data": [{"$skip": skip}, {"$limit": limit}]
            }
        })

        # Execute aggregation
        cursor = db.uploads.aggregate(pipeline)
        result = await cursor.to_list(length=1)
        
        if not result or not result[0]["metadata"]:
            return {
                "items": [],
                "total": 0,
                "page": page,
                "limit": limit,
                "total_pages": 0
            }
            
        total_items = result[0]["metadata"][0]["total"]
        raw_items = result[0]["data"]
        
        # Format IDs for frontend
        formatted_items = []
        for item in raw_items:
            item["id"] = str(item["_id"])
            item["item_id"] = str(item["item_id"])
            if "data" in item:
                item["data"] = HistoryService._format_id(item["data"])
            formatted_items.append(item)

        return {
            "items": formatted_items,
            "total": total_items,
            "page": page,
            "limit": limit,
            "total_pages": math.ceil(total_items / limit)
        }

    @staticmethod
    async def soft_delete(user_id: str, item_type: str, item_id: str) -> bool:
        db = get_database()
        collection_map = {
            "upload": db.uploads,
            "recommendation": db.recommendations,
            "virtual_tryon": db.virtual_tryon
        }
        
        coll = collection_map.get(item_type)
        if not coll:
            raise APIException(status_code=400, detail="Invalid item type")
            
        res = await coll.update_one(
            {"_id": ObjectId(item_id), "user_id": user_id},
            {"$set": {"is_deleted": True}}
        )
        
        if res.modified_count == 0:
            raise APIException(status_code=404, detail="Item not found")
        return True

    @staticmethod
    async def restore(user_id: str, item_type: str, item_id: str) -> bool:
        db = get_database()
        collection_map = {
            "upload": db.uploads,
            "recommendation": db.recommendations,
            "virtual_tryon": db.virtual_tryon
        }
        
        coll = collection_map.get(item_type)
        if not coll:
            raise APIException(status_code=400, detail="Invalid item type")
            
        res = await coll.update_one(
            {"_id": ObjectId(item_id), "user_id": user_id},
            {"$set": {"is_deleted": False}}
        )
        return True

    @staticmethod
    async def clear_history(user_id: str) -> bool:
        db = get_database()
        # Soft delete everything for this user
        await db.uploads.update_many({"user_id": user_id}, {"$set": {"is_deleted": True}})
        await db.recommendations.update_many({"user_id": user_id}, {"$set": {"is_deleted": True}})
        await db.virtual_tryon.update_many({"user_id": user_id}, {"$set": {"is_deleted": True}})
        return True
