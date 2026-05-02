# Tài Liệu API Backend - Water Billing App

Tất cả các API đều có tiền tố mặc định là: `http://localhost:8000/api/v1`

---

## 1. Authentication (Xác thực)

### 🔑 Đăng nhập (Login)
- **Endpoint**: `POST /auth/login`
- **Quyền truy cập**: Công khai (Public)
- **Input (JSON)**:
    - `username`: Tên đăng nhập (hoặc Mã khách hàng)
    - `password`: Mật khẩu
- **Output (200 OK)**:
    ```json
    {
      "access_token": "string",
      "refresh_token": "string",
      "token_type": "bearer"
    }
    ```

### 🔄 Làm mới Token (Refresh Token)
- **Endpoint**: `POST /auth/refresh`
- **Input (JSON)**:
    - `refresh_token`: Token dùng để làm mới
- **Output (200 OK)**:
    ```json
    {
      "access_token": "new_access_token",
      "refresh_token": "old_refresh_token",
      "token_type": "bearer"
    }
    ```

### 🚪 Đăng xuất (Logout)
- **Endpoint**: `POST /auth/logout`
- **Input (JSON)**:
    - `refresh_token`: Token cần thu hồi
- **Output (200 OK)**:
    ```json
    { "message": "Successfully logged out" }
    ```

### 👤 Lấy thông tin cá nhân (Get Profile)
- **Endpoint**: `GET /auth/me`
- **Quyền truy cập**: Đã đăng nhập
- **Output (200 OK)**:
    ```json
    {
      "id": 1,
      "username": "admin",
      "customer_id": "C001",
      "role": "admin",
      "phone_number": "0987654321",
      "address": "Hà Nội",
      "created_at": "2026-05-01T..."
    }
    ```

### ✏️ Cập nhật thông tin cá nhân (Update Profile)
- **Endpoint**: `PATCH /auth/me`
- **Quyền truy cập**: Đã đăng nhập
- **Input (JSON)**:
    ```json
    {
      "phone_number": "0123456789",
      "address": "TP.HCM",
      "password": "newpassword123"
    }
    ```
- **Output (200 OK)**: Đối tượng User đã cập nhật.


---

## 2. Hộ dân (Customers)

### 📋 Liệt kê hộ dân
- **Endpoint**: `GET /customers/`
- **Quyền**: Admin / Worker
- **Query Params**: `skip` (mặc định 0), `limit` (mặc định 100)
- **Output**: Danh sách các đối tượng Customer.

### ➕ Tạo hộ dân mới
- **Endpoint**: `POST /customers/`
- **Quyền**: Admin
- **Input (JSON)**:
    ```json
    {
      "name": "Nguyễn Văn A",
      "address": "123 Đường ABC",
      "customer_type": "residential", // hoặc "business"
      "status": "active"
    }
    ```
- **Output**: Đối tượng Customer vừa tạo kèm ID.

---

## 3. Ghi chỉ số (Meter Readings)

### 📝 Gửi chỉ số nước mới
- **Endpoint**: `POST /readings/`
- **Quyền**: Admin / Worker
- **Input (JSON)**:
    ```json
    {
      "customer_id": 1,
      "reading": 150.5,
      "month": "2026-05",
      "image_url": "path/to/image.jpg"
    }
    ```
- **Output (200 OK)**:
    ```json
    {
      "reading": { "id": 1, "is_anomaly": false, ... },
      "bill": {
        "id": 10,
        "consumption": 15.0,
        "total_amount": 125000.0,
        "status": "unpaid",
        "due_date": "2026-05-16T..."
      }
    }
    ```

### ⚠️ Danh sách cảnh báo bất thường
- **Endpoint**: `GET /readings/anomalies`
- **Quyền**: Admin
- **Output**: Danh sách các bản ghi `MeterReading` có `is_anomaly=true`.

### 📖 Xem lịch sử cá nhân (My Readings)
- **Endpoint**: `GET /readings/me`
- **Quyền truy cập**: Đã đăng nhập (Vai trò User/Customer)
- **Output**: Danh sách lịch sử ghi chỉ số của chính mình.


---

## 4. Thanh toán (Payments)

### 📥 Webhook tiếp nhận thanh toán (SePay)
- **Endpoint**: `POST /payments/webhook/sepay`
- **Quyền**: Công khai (SePay gọi)
- **Input (JSON)**: Theo cấu trúc SePay (chứa `content` và `transferAmount`).
- **Logic**: Tự động tìm hóa đơn từ `content` và gạch nợ.

### 📜 Lịch sử thanh toán
- **Endpoint**: `GET /payments/history`
- **Quyền**: Admin (xem tất cả) / User (xem của mình)
- **Output**: Danh sách các giao dịch thanh toán thành công.

### 💳 Xem thanh toán cá nhân (My Payments)
- **Endpoint**: `GET /payments/me`
- **Quyền truy cập**: Đã đăng nhập (Vai trò User/Customer)
- **Output**: Danh sách lịch sử thanh toán của chính mình.


---

## 5. Báo cáo (Admin Reports)

### 📉 Hóa đơn chưa thanh toán (Nợ đọng)
- **Endpoint**: `GET /reports/unpaid`
- **Quyền**: Admin
- **Output**: Danh sách các `Bill` có trạng thái khác `paid`.

### 💰 Thống kê doanh thu
- **Endpoint**: `GET /reports/revenue-stats`
- **Quyền**: Admin
- **Output**:
    ```json
    [
      {
        "month": "2026-05",
        "total_billed": 5000000,
        "total_collected": 3500000
      }
    ]
    ```

### 🚨 Lọc hộ tiêu thụ cao
- **Endpoint**: `GET /reports/high-consumption`
- **Query Params**: `threshold` (ngưỡng tiêu thụ, mặc định 50.0)
- **Output**: Danh sách hộ dân tiêu thụ >= ngưỡng.

---

## 6. Lưu trữ (Uploads)

### 📸 Upload ảnh đồng hồ nước (Meter Image)
- **Endpoint**: `POST /uploads/meter-image/{customer_id}`
- **Quyền truy cập**: Admin, Worker
- **Input (Multipart/Form-Data)**:
    - `file`: File ảnh chụp đồng hồ
- **Output (200 OK)**:
    ```json
    {
      "image_path": "customers/1/uuid_filename.jpg",
      "filename": "original_name.jpg"
    }
    ```
- **Lưu ý**: Bucket MinIO được cấu hình **Public Read**. Client có thể truy cập ảnh trực tiếp qua: 
  `http://<minio-host>:<port>/<bucket>/<image_path>`

---

## 7. User Management (Quản lý người dùng - Excel)

Dành riêng cho **Admin** để quản lý danh sách tài khoản khách hàng qua Excel.

### 📤 Tải lên danh sách Excel (Upload)
- **Endpoint**: `POST /users/upload`
*   **Quyền truy cập**: Admin
- **Input (Multipart/Form-Data)**:
    - `file`: File Excel (.xlsx hoặc .xls)
- **Cấu trúc File Excel (6 cột)**:
    - `mã khách hàng` (Bắt buộc): Định danh duy nhất.
    - `tên đăng nhập`: Nếu trống sẽ lấy mã khách hàng.
    - `mật khẩu`: Nếu trống sẽ lấy SĐT hoặc mặc định `zxcvbnm12345`.
    - `vai trò`: `admin`, `worker`, `user` (mặc định là `user`).
    - `số điện thoại`: Thông tin SĐT.
    - `địa chỉ`: Địa chỉ khách hàng.
- **Output (201 Created)**:
    ```json
    {
      "message": "Processing complete",
      "created": 10,
      "skipped": 2
    }
    ```

### 📥 Xuất danh sách Excel (Export)
- **Endpoint**: `GET /users/export`
*   **Quyền truy cập**: Admin
- **Output**: File Excel `customers_export.xlsx` chứa danh sách toàn bộ khách hàng.
