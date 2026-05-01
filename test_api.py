import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

def test_water_app():
    print("🚀 Bắt đầu test hệ thống Water Billing API...")

    # 1. Login Admin
    print("\n1. Đang đăng nhập Admin...")
    login_data = {
        "username": ADMIN_USER,
        "password": ADMIN_PASS
    }
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if response.status_code != 200:
        print("❌ Login thất bại! Hãy chắc chắn server đang chạy.")
        return
    
    tokens = response.json()
    access_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    print("✅ Login thành công!")

    # 2. Tạo Hộ Dân mẫu
    print("\n2. Đang tạo hộ dân mẫu...")
    customer_data = {
        "name": "Nguyễn Văn A",
        "address": "123 Đường ABC, Quận 1",
        "customer_type": "residential",
        "status": "active"
    }
    resp_cust = requests.post(f"{BASE_URL}/customers/", json=customer_data, headers=headers)
    customer = resp_cust.json()
    customer_id = customer["id"]
    print(f"✅ Tạo hộ dân thành công: ID {customer_id}")

    # 3. Test Upload Ảnh (Giả lập)
    print("\n3. Đang test upload ảnh đồng hồ...")
    with open("test_image.jpg", "wb") as f:
        f.write(b"fake image data") # Tạo file giả
        
    with open("test_image.jpg", "rb") as f:
        files = {"file": ("test.jpg", f, "image/jpeg")}
        resp_upload = requests.post(f"{BASE_URL}/uploads/meter-image/{customer_id}", files=files, headers=headers)
    
    upload_res = resp_upload.json()
    image_url = upload_res["image_url"]
    print(f"✅ Upload thành công: {image_url}")

    # 4. Ghi chỉ số nước tháng 1 (Số đầu 0, Số mới 15)
    print("\n4. Đang ghi chỉ số nước tháng 2026-05...")
    reading_data = {
        "customer_id": customer_id,
        "reading": 15.0,
        "month": "2026-05",
        "image_url": image_url
    }
    resp_reading = requests.post(f"{BASE_URL}/readings/", json=reading_data, headers=headers)
    reading_res = resp_reading.json()
    bill = reading_res["bill"]
    print(f"✅ Ghi số thành công!")
    print(f"   - Tiêu thụ: {bill['consumption']} m3")
    print(f"   - Tiền nước (bậc thang): {bill['water_amount']} đ")
    print(f"   - Thuế VAT (5%): {bill['vat_amount']} đ")
    print(f"   - Phí BVMT (10%): {bill['env_fee_amount']} đ")
    print(f"   - Tổng cộng: {bill['total_amount']} đ")

    # 5. Giả lập Webhook Thanh toán từ SePay
    print("\n5. Giả lập Webhook thanh toán từ SePay...")
    webhook_data = {
        "id": 9999,
        "content": f"Thanh toan BILL {bill['id']}", # Nội dung chứa mã bill
        "transferType": "IN",
        "transferAmount": bill['total_amount'],
        "accumulated": bill['total_amount'],
        "transactionDate": "2026-05-01 13:00:00",
        "referenceCode": "ABC123XYZ",
        "description": "Thanh toan tien nuoc",
        "gateway": "VCB"
    }
    resp_webhook = requests.post(f"{BASE_URL}/payments/webhook/sepay", json=webhook_data)
    print(f"✅ Webhook Response: {resp_webhook.json()}")

    # 6. Kiểm tra báo cáo doanh thu
    print("\n6. Kiểm tra báo cáo doanh thu Admin...")
    resp_report = requests.get(f"{BASE_URL}/reports/revenue-stats", headers=headers)
    print(f"✅ Báo cáo: {json.dumps(resp_report.json(), indent=2)}")

    print("\n✨ Hoàn thành test toàn bộ luồng!")

if __name__ == "__main__":
    test_water_app()
