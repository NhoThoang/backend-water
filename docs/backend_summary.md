# Báo Cáo Kết Quả Triển Khai Backend - Water Billing App

Hệ thống Backend cho ứng dụng Quản lý nước đã được xây dựng hoàn tất với đầy đủ các tính năng nghiệp vụ cốt lõi, bảo mật và khả năng mở rộng cao.

## 1. Công Nghệ Sử Dụng
- **Ngôn ngữ**: Python 3.10+
- **Framework**: FastAPI (High performance).
- **Database**: PostgreSQL (Quản lý dữ liệu quan hệ).
- **Storage**: MinIO (Lưu trữ ảnh đồng hồ nước tập trung).
- **Containerization**: Docker & Docker Compose.
- **ORM**: SQLAlchemy 2.0.

## 2. Các Tính Năng Đã Hoàn Thành

### 🔐 Bảo mật & Xác thực
- **JWT Authentication**: Cơ chế Access Token (30 phút) và Refresh Token (30 ngày).
- **Token Revocation**: Hỗ trợ thu hồi Refresh Token trong DB khi người dùng đăng xuất.
- **Role-based Access Control (RBAC)**: Phân quyền rõ ràng Admin, Worker (Thợ), và User (Khách hàng).
- **Auto-Initialization**: Tự động tạo Admin mặc định từ cấu hình `.env` khi startup.

### 💧 Quản lý Hộ dân & Chỉ số nước
- **Quản lý hộ dân**: CRUD thông tin khách hàng, phân loại Hộ sinh hoạt / Kinh doanh.
- **Ghi chỉ số thông minh**:
    - Tự động tính lượng tiêu thụ dựa trên chỉ số tháng trước.
    - **Cảnh báo bất thường**: Tự động phát hiện và gắn cờ nếu tiêu thụ tăng đột biến (>50%).
    - **MinIO Integration**: Hỗ trợ upload ảnh chụp đồng hồ trực tiếp để làm minh chứng.

### 💰 Nghiệp vụ Tài chính & Thanh toán
- **Tính tiền bậc thang**: Hỗ trợ tính giá nước lũy tiến nhiều bậc (mặc định 4 bậc cho hộ dân).
- **Thuế & Phí**: Tự động tính 5% Thuế GTGT và 10% Phí bảo vệ môi trường.
- **Quản lý nợ**: Tự động quét và cộng dồn nợ cũ chưa thanh toán vào hóa đơn mới.
- **Thanh toán tự động**: Tích hợp Webhook SePay/Napas để gạch nợ hóa đơn ngay khi khách hàng chuyển khoản thành công.

### 📊 Quản lý cho Admin
- **Báo cáo nợ đọng**: API lọc danh sách các hóa đơn chưa thanh toán.
- **Thống kê doanh thu**: Báo cáo tiền thực thu vs tiền đã lập hóa đơn theo tháng.
- **Cảnh báo rò rỉ**: Dashboard lọc các hộ có chỉ số tăng vọt để kịp thời xử lý.

### 🛠 Hệ thống & Vận hành
- **Logging**: Cơ chế xoay vòng 3 file log (mỗi file 5MB) giúp quản lý log hiệu quả, tránh đầy ổ cứng.
- **Startup Logic**: Tự tạo bảng, nạp bảng giá mẫu và cấu hình môi trường tự động.

## 3. Danh sách API chính (V1)
- `/auth`: `login`, `refresh`, `logout`
- `/customers`: CRUD hộ dân.
- `/readings`: Ghi số nước, xem lịch sử, xem cảnh báo bất thường.
- `/payments`: Tiếp nhận Webhook thanh toán, lịch sử giao dịch.
- `/reports`: Thống kê doanh thu, lọc nợ đọng, lọc hộ tiêu thụ cao.
- `/uploads`: Upload ảnh chụp đồng hồ nước.

## 4. Hướng dẫn sử dụng nhanh
1. **Khởi chạy hạ tầng**: `docker-compose up -d`
2. **Cài đặt thư viện**: `pip install -r requirements.txt`
3. **Chạy Server**: `uvicorn app.main:app --reload`
4. **Kiểm tra hệ thống**: `python test_api.py`

---
Hệ thống hiện tại đã sẵn sàng để tích hợp với Mobile App hoặc Web Frontend.
