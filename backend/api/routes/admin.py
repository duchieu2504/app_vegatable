"""
Admin API routes - System administration endpoints.
"""
import os
from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from services.admin_service import (
    EncyclopediaEntry,
    add_disease_to_encyclopedia,
    save_dataset_image,
    export_dataset_zip,
    trigger_kaggle_training,
)
from services.llm_service import update_api_key, get_masked_api_key

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


@router.post("/add_disease")
def add_new_disease(entry: EncyclopediaEntry):
    """Add a new disease entry to the encyclopedia."""
    success = add_disease_to_encyclopedia(entry)
    if success:
        return {"status": "success", "message": "Đã thêm bệnh mới thành công."}
    return {"status": "error", "message": "Bệnh này đã tồn tại!"}


@router.post("/upload_image")
async def upload_dataset_image(disease_id: str, file: UploadFile = File(...)):
    """Upload a sample image for a specific disease to the dataset."""
    file_path = await save_dataset_image(disease_id, file)
    return {"status": "success", "message": f"Đã lưu ảnh vào {file_path}"}


@router.get("/export_zip")
def export_zip():
    """Export the entire dataset as a ZIP archive."""
    zip_path = export_dataset_zip()
    if os.path.exists(zip_path):
        return FileResponse(zip_path, media_type="application/zip", filename="dataset_export.zip")
    return {"status": "error", "message": "Không thể tạo file ZIP"}


@router.post("/auto_train")
def auto_train(background_tasks: BackgroundTasks):
    """Trigger model training on Kaggle in the background."""
    background_tasks.add_task(trigger_kaggle_training)
    return {
        "status": "success",
        "message": "Đã ra lệnh huấn luyện ngầm trên Kaggle. Quá trình này sẽ diễn ra ở chế độ nền.",
    }


@router.post("/config_api_key")
def config_api_key(payload: dict):
    """Update the Gemini API key, saves to .env and tests connection."""
    success, msg = update_api_key(payload.get('api_key', ''))
    return {"status": "success" if success else "error", "message": msg}


@router.get("/config_api_key")
def get_api_key():
    """Returns a masked version of the current API key for display purposes."""
    return {"api_key": get_masked_api_key()}
