# Kế hoạch Triển khai Front-end (Next.js) - Hệ thống Quản lý Nước

Dự án này mục tiêu xây dựng một giao diện Web quản trị hiện đại, chuyên nghiệp dành cho Admin và Nhân viên kỹ thuật, tích hợp với Backend FastAPI.

## 1. Công nghệ sử dụng (Tech Stack)
*   **Framework**: Next.js 14+ (App Router)
*   **Ngôn ngữ**: **TypeScript** (Bắt buộc để đảm bảo Type-safety cho dữ liệu Billing/User)
*   **Styling**: **Tailwind CSS v4** (Hiệu suất cao hơn, cấu hình hiện đại qua CSS)
*   **UI Components**: Shadcn UI (Radix UI) - mang lại cảm giác Premium và tùy biến cao.
*   **State Management & Data Fetching**: TanStack Query (React Query) v5.
*   **Form Handling**: React Hook Form + Zod (Validation).
*   **Icons**: Lucide React.
*   **Charts**: Recharts (Hiển thị biểu đồ doanh thu, sản lượng).

## 2. Các Module Tính năng Chính

### A. Hệ thống Xác thực (Authentication)
*   Trang Login (Hỗ trợ đăng nhập bằng Username hoặc Mã khách hàng via JSON body).
*   Quản lý Access Token & Refresh Token (Lưu trữ an toàn trong HttpOnly Cookie hoặc LocalStorage với cơ chế auto-refresh).
*   Middleware bảo vệ route dựa trên Role (Admin/Worker).

### B. Dashboard (Trang chủ)
*   Thống kê tổng quan: Tổng doanh thu tháng, Số hộ dân, Số hóa đơn chưa thanh toán.
*   Biểu đồ đường: Diễn biến sản lượng nước tiêu thụ 6 tháng gần nhất.
*   Biểu đồ cột: So sánh doanh thu kế hoạch vs thực tế thu được.

### C. Quản lý Người dùng & Khách hàng
*   Danh sách khách hàng (Pagination, Search theo tên/mã).
*   **Module Excel**:
    *   Upload file Excel (6 cột) để tạo tài khoản hàng loạt.
    *   Preview dữ liệu Excel trước khi nhấn "Lưu".
    *   Export danh sách khách hàng ra Excel.
*   Thêm/Sửa/Xóa thông tin hộ dân.

### D. Ghi Chỉ số & Hóa đơn (Meter Reading)
*   Giao diện nhập chỉ số nhanh cho Worker.
*   Tích hợp Upload ảnh đồng hồ (MinIO).
*   Cảnh báo tức thời (Anomaly Detection) nếu chỉ số tăng đột biến (>50%).
*   Xem lịch sử chỉ số và hóa đơn theo từng hộ.

### E. Quản lý Thanh toán & Báo cáo
*   Danh sách hóa đơn nợ đọng.
*   Theo dõi lịch sử thanh toán từ SePay Webhook.
*   Báo cáo hộ tiêu thụ cao (High Consumption).

## 3. Kiến trúc Thư mục (Folder Structure)
```text
src/
├── app/                  # App Router (Pages, Layouts)
├── components/           # UI Components (shared, ui, forms)
├── hooks/                # Custom hooks (useAuth, useCustomers, etc.)
├── lib/                  # Utilities (axios, utils, constants)
├── services/             # API Calls (auth, customer, reading)
├── store/                # Global state (Zustand nếu cần)
└── types/                # TypeScript Interfaces
```

## 4. Thiết kế Giao diện (UI/UX)
*   **Rich Aesthetics**: Sử dụng Glassmorphism cho các Card.
*   **Dark Mode**: Hỗ trợ đầy đủ Dark/Light mode.
*   **Responsive**: Tối ưu hóa cho cả Laptop và Máy tính bảng (cho Worker đi hiện trường).
*   **Micro-animations**: Sử dụng Framer Motion cho các hiệu ứng chuyển trang và modal.

## 5. Lộ trình thực hiện (Roadmap)
*   **Giai đoạn 1**: Khởi tạo dự án, Setup Auth logic & Layout chính.
*   **Giai đoạn 2**: Xây dựng module Quản lý Khách hàng & Excel Integration.
*   **Giai đoạn 3**: Triển khai module Ghi chỉ số & Hóa đơn.
*   **Giai đoạn 4**: Xây dựng Dashboard & Báo cáo thống kê.
*   **Giai đoạn 5**: Optimize hiệu năng, SEO và Deploy.

---
*Người lập kế hoạch: Antigravity AI Assistant*
