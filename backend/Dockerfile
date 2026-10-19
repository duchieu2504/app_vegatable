# Sử dụng image Python 3.10 slim để dung lượng nhẹ nhất có thể
FROM python:3.10-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Khai báo các biến môi trường để Python không tạo file cache và log in ngay ra terminal
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Cài đặt các thư viện hệ thống cần thiết (nếu có)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy file requirements.txt vào container
COPY requirements.txt .

# Cài đặt các thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn backend vào container
COPY . .

# Expose cổng 8000 cho FastAPI
EXPOSE 8000

# Lệnh khởi chạy server bằng Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
