import os
import json
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
from collections import defaultdict

MODEL_PATH = "saved_models/best_model.pt"
CLASS_INDICES_PATH = "saved_models/class_indices.json"
# Path to original training data
TEST_DATA_PATH = "E:/RAU REN/Du_lieu_rau_den"

def main():
    # Load class indices
    with open(CLASS_INDICES_PATH, "r", encoding="utf-8") as f:
        class_indices = json.load(f)
    
    num_classes = len(class_indices)
    
    model = models.resnet18(weights=None)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, num_classes)
    
    model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
    model.eval()
    print(f"\nModel loaded successfully ({num_classes} classes)")
    
    # Same transform as inference
    transform = transforms.Compose([
        transforms.Resize(255),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    # Check if test data exists
    if not os.path.exists(TEST_DATA_PATH):
        print(f"\nERROR: Test data path not found: {TEST_DATA_PATH}")
        print("Falling back to backend/dataset...")
        test_path = "dataset"
    else:
        test_path = TEST_DATA_PATH
    
    # Test images from each class folder
    print("\n" + "=" * 60)
    print("TESTING PREDICTIONS")
    print("=" * 60)
    
    results = defaultdict(lambda: {"correct": 0, "total": 0, "predictions": defaultdict(int)})
    
    for class_folder in sorted(os.listdir(test_path)):
        folder_path = os.path.join(test_path, class_folder)
        if not os.path.isdir(folder_path):
            continue
        if not class_folder.startswith("RAUDEN"):
            continue
            
        images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp'))]
        
        # Test first 20 images from each class
        test_count = min(20, len(images))
        print(f"\n--- {class_folder} (testing {test_count}/{len(images)} images) ---")
        
        for img_name in images[:test_count]:
            img_path = os.path.join(folder_path, img_name)
            try:
                image = Image.open(img_path).convert('RGB')
                tensor = transform(image).unsqueeze(0)
                
                with torch.no_grad():
                    output = model(tensor)
                    probabilities = torch.nn.functional.softmax(output[0], dim=0)
                    confidence, predicted_idx = torch.max(probabilities, 0)
                
                predicted_name = class_indices[str(predicted_idx.item())]
                is_correct = predicted_name == class_folder
                
                results[class_folder]["total"] += 1
                results[class_folder]["predictions"][predicted_name] += 1
                if is_correct:
                    results[class_folder]["correct"] += 1
                
                status = "OK" if is_correct else "WRONG"
                print(f"  [{status}] {img_name[:30]:30s} -> {predicted_name} ({confidence.item()*100:.1f}%)")
                
            except Exception as e:
                print(f"  [ERR] {img_name}: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total_correct = 0
    total_all = 0
    for class_name, data in sorted(results.items()):
        acc = data["correct"] / data["total"] * 100 if data["total"] > 0 else 0
        total_correct += data["correct"]
        total_all += data["total"]
        print(f"\n{class_name}:")
        print(f"  Accuracy: {data['correct']}/{data['total']} ({acc:.1f}%)")
        print(f"  Predictions distribution:")
        for pred, count in sorted(data["predictions"].items(), key=lambda x: -x[1]):
            print(f"    {pred}: {count} times")
    
    if total_all > 0:
        print(f"\nOVERALL ACCURACY: {total_correct}/{total_all} ({total_correct/total_all*100:.1f}%)")

if __name__ == "__main__":
    main()
