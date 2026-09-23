import asyncio
import os
from dotenv import load_dotenv
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate
from app.database.mongodb import db_manager

async def test_auth():
    load_dotenv()
    await db_manager.connect()
    try:
        user = UserCreate(
            email="test_exception@example.com",
            password="Password123!",
            first_name="Test",
            last_name="Test"
        )
        res = await AuthService.register_user(user)
        print("Success:", res)
    except Exception as e:
        print("Error type:", type(e))
        print("Error message:", e)
    finally:
        await db_manager.close()

if __name__ == "__main__":
    asyncio.run(test_auth())
