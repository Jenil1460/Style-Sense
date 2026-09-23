from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.dependencies.auth import get_current_active_user
from app.schemas.history import PaginatedHistoryResponse
from app.services.history_service import HistoryService

router = APIRouter(prefix="/history", tags=["History & Timeline"])

@router.get("/", response_model=PaginatedHistoryResponse)
async def get_history(
    type: Optional[str] = Query(None, description="Filter by: upload, recommendation, virtual_tryon"),
    sort: str = Query("desc", description="Sort direction: asc or desc"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_active_user)
):
    """Retrieves a unified, paginated timeline of all user activity."""
    return await HistoryService.get_unified_history(
        current_user["id"], item_type=type, sort=sort, page=page, limit=limit
    )

@router.get("/favorites", response_model=PaginatedHistoryResponse)
async def get_favorites(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_active_user)
):
    """Retrieves a unified timeline of only favorited items."""
    return await HistoryService.get_unified_history(
        current_user["id"], favorites_only=True, page=page, limit=limit
    )

@router.delete("/{item_type}/{item_id}")
async def delete_history_item(
    item_type: str,
    item_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Soft deletes a specific item from the timeline."""
    await HistoryService.soft_delete(current_user["id"], item_type, item_id)
    return {"success": True, "message": "Item removed from timeline"}

@router.post("/{item_type}/{item_id}/restore")
async def restore_history_item(
    item_type: str,
    item_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Restores a soft-deleted item to the timeline."""
    await HistoryService.restore(current_user["id"], item_type, item_id)
    return {"success": True, "message": "Item restored to timeline"}

@router.delete("/clear/all")
async def clear_all_history(current_user: dict = Depends(get_current_active_user)):
    """Soft deletes all items in the user's history."""
    await HistoryService.clear_history(current_user["id"])
    return {"success": True, "message": "History cleared"}
