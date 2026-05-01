import logging
import os
from logging.handlers import RotatingFileHandler

# Tạo thư mục logs nếu chưa có
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Cấu hình logger
logger = logging.getLogger("water_app")
logger.setLevel(logging.INFO)

# Cấu hình RotatingFileHandler
# maxBytes = 5 * 1024 * 1024 (5MB)
# backupCount = 3 (giữ tối đa 3 file cũ)
handler = RotatingFileHandler(
    LOG_FILE, 
    maxBytes=5 * 1024 * 1024, 
    backupCount=3,
    encoding="utf-8"
)

# Định dạng log
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

# Thêm handler vào logger
logger.addHandler(handler)

# Thêm StreamHandler để log ra console trong quá trình dev
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
