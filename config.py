import os
from dotenv import load_dotenv

load_dotenv()

# Thông tin đăng nhập MT5
LOGIN = int(os.getenv("MT5_LOGIN", 0))
PASSWORD = os.getenv("MT5_PASSWORD", "")
SERVER = os.getenv("MT5_SERVER", "")

# Cài đặt giao dịch
TRADE_MODE = "XAU"   # Lựa chọn: "BTC" (Bitcoin) hoặc "XAU" (Vàng)
ACCOUNT_SUFFIX = "c" # Hậu tố tài khoản Exness ("m", "c", hoặc "")

if TRADE_MODE == "BTC":
    SYMBOL = "BTCUSD" + ACCOUNT_SUFFIX
elif TRADE_MODE == "XAU":
    SYMBOL = "XAUUSD" + ACCOUNT_SUFFIX
else:
    SYMBOL = "BTCUSD" + ACCOUNT_SUFFIX

# ----------------- TELEGRAM BOT -----------------
TELEGRAM_BOT_TOKEN = "" # Tạm tắt thông báo Telegram
TELEGRAM_CHAT_ID = "6244136486"        # Sẽ điền Chat ID vào đây

# ----------------- CÀI ĐẶT BOT -----------------
UPDATE_INTERVAL = 1          # Tốc độ quét giá (giây)
PRINT_ORDER_OPENING = True   # In dòng vào lệnh
SHOW_CONTINUOUS_STATUS = False # In trạng thái Lãi/Lỗ liên tục
SHOW_DEBUG_LOGS = False      # Bật/tắt in chi tiết tiến trình tìm lệnh (mặc định Tắt để đỡ rối mắt)

# ----------------- HƯỚNG GIAO DỊCH -----------------
ALLOW_BUY = True             # Cho phép bot mở lệnh BUY (Bắt đáy / Mua khi giá thấp)
ALLOW_SELL = True            # Cho phép bot mở lệnh SELL (Đánh đỉnh / Bán khi giá cao)

# ----------------- CHIẾN LƯỢC VÀO LỆNH (DCA BOT) -----------------
TF_LTF = "M5"                # Khung thời gian để bot chạy (Mặc định: M5)
DCA_CONSECUTIVE_BEAR_CANDLES = 2 # Số nến giảm liên tiếp trên khung M5 để kích hoạt bắt đáy (BUY)
DCA_CONSECUTIVE_BULL_CANDLES = 2 # Số nến tăng liên tiếp trên khung M5 để kích hoạt đánh đỉnh (SELL)
DCA_RSI_PERIOD = 14          # Chu kỳ RSI để xác định "Giá thấp/cao"
DCA_RSI_OVERSOLD = 40        # RSI < 40 là vào lệnh BUY (giá thấp)
DCA_RSI_OVERBOUGHT = 70      # RSI > 70 là vào lệnh SELL (giá cao)
DCA_MAX_CANDLE_SIZE = 3.0    # Kích thước nến M5 tối đa (USD). Nếu nến dài hơn mức này -> Đang xả/bơm mạnh -> Tạm dừng nhồi lệnh

# ----------------- QUẢN LÝ RỦI RO -----------------
LOT_SIZE = 0.02          # Khối lượng lệnh ban đầu
# ----------------- CƠ CHẾ DCA (Dollar Cost Averaging) -----------------
DCA_MAX_LEVELS = 50          # Số lệnh DCA tối đa nhồi thêm (tổng 51 lệnh)
DCA_VOL_ADD = 0.04          # Cộng thêm khối lượng cho lệnh sau (Ví dụ: 0.01 -> 0.02 -> 0.03)
DCA_STEP_USD = 4           # Giá đi ngược bao nhiêu USD thì nhồi lệnh tiếp theo

# -- Cơ chế chốt lời linh hoạt --
DCA_TARGET_PROFIT_PERCENT_LOW = 10.0  # Tỷ lệ chốt lời khi Tổng Lot < 0.5
DCA_TARGET_PROFIT_PERCENT_HIGH = 10.0  # Tỷ lệ chốt lời khi Tổng Lot >= 0.5
DCA_VOL_THRESHOLD = 0.5               # Mốc Tổng Lot để đổi tỷ lệ chốt lời

DCA_TARGET_PROFIT_USD = 5.0      # Chốt lời USD CỐ ĐỊNH bất chấp số Lot. Chỉ dùng khi các mốc % trên = 0.

# ----------------- GIỜ VÀNG GIAO DỊCH (UTC) -----------------
USE_KILLZONE = False         # Chỉ trade trong giờ vàng
KILLZONE_LONDON_START = 7    # 7:00 UTC = 14:00 VN (Phiên Âu)
KILLZONE_LONDON_END = 10     # 10:00 UTC = 17:00 VN
KILLZONE_NY_START = 12       # 12:00 UTC = 19:00 VN (Giao thoa Âu/Mỹ)
KILLZONE_NY_END = 15         # 15:00 UTC = 22:00 VN
