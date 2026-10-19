import json

notebook = {
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 1. Hướng dẫn Add Dataset vào Kaggle\n",
    "Trong Kaggle, bạn KHÔNG CẦN dùng lệnh `!git clone` vì nó rất chậm và hay lỗi.\n",
    "1. Nhìn sang cột bên phải của giao diện Kaggle, bấm nút **Add Input** (hoặc Add Data).\n",
    "2. Gõ tìm kiếm: **PlantDoc Classification** (hoặc Plant Village) và bấm phím **+ (Add)**.\n",
    "3. Sửa đường dẫn biến `DATASET_PATH` ở Ô Code bên dưới thành đường dẫn thư mục `train` của dataset bạn vừa thêm (thường nằm trong `/kaggle/input/tên-dataset/train`)."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "\n",
    "# Script tự động tìm thư mục dữ liệu của bạn\n",
    "DATASET_PATH = None\n",
    "for root, dirs, files in os.walk('/kaggle/input'):\n",
    "    # PyTorch ImageFolder yêu cầu một thư mục chứa nhiều thư mục con (mỗi thư mục con là 1 loại bệnh).\n",
    "    # Chúng ta tìm thư mục nào có từ 10 thư mục con trở lên.\n",
    "    if len(dirs) >= 10:\n",
    "        DATASET_PATH = root\n",
    "        break\n",
    "\n",
    "if DATASET_PATH:\n",
    "    print(f'🎉 TUYỆT VỜI! Đã tự động tìm thấy dữ liệu tại: {DATASET_PATH}')\n",
    "else:\n",
    "    print('❌ LỖI: Kaggle có thể đang mất thời gian để tải dữ liệu vào phiên làm việc. Bạn hãy đợi khoảng 1 phút rồi bấm chạy lại ô Code này nhé!')\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 2. Import Thư viện PyTorch"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "import torch\n",
    "import torch.nn as nn\n",
    "from torchvision import datasets, transforms, models\n",
    "from torch.utils.data import DataLoader\n",
    "import json\n",
    "\n",
    "device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')\n",
    "print(f'Sử dụng thiết bị: {device}')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 3. Load Dữ liệu"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "transform = transforms.Compose([\n",
    "    transforms.Resize((224, 224)),\n",
    "    transforms.ToTensor(),\n",
    "    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])\n",
    "])\n",
    "\n",
    "train_dataset = datasets.ImageFolder(DATASET_PATH, transform=transform)\n",
    "train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)\n",
    "\n",
    "# Lưu tên các loại bệnh ra file json để Backend sử dụng\n",
    "class_indices = {v: k for k, v in train_dataset.class_to_idx.items()}\n",
    "with open('class_indices.json', 'w') as f:\n",
    "    json.dump(class_indices, f)\n",
    "print(f'Số lượng loại bệnh: {len(class_indices)}')\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 4. Xây dựng Model (Sử dụng Transfer Learning ResNet18)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "model = models.resnet18(pretrained=True)\n",
    "num_ftrs = model.fc.in_features\n",
    "model.fc = nn.Linear(num_ftrs, len(class_indices))\n",
    "model = model.to(device)\n",
    "\n",
    "criterion = nn.CrossEntropyLoss()\n",
    "optimizer = torch.optim.Adam(model.parameters(), lr=0.001)"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 5. Huấn luyện Model"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "epochs = 10\n",
    "for epoch in range(epochs):\n",
    "    model.train()\n",
    "    running_loss = 0.0\n",
    "    for inputs, labels in train_loader:\n",
    "        inputs, labels = inputs.to(device), labels.to(device)\n",
    "        \n",
    "        optimizer.zero_grad()\n",
    "        outputs = model(inputs)\n",
    "        loss = criterion(outputs, labels)\n",
    "        loss.backward()\n",
    "        optimizer.step()\n",
    "        \n",
    "        running_loss += loss.item()\n",
    "        \n",
    "    print(f'Epoch {epoch+1}/{epochs}, Loss: {running_loss/len(train_loader):.4f}')"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## 6. Lưu file Model"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": [
    "torch.save(model.state_dict(), 'best_model.pt')\n",
    "print('Đã lưu model thành best_model.pt! Vui lòng tải file này và class_indices.json về máy.')"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.8.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}

with open('../notebooks/kaggle_train.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=1)

print("Created kaggle_train.ipynb successfully!")
