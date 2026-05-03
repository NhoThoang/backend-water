# 💧 Water Billing App - Toàn Tập Kiến Trúc & Hướng Dẫn Triển Khai

Chào mừng bạn đến với dự án **Water Billing App** (Ứng dụng Quản lý & Thu tiền nước). Đây là một hệ thống phần mềm toàn diện (End-to-End) được thiết kế theo kiến trúc Microservices hiện đại, hỗ trợ nền tảng Web cho Quản trị viên và Mobile App cho nhân viên ghi nước hiện trường.

---

## 🏗 Hệ Sinh Thái Github Repositories

Dự án được chia tách theo chuẩn production thành 4 repository độc lập nhằm dễ dàng bảo trì, áp dụng CI/CD và scale:

1. ⚙️ **[Backend (FastAPI)](https://github.com/NhoThoang/backend-water):** Xử lý logic nghiệp vụ cốt lõi, Authentication (JWT), phân quyền, thao tác với PostgreSQL (asyncpg) và MinIO (lưu trữ ảnh đồng hồ nước).
2. 🌐 **[Frontend (Next.js)](https://github.com/NhoThoang/frontend-water):** Bảng điều khiển (Admin Dashboard) Server-Side Rendering siêu tốc dành cho Quản lý.
3. 📱 **[Mobile App (Flutter)](https://github.com/NhoThoang/mobile-water-app):** Ứng dụng di động (Android & iOS) để nhân viên cầm đi ghi chỉ số nước thực tế, quét QR code và in hóa đơn Bluetooth.
4. 🚦 **[Nginx & Orchestration](https://github.com/NhoThoang/nginx-water-app):** Bộ định tuyến Proxy, Rate Limiting, Caching, điều phối giao thông mạng giữa Frontend/Backend/MinIO và bảo vệ máy chủ.

*(Repository hiện tại bạn đang xem chính là Backend, chứa bộ khung Orchestration `run_product` dùng để chạy TOÀN BỘ hệ thống ở môi trường Production).*

---

## 📐 Kiến Trúc Triển Khai (Docker Network)

Toàn bộ hệ thống chạy ngầm bên trong một mạng Docker nội bộ (`app_network`). Các cổng (port) được khóa kín và chỉ duy nhất cổng `80` (hoặc `443`) của **Nginx** được mở ra thế giới bên ngoài.

**Luồng dữ liệu qua Nginx:**
- 🌍 `http://<domain>/` ➡️ Chuyển hướng tới Frontend Container (Next.js).
- 🌍 `http://<domain>/api/v1/*` ➡️ Chuyển hướng tới Backend Container (FastAPI).
- 🌍 `http://<domain>/uploads/*` ➡️ Chuyển hướng tới MinIO Container (Quản lý File/Ảnh).

Việc này giải quyết bài toán CORS khét tiếng, che giấu hoàn toàn kiến trúc server khỏi tin tặc và tăng tốc độ nhờ cơ chế Cache mạnh mẽ của Nginx.

---

## 🚀 Hướng Dẫn Deploy (Triển Khai Môi Trường Production)

Nhờ có file `Makefile` và Docker, việc triển khai nguyên cả một hệ sinh thái khổng lồ này lên Server Linux chỉ mất vỏn vẹn **2 thao tác**.

### Bước 1: Khởi tạo trên Server Linux
Đảm bảo máy chủ Linux của bạn đã cài đặt sẵn `Git`, `Docker`, `Docker Compose` và `Make`.

```bash
# Clone repository backend (Chứa thư mục run_product điều phối toàn bộ)
git clone https://github.com/NhoThoang/backend-water.git
cd backend-water/run_product
```

### Bước 2: Cấu hình biến môi trường
Mở và kiểm tra cấu hình file `.env` bên trong thư mục `run_product/backend/.env`. Đảm bảo nó trỏ đúng các `POSTGRES_SERVER` và `MINIO_ENDPOINT` tới các docker container tương ứng.

### Bước 3: Tạo Docker Network (Bắt buộc)
Toàn bộ các container trong hệ thống liên lạc với nhau qua mạng nội bộ `app_network`. Bạn **phải** tạo network này trước khi khởi chạy hệ thống:

```bash
make network
```

### Bước 4: Chạy hệ thống bằng Makefile "Thần Thánh"
Đứng tại thư mục `run_product`, chỉ cần gõ lệnh:

```bash
make up
```

Lệnh này sẽ tự động:
1. Khởi chạy Database Server (PostgreSQL, PgAdmin, MinIO).
2. Tự động kéo (Pull) Image mới nhất của Backend từ Docker Hub và khởi chạy.
3. Tự động kéo Image mới nhất của Frontend và khởi chạy.
4. Tự động kéo Image của Nginx Proxy và khởi chạy.

*(Hệ thống sẽ chạy theo đúng thứ tự ưu tiên, chờ Database khởi động xong mới mở Backend để tránh sập).*

---

## 🛠 Danh sách các lệnh thao tác nhanh (Makefile)

Trong quá trình bảo trì server, thay vì gõ các lệnh Docker Compose dài dòng, bạn chỉ cần dùng:

| Lệnh | Ý nghĩa |
|---|---|
| `make network` | **(Quan trọng)** Tạo network `app_network` cho hệ thống. |
| `make up` | Khởi chạy toàn bộ hệ thống từ A-Z. |
| `make down` | Tắt toàn bộ hệ thống (dữ liệu DB không bị mất). |
| `make restart` | Khởi động lại toàn bộ hệ thống. |
| `make status` | Xem trạng thái các container đang chạy. |
| `make logs-backend` | Xem log trực tiếp của Backend (Dùng để debug lỗi API). |
| `make logs-frontend` | Xem log trực tiếp của Frontend (Next.js). |
| `make pull` | Kéo toàn bộ code/Image mới nhất từ kho chứa Docker Hub. |

---

## 🔄 Quy trình Update Code (CI/CD)

Hệ thống đã được tích hợp **Github Actions** cho toàn bộ 4 repositories. 

**Quy trình chuẩn khi bạn code thêm tính năng mới:**
1. Code trên máy cá nhân, sau đó gõ `git push` lên Github.
2. Github Actions sẽ tự động Build thành Docker Image mới (với Backend/Frontend/Nginx) hoặc build ra file cài đặt `.apk` (với Mobile) rồi đẩy lưu trữ trên Cloud.
3. Chui vào Server Linux, gõ:
```bash
make pull     # Lấy code mới nhất về
make restart  # Áp dụng ngay lập tức
```
👉 Tuyệt đối **không** cần build lại code trên server thật, giúp máy chủ không bị treo do ngốn CPU.

---

> 💡 **Bí kíp:** Nếu có lỗi xảy ra với biến môi trường Pydantic của Backend, hãy vào `run_product/backend/.env` kiểm tra, thường là do thiếu hoặc sai `POSTGRES_SERVER=postgres_db`. Nếu Frontend gọi API bị lỗi, hãy xem log của Nginx!

*Được kiến trúc bởi sự kết hợp của bạn và Antigravity!* 🚀
