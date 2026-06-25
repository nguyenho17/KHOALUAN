from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean, BigInteger, Text
import datetime

# Import Base từ database.py để đồng bộ với Engine
from app.db.database import Base

# ==============================================================
# LƯU Ý VỀ KIỂU DỮ LIỆU — Cross-database compatibility
# ==============================================================
# NVARCHAR (SQL Server) → Text (PostgreSQL / SQLite)
# Text trong SQLAlchemy tự động map sang kiểu phù hợp theo DB
# ==============================================================

# ==========================================
# 1. BẢNG VAI TRÒ & NGƯỜI DÙNG
# ==========================================
class VaiTro(Base):
    __tablename__ = "VaiTro"
    MaVaiTro = Column(Integer, primary_key=True, autoincrement=True)
    TenVaiTro = Column(String(50), nullable=False)
    MoTa = Column(String(255))

class NguoiDung(Base):
    __tablename__ = "NguoiDung"
    MaNguoiDung = Column(Integer, primary_key=True, autoincrement=True)
    HoTen = Column(Text, nullable=False)                # NVARCHAR → Text
    Email = Column(String(100), unique=True)
    SoDienThoai = Column(String(20))
    DiaChi = Column(Text)                               # NVARCHAR → Text
    NgayDangKy = Column(DateTime, default=datetime.datetime.now)
    Avatar = Column(Text)                               # Lưu ảnh định dạng chuỗi Base64

# ==========================================
# 2. BẢNG TÀI KHOẢN (ĐĂNG NHẬP)
# ==========================================
class TaiKhoan(Base):
    __tablename__ = "TaiKhoan"
    MaTaiKhoan = Column(Integer, primary_key=True, autoincrement=True)
    TenDangNhap = Column(String(50), unique=True, nullable=False)
    MatKhau = Column(String(255), nullable=False)
    MaNguoiDung = Column(Integer, ForeignKey("NguoiDung.MaNguoiDung"))
    MaVaiTro = Column(Integer, ForeignKey("VaiTro.MaVaiTro"))
    TrangThai = Column(Text, default="Hoạt động")      # NVARCHAR → Text

# ==========================================
# 3. BẢNG PHIÊN CHAT & LOG HỆ THỐNG
# ==========================================
class PhienChat(Base):
    __tablename__ = "PhienChat"
    MaPhien = Column(Integer, primary_key=True, autoincrement=True)
    MaNguoiDung = Column(Integer, ForeignKey("NguoiDung.MaNguoiDung"))
    ThoiGianBatDau = Column(DateTime, default=datetime.datetime.now)
    ThoiGianKetThuc = Column(DateTime, nullable=True)
    TieuDe = Column(Text, nullable=True)               # Tên câu hỏi đầu tiên

class LogHeThong(Base):
    __tablename__ = "LogHeThong"
    MaLog = Column(Integer, primary_key=True, autoincrement=True)
    HanhDong = Column(String(255))
    NguoiThucHien = Column(Integer, ForeignKey("NguoiDung.MaNguoiDung"))
    ThoiGian = Column(DateTime, default=datetime.datetime.now)

# ==========================================
# 4. BẢNG LỊCH SỬ CHAT (BỘ TIÊU CHÍ ĐÁNH GIÁ LEXRAG++)
# ==========================================
class LichSuChat(Base):
    __tablename__ = "LichSuChat"
    MaChat = Column(Integer, primary_key=True, autoincrement=True)
    MaPhien = Column(Integer, ForeignKey("PhienChat.MaPhien"))
    MaNguoiDung = Column(Integer, ForeignKey("NguoiDung.MaNguoiDung"))

    CauHoi = Column(Text)                              # NVARCHAR → Text
    TraLoi = Column(Text)                              # NVARCHAR → Text

    ThoiGian = Column(DateTime, default=datetime.datetime.now)
    TieuDe = Column(String(255))
    Pinned = Column(Boolean, default=False)
    SessionId = Column(BigInteger)
    NguonTrichDan = Column(Text)                       # NVARCHAR → Text
    ThoiGianPhanHoi = Column(Float)

    # ── Bộ 7 chỉ số đánh giá chất lượng LexRAG++ ──────────────
    DiemKeywordAccuracy = Column(Float)                # Keyword Accuracy (0-100)
    DiemLLMJudge = Column(Float)                       # LLM Judge tổng hợp (0-100)

    DiemFactuality = Column(Float)                     # Tính xác thực (0-100)
    DiemCompleteness = Column(Float)                   # Tính đầy đủ (0-100)
    DiemCoherence = Column(Float)                      # Tính mạch lạc (0-100)
    DiemClarity = Column(Float)                        # Tính rõ ràng (0-100)
    DiemRelevance = Column(Float)                      # Đúng trọng tâm (0-100)

    DiemTongHop = Column(Float)                        # Điểm tổng hợp

    # ── Human-in-the-Loop (Admin phê duyệt) ────────────────────
    TrangThaiDuyet = Column(String(50), default="Pending")
    GroundTruth = Column(Text)                         # NVARCHAR → Text

# ==========================================
# 5. BẢNG ĐÁNH GIÁ TỪ NGƯỜI DÙNG
# ==========================================
class DanhGiaChatbot(Base):
    __tablename__ = "DanhGiaChatbot"
    MaDanhGia = Column(Integer, primary_key=True, autoincrement=True)
    MaNguoiDung = Column(Integer, ForeignKey("NguoiDung.MaNguoiDung"))
    MaChat = Column(Integer, ForeignKey("LichSuChat.MaChat"))
    DiemDanhGia = Column(Integer)                      # 1-5 sao
    NhanXet = Column(Text)
    ThoiGian = Column(DateTime, default=datetime.datetime.now)
    DoChinhXac = Column(Float)

# ==========================================
# 6. BẢNG KHO TRI THỨC & XÁC THỰC OTP
# ==========================================
class KhoTriThuc(Base):
    __tablename__ = "KhoTriThuc"
    MaVanBan = Column(Integer, primary_key=True, autoincrement=True)
    TenVanBan = Column(Text, nullable=False)           # NVARCHAR → Text
    SoHieu = Column(String(50))
    LoaiVanBan = Column(Text)                          # NVARCHAR → Text
    NgayBanHanh = Column(DateTime)
    TepTinPath = Column(String(255))
    TrangThai = Column(Text, default="Đang áp dụng")  # NVARCHAR → Text
    ThoiGianCapNhat = Column(DateTime, default=datetime.datetime.now)

class XacThucOTP(Base):
    __tablename__ = "XacThucOTP"
    MaOTP = Column(Integer, primary_key=True, autoincrement=True)
    Email = Column(String(100), nullable=False)
    MaXacThuc = Column(String(10), nullable=False)
    ThoiGianTao = Column(DateTime, default=datetime.datetime.now)
    ThoiGianHetHan = Column(DateTime, nullable=False)
    TrangThai = Column(Boolean, default=False)