import os
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext

# =====================================================================
# CẤU HÌNH JWT — Đọc từ .env, fallback về giá trị mặc định nếu không có
# =====================================================================
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "khoaluan_chatbot_bi_mat_123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # Token sống được 1 ngày

# =====================================================================
# CẤU HÌNH BCRYPT — Hash và verify mật khẩu an toàn
# =====================================================================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str) -> str:
    """Hash mật khẩu trước khi lưu vào DB"""
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiểm tra mật khẩu nhập vào có khớp với hash trong DB không"""
    # Tương thích ngược: nếu mật khẩu trong DB chưa được hash (plain text cũ)
    # thì so sánh trực tiếp, đảm bảo không khóa tài khoản cũ
    if hashed_password and not hashed_password.startswith("$2b$"):
        return plain_password == hashed_password
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    """Tạo vé thông hành (JWT Token)"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt