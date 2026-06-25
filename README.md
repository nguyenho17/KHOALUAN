---
title: ChatBot AI Luật Hôn Nhân và Gia Đình
emoji: ⚖️
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: true
license: other
short_description: ChatBot tư vấn Luật Hôn nhân và Gia đình Việt Nam
---

<div align="center">

# ⚖️ ChatBot AI – Luật Hôn Nhân và Gia Đình Việt Nam

### **LexRAG++ · Retrieval-Augmented Generation cho Tư Vấn Pháp Lý**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python)](https://python.org/)
[![SQL Server](https://img.shields.io/badge/SQL%20Server-2019+-CC2927?style=for-the-badge&logo=microsoftsqlserver)](https://www.microsoft.com/sql-server)
[![FAISS](https://img.shields.io/badge/FAISS-Vector%20DB-009688?style=for-the-badge)](https://github.com/facebookresearch/faiss)
[![License](https://img.shields.io/badge/License-Academic-blue?style=for-the-badge)](LICENSE)

> Hệ thống chatbot AI chuyên biệt, ứng dụng kiến trúc **RAG++ 4 giai đoạn** kết hợp FAISS · BM25 · Cross-Encoder · LLM Llama-3.3-70B, được đánh giá tự động bằng bộ chỉ số học thuật LexRAG.

[📺 Demo](#-demo) · [🚀 Cài đặt nhanh](#-cài-đặt-nhanh) · [📖 Tài liệu API](#-api-endpoints) · [🧠 Kiến trúc](#-kiến-trúc-hệ-thống)

</div>

---

## 📋 Mục Lục

- [Giới thiệu](#-giới-thiệu)
- [Tính năng nổi bật](#-tính-năng-nổi-bật)
- [Kiến trúc hệ thống](#-kiến-trúc-hệ-thống)
- [Cấu trúc thư mục](#-cấu-trúc-thư-mục)
- [Yêu cầu hệ thống](#-yêu-cầu-hệ-thống)
- [Cài đặt nhanh](#-cài-đặt-nhanh)
- [Cấu hình môi trường](#-cấu-hình-môi-trường-env)
- [Khởi động hệ thống](#-khởi-động-hệ-thống)
- [RAG++ Pipeline](#-rag-pipeline-4-giai-đoạn)
- [API Endpoints](#-api-endpoints)
- [Cơ sở dữ liệu](#-cơ-sở-dữ-liệu)
- [Giao diện người dùng](#-giao-diện-người-dùng)
- [Hệ thống đánh giá LexRAG](#-hệ-thống-đánh-giá-lexrag)
- [Benchmark & Thực nghiệm](#-benchmark--thực-nghiệm)
- [Đóng góp](#-đóng-góp)

---

## 📖 Giới Thiệu

**ChatBot AI Luật Hôn Nhân và Gia Đình** là đồ án khóa luận tốt nghiệp ứng dụng trí tuệ nhân tạo vào lĩnh vực tư vấn pháp lý tại Việt Nam. Hệ thống được xây dựng trên nền tảng **RAG++ (Retrieval-Augmented Generation nâng cao)** — một kiến trúc kết hợp đa chiến lược tìm kiếm nhằm đảm bảo độ chính xác pháp lý cao nhất.

### Hệ thống có khả năng tư vấn về:

| Lĩnh vực | Ví dụ câu hỏi |
|---|---|
| 💍 Kết hôn | Điều kiện kết hôn, thủ tục đăng ký, kết hôn có yếu tố nước ngoài |
| 📝 Ly hôn | Thuận tình / Đơn phương ly hôn, thủ tục, thời gian |
| 🏠 Tài sản | Chia tài sản chung/riêng, quyền sử dụng đất, thừa kế |
| 👶 Quyền nuôi con | Ai được nuôi con, cấp dưỡng, thăm nom |
| 💰 Cấp dưỡng | Mức cấp dưỡng tối thiểu, nghĩa vụ cấp dưỡng |
| 📜 Hợp đồng hôn nhân | Thỏa thuận tài sản trước hôn nhân |

---

## ✨ Tính Năng Nổi Bật

### 🤖 Về AI / RAG
- **RAG++ 4 giai đoạn**: FAISS Dense → BM25 Sparse → RRF Fusion → Cross-Encoder Reranking
- **Phân loại tự động**: LLM lọc câu hỏi ngoài phạm vi (out-of-scope classifier)
- **Viết lại câu hỏi**: Chuyển ngôn ngữ thông thường thành từ khóa pháp lý chuẩn
- **Multi-turn Context**: Duy trì ngữ cảnh 5 lượt hội thoại gần nhất
- **Temporal Decay**: Ưu tiên văn bản pháp luật mới hơn (phạt 20%/năm)
- **Xoay vòng API Key**: Tự động chuyển dự phòng khi key cạn token (hỗ trợ tới 50 keys)

### 🧑‍💼 Về người dùng
- Đăng ký / Đăng nhập với username, email, hoặc số điện thoại
- Khôi phục mật khẩu qua OTP email (hết hạn 5 phút)
- Lưu & tải lại lịch sử hội thoại theo phiên
- Chỉnh sửa hồ sơ, cập nhật ảnh đại diện (Base64)

### 👨‍💻 Về Admin
- Dashboard tổng quan: lưu lượng hôm nay, tăng trưởng, biểu đồ 7/30 ngày
- Phân phối chủ đề pháp lý (Hôn nhân / Tài sản / Nuôi con)
- Quản lý hội thoại: phân trang, tìm kiếm, lọc theo chủ đề
- **Human-in-the-Loop**: Phê duyệt / từ chối từng câu trả lời, nhập Ground Truth
- Xem 7 chỉ số đánh giá chất lượng cho mỗi phản hồi AI
- Tải xuống báo cáo thực nghiệm dạng Excel

### 📊 Về đánh giá chất lượng (LexRAG Evaluation)
- **Keyword Accuracy**: Tỷ lệ từ khóa khớp với đáp án chuẩn (0–100)
- **LLM-as-a-Judge** 5 tiêu chí học thuật: Factuality · Completeness · Coherence · Clarity · Relevance
- Chạy **bất đồng bộ nền** sau mỗi câu hỏi — không ảnh hưởng tốc độ phản hồi

---

## 🏗️ Kiến Trúc Hệ Thống

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (HTML + JS)                         │
│                                                                     │
│   trangchu.html → login.html ──┐                                    │
│   dangky.html ─────────────────┤                                    │
│   quenmatkhau.html ────────────┘                                    │
│                                                                     │
│   chat.html ◄──── app.js ────► admin.html                          │
│   (Sidebar lịch sử)              (Dashboard, qlytuvan, phantich)    │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ HTTP REST API (port 8000)
┌──────────────────────────▼──────────────────────────────────────────┐
│                     BACKEND (FastAPI)                               │
│                         main.py                                     │
│                                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────┐  ┌────────────┐  │
│  │  Auth APIs  │  │   Chat API   │  │Admin APIs│  │Profile APIs│  │
│  │  /login     │  │   /chat      │  │/dashboard│  │/profile    │  │
│  │  /register  │  │   /history   │  │/conversat│  │            │  │
│  │  /forgot-pw │  │   /sessions  │  │/stats    │  │            │  │
│  └─────────────┘  └──────┬───────┘  └──────────┘  └────────────┘  │
│                           │                                         │
│              ┌────────────▼─────────────────────┐                  │
│              │         RAG++ PIPELINE            │                  │
│              │                                   │                  │
│              │  1. processor.is_out_of_scope()   │                  │
│              │  2. processor.reformulate_query() │                  │
│              │  3. retrieval.hybrid_search()     │                  │
│              │     ├─ FAISS Dense (top 35)       │                  │
│              │     ├─ BM25+ViTokenizer (top 35)  │                  │
│              │     ├─ RRF + Temporal Decay        │                  │
│              │     └─ Cross-Encoder Rerank (top7)│                  │
│              │  4. generation.generate_answer()  │                  │
│              └────────────┬──────────────────────┘                  │
│                           │  background_task                        │
│              ┌────────────▼──────────────────────┐                 │
│              │      online_evaluator              │                 │
│              │  ├─ Keyword Accuracy               │                 │
│              │  └─ LLM Judge (5 tiêu chí)         │                 │
│              └───────────────────────────────────┘                 │
│                                                                     │
│       APIKeyRotator (tự động xoay ≤50 OpenRouter keys)             │
└──────────────────┬──────────────────────┬───────────────────────────┘
                   │                      │
        ┌──────────▼──────┐    ┌──────────▼─────────┐
        │  SQL Server     │    │  FAISS Vector DB    │
        │  (10 bảng)      │    │  vector_db.index    │
        │  SQLAlchemy ORM │    │  metadata.pkl       │
        └─────────────────┘    └────────────────────┘
```

---

## 📂 Cấu Trúc Thư Mục

```
KHOALUAN/
│
├── 📁 backend/                          # Toàn bộ mã nguồn Backend
│   ├── 📄 .env                          # ⚙️ Biến môi trường (không commit Git)
│   ├── 📄 requirements.txt             # Danh sách thư viện Python
│   │
│   ├── 📁 app/                          # Package ứng dụng FastAPI
│   │   ├── 📄 main.py                   # 🧠 Điểm vào chính — toàn bộ API endpoints
│   │   │
│   │   ├── 📁 db/                       # Tầng cơ sở dữ liệu
│   │   │   ├── 📄 database.py           # Kết nối SQL Server (SQLAlchemy Engine)
│   │   │   ├── 📄 models.py             # ORM Models — 9 bảng dữ liệu
│   │   │   └── 📄 Modelfile.txt         # Cấu hình Ollama model (tham khảo)
│   │   │
│   │   └── 📁 services/                 # Các service nghiệp vụ
│   │       ├── 📄 retrieval.py          # 🔍 RAG++ Retrieval (FAISS+BM25+Cross-Encoder)
│   │       ├── 📄 generation.py         # ✍️  Sinh câu trả lời bằng LLM
│   │       ├── 📄 processor.py          # 🧹 Lọc scope + viết lại câu hỏi
│   │       ├── 📄 online_evaluator.py   # 📊 Đánh giá tự động nền (LexRAG)
│   │       ├── 📄 embedding.py          # 🧮 Tạo vector embedding FAISS
│   │       ├── 📄 ingestion.py          # 📄 Đọc PDF + tách chunks
│   │       ├── 📄 vector_store.py       # 🗃️  Quản lý FAISS index
│   │       ├── 📄 llm_service.py        # 🤖 Wrapper LLM service
│   │       └── 📄 security.py           # 🔐 JWT + Bcrypt
│   │
│   ├── 📁 data/                         # Kho văn bản pháp luật PDF
│   │   ├── 📄 Luat_Hon_Nhan_Gia_Dinh_2014.pdf
│   │   ├── 📄 10_2015_ND-CP_264622.pdf
│   │   ├── 📄 123_2015_ND-CP_282304.pdf
│   │   ├── 📄 126_2014_ND-CP_262379.pdf
│   │   ├── 📄 82_2020_ND-CP_392611.pdf
│   │   ├── 📄 98_2016_ND-CP_315458.pdf
│   │   ├── 📄 109_2026_ND-CP_700787.pdf
│   │   ├── 📄 207_2025_ND-CP_306858.pdf
│   │   ├── 📄 01_2016_TTLT-TANDTC-VKSNDTC-BTP_293202.pdf
│   │   ├── 📄 01_2024_NQ-HDTP_515531.pdf
│   │   ├── 🗃️  vector_db.index           # FAISS index (tự động tạo)
│   │   └── 🗃️  metadata.pkl             # Metadata chunks (tự động tạo)
│   │
│   ├── 📁 scripts/
│   │   └── 📄 ingest_law.py             # Script nạp dữ liệu PDF → FAISS
│   │
│   ├── 📄 evaluate.py                   # Đánh giá offline toàn bộ dataset
│   ├── 📄 generate_dataset.py           # Tạo bộ câu hỏi benchmark
│   ├── 📄 run_benchmark.py              # Chạy benchmark cơ bản
│   ├── 📄 run_full_benchmark.py         # Chạy benchmark đầy đủ
│   ├── 📄 run_groq_benchmark.py         # Benchmark với Groq API
│   ├── 📄 benchmarks.xlsx              # Dataset câu hỏi + Ground Truth
│   └── 📄 lexrag_summary_report.xlsx   # Báo cáo tổng hợp kết quả
│
└── 📁 frontend/                         # Toàn bộ giao diện người dùng
    ├── 📄 app.js                        # ⚡ Logic JS dùng chung (717 dòng)
    ├── 📄 trangchu.html                 # 🏠 Trang chủ marketing
    ├── 📄 login.html                    # 🔑 Đăng nhập
    ├── 📄 dangky.html                   # 📝 Đăng ký tài khoản
    ├── 📄 quenmatkhau.html              # 🔓 Quên mật khẩu / OTP
    ├── 📄 chat.html                     # 💬 Giao diện chat chính
    ├── 📄 timhiuthem.html               # ℹ️  Tìm hiểu thêm về hệ thống
    ├── 📄 admin.html                    # 📊 Dashboard quản trị viên
    ├── 📄 qlytuvan.html                 # 📋 Danh sách quản lý hội thoại
    ├── 📄 qlytuvan_chitiet.html         # 🔎 Chi tiết & phê duyệt hội thoại
    ├── 📄 phantich.html                 # 📈 Trang thống kê thực nghiệm
    └── 📄 caidat.html                   # ⚙️  Cài đặt hệ thống (Dark Mode, v.v.)
```

---

## 💻 Yêu Cầu Hệ Thống

| Thành phần | Phiên bản tối thiểu | Ghi chú |
|---|---|---|
| Python | 3.10+ | Bắt buộc |
| Microsoft SQL Server | 2019+ | Hoặc SQL Server Express |
| ODBC Driver for SQL Server | 17+ | Cài từ Microsoft |
| RAM | 8 GB+ | Model Cross-Encoder tốn ~2GB |
| Disk | 5 GB+ | FAISS index + Model cache |
| OS | Windows 10 / Ubuntu 20.04+ | Đã test trên cả hai |

---

## 🚀 Cài Đặt Nhanh

### Bước 1: Clone dự án

```bash
git clone https://github.com/your-username/KHOALUAN.git
cd KHOALUAN
```

### Bước 2: Tạo môi trường ảo Python

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### Bước 3: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

> **Lưu ý:** Lần đầu chạy, `sentence-transformers` sẽ tự tải model `multilingual-e5-base` (~1.1 GB) và `ms-marco-MiniLM-L-6-v2` (~80 MB) từ HuggingFace.

### Bước 4: Tạo cơ sở dữ liệu SQL Server

Tạo database mới trong SQL Server Management Studio (SSMS):

```sql
CREATE DATABASE ChatbotLuatHonNhan;
GO
```

> Các bảng sẽ được **tự động tạo** khi FastAPI khởi động lần đầu qua SQLAlchemy `Base.metadata.create_all()`.

### Bước 5: Cấu hình file `.env`

```bash
cp .env.example .env   # hoặc tạo file .env mới (xem hướng dẫn bên dưới)
```

### Bước 6: Nạp dữ liệu luật vào FAISS

```bash
# Chạy từ thư mục backend/
python scripts/ingest_law.py
```

Lệnh này sẽ:
- Đọc toàn bộ 10 file PDF trong `/data/`
- Tách văn bản theo từng Điều luật
- Tạo embedding và lưu vào `data/vector_db.index` + `data/metadata.pkl`

### Bước 7: Khởi động Backend

```bash
# Chạy từ thư mục backend/
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Bước 8: Mở Frontend

Mở file `frontend/trangchu.html` trong trình duyệt bất kỳ.

> **Khuyến nghị**: Dùng VS Code extension **Live Server** để tránh vấn đề CORS với file:// protocol.

---

## ⚙️ Cấu Hình Môi Trường `.env`

Tạo file `.env` trong thư mục `backend/` với nội dung:

```dotenv
# =============================================
# 1. KẾT NỐI SQL SERVER
# =============================================
DB_SERVER=localhost                # Tên server SQL (hoặc IP)
DB_NAME=ChatbotLuatHonNhan         # Tên database
DB_USER=sa                         # Username SQL Server
DB_PASS=your_password_here         # Mật khẩu SQL Server

# =============================================
# 2. BẢO MẬT JWT
# =============================================
JWT_SECRET_KEY=khoaluan_chatbot_bi_mat_123   # Thay bằng chuỗi ngẫu nhiên

# =============================================
# 3. API KEYS OPENROUTER (xoay vòng tự động)
# Đăng ký miễn phí tại: https://openrouter.ai
# Thêm nhiều key để tăng khả năng dự phòng (tối đa 50)
# =============================================
OPENROUTER_API_KEY_1=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENROUTER_API_KEY_2=sk-or-v1-yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
OPENROUTER_API_KEY_3=sk-or-v1-zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
# Thêm OPENROUTER_API_KEY_4 đến OPENROUTER_API_KEY_50 nếu cần
```

> ⚠️ **Quan trọng**: Không bao giờ commit file `.env` lên Git. File `.gitignore` đã loại trừ nó.

---

## ▶️ Khởi Động Hệ Thống

### Khởi động Backend (FastAPI)

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Sau khi khởi động thành công, bạn sẽ thấy:

```
🔑 [HỆ THỐNG] Đã nạp thành công 3 API Keys dự phòng.
Đang khởi động Bộ truy xuất RAG++ (FAISS + BM25 + Cross-Encoder)...
-> Đang nạp Cross-Encoder (ms-marco-MiniLM-L-6-v2)...
-> Cross-Encoder đã sẵn sàng.
-> Đã tải thành công 1247 đoạn luật vào hệ thống tìm kiếm.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Tài liệu API tương tác** (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)

### Tài khoản Admin mặc định

Tạo tài khoản Admin đầu tiên bằng cách chèn thủ công vào SQL Server:

```sql
-- 1. Tạo thông tin người dùng
INSERT INTO NguoiDung (HoTen, Email, SoDienThoai)
VALUES (N'Quản Trị Viên', 'admin@example.com', '0900000000');

-- 2. Lấy MaNguoiDung vừa tạo
-- Giả sử là 1

-- 3. Tạo tài khoản với vai trò Admin (MaVaiTro = 1)
-- Mật khẩu: Admin@123 (đã bcrypt hash — thay hash thực tế tại đây)
INSERT INTO TaiKhoan (TenDangNhap, MatKhau, MaNguoiDung, MaVaiTro, TrangThai)
VALUES ('admin', '$2b$12$...hash_bcrypt...', 1, 1, N'Hoạt động');

-- Hoặc đơn giản hơn: dùng plain text (hệ thống hỗ trợ tương thích ngược)
INSERT INTO TaiKhoan (TenDangNhap, MatKhau, MaNguoiDung, MaVaiTro, TrangThai)
VALUES ('admin', 'Admin@123', 1, 1, N'Hoạt động');
```

---

## 🔍 RAG++ Pipeline 4 Giai Đoạn

Khi người dùng gửi một câu hỏi, hệ thống thực hiện theo luồng sau:

```
                    ┌─────────────────────┐
  Câu hỏi thô  ──► │  BƯỚC 0: OOS Check  │
 "chồng tôi       │  is_out_of_scope()  │
  ngoại tình,     │  LLM phân loại:     │
  ly hôn được     │  IN_SCOPE ✅         │
  không?"         │  OUT_OF_SCOPE ❌     │
                    └──────────┬──────────┘
                               │ IN_SCOPE
                    ┌──────────▼──────────┐
                    │  BƯỚC 1: Viết lại   │
                    │  reformulate_query()│
                    │  → "Điều kiện đơn  │
                    │    phương ly hôn   │
                    │    theo Luật Hôn   │
                    │    nhân 2014"      │
                    └──────────┬──────────┘
                               │
               ┌───────────────▼───────────────┐
               │      BƯỚC 2: HYBRID SEARCH     │
               │                               │
               │  Phase 1: FAISS Dense         │
               │  ├─ Encode "query: {text}"    │
               │  └─ Search top 35 vectors     │
               │                               │
               │  Phase 2: BM25 Sparse         │
               │  ├─ ViTokenizer (tách từ VN)  │
               │  └─ BM25Okapi top 35          │
               │                               │
               │  Phase 3: RRF + Temporal Decay│
               │  ├─ RRF(FAISS×1.5, BM25×1.5) │
               │  ├─ Phạt 20%/năm tuổi luật   │
               │  └─ Top 20 ứng viên           │
               │                               │
               │  Phase 4: Cross-Encoder Rerank│
               │  ├─ Chấm (query, doc) pairs  │
               │  ├─ α=0.7×CrossEnc + 0.3×RRF │
               │  └─ Top 7 tài liệu cuối cùng │
               └───────────────┬───────────────┘
                               │ 7 điều luật
                    ┌──────────▼──────────┐
                    │  BƯỚC 3: GENERATE   │
                    │  Llama-3.3-70B      │
                    │  Prompt 4 phần:     │
                    │  I.  Xác nhận vấn đề│
                    │  II. Căn cứ pháp lý │
                    │  III.Phân tích chi  │
                    │      tiết           │
                    │  IV. Lời khuyên     │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────────────┐
                    │  Trả về người dùng:          │
                    │  { answer, citations,        │
                    │    session_id }              │
                    └──────────┬──────────────────┘
                               │ (background)
                    ┌──────────▼──────────────────┐
                    │  ĐÁNH GIÁ TỰ ĐỘNG (nền)     │
                    │  ├─ Keyword Accuracy         │
                    │  ├─ LLM Judge (5 tiêu chí)  │
                    │  └─ Lưu 7 chỉ số → DB       │
                    └─────────────────────────────┘
```

---

## 📡 API Endpoints

> **Base URL:** `http://localhost:8000`
> **Xem Swagger UI tương tác:** [http://localhost:8000/docs](http://localhost:8000/docs)

### 🔐 Authentication

| Method | Endpoint | Mô tả | Auth |
|---|---|---|---|
| `POST` | `/api/login` | Đăng nhập (username / email / SĐT) | ❌ |
| `POST` | `/api/register` | Đăng ký tài khoản mới | ❌ |
| `POST` | `/api/forgot-password` | Reset mật khẩu về `123456` | ❌ |
| `POST` | `/api/forgot-password/send-otp` | Gửi OTP 6 số qua email | ❌ |
| `POST` | `/api/forgot-password/verify-otp` | Xác minh mã OTP | ❌ |
| `POST` | `/api/forgot-password/reset` | Đặt mật khẩu mới sau OTP | ❌ |

**Ví dụ đăng nhập:**
```json
POST /api/login
{
  "TenDangNhap": "admin",
  "MatKhau": "Admin@123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_info": {
    "ten_dang_nhap": "admin",
    "ma_vai_tro": 1,
    "ho_ten": "Quản Trị Viên"
  }
}
```

---

### 💬 Chat & Lịch Sử

| Method | Endpoint | Mô tả | Auth |
|---|---|---|---|
| `POST` | `/api/chat` | **Chat RAG++ chính** | 🔓 Tùy chọn |
| `POST` | `/api/chat/history` | Lấy lịch sử theo username | ❌ |
| `GET` | `/api/chat/sessions` | Danh sách phiên chat | 🔓 Tùy chọn |

**Ví dụ gửi câu hỏi:**
```json
POST /api/chat
Authorization: Bearer {token}

{
  "question": "Vợ ngoại tình thì có được ly hôn không?",
  "session_id": "123"
}
```

**Response:**
```json
{
  "answer": "PHẦN I: LỜI CHÀO VÀ XÁC NHẬN VẤN ĐỀ\n...",
  "citations": ["Điều 51", "Điều 56", "Điều 58"],
  "session_id": "123"
}
```

---

### 👤 Hồ Sơ Người Dùng

| Method | Endpoint | Mô tả | Auth |
|---|---|---|---|
| `POST` | `/api/profile/get` | Lấy thông tin hồ sơ | ❌ |
| `PUT` | `/api/profile/update` | Cập nhật tên, username, avatar | ❌ |

---

### 🛡️ Admin (Yêu cầu role = 1)

| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/api/admin/dashboard-stats` | Thống kê tổng quan + biểu đồ 7/30 ngày |
| `GET` | `/api/admin/conversations` | Danh sách hội thoại (phân trang, tìm kiếm) |
| `GET` | `/api/admin/conversations/{id}` | Chi tiết hội thoại + 7 chỉ số đánh giá |
| `PUT` | `/api/admin/conversations/{id}/review` | Phê duyệt + nhập Ground Truth |
| `GET` | `/api/admin/experimental-stats` | Số liệu thực nghiệm từ Excel |
| `GET` | `/api/admin/download-excel` | Tải báo cáo Excel |

**Ví dụ phê duyệt hội thoại:**
```json
PUT /api/admin/conversations/42/review
Authorization: Bearer {admin_token}

{
  "trang_thai": "Approved",
  "ground_truth": "Theo Điều 56 Luật Hôn nhân và Gia đình 2014..."
}
```

---

## 🗄️ Cơ Sở Dữ Liệu

### Sơ đồ quan hệ (ERD)

```
VaiTro (1) ──────── (N) TaiKhoan (N) ─────── (1) NguoiDung
                                                      │
                                              ┌───────┴───────┐
                                              │               │
                                           PhienChat    DanhGiaChatbot
                                              │
                                           LichSuChat
                                    (7 cột chỉ số đánh giá AI)
```

### Bảng `LichSuChat` — Bảng trung tâm

| Cột | Kiểu | Mô tả |
|---|---|---|
| `MaChat` | INT PK | ID tự tăng |
| `MaPhien` | INT FK | Liên kết phiên hội thoại |
| `MaNguoiDung` | INT FK | Người dùng (NULL = ẩn danh) |
| `CauHoi` | NVARCHAR | Câu hỏi người dùng |
| `TraLoi` | NVARCHAR | Câu trả lời AI |
| `ThoiGian` | DATETIME | Thời điểm xảy ra |
| `NguonTrichDan` | NVARCHAR | "Điều 51, Điều 56, Điều 58" |
| `ThoiGianPhanHoi` | FLOAT | Thời gian sinh câu trả lời (giây) |
| `DiemKeywordAccuracy` | FLOAT | Keyword Accuracy (0–100) |
| `DiemLLMJudge` | FLOAT | Điểm LLM Judge trung bình (0–100) |
| `DiemFactuality` | FLOAT | Tính xác thực (0–100) |
| `DiemCompleteness` | FLOAT | Tính đầy đủ (0–100) |
| `DiemCoherence` | FLOAT | Tính mạch lạc (0–100) |
| `DiemClarity` | FLOAT | Tính rõ ràng (0–100) |
| `DiemRelevance` | FLOAT | Đúng trọng tâm (0–100) |
| `TrangThaiDuyet` | VARCHAR | Pending / Approved / Rejected |
| `GroundTruth` | NVARCHAR | Đáp án chuẩn do Admin nhập |

---

## 🖥️ Giao Diện Người Dùng

### Sơ đồ điều hướng

```
trangchu.html (Landing Page)
    │
    ├─► login.html ──────────────────────────► admin.html (role=1)
    │       │                                       │
    │       └─► chat.html (role=2)           qlytuvan.html
    │               │                               │
    │               └─ Sidebar lịch sử     qlytuvan_chitiet.html
    │                                               │
    └─► dangky.html                         phantich.html
    │                                               │
    └─► quenmatkhau.html                    caidat.html
    │
    └─► timhiuthem.html
```

### Mô tả từng trang

| Trang | Mô tả |
|---|---|
| **trangchu.html** | Landing page marketing, giới thiệu 4 tính năng chính, CTA đến chat |
| **login.html** | Form đăng nhập; hỗ trợ username/email/SĐT |
| **dangky.html** | Form đăng ký gồm: Họ tên, Email, SĐT, Mật khẩu |
| **quenmatkhau.html** | 2 luồng: Reset về 123456 hoặc OTP 6 số qua email |
| **chat.html** | Giao diện chat chính: sidebar lịch sử phiên + khung hội thoại + hiển thị trích dẫn điều luật |
| **admin.html** | Dashboard tổng quan: lưu lượng hôm nay, biểu đồ 7/30 ngày, phân phối chủ đề, phân tích AI |
| **qlytuvan.html** | Bảng quản lý hội thoại: phân trang 10/trang, tìm kiếm, lọc theo 5 chủ đề |
| **qlytuvan_chitiet.html** | Xem chi tiết 1 hội thoại: câu hỏi, câu trả lời, 7 chỉ số điểm số, nút Phê duyệt/Từ chối, nhập Ground Truth |
| **phantich.html** | Thống kê thực nghiệm LexRAG từ file Excel, có nút tải xuống báo cáo |
| **caidat.html** | Dark/Light mode, cấu hình API, tùy chỉnh hệ thống |
| **timhiuthem.html** | Giới thiệu chi tiết về công nghệ RAG++, mô hình, dữ liệu |

---

## 📊 Hệ Thống Đánh Giá LexRAG

Sau mỗi câu hỏi, `OnlineEvaluator` chạy **bất đồng bộ nền** để tính 7 chỉ số:

### Phương pháp 1: Keyword Accuracy

```
KW_Acc = |{từ_khóa_GT} ∩ {từ_khóa_AI}| / |{từ_khóa_GT}| × 100
```

- Ground Truth được tìm tự động từ `benchmarks.xlsx` bằng `difflib.SequenceMatcher` (ngưỡng tương đồng ≥ 0.6)

### Phương pháp 2: LLM-as-a-Judge (5 tiêu chí)

| Tiêu chí | Mô tả | Thang điểm |
|---|---|---|
| **Factuality** | Tính xác thực pháp lý, không bịa đặt | 0–100 |
| **Completeness** | Bao phủ đủ các ý và căn cứ pháp lý | 0–100 |
| **Coherence** | Bố cục, lập luận logic, mạch lạc | 0–100 |
| **Clarity** | Câu từ dễ hiểu, rõ ràng, tường minh | 0–100 |
| **Relevance** | Trả lời trực diện đúng câu hỏi | 0–100 |

**Điểm LLM Judge tổng hợp:**
```
LLM_Judge = (Factuality + Completeness + Coherence + Clarity + Relevance) / 5
```

### Kết quả thực nghiệm trên tập 377 câu hỏi

| Chỉ số | Kết quả |
|---|---|
| Keyword Accuracy | **0.81 / 1.0** |
| LLM Judge (tổng hợp) | **8.18 / 10** |
| Factuality | 8.22 / 10 |
| Completeness | 7.62 / 10 |
| Coherence | 8.20 / 10 |
| Clarity | 8.23 / 10 |
| Relevance | **8.65 / 10** |

---

## 🔬 Benchmark & Thực Nghiệm

### Chạy đánh giá offline

```bash
cd backend

# Đánh giá trên toàn bộ dataset (chậm, ~377 câu hỏi)
python evaluate.py

# Chạy benchmark nhanh
python run_benchmark.py

# Benchmark đầy đủ với nhiều model
python run_full_benchmark.py

# Benchmark với Groq API (tốc độ cao)
python run_groq_benchmark.py

# Tạo thêm dataset câu hỏi
python generate_dataset.py
```

### Cấu trúc file benchmark

```
benchmarks.xlsx         — Dataset câu hỏi + Ground Truth (cột: CauHoi, GroundTruth)
evaluation_results.csv  — Chi tiết kết quả đánh giá từng câu
lexrag_summary_report.xlsx — Báo cáo tổng hợp (đọc bởi API /admin/experimental-stats)
```

---

## 📦 Thư Viện Chính

```
# requirements.txt
fastapi[all]          # Web framework
uvicorn               # ASGI server
sqlalchemy            # ORM
pyodbc                # Kết nối SQL Server
python-dotenv         # Đọc .env
python-jose[cryptography]  # JWT
passlib[bcrypt]       # Hash mật khẩu

# AI/RAG
faiss-cpu             # Vector similarity search
sentence-transformers # Embedding + Cross-Encoder
rank_bm25             # BM25 sparse retrieval
pyvi                  # Vietnamese tokenizer
langchain-text-splitters  # Document chunking
pdfplumber            # Đọc PDF tiếng Việt
openai                # Client gọi OpenRouter API

# Benchmark
pandas
openpyxl
```

---

## 🔒 Bảo Mật

| Khía cạnh | Giải pháp |
|---|---|
| Mật khẩu | Bcrypt hash (cost factor 12) |
| Authentication | JWT HS256, TTL 24 giờ |
| Authorization | Kiểm tra `ma_vai_tro` tại mọi Admin route |
| API Keys | Xoay vòng tự động, vô hiệu hóa key lỗi vào `.env` |
| CORS | `allow_origins=["*"]` (cần giới hạn khi deploy production) |
| OTP | 6 chữ số, hết hạn sau 5 phút, lưu RAM |

> ⚠️ Trước khi deploy production, hãy:
> 1. Thay `allow_origins=["*"]` bằng domain cụ thể
> 2. Chuyển `EMAIL_PASSWORD` trong `main.py` vào file `.env`
> 3. Dùng HTTPS thay HTTP

---

## 🔧 Xử Lý Sự Cố Thường Gặp

### ❌ Lỗi kết nối SQL Server
```
pyodbc.OperationalError: ('08001', ...)
```
**Giải pháp:** Kiểm tra ODBC Driver 17 đã được cài chưa, kiểm tra lại `DB_SERVER`, `DB_USER`, `DB_PASS` trong `.env`.

### ❌ Không tìm thấy dữ liệu luật
```
⚠️ CẢNH BÁO: Chưa tìm thấy dữ liệu luật. Vui lòng chạy file ingest_law.py!
```
**Giải pháp:** Chạy `python scripts/ingest_law.py` để nạp dữ liệu PDF vào FAISS.

### ❌ API Key cạn token
```
❌ [NGUY CẤP] Toàn bộ danh sách API Keys dự phòng đã cạn kiệt!
```
**Giải pháp:** Thêm key mới vào `.env` dưới dạng `OPENROUTER_API_KEY_4=sk-or-...` và restart server.

### ❌ Lỗi import module
```
ModuleNotFoundError: No module named 'app'
```
**Giải pháp:** Đảm bảo bạn đang chạy lệnh từ thư mục `backend/`, không phải từ thư mục con.

---

## 🤝 Đóng Góp

Dự án hiện là **đồ án khóa luận tốt nghiệp** — mọi đóng góp cải thiện đều được chào đón thông qua Pull Request.

1. Fork dự án
2. Tạo branch mới (`git checkout -b feature/ten-tinh-nang`)
3. Commit thay đổi (`git commit -m 'feat: thêm tính năng X'`)
4. Push lên branch (`git push origin feature/ten-tinh-nang`)
5. Mở Pull Request

---

## 📄 Giấy Phép

Dự án này được phát triển cho mục đích học thuật. Mọi việc sử dụng thương mại cần có sự chấp thuận từ tác giả.

---

<div align="center">

**Xây dựng bởi:** Nguyễn Hồ · Khóa luận Tốt nghiệp 2026

*"Sự thấu hiểu và đúng luật là bước đầu tiên để tìm lại bình yên cho gia đình bạn."*

</div>
