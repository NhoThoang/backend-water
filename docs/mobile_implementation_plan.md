# Kế hoạch Triển khai Mobile App (Flutter) - Hệ thống Quản lý Nước

Ứng dụng di động được thiết kế chuyên biệt cho hai nhóm đối tượng: **Nhân viên hiện trường (Worker)** và **Khách hàng (Customer)**, hỗ trợ cơ chế hoạt động Offline để đảm bảo công việc không bị gián đoạn.

## 1. Công nghệ & Thư viện (Tech Stack)
- **Framework**: Flutter 3.x (Clean Architecture).
- **State Management**: `provider` hoặc `bloc` (Quản lý trạng thái login và đồng bộ dữ liệu).
- **Networking**: `dio` + `interceptors` (Xử lý JWT Token & Auto-refresh).
- **Local Storage**: 
    - `sqflite`: Lưu trữ danh mục hộ dân và hàng đợi đồng bộ (Sync Queue) khi Offline.
    - `flutter_secure_storage`: Lưu trữ token an toàn.
- **Media**: `image_picker` & `camera` (Chụp ảnh đồng hồ nước).
- **UI**: `google_fonts`, `font_awesome_flutter`, `cached_network_image`.

## 2. Tính năng chính cho Nhân viên (Worker Flow)

### A. Đồng bộ dữ liệu (Sync Strategy)
- Gọi API `GET /customers/` để tải toàn bộ danh sách hộ dân về SQLite.
- Lưu trữ offline các thông tin cơ bản: Mã KH, Tên, Địa chỉ, Số seri đồng hồ.

### B. Ghi chỉ số tại hiện trường
- Tìm kiếm hộ dân trong SQLite (nhanh, không cần mạng).
- Chụp ảnh đồng hồ xác thực.
- Nhập chỉ số mới.
- **Xử lý Offline**: Nếu không có mạng, bản ghi được lưu vào hàng đợi (Queue) kèm đường dẫn ảnh cục bộ.
- **Xử lý Online**: Tự động gọi `POST /uploads/meter-image/` rồi `POST /readings/`.

## 3. Tính năng chính cho Khách hàng (Customer Flow)

### A. Dashboard cá nhân
- Sử dụng API `GET /reports/dashboard-summary` để hiển thị: Tổng nợ, Chỉ số mới nhất, Biểu đồ tiêu thụ.

### B. Hóa đơn & Thanh toán
- `GET /reports/unpaid`: Xem các hóa đơn chưa trả.
- `GET /payments/me`: Xem lịch sử giao dịch.
- Tích hợp hiển thị mã QR thanh toán (VietQR) dựa trên thông tin hóa đơn.

## 4. Danh sách API tích hợp (Mobile-Specific)

- **Auth**: `/auth/login`, `/auth/refresh`, `/auth/me`.
- **Worker**:
    - `GET /customers/` (Tải danh sách).
    - `POST /uploads/meter-image/{id}` (Tải ảnh lên MinIO).
    - `POST /readings/` (Gửi chỉ số & tạo hóa đơn).
- **Customer**:
    - `GET /reports/dashboard-summary` (Tổng quan).
    - `GET /reports/unpaid` (Nợ đọng).
    - `GET /readings/me` (Lịch sử chỉ số).
    - `GET /payments/me` (Lịch sử thanh toán).

## 5. Lộ trình thực hiện (Roadmap)

### Giai đoạn 1: Core & Auth
- Thiết lập Project, Dio Client, Secure Storage.
- Xây dựng module Đăng nhập & Quản lý phiên.

### Giai đoạn 2: Worker Offline Module
- Triển khai SQLite schema cho Customers & Readings.
- Xây dựng logic "Queue" để tự động đẩy dữ liệu khi có mạng trở lại.
- Tích hợp Camera & Image Processing.

### Giai đoạn 3: Customer Module
- Phát triển giao diện Dashboard và biểu đồ tiêu thụ.
- Hiển thị danh sách hóa đơn và tích hợp QR Code.

### Giai đoạn 4: Testing & Polish
- Kiểm thử cơ chế mất mạng giữa chừng khi đang upload.
- Tối ưu hiệu năng render danh sách lớn.

---
*Cập nhật: 2026-05-02 - Đội ngũ Antigravity*
