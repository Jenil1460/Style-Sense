import asyncio
import motor.motor_asyncio
import os
from dotenv import load_dotenv

async def check_db():
    load_dotenv()
    client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv('MONGODB_URL'), serverSelectionTimeoutMS=5000)
    try:
        info = await client.server_info()
        print("MongoDB connection successful!")
        print(info)
    except Exception as e:
        print("MongoDB connection failed!")
        print(e)

if __name__ == '__main__':
    asyncio.run(check_db())
