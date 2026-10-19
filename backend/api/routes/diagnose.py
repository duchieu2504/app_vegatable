"""
Diagnose API routes - Plant disease diagnosis endpoint.
"""
from fastapi import APIRouter, UploadFile, File, Request
from services.vision_service import predict_image, CONFIDENCE_THRESHOLD
from services.admin_service import get_or_create_disease_details
from database.db import add_diagnosis_record
from utils.name_mapping import parse_disease_id

router = APIRouter(prefix="/api/v1", tags=["Diagnose"])


@router.post("/diagnose")
async def diagnose_plant(request: Request, file: UploadFile = File(...)):
    """
    Receives an image, runs it through PyTorch Vision model,
    then retrieves encyclopedia details for the detected disease.
    """
    # Step 1: Read image bytes from client
    image_bytes = await file.read()

    # Step 2: Run image through AI PyTorch model (Vision)
    disease_id, confidence = predict_image(image_bytes)

    # Step 3: Handle low-confidence or error cases
    if disease_id.startswith("UNKNOWN___"):
        reason = disease_id.split("___")[1]
        messages = {
            "LOWCONFIDENCE": f"Không thể nhận diện chính xác. Độ tin cậy ({confidence:.0%}) thấp hơn ngưỡng ({CONFIDENCE_THRESHOLD:.0%}). Vui lòng chụp ảnh rõ hơn.",
            "NOMODEL": "Mô hình AI chưa được huấn luyện. Vui lòng liên hệ quản trị viên.",
            "ERROR": "Đã xảy ra lỗi khi phân tích hình ảnh. Vui lòng thử lại.",
        }
        return {
            "status": "low_confidence",
            "vision_result": {
                "disease_name": "Không nhận diện được",
                "confidence": confidence,
                "is_healthy": False,
            },
            "llm_advice": {
                "name": "Không nhận diện được",
                "plant": "Không xác định",
                "symptoms": messages.get(reason, "Lỗi không xác định."),
                "causes": "",
                "harm": "",
                "treatment": "Hãy chụp lại ảnh với ánh sáng tốt hơn, lá rõ nét, và nền không quá phức tạp.",
                "recovery_time": "",
            },
            "filename": file.filename,
        }

    # Step 4: Retrieve info from encyclopedia (cache or LLM)
    host_url = str(request.base_url).rstrip('/')
    disease_info = await get_or_create_disease_details(disease_id, "", host_url)

    disease_name = disease_info.get("name", disease_id)
    is_healthy = "KHOEMANH" in disease_id.upper() or "HEALTHY" in disease_id.upper()

    # Step 5: Save to diagnosis history
    plant_name = disease_info.get("plant", "")
    if not plant_name:
        plant_name, _ = parse_disease_id(disease_id)
    add_diagnosis_record(
        disease_id=disease_id,
        disease_name=disease_name,
        plant_name=plant_name,
        confidence=confidence,
        is_healthy=is_healthy,
        image_filename=file.filename or "",
    )

    # Step 6: Return unified JSON result to Mobile App
    return {
        "status": "success",
        "vision_result": {
            "disease_name": disease_name,
            "confidence": confidence,
            "is_healthy": is_healthy
        },
        "llm_advice": disease_info,
        "filename": file.filename
    }
