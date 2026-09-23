import asyncio
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from app.config.settings import settings

logger = logging.getLogger(__name__)

class MongoDBManager:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.max_retries = 2
        self.retry_delay = 1 # seconds

    async def connect(self):
        """Establish connection to MongoDB with safe retry logic."""
        if not settings.MONGODB_URL:
            logger.warning("[MongoDB] MONGODB_URL is not set — database features will be unavailable.")
            return

        logger.info("[MongoDB] Connecting to MongoDB Atlas...")
        
        for attempt in range(1, self.max_retries + 1):
            try:
                self.client = AsyncIOMotorClient(
                    settings.MONGODB_URL,
                    uuidRepresentation="standard",
                    serverSelectionTimeoutMS=4000,
                    connectTimeoutMS=4000,
                    maxPoolSize=50,
                    minPoolSize=5,
                )
                
                # Verify connection with ping
                await self.client.admin.command('ping')
                
                self.db = self.client[settings.DATABASE_NAME]
                logger.info("[MongoDB] Successfully connected to MongoDB Atlas.")
                return
            
            except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as e:
                logger.warning(f"[MongoDB] Connection attempt {attempt}/{self.max_retries} failed: {e}")
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error(f"[MongoDB] Could not connect to MongoDB Atlas: {e}. Check IP whitelist (0.0.0.0/0) and credentials.")

    async def close(self):
        """Close the MongoDB connection gracefully."""
        if self.client:
            logger.info("[MongoDB] Closing connection...")
            self.client.close()
            self.client = None
            self.db = None
            logger.info("[MongoDB] Connection closed.")

    async def ping(self) -> bool:
        """Health check for MongoDB."""
        if not self.client:
            return False
        try:
            await self.client.admin.command('ping')
            return True
        except Exception:
            return False

# Global Database Manager Instance
db_manager = MongoDBManager()

def get_database() -> AsyncIOMotorDatabase:
    """Dependency injection helper."""
    if db_manager.db is None:
        raise RuntimeError("Database connection is not initialized. Please verify MONGODB_URL and Atlas IP whitelist.")
    return db_manager.db
