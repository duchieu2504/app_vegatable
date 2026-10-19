# Kiến trúc và Cấu trúc Dự án: AgriDoc AI

Tài liệu này mô tả luồng logic hoạt động và cấu trúc thư mục tối ưu của dự án AgriDoc AI. Việc tổ chức theo mô hình Monorepo (chứa cả AI, Backend và Mobile App trong cùng một repository) giúp dễ dàng quản lý phiên bản và đồng bộ code giữa các team.

---

## 1. Cấu trúc Logic Hệ thống (Logical Architecture)

Dự án hoạt động dựa trên luồng khép kín (End-to-End) theo các bước sau:

1.  **Thu thập hình ảnh (Client):** 
    Người dùng chụp ảnh lá cây hoặc tải ảnh từ thư viện qua ứng dụng di động (Mobile App).
2.  **Tiếp nhận yêu cầu (Backend API):** 
    Ảnh được mã hóa và gửi qua RESTful API (POST `/api/v1/diagnose`) đến máy chủ Backend (FastAPI).
3.  **Chuẩn đoán Hình ảnh (AI Core - Computer Vision):** 
    Backend chuyển ảnh cho mô hình PyTorch (Mạng CNN đã được Fine-tune bằng bộ dữ liệu PlantDoc). Mô hình sẽ xuất ra `Tên Bệnh` (ví dụ: *Tomato_Early_Blight*) và độ tin cậy (`Confidence Score`).
4.  **Suy luận Ngôn ngữ (AI Core - NLP):** 
    Backend lấy `Tên Bệnh`, đưa vào một System Prompt đã cấu hình sẵn và gọi API của LLM (Gemini/ChatGPT). LLM sẽ phân tích và trả về phác đồ điều trị, thuốc bảo vệ thực vật phù hợp.
5.  **Tổng hợp và Trả về (Backend -> Client):** 
    Backend ghép `Tên Bệnh` và `Phác đồ điều trị` thành một chuỗi JSON hợp nhất, lưu lịch sử vào Database và trả về cho Mobile App hiển thị.

---

## 2. Thiết kế Cấu trúc Thư mục (Folder Structure)

Dự án được chia thành 3 module chính độc lập để dễ dàng bảo trì và scale (mở rộng) sau này:

```text
app_vegetable_photo/
│
├── ai_core/                  # Khu vực dành riêng cho việc Train/Test mô hình Computer Vision
│   ├── dataset/              # Chứa ảnh từ PlantDoc (chia sẵn train/val/test)
│   ├── notebooks/            # Các file .ipynb để train và thử nghiệm (dựa trên Manthan89-py)
│   ├── scripts/              # Chứa file Python (train.py, evaluate.py) nếu chạy trên terminal
│   ├── saved_models/         # Nơi lưu trữ file model .pt (vd: best_model.pt) sau khi train
│   └── requirements.txt      # Thư viện riêng cho AI (torch, torchvision, pandas, numpy)
│
├── backend/                  # Khu vực API Server (Orchestrator)
│   ├── api/                  # Định nghĩa các endpoint (routes)
│   │   ├── routes/           # vd: diagnose_route.py, history_route.py
│   │   └── schemas.py        # Pydantic schemas để validate Data In/Out
│   ├── core/                 # Cấu hình hệ thống (config, biến môi trường, logging)
│   ├── database/             # Kết nối Database và Models (SQLAlchemy / Prisma)
│   ├── services/             # Nơi chứa Logic xử lý phức tạp nhất
│   │   ├── vision_service.py # Code load model .pt và chạy Inference (chuẩn đoán ảnh)
│   │   └── llm_service.py    # Code giao tiếp với Gemini/OpenAI API
│   ├── tests/                # Unit test cho Backend API
│   ├── main.py               # File gốc khởi chạy FastAPI
│   └── requirements.txt      # Thư viện riêng cho Backend (fastapi, uvicorn, google-generativeai)
│
├── mobile_app/               # Khu vực Frontend Ứng dụng Di động
│   ├── assets/               # Hình ảnh tĩnh, icons, fonts
│   ├── src/
│   │   ├── components/       # Các UI Component dùng chung (Button, Card, Modal)
│   │   ├── screens/          # Các trang giao diện (CameraScreen, ResultScreen, HistoryScreen)
│   │   ├── services/         # Code gọi API tới Backend (Axios/Fetch)
│   │   ├── utils/            # Các hàm hỗ trợ xử lý string, màu sắc, quyền camera
│   │   └── navigation/       # Định nghĩa luồng chuyển trang (React Navigation)
│   ├── App.js                # File gốc của ứng dụng React Native / Expo
│   └── package.json          # Quản lý thư viện NPM của Frontend
│
├── docs/                     # Tài liệu API (Postman/Swagger) và hướng dẫn cài đặt hệ thống
├── .gitignore                # Bỏ qua các file rác, model quá lớn, node_modules
├── .env.example              # Mẫu các biến môi trường cần thiết
└── README.md                 # Tài liệu tổng quan của Repository
```

## 3. Lý do lựa chọn Cấu trúc này
*   **Separation of Concerns (Tách biệt mối quan tâm):** Team AI chỉ làm việc trong `ai_core`, Team Backend lo phần `backend`, và Frontend ở `mobile_app`. Tránh xung đột (conflict) code khi làm việc nhóm.
*   **Tối ưu Deploy:** Khi đưa lên server thật (Production), chúng ta chỉ cần đóng gói (Dockerize) thư mục `backend` (bao gồm model trong `saved_models`), hoàn toàn không cần copy các file Train nặng nề trong `ai_core`.
*   **Module hóa LLM & CV:** Việc tách riêng `vision_service.py` và `llm_service.py` giúp sau này nếu bạn muốn đổi từ Gemini sang ChatGPT, hay đổi từ mô hình PyTorch sang YOLO, bạn chỉ cần sửa đúng 1 file mà không sợ sập toàn bộ hệ thống.
