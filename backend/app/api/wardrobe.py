from fastapi import APIRouter, Depends, Body, status
from typing import List, Dict, Any

from app.dependencies.auth import get_current_user
from app.services.wardrobe_service import WardrobeService

router = APIRouter(prefix="/wardrobe", tags=["Wardrobe"])

@router.get("", response_model=List[Dict[str, Any]])
async def get_user_wardrobe(current_user: dict = Depends(get_current_user)):
    return await WardrobeService.get_user_wardrobe(str(current_user["_id"]))

@router.post("", status_code=status.HTTP_201_CREATED)
async def add_wardrobe_item(
    item_data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    return await WardrobeService.add_item(str(current_user["_id"]), item_data)

@router.delete("/{item_id}")
async def delete_wardrobe_item(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    await WardrobeService.delete_item(str(current_user["_id"]), item_id)
    return {"status": "success", "message": "Item deleted from wardrobe."}

@router.get("/combinations")
async def get_outfit_combinations(current_user: dict = Depends(get_current_user)):
    return await WardrobeService.generate_combinations(str(current_user["_id"]))
