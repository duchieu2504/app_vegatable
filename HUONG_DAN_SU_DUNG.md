# 📖 Hướng Dẫn Sử Dụng Chi Tiết - Dự Án AgriDoc AI

Dự án **AgriDoc AI** là hệ thống thông minh ứng dụng Trí tuệ Nhân tạo (AI) để nhận diện sớm các bệnh trên lá rau tại địa phương. Hệ thống gồm 2 thành phần chính: **Mobile App (Frontend)** và **AI Server (Backend)**.

---

## 🚀 1. Hướng Dẫn Cài Đặt & Khởi Chạy

### A. Khởi động Máy chủ AI (Backend)
Máy chủ Backend xử lý hình ảnh qua mô hình PyTorch và giao tiếp với Gemini để lấy phác đồ điều trị.
1. Mở Terminal (Command Prompt / PowerShell).
2. Di chuyển vào thư mục backend:
   ```bash
   cd e:\Tradingbot\app_vegetable_photo\backend
   ```
3. Cài đặt các thư viện cần thiết (nếu chạy lần đầu):
   ```bash
   pip install -r requirements.txt
   ```
4. Khởi chạy Server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0
   ```
   *Lưu ý: Giữ Terminal này luôn mở trong quá trình sử dụng App.*

### B. Khởi động Ứng dụng Di động (Frontend)
1. Mở một Terminal mới.
2. Di chuyển vào thư mục mobile_app:
   ```bash
   cd e:\Tradingbot\app_vegetable_photo\mobile_app
   ```
3. Cài đặt gói (nếu chạy lần đầu):
   ```bash
   npm install
   ```
4. Cấp quyền chạy script (Nếu bị lỗi PowerShell):
   ```bash
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```
5. Khởi chạy Ứng dụng qua trình duyệt Web (ổn định nhất):
   ```bash
   npx expo start --web
   ```
6. Mở trình duyệt trên điện thoại (cùng mạng Wi-Fi với máy tính) và truy cập địa chỉ IP hiện trên Terminal (Ví dụ: `http://192.168.43.218:8081`).

---

## 🌿 2. Hướng Dẫn Sử Dụng Ứng Dụng (App)

Hệ thống có 3 chức năng chính (Tab) nằm ở dưới cùng màn hình:

- **📸 Tab Chẩn đoán:** 
  - Bấm vào nút Camera để chụp ảnh lá rau thực tế, hoặc nút Thư viện để tải ảnh có sẵn.
  - Hệ thống sẽ tự động tải ảnh lên AI Server. Sau vài giây, nó sẽ hiển thị Tên Bệnh, Mức độ tin cậy (%) và **Phác đồ điều trị sinh học** (Do Gemini tự động sinh ra).
- **📖 Tab Từ điển:** 
  - Hiển thị danh sách toàn bộ các loại rau và bệnh mà AI đã được huấn luyện.
  - Chạm vào tên cây (VD: Cà chua) để xem danh sách bệnh. Bấm "Xem chi tiết" để đọc triệu chứng và cách chữa.
- **⚙️ Tab Quản trị:** 
  - Dành cho Quản trị viên/Giáo viên để thêm thông tin chi tiết về các bệnh mới vào Từ điển.

---

## 🧠 3. Quy Trình Cập Nhật AI (Huấn Luyện Các Loại Rau Địa Phương)

Hiện tại, hệ thống đang dùng mô hình có sẵn 38 loại bệnh. Theo đề tài nghiên cứu, để chuyển sang nhận diện các loại rau địa phương (Rau muống, Rau dền, Bắp cải...), hệ thống đã được thiết kế sẵn một **Kiến trúc đồng bộ hoàn toàn tự động**.

Bạn chỉ cần thực hiện việc huấn luyện mô hình mới, ứng dụng sẽ tự động cập nhật mọi thứ (Từ điển, Camera chẩn đoán) mà không cần sửa bất kỳ dòng code nào!

👉 **[Bấm vào đây để xem Hướng dẫn chi tiết cách dùng Roboflow và Kaggle để tự huấn luyện AI](HUONG_DAN_ROBOFLOW_KAGGLE.md)**

---

*Chúc bạn bảo vệ đề tài NCKHKT thành công và đạt giải cao!* 🏆🦊
