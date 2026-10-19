"""
LLM Service - Handles all Gemini AI interactions.

Features:
- Treatment plan generation
- Encyclopedia entry generation
- API key management (masked retrieval for security)
- Exponential backoff retry on rate limit (429) errors
- In-memory LRU cache for encyclopedia responses
"""
import os
import json
import time
import warnings
import functools

# Suppress FutureWarning from Google libraries
warnings.filterwarnings("ignore", category=FutureWarning)
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)


# --- Security: Masked API Key ---

def get_masked_api_key() -> str:
    """Returns a masked version of the API key for safe display.
    Example: 'AIzaSyBe...o-gs'
    """
    if not API_KEY or len(API_KEY) < 10:
        return ""
    return f"{API_KEY[:8]}...{API_KEY[-4:]}"


def update_api_key(new_key: str):
    """
    Update the API Key, save to .env and test the connection.
    """
    global API_KEY, model, encyclopedia_model
    new_key = new_key.strip()
    try:
        # Test with a quick call
        genai.configure(api_key=new_key)
        test_model = genai.GenerativeModel(model_name="gemini-3.6-flash")
        test_model.generate_content("Hello")

        # If no error, persist the key
        API_KEY = new_key
        env_path = ".env"
        env_content = ""
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            updated = False
            for i, line in enumerate(lines):
                if line.startswith("GEMINI_API_KEY="):
                    lines[i] = f"GEMINI_API_KEY={new_key}\n"
                    updated = True
            if not updated:
                lines.append(f"\nGEMINI_API_KEY={new_key}\n")
            env_content = "".join(lines)
        else:
            env_content = f"GEMINI_API_KEY={new_key}\n"

        with open(env_path, "w", encoding="utf-8") as f:
            f.write(env_content)

        # Rebuild model instances with the new key
        _rebuild_models()

        return True, "API Key hợp lệ và đã được lưu."
    except Exception as e:
        # Restore old config
        if API_KEY:
            genai.configure(api_key=API_KEY)
        return False, f"API Key không hợp lệ: {str(e)}"


# --- Model Configuration ---

generation_config = {
    "temperature": 0.2,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}

# System prompt for treatment plans
system_instruction = """
Bạn là một chuyên gia nông nghiệp hàng đầu tại Việt Nam.
Dựa vào tên loại bệnh thực vật được cung cấp, hãy phân tích và đưa ra giải pháp điều trị.
TRẢ VỀ KẾT QUẢ BẮT BUỘC THEO ĐỊNH DẠNG JSON MÀ KHÔNG KÈM THEO BẤT KỲ VĂN BẢN NÀO KHÁC.

Định dạng JSON yêu cầu:
{
  "warning_level": "Thấp (Màu Xanh) | Trung bình (Màu Vàng) | Cao (Màu Đỏ)",
  "treatment": [
    "Hành động xử lý 1",
    "Hành động xử lý 2"
  ],
  "medicine": [
    "Tên thuốc 1",
    "Tên thuốc 2"
  ]
}
"""

# System prompt for encyclopedia entries
encyclopedia_system_instruction = """
Bạn là một chuyên gia bách khoa toàn thư về bệnh lý thực vật nông nghiệp.
Dựa vào tên bệnh thực vật được cung cấp, hãy biên soạn một hồ sơ bệnh học chi tiết.
TRẢ VỀ KẾT QUẢ BẮT BUỘC THEO ĐỊNH DẠNG JSON MÀ KHÔNG KÈM THEO BẤT KỲ VĂN BẢN NÀO KHÁC.
LƯU Ý: KHÔNG sử dụng dấu ngoặc kép (") bên trong nội dung của các trường giá trị để tránh lỗi parse JSON. Thay vào đó hãy dùng dấu nháy đơn (').

Định dạng JSON yêu cầu:
{
  "symptoms": "Mô tả chi tiết các triệu chứng trên lá, thân, quả...",
  "causes": "Nguyên nhân gây bệnh (nấm, vi khuẩn, virus, thiếu chất...)",
  "harm": "Tác hại của bệnh đến năng suất và sự phát triển của cây",
  "treatment": "Phương pháp điều trị chi tiết (hữu cơ, hóa học, canh tác)",
  "recovery_time": "Dự kiến thời gian phục hồi nếu điều trị đúng cách"
}
"""

model = genai.GenerativeModel(
    model_name="gemini-3.6-flash",
    generation_config=generation_config,
    system_instruction=system_instruction
)

encyclopedia_model = genai.GenerativeModel(
    model_name="gemini-3.6-flash",
    generation_config=generation_config,
    system_instruction=encyclopedia_system_instruction
)


def _rebuild_models():
    """Rebuild model instances after API key change."""
    global model, encyclopedia_model
    model = genai.GenerativeModel(
        model_name="gemini-3.6-flash",
        generation_config=generation_config,
        system_instruction=system_instruction
    )
    encyclopedia_model = genai.GenerativeModel(
        model_name="gemini-3.6-flash",
        generation_config=generation_config,
        system_instruction=encyclopedia_system_instruction
    )


# --- Retry Logic with Exponential Backoff ---

MAX_RETRIES = 3
INITIAL_DELAY = 1.0  # seconds


def _call_with_retry(model_instance, prompt: str) -> str:
    """
    Call Gemini API with exponential backoff retry on 429 errors.
    Returns the raw text response.
    """
    last_exception = None
    delay = INITIAL_DELAY

    for attempt in range(MAX_RETRIES):
        try:
            response = model_instance.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            last_exception = e
            error_str = str(e)
            # Only retry on rate limit (429) errors
            if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                print(f"[Retry {attempt + 1}/{MAX_RETRIES}] Gemini rate limited. Waiting {delay}s...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff: 1s -> 2s -> 4s
            else:
                # Non-retryable error, raise immediately
                raise e

    # All retries exhausted
    raise last_exception


def _parse_json_response(text: str) -> dict:
    """Safely parse JSON from LLM response, stripping markdown fences."""
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return json.loads(text.strip())


# --- In-memory LRU Cache for Encyclopedia ---

@functools.lru_cache(maxsize=64)
def _cached_encyclopedia_call(disease_name: str) -> str:
    """
    Cached wrapper for encyclopedia AI calls.
    Returns raw JSON string (hashable for lru_cache).
    """
    disease_upper = disease_name.upper()
    if "KHOEMANH" in disease_upper or "HEALTHY" in disease_upper:
        prompt = f"Cây trồng đang ở trạng thái khỏe mạnh: {disease_name}. Bắt buộc trả về JSON. symptoms = 'Mô tả dấu hiệu rau khỏe mạnh', causes = 'Không', harm = 'Không', treatment = 'Hướng dẫn chăm sóc tiếp theo (tưới nước, bón phân)', recovery_time = 'Không'."
    else:
        prompt = f"Hãy viết hồ sơ bệnh học chi tiết cho bệnh: {disease_name}."

    return _call_with_retry(encyclopedia_model, prompt)


# --- Public API Functions ---

async def generate_treatment_plan(disease_name: str) -> dict:
    """Calls Gemini API to generate a treatment plan based on the disease name."""
    if not API_KEY:
        return {
            "warning_level": "Lỗi: Chưa cấu hình API Key",
            "treatment": ["Vui lòng thêm GEMINI_API_KEY vào file .env tại thư mục backend."],
            "medicine": []
        }

    prompt = f"Bệnh phát hiện: {disease_name}. Hãy đưa ra phác đồ điều trị."

    try:
        text = _call_with_retry(model, prompt)
        return _parse_json_response(text)
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return {
            "warning_level": "Lỗi kết nối AI",
            "treatment": [f"Chi tiết lỗi: {str(e)}"],
            "medicine": []
        }


async def generate_encyclopedia_details(disease_name: str) -> dict:
    """Calls Gemini API to generate a detailed encyclopedia entry (with cache + retry)."""
    if not API_KEY:
        return {
            "symptoms": "Chưa cấu hình API Key",
            "causes": "N/A",
            "harm": "N/A",
            "treatment": "Vui lòng thêm GEMINI_API_KEY",
            "recovery_time": "N/A"
        }

    try:
        raw_text = _cached_encyclopedia_call(disease_name)
        return _parse_json_response(raw_text)
    except Exception as e:
        print(f"Error calling Gemini for encyclopedia: {e}")
        return {
            "symptoms": f"Lỗi kết nối AI: {str(e)}",
            "causes": "",
            "harm": "",
            "treatment": "",
            "recovery_time": ""
        }
