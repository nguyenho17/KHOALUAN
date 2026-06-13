import jwt
from datetime import datetime, timedelta

# Cấu hình chuẩn JWT
SECRET_KEY = "khoaluan_chatbot_bi_mat_123" # Điền một chuỗi thô cố định
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # Token sống được 1 ngày

def create_access_token(data: dict):
    """Tạo vé thông hành (JWT Token)"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt