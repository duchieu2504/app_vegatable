# 🚀 Hướng Dẫn Cài Đặt & Khởi Chạy Dự Án AgriDoc AI (Từ GitHub)

Tài liệu này hướng dẫn chi tiết từng bước dành cho **người mới bắt đầu**, giúp bạn tự cài đặt môi trường và chạy toàn bộ hệ thống nhận diện bệnh rau **AgriDoc AI** trên laptop cá nhân sau khi tải mã nguồn từ GitHub: [https://github.com/duchieu2504/app_vegatable](https://github.com/duchieu2504/app_vegatable).

---

## 📋 MỤC LỤC
1. [Yêu cầu phần mềm nền tảng](#1-yêu-cầu-phần-mềm-nền-tảng-prerequisites)
2. [Tải dự án từ GitHub](#2-tải-dự-án-từ-github-clone)
3. [Cài đặt & Cấu hình Backend (AI Server)](#3-cài-đặt--cấu-hình-backend-ai-server)
4. [Cài đặt & Cấu hình Frontend (Mobile App / Web)](#4-cài-đặt--cấu-hình-frontend-mobile-app--web)
5. [Khởi chạy và Trải nghiệm ứng dụng](#5-khởi-chạy-và-trải-nghiệm-ứng-dụng)
6. [Khắc phục các lỗi thường gặp (Troubleshooting)](#6-khắc-phục-các-lỗi-thường-gặp-troubleshooting)

---

## 1. Yêu Cầu Phần Mềm Nền Tảng (Prerequisites)

Trước khi tải dự án, hãy đảm bảo máy tính cá nhân của bạn đã cài đặt 3 công cụ sau:

### 1.1. Cài đặt Git
* **Tải tại:** [https://git-scm.com/downloads](https://git-scm.com/downloads)
* Cài đặt với các lựa chọn mặc định.
* **Kiểm tra sau khi cài:** Mở Terminal (Command Prompt hoặc PowerShell) và gõ:
  ```bash
  git --version
  ```
  *(Nếu hiện `git version 2.x.x` là thành công).*

### 1.2. Cài đặt Python (Khuyên dùng bản 3.10 hoặc 3.11)
* **Tải tại:** [https://www.python.org/downloads/](https://www.python.org/downloads/) *(Chọn bản 3.10.x hoặc 3.11.x để tương thích tốt nhất với thư viện PyTorch)*.
* ⚠️ **LƯU Ý CỰC KỲ QUAN TRỌNG:** Ở màn hình cài đặt đầu tiên, **bắt buộc phải tích chọn ô: `Add Python to PATH`** (hoặc `Add python.exe to PATH`) ở phía dưới cùng trước khi bấm **Install Now**.
* **Kiểm tra sau khi cài:**
  ```bash
  python --version
  pip --version
  ```

### 1.3. Cài đặt Node.js (Khuyên dùng bản LTS)
* **Tải tại:** [https://nodejs.org/](https://nodejs.org/) *(Chọn bản **LTS - Long Term Support**, ví dụ v18.x hoặc v20.x)*.
* Cài đặt với các lựa chọn mặc định (bấm Next đến khi hoàn tất).
* **Kiểm tra sau khi cài:**
  ```bash
  node -v
  npm -v
  ```

---

## 2. Tải Dự Án Từ GitHub (Clone)

1. Mở cửa sổ **Terminal** (hoặc PowerShell) trên máy tính của bạn.
2. Di chuyển đến thư mục bạn muốn lưu dự án (Ví dụ ổ `D:\` hoặc `E:\` hoặc Desktop):
   ```bash
   cd D:\
   ```
3. Chạy lệnh clone dự án về máy:
   ```bash
   git clone https://github.com/duchieu2504/app_vegatable.git
   ```
4. Di chuyển vào thư mục dự án vừa tải:
   ```bash
   cd app_vegatable
   ```

---

## 3. Cài Đặt & Cấu Hình Backend (AI Server)

Backend được viết bằng **Python (FastAPI + PyTorch)** để nạp mô hình nhận diện AI và cung cấp API.

### Bước 3.1: Di chuyển vào thư mục backend
```bash
cd backend
```

### Bước 3.2: Tạo và kích hoạt môi trường ảo (Virtual Environment)
Môi trường ảo giúp các thư viện của dự án không bị xung đột với các phiên bản Python khác trên máy:

* **Tạo môi trường ảo:**
  ```bash
  python -m venv venv
  ```
* **Kích hoạt môi trường ảo:**
  - Trên **Windows (PowerShell / CMD):**
    ```bash
    venv\Scripts\activate
    ```
    *(Nếu kích hoạt thành công, bạn sẽ thấy chữ `(venv)` xuất hiện ở đầu dòng lệnh).*
  - Trên **macOS / Linux:**
    ```bash
    source venv/bin/activate
    ```

### Bước 3.3: Cài đặt toàn bộ thư viện Python
Chạy lệnh cài đặt tự động từ file `requirements.txt`:
```bash
pip install -r requirements.txt
```
*(Quá trình này sẽ tải các thư viện: `torch`, `torchvision`, `fastapi`, `uvicorn`, `Pillow`, `google-generativeai`... Hãy kiên nhẫn đợi 2 - 5 phút tùy tốc độ mạng).*

### Bước 3.4: Cấu hình file API Key `.env`
1. Trong thư mục `backend`, tạo một file mới đặt tên là `.env` (bạn có thể copy từ `.env.example`).
2. Mở file `.env` bằng Notepad hoặc VS Code và dán mã API Key của bạn:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
   > 💡 **Cách lấy API Key miễn phí:** Truy cập [Google AI Studio](https://aistudio.google.com/) ➔ Đăng nhập Gmail ➔ Chọn **Get API Key** ➔ **Create API Key**.

---

## 4. Cài Đặt & Cấu Hình Frontend (Mobile App / Web)

Frontend được phát triển bằng **React Native (Expo)**, có thể chạy trên trình duyệt Web hoặc ứng dụng di động.

### Bước 4.1: Mở một cửa sổ Terminal MỚI
*(Giữ nguyên cửa sổ Terminal của Backend và mở thêm 1 cửa sổ Terminal thứ 2).*

### Bước 4.2: Di chuyển vào thư mục `mobile_app`
```bash
cd app_vegatable/mobile_app
```

### Bước 4.3: Cài đặt các gói thư viện JavaScript
Chạy lệnh npm:
```bash
npm install
```
*(Lệnh này sẽ tự động tải các gói trong `package.json` vào thư mục `node_modules`).*

---

## 5. Khởi Chạy Và Trải Nghiệm Ứng Dụng

Sau khi hoàn tất cài đặt, bạn khởi động 2 phần theo thứ tự:

### 🔹 Bước 5.1: Khởi động Backend (Tại Terminal 1)
Đảm bảo đang ở thư mục `backend` và môi trường ảo `(venv)` đang bật:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
* **Kiểm tra thành công:** Mở trình duyệt máy tính vào [http://localhost:8000](http://localhost:8000) ➔ Hiện thông báo: `{"message":"Welcome to AgriDoc AI Backend"}`.
* Xem tài liệu API tự động tại: [http://localhost:8000/docs](http://localhost:8000/docs).
* ⚠️ *Lưu ý: Giữ cửa sổ Terminal này luôn chạy trong suốt quá trình dùng app.*

---

### 🔹 Bước 5.2: Khởi động Frontend (Tại Terminal 2)
Tại thư mục `mobile_app`:
```bash
npx expo start --web
```
* Trình duyệt máy tính sẽ tự động bật lên địa chỉ [http://localhost:8081](http://localhost:8081).
* Bạn đã có thể trải nghiệm đầy đủ các tính năng:
  - **Tab Chẩn đoán:** Chọn ảnh lá rau dền, rau muống, mồng tơi, rau ngót để AI dự đoán bệnh và hiển thị phác đồ điều trị.
  - **Tab Từ điển:** Xem chi tiết triệu chứng, tác nhân và cách phòng trị 13 nhóm bệnh.
  - **Tab Lịch sử:** Xem lại các lần chẩn đoán trước đó.

---

### 📱 Bước 5.3: Mở ứng dụng trên Điện thoại thông minh (Cùng mạng Wi-Fi)

1. Kết nối laptop và điện thoại của bạn vào **cùng một mạng Wi-Fi** (hoặc laptop phát Wi-Fi cho điện thoại kết nối).
2. Kiểm tra địa chỉ IPv4 của máy tính:
   - Trên Terminal gõ `ipconfig` ➔ Tìm dòng `IPv4 Address` của card Wi-Fi (ví dụ: `192.168.1.15`).
3. Mở trình duyệt trên điện thoại (Chrome / Safari), nhập địa chỉ:
   ```text
   http://<IP_MÁY_TÍNH>:8081
   Ví dụ: http://192.168.1.15:8081
   ```
4. Hệ thống đã có cơ chế tự động nhận diện IP, bạn có thể dùng camera điện thoại chụp ảnh lá rau thật ngoài vườn để chẩn đoán ngay lập tức!

---

## 6. Khắc Phục Các Lỗi Thường Gặp (Troubleshooting)

### ❌ Lỗi 1: `python` hoặc `pip` không được nhận diện (Command not found)
* **Nguyên nhân:** Khi cài đặt Python chưa tích chọn `Add Python to PATH`.
* **Cách sửa:** Gỡ Python ra cài lại, hoặc tìm `Edit the system environment variables` trên Windows ➔ Thêm đường dẫn thư mục cài Python vào biến `Path`.

### ❌ Lỗi 2: PowerShell báo lỗi `PSSecurityException` khi chạy `activate` hoặc `npm`
* **Nguyên nhân:** Windows chặn chạy script chưa ký.
* **Cách sửa:** Mở PowerShell và chạy lệnh sau (chọn Yes / All):
  ```bash
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  ```

### ❌ Lỗi 3: Điện thoại không kết nối được tới Backend (Báo lỗi mạng)
* **Nguyên nhân:** Tường lửa của Windows (Windows Firewall) đang chặn cổng `8000`.
* **Cách sửa:**
  1. Vào **Windows Defender Firewall** trên máy tính ➔ **Allow an app or feature through Windows Defender Firewall**.
  2. Tìm **Python** và tích chọn cả 2 ô **Private** và **Public**.
  3. Đảm bảo điện thoại và máy tính đang bắt chung một mạng Wi-Fi.

---

Chúc bạn cài đặt và trải nghiệm thành công dự án **AgriDoc AI**! 🌿🦊
