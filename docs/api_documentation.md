# Tài Liệu API Backend - Water Billing App

Tất cả các API đều có tiền tố mặc định là: `http://localhost:8000/api/v1`

---

## 1. Authentication (Xác thực)

### 🔑 Đăng nhập (Login)
- **Endpoint**: `POST /auth/login`
- **Quyền truy cập**: Công khai (Public)
- **Input (JSON)**: `username`, `password`
- **Output**: `access_token`, `refresh_token`, `token_type`

### 👤 Lấy thông tin cá nhân (Get Profile)
- **Endpoint**: `GET /auth/me`
- **Quyền**: Đã đăng nhập
- **Output**: Thông tin chi tiết User, Role, Customer ID.

### ✏️ Cập nhật thông tin cá nhân (Update Profile)
- **Endpoint**: `PATCH /auth/me`
- **Input**: `phone_number`, `address`, `password`.

---

## 2. Quản lý Hộ dân (Customers)

### 📋 Liệt kê hộ dân
- **Endpoint**: `GET /customers/`
- **Quyền**: Admin / Worker
- **Params**: `skip`, `limit`.

### ➕ Tạo hộ dân mới
- **Endpoint**: `POST /customers/`
- **Quyền**: Admin
- **Logic**: Tạo Customer và tài khoản User (Role: user) tương ứng.

### 🔍 Xem chi tiết hộ dân
- **Endpoint**: `GET /customers/{id}`
- **Quyền**: Admin / Worker / Bản thân Customer.

### ✏️ Cập nhật hộ dân
- **Endpoint**: `PATCH /customers/{id}`
- **Quyền**: Admin
- **Lưu ý**: Cập nhật cả thông tin Customer và password tài khoản User.

### 🗑️ Xóa hộ dân
- **Endpoint**: `DELETE /customers/{id}`
- **Quyền**: Admin
- **Lưu ý**: Xóa cả Customer và User liên kết.

---

## 3. Ghi chỉ số & Hóa đơn (Meter Readings)

### 📝 Gửi chỉ số nước mới
- **Endpoint**: `POST /readings/`
- **Quyền**: Admin / Worker
- **Logic**: Tự động tính tiền, tạo `Bill`. Kiểm tra bất thường (>50%).

### ⚠️ Danh sách chỉ số bất thường
- **Endpoint**: `GET /readings/anomalies`
- **Quyền**: Admin.

### 📜 Lịch sử ghi số theo khách hàng
- **Endpoint**: `GET /readings/customer/{customer_id}`
- **Quyền**: Admin / Worker.

### 📖 Lịch sử ghi số cá nhân
- **Endpoint**: `GET /readings/me`
- **Quyền**: Customer.

---

## 4. Thanh toán (Payments)

### 📥 Webhook SePay
- **Endpoint**: `POST /payments/webhook/sepay`
- **Quyền**: Công khai (SePay gọi).
- **Logic**: Gạch nợ hóa đơn dựa trên nội dung chuyển khoản.

### 📜 Lịch sử giao dịch
- **Endpoint**: `GET /payments/history`
- **Quyền**: Admin/Worker (xem hết), Customer (xem của mình).

### 💳 Lịch sử giao dịch cá nhân
- **Endpoint**: `GET /payments/me`
- **Quyền**: Customer.

---

## 5. Báo cáo & Dashboard (Reports)

### 📊 Tóm tắt Dashboard
- **Endpoint**: `GET /reports/dashboard-summary`
- **Quyền**: Tất cả. Trả về dữ liệu tùy biến theo Role.

### 📉 Hóa đơn chưa thanh toán
- **Endpoint**: `GET /reports/unpaid`
- **Quyền**: Admin/Worker (xem hết), Customer (xem của mình).

### 💰 Thống kê doanh thu tháng
- **Endpoint**: `GET /reports/revenue-stats`
- **Quyền**: Admin / Worker.

### 🚨 Lọc hộ tiêu thụ cao
- **Endpoint**: `GET /reports/high-consumption`
- **Quyền**: Admin / Worker.

---

## 6. Lưu trữ (Uploads)

### 📸 Upload ảnh đồng hồ
- **Endpoint**: `POST /uploads/meter-image/{customer_id}`
- **Quyền**: Admin / Worker.
- **Output**: `image_path` (Dùng để hiển thị ảnh từ MinIO).

---

## 7. Quản lý Nhân sự & Excel (Users)

### 📤 Tải lên Excel (Bulk Import)
- **Endpoint**: `POST /users/upload`
- **Quyền**: Admin. Hỗ trợ tạo hàng loạt Customer & User.

### 📥 Xuất danh sách Excel
- **Endpoint**: `GET /users/export`
- **Quyền**: Admin.

### 📋 Liệt kê nhân sự
- **Endpoint**: `GET /users/`
- **Quyền**: Admin.

### ➕ Tạo nhân sự mới (Admin/Worker)
- **Endpoint**: `POST /users/`
- **Quyền**: Admin.

### ✏️ Cập nhật nhân sự
- **Endpoint**: `PUT /users/{user_id}`
- **Quyền**: Admin. (Cập nhật role, password, trạng thái active).

### 🗑️ Xóa tài khoản nhân sự
- **Endpoint**: `DELETE /users/{user_id}`
- **Quyền**: Admin.
