import os
import urllib
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

# ==============================================================
# DATABASE CONNECTION — Hỗ trợ đa môi trường
# ==============================================================
# Ưu tiên 1: DATABASE_URL (PostgreSQL từ Neon.tech — production HuggingFace)
# Ưu tiên 2: Các biến DB_* riêng lẻ (SQL Server — local Windows)
# Ưu tiên 3: SQLite fallback (demo nhanh không cần server)
# ==============================================================

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # ── Chế độ Production: PostgreSQL (Neon.tech, Supabase, Railway...) ──
    # HuggingFace Spaces đặt DATABASE_URL trong Secrets
    print(f"🐘 [Database] Kết nối PostgreSQL (production mode)...")
    
    # Fix: Neon.tech trả về URL dạng "postgres://..." nhưng SQLAlchemy cần "postgresql://..."
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,        # Kiểm tra kết nối còn sống trước khi dùng
        pool_recycle=300,          # Tái tạo connection mỗi 5 phút (Neon.tech idle timeout)
        connect_args={
            "sslmode": "require"   # Bắt buộc SSL cho Neon.tech
        } if "neon.tech" in DATABASE_URL or "sslmode" in DATABASE_URL else {}
    )

elif os.getenv("DB_SERVER"):
    # ── Chế độ Local: SQL Server (Windows development) ────────────────
    print(f"🗄️  [Database] Kết nối SQL Server (local mode)...")
    params = urllib.parse.quote_plus(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER', 'localhost')};"
        f"DATABASE={os.getenv('DB_NAME', 'ChatbotLuatHonNhan')};"
        f"UID={os.getenv('DB_USER', 'sa')};"
        f"PWD={os.getenv('DB_PASS', '123456')}"
    )
    SQLSERVER_URL = f"mssql+pyodbc:///?odbc_connect={params}"
    engine = create_engine(SQLSERVER_URL, pool_size=10, max_overflow=20)

else:
    # ── Chế độ Fallback: SQLite (demo, không cần server) ──────────────
    print("💾 [Database] Dùng SQLite fallback (chế độ demo)...")
    sqlite_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data", "chatbot.db"
    )
    os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
    engine = create_engine(
        f"sqlite:///{sqlite_path}",
        connect_args={"check_same_thread": False}
    )

# ── Session Factory ────────────────────────────────────────────
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency injection: cung cấp DB session cho mỗi request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()