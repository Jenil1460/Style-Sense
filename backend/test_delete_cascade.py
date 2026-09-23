import asyncio
import logging
from bson import ObjectId
from datetime import datetime, timezone

from app.database.mongodb import get_database
from app.services.upload_service import UploadService
from app.services.analysis_service import FashionAnalysisService

logging.basicConfig(level=logging.INFO)

async def test_delete():
    from app.database.mongodb import db_manager
    await db_manager.connect()
    db = get_database()


    test_user_id = "test_user_del_123"
    
    # 1. Insert dummy upload
    upload_doc = {
        "user_id": test_user_id,
        "image_url": "https://res.cloudinary.com/demo/image/upload/sample.jpg",
        "public_id": "sample_demo_test_public_id",
        "status": "analyzed",
        "created_at": datetime.now(timezone.utc)
    }
    up_res = await db.uploads.insert_one(upload_doc)
    upload_id = up_res.inserted_id
    print(f"Inserted dummy upload: {upload_id}")

    # 2. Insert dummy analysis
    analysis_doc = {
        "user_id": test_user_id,
        "upload_id": upload_id,
        "image_url": "https://res.cloudinary.com/demo/image/upload/sample.jpg",
        "fashion_score": 88,
        "created_at": datetime.now(timezone.utc)
    }
    an_res = await db.analysis.insert_one(analysis_doc)
    analysis_id = an_res.inserted_id
    print(f"Inserted dummy analysis: {analysis_id}")

    # 3. Insert dummy tryon job
    tryon_doc = {
        "user_id": test_user_id,
        "analysis_id": str(analysis_id),
        "public_id": "stylesense/tryon/sample_tryon_id",
        "result_image_url": "https://res.cloudinary.com/demo/image/upload/tryon.jpg",
        "status": "completed"
    }
    await db.virtual_tryon.insert_one(tryon_doc)
    print("Inserted dummy tryon job")

    # 4. Perform cascading delete via FashionAnalysisService
    print(f"\nDeleting analysis {analysis_id}...")
    del_res = await FashionAnalysisService.delete_analysis(test_user_id, str(analysis_id))
    print(f"Delete Result: {del_res}")

    # 5. Verify all collections are clean
    check_up = await db.uploads.find_one({"_id": upload_id})
    check_an = await db.analysis.find_one({"_id": analysis_id})
    check_tr = await db.virtual_tryon.find_one({"analysis_id": str(analysis_id)})

    print("\n--- VERIFICATION ---")
    print(f"Upload remaining in MongoDB: {check_up is not None}")
    print(f"Analysis remaining in MongoDB: {check_an is not None}")
    print(f"Try-On remaining in MongoDB: {check_tr is not None}")

    if check_up is None and check_an is None and check_tr is None:
        print("[SUCCESS] CASCADING DELETE TEST PASSED!")
    else:
        print("[FAILED] CASCADING DELETE TEST FAILED!")


if __name__ == "__main__":
    asyncio.run(test_delete())
