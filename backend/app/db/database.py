import os
import urllib
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Lấy dữ liệu chuẩn từ file .env
params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={os.getenv('DB_SERVER', 'localhost')};"
    f"DATABASE={os.getenv('DB_NAME', 'ChatbotLuatHonNhan')};"
    f"UID={os.getenv('DB_USER', 'sa')};"
    f"PWD={os.getenv('DB_PASS', '123456')}" # Đảm bảo pass ở đây giống trong SQL Server
)

# Gắn chuỗi params vào URL
SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={params}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()