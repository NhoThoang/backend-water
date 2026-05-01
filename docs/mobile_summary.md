# Báo Cáo Kết Quả Triển Khai Mobile App - Water Billing App

Ứng dụng Mobile đã được xây dựng hoàn thiện trên nền tảng Flutter, hỗ trợ đầy đủ các vai trò thợ ghi số (Worker) và người dân (User) với thiết kế hiện đại và khả năng hoạt động ổn định.

## 1. Công Nghệ Sử Dụng
- **Framework**: Flutter 3.x.
- **State Management**: Provider (Quản lý trạng thái tập trung).
- **Networking**: Dio (Hỗ trợ Interceptor, Auto-refresh token).
- **Database Local**: SQLite (Lưu trữ offline cho thợ).
- **Storage**: Flutter Secure Storage (Lưu JWT an toàn).
- **Logging**: Cơ chế xoay vòng log file chuyên nghiệp.

## 2. Các Tính Năng Đã Hoàn Thành

### 🔐 Xác thực & Phân quyền (Auth)
- **Login/Logout**: Tích hợp đầy đủ luồng Access/Refresh Token.
- **Auto-Refresh**: Tự động lấy Token mới khi token cũ hết hạn mà không cần đăng nhập lại.
- **Role Switching**: Tự động chuyển giao diện dựa trên vai trò (Admin/Worker vào màn hình ghi số, User vào màn hình hóa đơn).

### 🛠 Tính năng cho Thợ (Worker)
- **Danh sách hộ dân**: Lấy dữ liệu thời gian thực từ Backend, hỗ trợ vuốt để tải lại.
- **Ghi chỉ số nước thông minh**:
    - Tích hợp **Camera** để chụp ảnh đồng hồ làm minh chứng.
    - Quy trình: Chụp ảnh -> Tự động upload lên MinIO -> Gửi chỉ số -> Server tính tiền & tạo hóa đơn.
- **Offline Mode**: 
    - Cho phép ghi số và chụp ảnh ngay cả khi không có mạng (vùng sâu, vùng xa).
    - Dữ liệu được lưu vào SQLite.
- **Đồng bộ hóa (Sync)**: Khi có mạng, thợ chỉ cần nhấn đồng bộ để đẩy toàn bộ dữ liệu offline lên server.

### 💰 Tính năng cho Khách hàng (User)
- **Tra cứu hóa đơn**: Xem danh sách hóa đơn theo tháng, trạng thái thanh toán (Đã đóng/Chưa đóng).
- **Xem chi tiết**: Hiển thị rõ lượng tiêu thụ, tiền nước bậc thang, thuế phí và nợ cũ.
- **Thanh toán QR (VietQR)**: Tích hợp mã QR thông minh chứa thông tin hóa đơn. Khách hàng chỉ cần quét mã bằng App ngân hàng để thanh toán nhanh.

### 🐞 Hệ thống Debug & Nhật ký (Logging)
- **Local Logging**: Ghi lại mọi hoạt động và lỗi của App vào file `app_log_x.txt`.
- **Log Rotation**: Cơ chế tự động xoay vòng 3 file (mỗi file 2MB) giúp kiểm soát dung lượng bộ nhớ điện thoại.
- **API Tracking**: Tự động ghi log chi tiết các lỗi kết nối hoặc lỗi từ server trả về.

## 3. Giao diện & Trải nghiệm (UI/UX)
- **Modern Design**: Sử dụng Material 3, font chữ Outfit cao cấp.
- **Branding**: Sử dụng tông màu Xanh (Water Blue) chủ đạo, hiệu ứng Gradient và Card hiện đại.
- **UX**: Luồng thao tác tối giản, tập trung vào tốc độ ghi số cho thợ.

## 4. Hướng dẫn vận hành cho Dev
1. **Cài đặt**: `flutter pub get` trong thư mục `mobile/`.
2. **Cấu hình**: Chỉnh sửa `baseUrl` trong `lib/core/api_client.dart` khớp với IP server của bạn.
3. **Log**: Xem file log tại thư mục `Application Documents` của App trên thiết bị.

---
Ứng dụng hiện tại đã sẵn sàng để build thành file APK (Android) hoặc triển khai lên iOS.
