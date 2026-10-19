import json

NOTEBOOK_PATH = "ai_core/notebooks/colab_train.ipynb"

def update_notebook():
    with open(NOTEBOOK_PATH, 'r', encoding='utf-8') as f:
        nb = json.load(f)

    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            source = "".join(cell['source'])
            
            # Thay thế mô hình CNN bằng ResNet18
            if "class CNN(nn.Module):" in source:
                new_source = [
                    "from torchvision import models\n",
                    "\n",
                    "# Sử dụng Transfer Learning với ResNet18 thay vì tự viết CNN\n",
                    "model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)\n",
                    "\n",
                    "# Thay thế lớp phân loại cuối cùng (fc) cho phù hợp với số loại bệnh của chúng ta\n",
                    "num_ftrs = model.fc.in_features\n",
                    "model.fc = nn.Linear(num_ftrs, targets_size)\n",
                    "\n",
                    "# Đưa mô hình lên GPU\n",
                    "model = model.to(device)\n",
                    "\n",
                    "print(f\"✅ Mô hình ResNet18 đã sẵn sàng với {targets_size} loại bệnh!\")\n",
                    "print(f\"📐 Tổng tham số: {sum(p.numel() for p in model.parameters()):,}\")\n"
                ]
                cell['source'] = new_source
                
            # Thay đổi Epochs và Optimizer
            if "train_losses, validation_losses = batch_gd(" in source:
                # Thay optimizer thành lr nhỏ hơn cho transfer learning
                source = source.replace(
                    "optimizer = torch.optim.Adam(model.parameters())", 
                    "optimizer = torch.optim.Adam(model.parameters(), lr=0.0001) # Learning rate nhỏ cho Transfer Learning"
                )
                
                # Tăng epochs từ 5 lên 20
                source = source.replace(
                    "model, criterion, train_loader, validation_loader, 5",
                    "model, criterion, train_loader, validation_loader, 20"
                )
                
                # Split back into list of strings (Jupyter format)
                lines = source.split('\n')
                cell['source'] = [line + '\n' for line in lines[:-1]] + [lines[-1]] if lines[-1] != "" else [line + '\n' for line in lines]

    with open(NOTEBOOK_PATH, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1, ensure_ascii=False)
        
    print("Updated notebook successfully.")

if __name__ == "__main__":
    update_notebook()
