from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.auth.jwt import decode_access_token
from app.database.mongodb import get_database
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
        
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
        
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if user is None:
            raise credentials_exception
            
        user["id"] = str(user["_id"])
        del user["_id"]
        return user
    except Exception:
        raise credentials_exception

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_verified", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Account is not verified"
        )
    return current_user

async def get_admin_user(current_user: dict = Depends(get_current_active_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privileges"
        )
    return current_user
