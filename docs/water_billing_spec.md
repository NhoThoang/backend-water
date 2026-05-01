# Tài Liệu Đặc Tả Kỹ Thuật & Kế Hoạch Triển Khai (Water Billing App)

Dựa trên file `plan.txt` và các yêu cầu bổ sung, hệ thống đã được thiết kế với một kiến trúc rất chuẩn, rõ ràng, dễ dàng mở rộng (scale) và có thể phát triển thành sản phẩm thực tế. Dưới đây là bản đặc tả chi tiết đã được cập nhật đầy đủ nghiệp vụ (Business Logic).

---

## 1. Tổng Quan Hệ Thống
Hệ thống quản lý thu phí nước sinh hoạt/kinh doanh với 3 luồng người dùng chính:
- **Admin**: Quản lý người dùng, hộ dân, bảng giá. Xem Dashboard thống kê, phát hiện rò rỉ (chỉ số tăng đột biến) và lọc nợ đọng để có phương án thu hồi hoặc ngắt nước.
- **Worker (Thợ)**: Ghi chỉ số nước (hỗ trợ offline), chụp ảnh minh chứng.
- **User (Khách hàng)**: Xem chỉ số, nhận hóa đơn, thanh toán online (Napas/SePay).

## 2. Stack Công Nghệ
- **Mobile App**: Flutter (Offline-first, SQLite local).
- **Backend**: FastAPI (Python), RESTful API.
- **Database**: PostgreSQL (Primary Data).
- **Storage**: MinIO (Lưu trữ ảnh chụp đồng hồ nước).
- **Deployment**: Docker, Nginx Reverse Proxy.

## 3. Kiến Trúc Database & Schema Core (Cập nhật)
Hệ thống sử dụng các bảng chính sau:
- `users`: Quản lý tài khoản (Admin, Worker, User).
- `customers`: Thông tin hộ dân (Name, Address, `customer_type` [Sinh hoạt, Kinh doanh], liên kết với `user_id`, trạng thái `status` [Active, Suspended]).
- `tariffs` (Mới): Bảng giá nước theo bậc thang và theo loại hộ dân.
- `meter_readings`: Chỉ số nước hàng tháng, ảnh chụp, người ghi nhận.
- `bills` (Mới): Hóa đơn hàng tháng sinh ra từ `meter_readings` (Tổng khối, Tiền nước, Thuế phí, Nợ cũ, Tổng thanh toán, Hạn chót đóng).
- `payments`: Giao dịch thanh toán (Số tiền, trạng thái, phương thức).
- `payment_logs`: Log chi tiết request/response từ cổng thanh toán (Audit).
- `system_logs`: Log hoạt động của hệ thống.

*Điểm sáng: Đã có chiến lược đánh Index rất tốt để tối ưu query (ví dụ: `customer_id` + `month`).*

## 4. Kiến Trúc Backend (FastAPI) & API Core
Cấu trúc thư mục chia theo pattern chuẩn: `routers`, `schemas`, `models`, `services`, `deps`.

**API Core & Nghiệp vụ Mới:**
- **Auth**: Đăng nhập, cấp Token (JWT).
- **Users/Customers**: Quản lý thông tin.
- **Readings**: Ghi số, tự động trigger logic tính tiền.
- **Billing & Payments**: Quản lý hóa đơn, tạo giao dịch, Webhook xử lý callback từ SePay/Napas.
- **Admin Reports** (Mới): 
  - API lọc danh sách hộ nợ tiền quá hạn.
  - API lọc danh sách hộ tiêu thụ nước nhiều bất thường (gấp 1.5 - 2 lần tháng trước).
  - API thống kê doanh thu theo tháng/khu vực.
- **Upload**: Upload ảnh lên MinIO.

## 5. Kiến Trúc Mobile (Flutter)
- Cấu trúc thư mục theo Feature-based: `core`, `data`, `features`, `local`.
- **Worker App**: Danh sách khách hàng, Nhập số, Chụp ảnh, Đồng bộ (Sync) khi có mạng. *Cảnh báo ngay trên app* nếu số nhập vào cao bất thường so với tháng trước.
- **User App**: Lịch sử hóa đơn, Nút thanh toán, Nhận thông báo Push.
- **Cơ chế Offline-first**: Lưu SQLite khi không có mạng -> Retry Queue + Exponential Backoff khi có mạng.

---

## 6. CHI TIẾT NGHIỆP VỤ (BUSINESS LOGIC) ĐÃ CHUẨN HÓA

Dựa trên các tiêu chuẩn thực tế, nghiệp vụ vận hành được thiết lập như sau:

### 6.1. Logic tính giá nước (Water Pricing - Bậc thang)
Tính tiền theo mô hình **lũy tiến bậc thang**. Bảng cấu hình `tariffs` trong DB sẽ linh hoạt cho phép Admin thay đổi giá.
- **Hộ sinh hoạt (Tham khảo):**
  - Bậc 1 (0 - 10 m³): Giá hỗ trợ (vd: 6,000đ/m³)
  - Bậc 2 (11 - 20 m³): Giá cơ bản (vd: 8,000đ/m³)
  - Bậc 3 (21 - 30 m³): Giá cao (vd: 10,000đ/m³)
  - Bậc 4 (Từ 31 m³ trở lên): Giá rất cao nhằm hạn chế lãng phí (vd: 15,000đ/m³)
- **Hộ kinh doanh/Dịch vụ:**
  - Áp dụng một mức giá chung cao hơn hoặc khung bậc thang kinh doanh riêng.

### 6.2. Thuế và Phí (Taxes & Fees)
Sau khi tính tổng tiền nước theo bậc thang, hệ thống tự động cộng thêm:
- **5% Thuế GTGT (VAT).**
- **10% Phí bảo vệ môi trường (BVMT).**
-> *Tổng tiền hóa đơn = Tiền nước + VAT + Phí BVMT + Nợ đọng (nếu có).*

### 6.3. Kỳ ghi chỉ số và Tự động sinh hóa đơn (Billing Cycle)
- Ngay khi Worker chốt số, hệ thống backend tự động validate.
- Nếu `current < previous` -> Báo lỗi không cho lưu.
- Nếu hợp lệ: Backend **tự động tính toán và sinh ra 1 bản ghi trong bảng `bills`** (Hóa đơn) ngay lập tức. Trạng thái Bill là `Unpaid`.

### 6.4. Xử lý Cảnh báo đột biến & Cắt nước (Anomaly Detection)
- **Cảnh báo đột biến:** Khi Worker nhập số, backend tính ra lượng tiêu thụ. Nếu lượng tiêu thụ **tăng > 50%** (hoặc một ngưỡng do Admin tự định nghĩa) so với tháng trước -> Gắn cờ (Flag) hóa đơn là `Anomaly` (Bất thường).
- **Quản lý bởi Admin:** Admin có một màn hình Dashboard "Cảnh Báo" riêng để lọc các hộ này. Có thể chủ động liên hệ người dân kiểm tra rò rỉ ống nước.
- **Cắt nước:** Nếu hộ dân nợ quá thời hạn (vd: nợ 2 tháng liên tiếp), Admin có quyền lọc danh sách và đổi trạng thái hộ dân sang `Suspended` (Tạm ngắt nước). Worker sẽ nhận được danh sách/Task đi khóa van nước.

### 6.5. Xử lý nợ đọng (Debt Management)
- Hệ thống hỗ trợ tra cứu các hộ dân còn nợ tiền.
- Nếu kỳ trước User chưa đóng tiền (Trạng thái hóa đơn cũ là `Unpaid`), số tiền nợ sẽ được **cộng dồn** vào hóa đơn của tháng hiện tại dưới dạng "Nợ cũ" (Previous Debt), tổng số tiền khách hàng cần thanh toán lúc này sẽ bao gồm cả tháng mới và nợ cũ.

### 6.6. Thông báo (Notifications)
- **Tự động gửi Push Notification (qua Firebase) / Zalo ZNS / SMS:** 
  - Gửi ngay khi có Hóa đơn mới.
  - Gửi cảnh báo rò rỉ nếu chỉ số nước tăng vọt.
  - Nhắc nợ tự động định kỳ (vd: ngày 10 và 15 hàng tháng) nếu chưa thanh toán.
  - Gửi biên lai điện tử báo thành công ngay khi cổng thanh toán (SePay/Napas) trả webhook về hệ thống.
