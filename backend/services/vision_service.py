"""
Vision Service - Handles plant disease image classification.

Uses a ResNet18 model (transfer learning) to classify leaf images
into disease categories. Includes a confidence threshold to avoid
returning low-confidence predictions.
"""
import torch
from torchvision import transforms, models
import torch.nn as nn
from PIL import Image
import io
import os
import json

MODEL_PATH = "saved_models/best_model.pt"
CLASS_INDICES_PATH = "saved_models/class_indices.json"

# Minimum confidence to accept a prediction.
# Below this threshold, the system returns "unrecognized" instead of a wrong guess.
CONFIDENCE_THRESHOLD = 0.55

# Global model cache to avoid reloading on every request
_model_cache = None
_class_indices_cache = None

def _load_model():
    """Load model and class indices into memory (cached)."""
    global _model_cache, _class_indices_cache

    if _model_cache is not None:
        return _model_cache, _class_indices_cache

    with open(CLASS_INDICES_PATH, "r", encoding="utf-8") as f:
        class_indices = json.load(f)

    num_classes = len(class_indices)

    # ResNet18 architecture (Transfer Learning)
    model = models.resnet18(weights=None)
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, num_classes)

    model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
    model.eval()

    _model_cache = model
    _class_indices_cache = class_indices
    return model, class_indices


def predict_image(image_bytes: bytes) -> tuple:
    """
    Receives image bytes, runs through the PyTorch model
    and returns (disease_class_name, confidence_score).

    If model files don't exist, returns a fallback message.
    If confidence is below CONFIDENCE_THRESHOLD, returns an 'unrecognized' result.
    """
    if not os.path.exists(MODEL_PATH) or not os.path.exists(CLASS_INDICES_PATH):
        # Fallback when model hasn't been trained yet
        return "UNKNOWN___NOMODEL", 0.0

    try:
        model, class_indices = _load_model()

        # Image preprocessing (must match training notebook transforms)
        transform = transforms.Compose([
            transforms.Resize(255),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        tensor = transform(image).unsqueeze(0)

        # Run inference
        with torch.no_grad():
            output = model(tensor)
            probabilities = torch.nn.functional.softmax(output[0], dim=0)
            confidence, predicted_idx = torch.max(probabilities, 0)

        confidence_value = confidence.item()

        # Check confidence threshold
        if confidence_value < CONFIDENCE_THRESHOLD:
            return "UNKNOWN___LOWCONFIDENCE", confidence_value

        disease_name = class_indices[str(predicted_idx.item())]
        return disease_name, confidence_value

    except Exception as e:
        print(f"Lỗi khi dự đoán ảnh: {e}")
        return "UNKNOWN___ERROR", 0.0
