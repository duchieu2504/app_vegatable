# 📘 Hướng Dẫn Chi Tiết: Từ Roboflow Đến Kaggle (Train AI)

Tài liệu này hướng dẫn bạn từng bước cách tự xây dựng tập dữ liệu các loại rau địa phương (Rau muống, Rau dền, Cải ngọt...) và huấn luyện mô hình Trí tuệ Nhân tạo (AI) để cập nhật vào ứng dụng **AgriDoc AI**.

---

## PHẦN 1: TẠO VÀ XỬ LÝ DỮ LIỆU TRÊN ROBOFLOW

Dự án của chúng ta sử dụng bài toán **Phân loại ảnh (Image Classification)**. Tức là hệ thống sẽ nhìn toàn bộ bức ảnh để phán đoán xem chiếc lá đó bị bệnh gì, thay vì tìm từng đốm bệnh nhỏ.

### Bước 1: Chuẩn bị dữ liệu (Tự chụp hoặc Lấy có sẵn)

**Cách 1: Tự chụp ảnh bằng điện thoại**
1. Chụp ảnh lá rau bằng điện thoại. Mỗi loại bệnh cần ít nhất **100-200 ảnh**.
2. Phân loại ảnh trên máy tính bằng cách tạo các thư mục. **Lưu ý cực kỳ quan trọng:** Đặt tên thư mục theo đúng cấu trúc `TênCây___TênBệnh` (3 dấu gạch dưới). 
   - *Ví dụ:* `RauMuong___KhoeManh`, `RauMuong___BenhRiSat`
3. Đưa tất cả các ảnh vào đúng thư mục của nó.

**Cách 2: Sử dụng kho dữ liệu khổng lồ có sẵn (Roboflow Universe)**
Nếu bạn không có thời gian đi chụp thực tế, Roboflow cung cấp kho tàng **Roboflow Universe** với hàng chục ngàn bộ dữ liệu Nông nghiệp miễn phí!
1. Truy cập [universe.roboflow.com](https://universe.roboflow.com/).
2. Gõ vào ô tìm kiếm các từ khóa: *"plant disease", "vegetable leaf", "cabbage disease", "tomato leaf"*...
3. Chọn một bộ dữ liệu bạn ưng ý (Chú ý xem cột Project Type có phải là *Classification* không).
4. Bấm vào nút **Download Dataset**, chọn định dạng **Folder Structure** và copy đoạn code API (Mã Python) để dán thẳng vào Kaggle. Bạn có thể bỏ qua hoàn toàn Bước 2, 3, 4 ở dưới!

### Bước 2: Tạo Project trên Roboflow
1. Truy cập [Roboflow.com](https://roboflow.com) và đăng ký/đăng nhập.
2. Bấm **Create New Project**.
3. Điền thông tin:
   - **Project Name:** `AgriDoc_Vegetables`
   - **License:** Public (hoặc Private nếu có gói Pro).
   - **Project Type:** **Bắt buộc chọn `Single-Label Classification`** (Tuyệt đối KHÔNG chọn Object Detection vì AI của ta là phân loại nguyên bức ảnh).
4. Bấm **Create Public Project**.

### Bước 3: Upload và Gán nhãn (Labeling)
1. Kéo thả **toàn bộ các thư mục** bạn đã phân loại ở Bước 1 vào giao diện Roboflow.
2. Roboflow sẽ cực kỳ thông minh: Nó tự động lấy **tên thư mục** làm **Nhãn (Label)** cho toàn bộ ảnh bên trong. Bạn không cần phải ngồi click gán nhãn từng tấm!
3. Bấm **Save and Continue**.
4. Ở phần chia tập dữ liệu (Split), giữ nguyên mặc định là **70% Train, 20% Valid, 10% Test**. Bấm **Continue**.

### Bước 4: Tăng cường dữ liệu (Augmentation) và Sinh phiên bản
1. Bấm vào **Generate New Version** bên menu trái.
2. **Preprocessing (Tiền xử lý):**
   - Chọn **Resize**: Kích thước **224 x 224** (Đây là chuẩn của mô hình ResNet18/MobileNet).
3. **Augmentation (Tăng cường dữ liệu):** Nhằm giúp AI học tốt hơn từ ít ảnh, hãy thêm:
   - *Flip:* Horizontal, Vertical (Lật ngang, lật dọc).
   - *Rotation:* Between -15° and +15° (Xoay ảnh).
   - *Brightness:* Between -15% and +15% (Đổi độ sáng tối).
4. Bấm **Generate**. Roboflow sẽ nhân bản số lượng ảnh của bạn lên gấp 2-3 lần (Tùy cấu hình).

### Bước 5: Lấy Code Tải Dữ Liệu
1. Khi phiên bản đã tạo xong, bấm nút **Export Dataset** (Góc trên bên phải).
2. Chọn Format: **Folder Structure**.
3. Tích chọn **"Show download code"**. Bấm Continue.
4. Chọn tab **Jupyter / Terminal**. Copy lại toàn bộ đoạn code Python chứa API Key mà Roboflow cung cấp (Đoạn mã bắt đầu bằng `!pip install roboflow`).

---

## PHẦN 2: HUẤN LUYỆN TRÊN KAGGLE (HOẶC GOOGLE COLAB)

### Bước 1: Mở môi trường huấn luyện
1. Truy cập [Kaggle.com](https://kaggle.com) hoặc [Google Colab](https://colab.research.google.com/).
2. Nếu dùng Kaggle: Tạo một Notebook mới. Nhớ bật GPU (Bên phải -> Settings -> Accelerator -> Chọn GPU T4).
3. (Khuyến nghị) Bạn có thể Upload thẳng file `ai_core/notebooks/colab_train.ipynb` có sẵn trong source code dự án lên Kaggle/Colab để chạy cho chuẩn.

### Bước 2: Dán Code từ Roboflow và Gom Dữ Liệu
1. Mở file notebook `colab_train.ipynb` (hoặc tạo một Notebook mới trên Kaggle/Colab).
2. Xóa ô code đầu tiên (ô chứa lệnh `!git clone...`).
3. Tạo một ô Code (Cell) mới ở trên cùng và **Dán đoạn code Python** mà bạn đã copy từ Roboflow vào đó.
4. **Cực kỳ quan trọng:** Dán thêm đoạn code Python sau đây ngay bên dưới đoạn code của Roboflow (chung 1 ô hoặc ô mới đều được):

```python
import os
import shutil

# rf_path chính là biến dataset.location do Roboflow tạo ra ở trên
rf_path = dataset.location
os.makedirs("Dataset", exist_ok=True)

# Gom tất cả ảnh từ train, valid, test vào chung 1 thư mục Dataset
for split in ['train', 'valid', 'test']:
    split_dir = os.path.join(rf_path, split)
    if os.path.exists(split_dir):
        for class_name in os.listdir(split_dir):
            src_class = os.path.join(split_dir, class_name)
            if os.path.isdir(src_class): # Bỏ qua các file rác/README của Roboflow
                dst_class = os.path.join("Dataset", class_name)
                os.makedirs(dst_class, exist_ok=True)
                for img in os.listdir(src_class):
                    shutil.copy(os.path.join(src_class, img), os.path.join(dst_class, img))
                
print("Gom dữ liệu thành công! Đã sẵn sàng huấn luyện.")
```

5. Bấm nút Play (Run) để chạy ô code đó. Toàn bộ hình ảnh sẽ được tải về và gom lại thành thư mục `Dataset` chuẩn xác.

### Bước 3: Chạy Huấn luyện (Train AI)
1. Vì chúng ta đã tự động gom dữ liệu vào thư mục `Dataset` ở Bước 2, bạn **KHÔNG CẦN SỬA BẤT CỨ DÒNG CODE NÀO** ở các ô bên dưới nữa!
2. Chỉ cần bấm **Run All** (Chạy tất cả các ô code từ trên xuống dưới).
3. Đợi mô hình huấn luyện xong (khoảng 30 phút - 1 tiếng tùy số lượng ảnh). Kéo xuống cuối cùng, bạn sẽ nhận được 2 file:
   - `best_model.pt` (Trọng số AI)
   - `class_indices.json` (Danh sách các bệnh)
4. Tải 2 file này về máy tính và chép đè vào thư mục `backend/saved_models/` của ứng dụng AgriDoc AI. Mọi thứ sẽ tự động cập nhật!
2. Bấm chạy tuần tự các đoạn code huấn luyện.
3. Chờ đợi từ 15-30 phút (tùy số lượng ảnh) để PyTorch thực hiện quá trình học (Epochs). Bạn sẽ thấy độ chính xác (Accuracy) tăng dần lên sau mỗi vòng học.

### Bước 4: Tải Mô Hình Mới Về
1. Sau khi quá trình Train kết thúc hoàn toàn (Đạt trên 90% accuracy là rất tốt). Đoạn code cuối cùng của Notebook sẽ xuất ra 2 file:
   - `best_model.pt` (Bộ não của AI).
   - `class_indices.json` (Bảng dịch: Bệnh số 0 là rau gì, số 1 là rau gì...).
2. Bấm chuột phải vào 2 file này trên Kaggle/Colab và chọn **Download**.

---

## PHẦN 3: ĐƯA VÀO ỨNG DỤNG (DEPLOYMENT)

Phần này là dễ nhất! Ứng dụng đã được Cáo lập trình sẵn cơ chế tự động nhận dạng:

1. Trở về thư mục dự án trên máy tính của bạn.
2. Vào thư mục `backend/saved_models/`.
3. Chép (Paste) 2 file `best_model.pt` và `class_indices.json` vừa tải về, ghi đè lên 2 file cũ.
4. (Tùy chọn) Khởi động lại Backend Server (Tắt Terminal bằng Ctrl+C và chạy lại `uvicorn main:app --reload --host 0.0.0.0`).
5. **HOÀN TẤT!** 
   - Mở App lên, vào tab **Từ Điển**, bạn sẽ thấy danh sách bệnh cũ đã biến mất, thay vào đó là **Rau muống, Rau dền**...
   - Mở Camera, chụp lá rau muống, AI sẽ nhận diện đúng mô hình bạn vừa huấn luyện! Gemini sẽ tự động viết nội dung chữa trị sinh học cho các loại rau này.
