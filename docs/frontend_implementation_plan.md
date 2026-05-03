# Kế hoạch Triển khai Front-end (Next.js) - Hệ thống Quản lý Nước

Dự án này xây dựng một giao diện Web hiện đại, đa vai trò (Admin, Worker, Customer), tích hợp sâu với Backend FastAPI và MinIO.

## 1. Công nghệ sử dụng (Tech Stack)
*   **Framework**: Next.js 16+ (App Router)
*   **Ngôn ngữ**: TypeScript
*   **Styling**: Tailwind CSS v4 + Framer Motion (Animations).
*   **UI Components**: Custom Glassmorphism UI components.
*   **State Management**: React Query v5 (Data caching) + Zustand (Auth State).
*   **Feedback**: **SweetAlert2** (Custom Glassmorphism Theme).
*   **Charts**: **Recharts** (Optimized for Next.js SSR).

## 2. Phân quyền & Vai trò (RBAC)

### 👑 Admin (Quản trị viên)
- Toàn quyền CRUD: Khách hàng, Nhân viên, Chỉ số, Hóa đơn.
- Xem báo cáo doanh thu và thống kê hệ thống chi tiết.
- Quản lý dữ liệu hàng loạt qua Excel (Import/Export).

### 🛠️ Worker (Nhân viên ghi số)
- Truy cập: Dashboard, Danh sách hộ dân, Ghi chỉ số, Hóa đơn.
- **Tính năng chính**: Tìm kiếm hộ dân nhanh và bấm nút **"Ghi nước"** để nhập số & tải ảnh đồng hồ tại hiện trường.
- Không có quyền xóa dữ liệu hoặc quản lý nhân sự.

### 👤 Customer (Hộ dân)
- Truy cập: Dashboard cá nhân, Hóa đơn của tôi, Lịch sử thanh toán của tôi.
- Chỉ xem được thông tin của chính mình. Toàn bộ các module quản trị đều bị ẩn.

## 3. Các Module Tính năng Chính

### A. Dashboard & Analytics
- **Admin**: Xem biểu đồ doanh thu, hiệu suất thu hồi và cảnh báo rò rỉ toàn hệ thống.
- **Customer**: Xem biểu đồ tiêu thụ 6 tháng của gia đình và thông báo tiền nước cần đóng.
- **Fix**: Sử dụng `isClient` và `key` cho Recharts để tránh lỗi kích thước biểu đồ.

### B. Quản lý Hộ dân & Nhân sự
- Danh sách hộ dân với các Action động (Admin thấy Edit/Delete, Worker thấy Ghi nước).
- Module Excel tích hợp: Xử lý dữ liệu hàng loạt nhanh chóng.
- Quản lý tài khoản nhân viên (Chỉ Admin).

### C. Ghi số & Xác thực Hình ảnh
- Form ghi số hiện đại, hỗ trợ chọn hộ dân từ Dropdown thông minh.
- Chụp ảnh và tải lên MinIO để lưu trữ bằng chứng ghi số.
- Tự động kích hoạt cảnh báo nếu sản lượng tăng đột biến (>50%).

### D. Thanh toán & Công nợ
- Đồng bộ lịch sử thanh toán từ SePay Webhook.
- Giao diện hóa đơn chuyên nghiệp với trạng thái (Đã trả, Chờ xử lý, Quá hạn).

## 4. Thiết kế & Trải nghiệm (UI/UX)
- **Aesthetic**: Phong cách **Glassmorphism** (trong suốt, hiện đại) với tông màu Primary (Blue/Emerald).
- **SweetAlert2**: Đồng nhất ngôn ngữ thiết kế với các thông báo Toast và Modal bo tròn, nhẹ nhàng.
- **Responsive**: Giao diện tối ưu hoàn hảo cho Tablet/Mobile để nhân viên dễ dàng thao tác tại hiện trường.

## 5. Lộ trình thực hiện
1.  **Auth & Layout**: Thiết lập cơ chế bảo vệ Route dựa trên Role. (Đã xong)
2.  **Customer & Staff**: Hoàn thiện CRUD và module Excel. (Đã xong)
3.  **Readings & MinIO**: Triển khai ghi số và upload ảnh. (Đã xong)
4.  **Analytics & Optimization**: Hoàn thiện Dashboard và fix lỗi biểu đồ. (Đã xong)
5.  **Documentation**: Cập nhật tài liệu hướng dẫn và bàn giao. (Đang thực hiện)

---
*Cập nhật lần cuối: 2026-05-02 by Antigravity*
