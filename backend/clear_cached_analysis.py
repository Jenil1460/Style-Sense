import asyncio
import logging
from app.database.mongodb import db_manager, get_database

logging.basicConfig(level=logging.INFO)

async def clear_cache():
    await db_manager.connect()
    db = get_database()

    # Delete existing cached analysis records so all images re-run through the new pipeline
    res = await db.analysis.delete_many({})
    print(f"Cleared {res.deleted_count} old cached analysis documents from MongoDB.")

if __name__ == "__main__":
    asyncio.run(clear_cache())
