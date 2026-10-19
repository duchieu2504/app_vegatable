import os
import sys
import random

# Thêm đường dẫn backend vào sys.path để có thể import từ services
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from collections import defaultdict
from services.vision_service import predict_image

DATASET_DIR = r"E:\RAU REN\Du_lieu"
MAX_SAMPLES_PER_CLASS = 50

def test_accuracy():
    print(f"Đang phân tích tập dữ liệu tại: {DATASET_DIR}...", flush=True)
    total_images = 0
    correct_predictions = 0
    
    class_stats = defaultdict(lambda: {'total': 0, 'correct': 0})
    
    for root, dirs, files in os.walk(DATASET_DIR):
        class_name = os.path.basename(root)
        
        image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not image_files:
            continue
            
        # Lấy mẫu ngẫu nhiên để test nhanh
        if len(image_files) > MAX_SAMPLES_PER_CLASS:
            image_files = random.sample(image_files, MAX_SAMPLES_PER_CLASS)
            
        print(f"Đang kiểm tra thư mục: {class_name} ({len(image_files)} ảnh)", flush=True)
        for img_name in image_files:
            img_path = os.path.join(root, img_name)
            with open(img_path, "rb") as f:
                img_bytes = f.read()
            
            try:
                predicted_class, confidence = predict_image(img_bytes)
                
                total_images += 1
                class_stats[class_name]['total'] += 1
                
                if predicted_class == class_name:
                    correct_predictions += 1
                    class_stats[class_name]['correct'] += 1
            except Exception as e:
                print(f"Lỗi khi xử lý {img_path}: {e}", flush=True)
                
    if total_images == 0:
        print("Không tìm thấy ảnh nào trong tập dữ liệu.", flush=True)
        return
        
    accuracy = (correct_predictions / total_images) * 100
    print("\n" + "="*40, flush=True)
    print("--- KẾT QUẢ ĐÁNH GIÁ MÔ HÌNH (LẤY MẪU) ---", flush=True)
    print("="*40, flush=True)
    print(f"Tổng số ảnh đã kiểm tra: {total_images}", flush=True)
    print(f"Dự đoán đúng: {correct_predictions}", flush=True)
    print(f"Độ chính xác tổng thể (Accuracy): {accuracy:.2f}%\n", flush=True)
    print("Chi tiết độ chính xác từng loại bệnh:", flush=True)
    for cls, stats in class_stats.items():
        if stats['total'] > 0:
            acc = (stats['correct'] / stats['total']) * 100
            print(f" - {cls}: {acc:.2f}% ({stats['correct']}/{stats['total']})", flush=True)

if __name__ == "__main__":
    test_accuracy()
