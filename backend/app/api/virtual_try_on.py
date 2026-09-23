from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.responses import JSONResponse
from typing import List, Optional
from app.dependencies.auth import get_current_active_user
from app.schemas.virtual_tryon import TryOnResponse
from app.services.virtual_tryon_service import VirtualTryonService

router = APIRouter(prefix="/virtual-try-on", tags=["Virtual Try-On"])
legacy_router = APIRouter(prefix="/try-on", tags=["Virtual Try-On Legacy"])

@router.post("/generate")
@legacy_router.post("/generate")
async def generate_tryon(
    image: Optional[UploadFile] = File(None),
    outfit_prompt: str = Form(...),
    person_image_url: Optional[str] = Form(None),
    analysis_id: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_active_user)
):
    """
    Processes OpenAI Virtual Try-On request.
    Expects multipart/form-data with fields: 'image' and 'outfit_prompt'.
    """
    res = await VirtualTryonService.create_tryon_job(
        user_id=current_user["id"],
        outfit_prompt=outfit_prompt,
        image_file=image,
        person_image_url=person_image_url,
        analysis_id=analysis_id
    )

    if not res.get("success", False):
        # Never return HTTP 200 when generation failed
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=res
        )

    return res

@router.get("/history", response_model=List[TryOnResponse])
@legacy_router.get("/history", response_model=List[TryOnResponse])
async def get_tryon_history(current_user: dict = Depends(get_current_active_user)):
    """Retrieves the history of all past OpenAI virtual try-ons."""
    return await VirtualTryonService.get_history(current_user["id"])

@router.delete("/{job_id}")
@legacy_router.delete("/{job_id}")
async def delete_tryon(
    job_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    """Deletes a virtual try-on record."""
    await VirtualTryonService.delete_job(current_user["id"], job_id)
    return {"success": True, "message": "Virtual Try-On successfully deleted"}
