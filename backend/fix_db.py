import asyncio
import motor.motor_asyncio
import os
from dotenv import load_dotenv

async def fix_users():
    load_dotenv()
    client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv('MONGODB_URL'))
    db = client[os.getenv('DATABASE_NAME')]
    result = await db.users.update_many({}, {'$set': {'is_verified': True}})
    print(f"Modified {result.modified_count} users.")

if __name__ == '__main__':
    asyncio.run(fix_users())
