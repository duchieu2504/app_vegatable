import os
import sys

sys.path.append("e:/Tradingbot/app_vegetable_photo/backend")
from services.llm_service import update_api_key

print("Testing API Key update...")
success, msg = update_api_key("AIzaSyB-invalid-key-here")
print(f"Success: {success}")
print(f"Msg: {msg}")
