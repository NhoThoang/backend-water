# Lộ Trình Triển Khai Backend (Water Billing App)

Hệ thống sẽ được triển khai theo các giai đoạn sau:

## Giai Đoạn 1: Khởi Tạo Cơ Sở Hạ Tầng & Database
1.  **Cấu trúc thư mục:** Tạo cấu trúc FastAPI chuẩn.
2.  **Môi trường:** Thiết lập `.env`, `docker-compose` (PostgreSQL, MinIO).
3.  **Database Models:** Định nghĩa các bảng `users`, `customers`, `tariffs`, `meter_readings`, `bills`, `payments`.

## Giai Đoạn 2: Xây Dựng Core Logic (Nghiệp Vụ)
1.  **Hệ thống tính tiền (Tariff Service):** Logic tính tiền bậc thang dựa trên loại hộ dân.
2.  **Ghi chỉ số & Cảnh báo (Reading Service):** API cho Worker, tích hợp kiểm tra chỉ số bất thường.
3.  **Hệ thống hóa đơn (Billing Service):** Tự động sinh hóa đơn, cộng dồn nợ cũ.

## Giai Đoạn 3: Xác Thực & Quản Lý Người Dùng
1.  **JWT Auth:** Đăng nhập, phân quyền Role-based (Admin, Worker, User).
2.  **Customer Management:** Quản lý hộ dân và trạng thái (Active/Suspended).

## Giai Đoạn 4: Thanh Toán & Tích Hợp
1.  **Payment Gateway:** Tích hợp Webhook (SePay/Napas).
2.  **Storage:** Tích hợp MinIO để lưu ảnh đồng hồ.

## Giai Đoạn 5: Báo Cáo & Admin Dashboard API
1.  **Reporting API:** Lọc hộ nợ, hộ tiêu thụ cao, thống kê doanh thu.

---

# Bước 1: Khởi tạo cấu trúc dự án và file môi trường
Tôi sẽ bắt đầu tạo các file nền tảng ngay bây giờ.
