import json
import os

notebook_path = "../notebooks/train.ipynb"
output_path = "../notebooks/colab_train.ipynb"

try:
    with open(notebook_path, "r", encoding="utf-8") as f:
        nb = json.load(f)

    new_cell = {
       "cell_type": "code",
       "execution_count": None,
       "metadata": {},
       "outputs": [],
       "source": [
        "# TẢI BỘ DỮ LIỆU PLANTDOC VỀ GOOGLE COLAB\n",
        "!git clone https://github.com/pratikkayal/PlantDoc-Dataset.git\n",
        "!mv PlantDoc-Dataset/train Dataset  # Đổi tên thư mục train thành Dataset để khớp với code cũ\n",
        "!ls Dataset\n"
       ]
    }
    
    save_cell = {
       "cell_type": "code",
       "execution_count": None,
       "metadata": {},
       "outputs": [],
       "source": [
        "# LƯU MÔ HÌNH SAU KHI TRAIN ĐỂ TẢI VỀ BACKEND\n",
        "import torch\n",
        "torch.save(model.state_dict(), 'best_model.pt')\n",
        "print('Đã lưu model thành best_model.pt. Bạn hãy tải file này về và bỏ vào thư mục backend/saved_models/')"
       ]
    }

    # Chèn ô tải data vào ngay sau ô đầu tiên
    nb["cells"].insert(1, new_cell)
    # Chèn ô save model vào cuối cùng
    nb["cells"].append(save_cell)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)

    print(f"Created {output_path} successfully!")
except Exception as e:
    print(f"Error: {e}")
