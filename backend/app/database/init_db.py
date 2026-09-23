import logging
import pymongo
from app.database.mongodb import get_database

logger = logging.getLogger(__name__)

async def init_db_collections_and_indexes():
    """
    Initialize all required collections and their indexes.
    MongoDB creates collections automatically when documents are inserted,
    but creating them explicitly allows us to set validation rules and create indexes beforehand.
    """
    try:
        db = get_database()
        existing_collections = await db.list_collection_names()
        
        required_collections = [
            "users", 
            "uploads", 
            "analysis", 
            "recommendations", 
            "virtual_tryon", 
            "wardrobe",
            "history", 
            "favorites", 
            "settings"
        ]
        
        # 1. Create Collections
        for coll in required_collections:
            if coll not in existing_collections:
                await db.create_collection(coll)
                logger.info(f"Created collection: {coll}")
                
        # 2. Create Indexes
        
        # Users: Unique email
        await db.users.create_index([("email", pymongo.ASCENDING)], unique=True)
        
        # Uploads: Index by user_id for fast lookup
        await db.uploads.create_index([("user_id", pymongo.ASCENDING)])
        await db.uploads.create_index([("created_at", pymongo.DESCENDING)])
        
        # Analysis
        await db.analysis.create_index([("user_id", pymongo.ASCENDING)])
        await db.analysis.create_index([("upload_id", pymongo.ASCENDING)])
        
        # Recommendations
        await db.recommendations.create_index([("user_id", pymongo.ASCENDING)])
        
        # Virtual Try On
        await db.virtual_tryon.create_index([("user_id", pymongo.ASCENDING)])
        
        # Wardrobe
        await db.wardrobe.create_index([("user_id", pymongo.ASCENDING)])
        await db.wardrobe.create_index([("created_at", pymongo.DESCENDING)])
        
        # History
        await db.history.create_index([("user_id", pymongo.ASCENDING)])
        await db.history.create_index([("created_at", pymongo.DESCENDING)])
        
        # Favorites
        await db.favorites.create_index(
            [("user_id", pymongo.ASCENDING), ("item_id", pymongo.ASCENDING)], 
            unique=True
        )

        
        logger.info("Successfully initialized database collections and indexes.")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # We don't raise here, as failing to create an index shouldn't crash the server entirely,
        # but it should be strongly logged.
