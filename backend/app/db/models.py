from sqlalchemy import Column, Integer, String, NVARCHAR, DateTime, ForeignKey, Float, Boolean, BigInteger, Text
import datetime

# ĐÃ SỬA: Import trực tiếp Base từ file database.py để đồng bộ với Engine
from app.db.database import Base 

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
    HoTen = Column(NVARCHAR(100), nullable=False)
    Email = Column(String(100), unique=True)
    SoDienThoai = Column(String(20))
    DiaChi = Column(String(255))
    NgayDangKy = Column(DateTime, default=datetime.datetime.now)
    Avatar = Column(Text) # Lưu ảnh định dạng chuỗi Base64 công nghệ cao

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
    TrangThai = Column(NVARCHAR(50), default="Hoạt động")

# ==========================================
# 3. BẢNG PHIÊN CHAT & LOG HỆ THỐNG
# ==========================================
class PhienChat(Base):
    __tablename__ = "PhienChat"
    MaPhien = Column(Integer, primary_key=True, autoincrement=True)
    MaNguoiDung = Column(Integer, ForeignKey("NguoiDung.MaNguoiDung"))
    ThoiGianBatDau = Column(DateTime, default=datetime.datetime.now)
    ThoiGianKetThuc = Column(DateTime, nullable=True)
    TieuDe = Column(NVARCHAR(255), nullable=True) # Lưu tên câu hỏi đầu tiên của phiên chat

class LogHeThong(Base):
    __tablename__ = "LogHeThong"
    MaLog = Column(Integer, primary_key=True, autoincrement=True)
    HanhDong = Column(String(255))
    NguoiThucHien = Column(Integer, ForeignKey("NguoiDung.MaNguoiDung"))
    ThoiGian = Column(DateTime, default=datetime.datetime.now)

# ==========================================
# 4. BẢNG LỊCH SỬ CHAT (ĐÃ CẬP NHẬT BỘ TIÊU CHÍ)
# ==========================================
class LichSuChat(Base):
    __tablename__ = "LichSuChat"
    MaChat = Column(Integer, primary_key=True, autoincrement=True)
    MaPhien = Column(Integer, ForeignKey("PhienChat.MaPhien"))
    MaNguoiDung = Column(Integer, ForeignKey("NguoiDung.MaNguoiDung"))
    
    CauHoi = Column(NVARCHAR)
    TraLoi = Column(NVARCHAR)
    
    ThoiGian = Column(DateTime, default=datetime.datetime.now)
    TieuDe = Column(String(255))
    Pinned = Column(Boolean, default=False)
    SessionId = Column(BigInteger)
    NguonTrichDan = Column(NVARCHAR)     
    ThoiGianPhanHoi = Column(Float)      # Lưu thời gian suy luận (giây) của mô hình RAG

    # 📊 ĐÃ FIX: Đổi từ '--' sang '#' để đúng quy chuẩn cú pháp Python comment
    DiemKeywordAccuracy = Column(Float)   # Phương pháp 1: Keyword Accuracy
    DiemLLMJudge = Column(Float)          # Phương pháp 2: Điểm số Thẩm phán AI tổng
    
    # 🎯 ĐÃ FIX: Đổi sang dấu '#' để lưu trữ trực tiếp bộ tiêu chí liên kết xuống SQL Server
    DiemFactuality = Column(Float)        # Tiêu chí 1: Tính xác thực
    DiemCompleteness = Column(Float)      # Tiêu chí 2: Tính đầy đủ
    DiemCoherence = Column(Float)         # Tiêu chí 3: Tính mạch lạc
    DiemClarity = Column(Float)           # Tiêu chí 4: Tính rõ ràng
    DiemRelevance = Column(Float)         # Tiêu chí 5: Đúng trọng tâm
    
    DiemTongHop = Column(Float)           # Điểm số tổng hợp cuối cùng gộp trọng số

    # 📐 BỘ TIÊU CHÍ TRÍCH DẪN CĂN CỨ PHÁP LÝ (CITATION METRICS)
    DiemCitationPrecision = Column(Float)  # Độ chính xác trích dẫn điều luật (0.0 - 1.0)
    DiemCitationRecall    = Column(Float)  # Độ bao phủ nguồn luật (0.0 - 1.0)
    DiemCitationF1        = Column(Float)  # F1-Score căn cứ pháp lý tổng hợp (0.0 - 1.0)

    # --- HUMAN-IN-THE-LOOP (ADMIN PHÊ DUYỆT) ---
    TrangThaiDuyet = Column(String(50), default="Pending")
    GroundTruth = Column(NVARCHAR)        # Lưu đáp án chuẩn lý thuyết từ sách giáo trình

# ==========================================
# 5. BẢNG ĐÁNH GIÁ TỪ NGƯỜI DÙNG
# ==========================================
class DanhGiaChatbot(Base):
    __tablename__ = "DanhGiaChatbot"
    MaDanhGia = Column(Integer, primary_key=True, autoincrement=True)
    MaNguoiDung = Column(Integer, ForeignKey("NguoiDung.MaNguoiDung"))
    MaChat = Column(Integer, ForeignKey("LichSuChat.MaChat")) 
    DiemDanhGia = Column(Integer) # Phân cấp đánh giá từ 1 đến 5 sao
    NhanXet = Column(Text)
    ThoiGian = Column(DateTime, default=datetime.datetime.now)
    DoChinhXac = Column(Float)

# ==========================================
# 6. BẢNG KHO TRI THỨC VÀ XÁC THỰC OTP GỐC
# ==========================================
class KhoTriThuc(Base):
    __tablename__ = "KhoTriThuc"
    MaVanBan = Column(Integer, primary_key=True, autoincrement=True)
    TenVanBan = Column(NVARCHAR(255), nullable=False)
    SoHieu = Column(String(50))
    LoaiVanBan = Column(NVARCHAR(50))
    NgayBanHanh = Column(DateTime)
    TepTinPath = Column(String(255))
    TrangThai = Column(NVARCHAR(50), default="Đang áp dụng")
    ThoiGianCapNhat = Column(DateTime, default=datetime.datetime.now)

class XacThucOTP(Base):
    __tablename__ = "XacThucOTP"
    MaOTP = Column(Integer, primary_key=True, autoincrement=True)
    Email = Column(String(100), nullable=False)
    MaXacThuc = Column(String(10), nullable=False)
    ThoiGianTao = Column(DateTime, default=datetime.datetime.now)
    ThoiGianHetHan = Column(DateTime, nullable=False)
    TrangThai = Column(Boolean, default=False)