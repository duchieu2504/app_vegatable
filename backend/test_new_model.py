import asyncio
import os
import sys

# Add current directory to path so we can import services
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.vision_service import predict_image

async def main():
    img_path = r"C:\Users\zero2\OneDrive\Máy tính\cay-rau-den-4.jpg"
    print(f"Testing image: {img_path}")
    
    with open(img_path, "rb") as f:
        img_bytes = f.read()
        
    disease, confidence = predict_image(img_bytes)
    print(f"Prediction: {disease}")
    print(f"Confidence: {confidence}%")

if __name__ == "__main__":
    asyncio.run(main())
