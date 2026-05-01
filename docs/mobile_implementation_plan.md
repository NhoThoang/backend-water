# Lộ Trình Triển Khai Mobile App (Flutter)

Ứng dụng sẽ được xây dựng theo kiến trúc đa người dùng (Worker & User) với khả năng hoạt động Offline.

## 1. Công Nghệ & Thư Viện
- **State Management**: `provider` (Đơn giản, hiệu quả).
- **Networking**: `dio` (Xử lý API, Interceptors cho JWT).
- **Storage**: 
    - `flutter_secure_storage` (Lưu JWT).
    - `sqflite` (Lưu dữ liệu Offline cho thợ ghi số).
- **UI/UX**: `google_fonts`, `image_picker` (Chụp ảnh đồng hồ).

## 2. Giai Đoạn 1: Khởi Tạo & Auth
- Thiết lập cấu trúc thư mục Feature-based.
- Xây dựng Base API Client (Dio).
- Màn hình Đăng nhập (Xử lý Access/Refresh Token).

## 3. Giai Đoạn 2: Tính Năng Cho Thợ (Worker)
- Màn hình Danh sách hộ dân.
- Màn hình Ghi chỉ số: Chụp ảnh -> Upload MinIO -> Submit Reading.
- Cơ chế Offline: Lưu tạm vào SQLite khi mất mạng -> Tự động đồng bộ khi có mạng.

## 4. Giai Đoạn 3: Tính Năng Cho Khách Hàng (User)
- Màn hình xem danh sách Hóa đơn.
- Xem chi tiết hóa đơn (Tiền nước, thuế, nợ cũ).
- Tích hợp hiển thị QR Code thanh toán (SePay/Napas).

---

# Bước 1: Khởi tạo dự án và Cấu trúc thư mục
Tôi sẽ bắt đầu tạo `pubspec.yaml` và cấu trúc thư mục `lib/` ngay bây giờ.
