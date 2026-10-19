import os
import json
import urllib.request
import urllib.error

# Load class indices
with open("saved_models/class_indices.json", "r", encoding="utf-8") as f:
    class_indices = json.load(f)

# Create dataset directory
os.makedirs("dataset", exist_ok=True)

# GitHub API URL template for PlantVillage raw color dataset
# We use the GitHub API to list files in a directory
api_url_template = "https://api.github.com/repos/spMohanty/PlantVillage-Dataset/contents/raw/color/{}"

print("Bắt đầu tải ảnh mẫu từ PlantVillage GitHub...")

for idx, class_name in class_indices.items():
    disease_dir = os.path.join("dataset", class_name)
    os.makedirs(disease_dir, exist_ok=True)
    
    # If already has images, skip
    existing_files = [f for f in os.listdir(disease_dir) if f.lower().endswith(('.jpg', '.png'))]
    if len(existing_files) >= 2:
        print(f"Bỏ qua {class_name}, đã có đủ ảnh.")
        continue
        
    print(f"Đang tìm ảnh cho: {class_name}...")
    
    # Fetch list of files from GitHub API
    req = urllib.request.Request(api_url_template.format(urllib.parse.quote(class_name)))
    req.add_header('User-Agent', 'Mozilla/5.0')
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            # Get first 2 images
            count = 0
            for item in data:
                if item['name'].lower().endswith(('.jpg', '.png', '.jpeg')):
                    download_url = item['download_url']
                    file_path = os.path.join(disease_dir, item['name'])
                    
                    if not os.path.exists(file_path):
                        print(f"  -> Tải: {item['name']}")
                        # Download the image
                        try:
                            urllib.request.urlretrieve(download_url, file_path)
                            count += 1
                        except Exception as e:
                            print(f"  -> Lỗi khi tải ảnh: {e}")
                            
                if count >= 3:  # Tải 3 ảnh cho mỗi bệnh
                    break
                    
    except urllib.error.HTTPError as e:
        print(f"Lỗi API cho {class_name}: {e}")
    except Exception as e:
        print(f"Lỗi không xác định cho {class_name}: {e}")

print("Hoàn tất việc tải ảnh mẫu!")
