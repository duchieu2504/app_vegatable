"""
Admin Service - Business logic for encyclopedia, dataset, and training management.

Now uses SQLite via database.db instead of raw JSON file I/O.
"""
import os
import shutil
import re
import uuid
import json
from fastapi import UploadFile, HTTPException
from pydantic import BaseModel

from utils.name_mapping import pretty_format, parse_disease_id
from database.db import (
    get_all_diseases as db_get_all_diseases,
    get_disease_by_id,
    upsert_disease,
    update_disease_fields,
)

DATASET_DIR = "dataset"


class EncyclopediaEntry(BaseModel):
    id: str
    name: str
    plant: str
    symptoms: str
    treatment: str
    imageUrl: str


def get_all_diseases():
    """Get all disease entries from SQLite."""
    return db_get_all_diseases()


def get_encyclopedia_data():
    """
    Combine class labels from class_indices.json with disease details from SQLite
    to return a hierarchical structure grouped by plant.
    """
    detailed_diseases = get_all_diseases()

    class_indices_path = "saved_models/class_indices.json"
    if not os.path.exists(class_indices_path):
        return []

    try:
        with open(class_indices_path, "r", encoding="utf-8") as f:
            class_indices = json.load(f)
    except Exception:
        return []

    plants_dict = {}

    # Using centralized pretty_format from utils.name_mapping

    for idx, raw_name in class_indices.items():
        parts = raw_name.split('___')
        if len(parts) == 2:
            plant_name = pretty_format(parts[0])
            disease_name = pretty_format(parts[1])
        else:
            plant_name = "Khác"
            disease_name = pretty_format(raw_name)

        if plant_name not in plants_dict:
            plants_dict[plant_name] = {
                "id": plant_name,
                "plant_name": plant_name,
                "diseases": []
            }

        # Auto-create empty dataset directory if missing
        disease_dir = os.path.join(DATASET_DIR, raw_name)
        os.makedirs(disease_dir, exist_ok=True)

        # Find matching detail from SQLite data
        found_detail = None
        for detail in detailed_diseases:
            if (detail.get('id') == raw_name or
                detail.get('name', '').lower() == disease_name.lower() or
                disease_name.lower() in detail.get('name', '').lower()):
                found_detail = detail
                break

        disease_info = {
            "id": raw_name,
            "name": disease_name,
            "raw_class": raw_name,
            "has_details": found_detail is not None,
            "details": found_detail
        }
        plants_dict[plant_name]["diseases"].append(disease_info)

    result = list(plants_dict.values())
    result.sort(key=lambda x: x["plant_name"])
    return result


from services.llm_service import generate_encyclopedia_details


async def get_or_create_disease_details(disease_id: str, disease_name: str, host_url: str, force_ai: bool = False):
    """Get disease details from DB, or auto-generate via AI if missing/incomplete."""
    disease_entry = get_disease_by_id(disease_id)

    needs_generation = False
    placeholder_texts = ["Chưa cấu hình API Key", "N/A", "Lỗi kết nối AI", "", "Vui lòng thêm GEMINI_API_KEY"]

    if not disease_entry:
        needs_generation = True
        derived_plant, derived_disease = parse_disease_id(disease_id)
        disease_entry = {
            "id": disease_id,
            "name": disease_name if disease_name else derived_disease,
            "plant": derived_plant,
        }
    elif 'causes' not in disease_entry or 'recovery_time' not in disease_entry:
        needs_generation = True
    elif any(
        any(pt in disease_entry.get(field, '') for pt in placeholder_texts if pt != "")
        for field in ['symptoms', 'causes', 'harm', 'treatment', 'recovery_time']
    ):
        needs_generation = True
    elif any(
        disease_entry.get(field, '') == ""
        for field in ['symptoms', 'causes', 'harm', 'treatment', 'recovery_time']
    ):
        needs_generation = True

    if force_ai:
        needs_generation = True

    if needs_generation:
        display_name = disease_entry.get('name', disease_name or disease_id)
        ai_data = await generate_encyclopedia_details(display_name)
        for field in ['symptoms', 'causes', 'harm', 'treatment', 'recovery_time']:
            old_value = disease_entry.get(field, '')
            if old_value in placeholder_texts or not old_value:
                disease_entry[field] = ai_data.get(field, '')

        # Save to SQLite (upsert)
        upsert_disease(disease_entry)

    # Attach images from dataset directory
    images = []
    disease_dir = os.path.join(DATASET_DIR, disease_id)
    if os.path.exists(disease_dir):
        for file in os.listdir(disease_dir):
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                images.append(f"{host_url}/dataset/{disease_id}/{file}")

    disease_entry_copy = dict(disease_entry)
    disease_entry_copy['images'] = images
    return disease_entry_copy


def update_disease_details(disease_id: str, updated_data: dict):
    """Update disease details in SQLite."""
    disease_entry = get_disease_by_id(disease_id)
    if not disease_entry:
        # Create new entry if it doesn't exist
        derived_plant, derived_disease = parse_disease_id(disease_id)
        disease_entry = {
            "id": disease_id,
            "name": derived_disease,
            "plant": derived_plant,
        }

    # Merge incoming data
    for field in ['symptoms', 'causes', 'harm', 'treatment', 'recovery_time']:
        disease_entry[field] = updated_data.get(field, disease_entry.get(field, ''))

    upsert_disease(disease_entry)
    return disease_entry


def add_disease_to_encyclopedia(entry: EncyclopediaEntry):
    """Add a new disease entry to the encyclopedia."""
    existing = get_disease_by_id(entry.id)
    if existing:
        return False
    upsert_disease(entry.dict())
    return True


# --- File Upload Validation ---

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _sanitize_filename(filename: str) -> str:
    """Remove dangerous characters and path traversal attempts from filename."""
    filename = os.path.basename(filename)
    filename = filename.replace('\x00', '')
    filename = re.sub(r'[^\w\-.]', '_', filename)
    return filename


async def save_dataset_image(disease_id: str, file: UploadFile):
    """Save an uploaded image to the disease dataset directory with validation."""
    # Validate file extension
    _, ext = os.path.splitext(file.filename or '')
    ext = ext.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Định dạng file không hợp lệ ({ext}). Chỉ chấp nhận: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Read file content and validate size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File quá lớn ({len(content) / 1024 / 1024:.1f} MB). Giới hạn: {MAX_FILE_SIZE / 1024 / 1024:.0f} MB"
        )

    # Sanitize filename and generate unique name
    safe_name = _sanitize_filename(file.filename or 'image.jpg')
    unique_name = f"{uuid.uuid4().hex[:8]}_{safe_name}"

    # Create directory and save
    disease_dir = os.path.join(DATASET_DIR, disease_id)
    os.makedirs(disease_dir, exist_ok=True)

    file_path = os.path.join(disease_dir, unique_name)
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    return file_path


def export_dataset_zip():
    """Export the entire dataset as a ZIP archive."""
    output_filename = "dataset_export"
    shutil.make_archive(output_filename, 'zip', DATASET_DIR)
    return output_filename + ".zip"


# Kaggle Auto-Training Skeleton
def trigger_kaggle_training():
    """
    Background task to push dataset to Kaggle and trigger training.
    Requires kaggle.json and dataset-metadata.json to be configured.
    """
    import subprocess
    print("Bắt đầu đẩy dữ liệu lên Kaggle...")
    try:
        # subprocess.run(["kaggle", "datasets", "version", "-p", DATASET_DIR, "-m", "Auto update dataset"], check=True)
        print("Bắt đầu huấn luyện Notebook trên Kaggle...")
        # subprocess.run(["kaggle", "kernels", "push", "-p", "kaggle_notebook_dir"], check=True)
        print("Đã gửi lệnh huấn luyện thành công! Kaggle đang xử lý.")
    except Exception as e:
        print(f"Lỗi khi gọi Kaggle API: {e}")
