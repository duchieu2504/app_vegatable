"""
Confusion Matrix Analysis Script for AgriDoc AI.

Generates a detailed confusion matrix to identify which classes
the model confuses most, helping prioritize data augmentation efforts.
"""
import os
import json
import random
import torch
from torchvision import transforms, models
import torch.nn as nn
from PIL import Image
from collections import defaultdict

MODEL_PATH = "saved_models/best_model.pt"
CLASS_INDICES_PATH = "saved_models/class_indices.json"
DATA_DIR = r"E:\RAU REN\Du_lieu"
SAMPLES_PER_CLASS = 50


def load_model():
    with open(CLASS_INDICES_PATH, "r", encoding="utf-8") as f:
        class_indices = json.load(f)

    num_classes = len(class_indices)
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    model.eval()
    return model, class_indices


def predict_single(model, image_path, transform):
    image = Image.open(image_path).convert("RGB")
    tensor = transform(image).unsqueeze(0)
    with torch.no_grad():
        output = model(tensor)
        probs = torch.nn.functional.softmax(output[0], dim=0)
        conf, idx = torch.max(probs, 0)
    return idx.item(), conf.item()


def main():
    model, class_indices = load_model()
    idx_to_name = {int(k): v for k, v in class_indices.items()}
    name_to_idx = {v: int(k) for k, v in class_indices.items()}

    transform = transforms.Compose([
        transforms.Resize(255),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    # Filter only Vietnamese vegetable classes
    rau_classes = {k: v for k, v in name_to_idx.items() if k.startswith("RAU")}
    num_classes = len(rau_classes)

    # Initialize confusion matrix
    confusion = defaultdict(lambda: defaultdict(int))
    class_correct = defaultdict(int)
    class_total = defaultdict(int)

    print(f"{'='*60}")
    print(f"CONFUSION MATRIX ANALYSIS - AgriDoc AI")
    print(f"{'='*60}")
    print(f"Model: {MODEL_PATH}")
    print(f"Data: {DATA_DIR}")
    print(f"Classes: {num_classes} | Samples/class: {SAMPLES_PER_CLASS}")
    print(f"{'='*60}\n")

    for class_name, class_idx in sorted(rau_classes.items()):
        class_dir = os.path.join(DATA_DIR, class_name)
        if not os.path.exists(class_dir):
            print(f"  [SKIP] {class_name} - directory not found")
            continue

        images = [f for f in os.listdir(class_dir) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        if len(images) > SAMPLES_PER_CLASS:
            images = random.sample(images, SAMPLES_PER_CLASS)

        for img_name in images:
            img_path = os.path.join(class_dir, img_name)
            try:
                pred_idx, conf = predict_single(model, img_path, transform)
                pred_name = idx_to_name.get(pred_idx, "UNKNOWN")
                confusion[class_name][pred_name] += 1
                class_total[class_name] += 1
                if pred_idx == class_idx:
                    class_correct[class_name] += 1
            except Exception as e:
                print(f"  [ERROR] {img_path}: {e}")

    # Print per-class accuracy
    print(f"\n{'='*60}")
    print("PER-CLASS ACCURACY")
    print(f"{'='*60}")
    print(f"{'Class':<35} {'Correct':>7} {'Total':>6} {'Accuracy':>9}")
    print(f"{'-'*60}")

    weak_classes = []
    for cls in sorted(rau_classes.keys()):
        correct = class_correct.get(cls, 0)
        total = class_total.get(cls, 0)
        acc = correct / total * 100 if total > 0 else 0
        marker = " ⚠️" if acc < 85 else ""
        print(f"{cls:<35} {correct:>7} {total:>6} {acc:>8.1f}%{marker}")
        if acc < 85:
            weak_classes.append((cls, acc))

    # Print confusion details for weak classes
    if weak_classes:
        print(f"\n{'='*60}")
        print("MISCLASSIFICATION DETAILS (Classes < 85%)")
        print(f"{'='*60}")
        for cls, acc in weak_classes:
            print(f"\n🔴 {cls} (Accuracy: {acc:.1f}%)")
            print(f"   Confused with:")
            for pred, count in sorted(confusion[cls].items(), key=lambda x: -x[1]):
                if pred != cls and count > 0:
                    pct = count / class_total[cls] * 100
                    print(f"     → {pred}: {count} times ({pct:.1f}%)")

    # Overall accuracy
    total_correct = sum(class_correct.values())
    total_samples = sum(class_total.values())
    overall = total_correct / total_samples * 100 if total_samples > 0 else 0

    print(f"\n{'='*60}")
    print(f"OVERALL ACCURACY: {overall:.2f}% ({total_correct}/{total_samples})")
    print(f"WEAK CLASSES ({len(weak_classes)}): {', '.join(c for c, _ in weak_classes)}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
