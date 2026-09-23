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
        self.max_retries = 3
        self.retry_delay = 2 # seconds

    async def connect(self):
        """Establish connection to MongoDB with retry logic."""
        logger.info("Connecting to MongoDB Atlas...")
        
        for attempt in range(1, self.max_retries + 1):
            try:
                self.client = AsyncIOMotorClient(
                    settings.MONGODB_URL,
                    uuidRepresentation="standard",
                    serverSelectionTimeoutMS=5000,
                    # Production optimizations
                    maxPoolSize=100,
                    minPoolSize=10,
                )
                
                # Verify connection
                await self.client.admin.command('ping')
                
                self.db = self.client[settings.DATABASE_NAME]
                logger.info("Successfully connected to MongoDB Atlas.")
                return
            
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                logger.warning(f"Failed to connect to MongoDB (Attempt {attempt}/{self.max_retries}): {e}")
                if attempt < self.max_retries:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    await asyncio.sleep(self.retry_delay)
                    # Exponential backoff
                    self.retry_delay *= 2
                else:
                    logger.error("Max retries reached. Could not connect to MongoDB.")
                    raise

    async def close(self):
        """Close the MongoDB connection gracefully."""
        if self.client:
            logger.info("Closing MongoDB connection...")
            self.client.close()
            logger.info("MongoDB connection closed.")

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
        raise RuntimeError("Database connection is not initialized.")
    return db_manager.db
