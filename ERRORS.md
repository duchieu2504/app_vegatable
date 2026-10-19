# BẢNG THEO DÕI LỖI (ERRORS LOG)

## [2026-04-25 15:51] - Lỗi không tìm thấy lệnh PIP (Infrastructure Error)

- **Type**: Process & Test Failure (Infrastructure Fail)
- **Severity**: High
- **File**: `N/A`
- **Agent**: emyeu
- **Root Cause**: Máy Windows của người dùng chưa cài đặt Python, hoặc cài đặt rồi nhưng chưa thêm `pip` vào biến môi trường `PATH`.
- **Error Message**: 
  ```text
  pip : The term 'pip' is not recognized as the name of a cmdlet, function, script file, or operable program.
  ```
- **Fix Applied**: Đề xuất kiểm tra `py --version`, tải Python và nhớ tick "Add to PATH", hoặc dùng lệnh thay thế.
- **Prevention**: Thêm bước kiểm tra môi trường Python vào quy trình trước khi cài đặt requirements trên Windows.
- **Status**: Fixed
---

## [2026-04-25 16:14] - AutoTrading Disabled (Integration Error)

- **Type**: Integration Error (MT5 Config)
- **Severity**: High
- **File**: `execution.py`
- **Agent**: emyeu
- **Root Cause**: Bot bắn lệnh thành công đến MT5 nhưng bị phần mềm MT5 từ chối do tính năng "Algo Trading" đang bị tắt trên giao diện người dùng.
- **Error Message**: 
  ```text
  retcode=10027, comment=AutoTrading disabled by client
  ```
- **Fix Applied**: Hướng dẫn người dùng bật nút "Algo Trading" trên thanh công cụ của phần mềm MT5.
- **Prevention**: Thêm cảnh báo hoặc code kiểm tra trạng thái `mt5.terminal_info().trade_allowed` ở đầu script.
- **Status**: Fixed
---

## [2026-04-25 16:28] - UnicodeEncodeError in Logging (Runtime Error)

- **Type**: Runtime Error
- **Severity**: Medium
- **File**: `main.py`
- **Agent**: emyeu
- **Root Cause**: Windows mặc định dùng encoding `cp1252` nên không thể ghi các ký tự tiếng Việt (ví dụ chữ 'ạ' trong "Trạng thái DCA") vào file `bot.log`.
- **Error Message**: 
  ```text
  UnicodeEncodeError: 'charmap' codec can't encode character '\u1ea1'
  ```
- **Fix Applied**: Bổ sung tham số `encoding="utf-8"` vào hàm `logging.FileHandler("bot.log")`.
- **Prevention**: Luôn set `encoding="utf-8"` khi xử lý File I/O trên Windows.
- **Status**: Fixed
---
