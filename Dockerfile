# ==============================================================
# Dockerfile — ChatBot AI Luật Hôn Nhân & Gia Đình (LexRAG++)
# Target: HuggingFace Spaces (port 7860)
# ==============================================================

FROM python:3.11-slim

# ── Metadata ──────────────────────────────────────────────────
LABEL maintainer="Nguyen Ho"
LABEL description="ChatBot AI Tư Vấn Luật Hôn Nhân và Gia Đình Việt Nam (LexRAG++)"

# ── Biến môi trường hệ thống ───────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend \
    PORT=7860 \
    # Tắt progress bar của transformers khi build image
    TRANSFORMERS_VERBOSITY=error \
    # Cache HuggingFace models vào thư mục cố định
    HF_HOME=/app/.cache/huggingface \
    SENTENCE_TRANSFORMERS_HOME=/app/.cache/sentence_transformers

# ── Cài đặt system dependencies ───────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build tools cho một số package Python
    gcc \
    g++ \
    # Cần thiết cho pdfplumber / PDFs
    libpoppler-cpp-dev \
    # Tiện ích
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# ── Tạo thư mục làm việc ──────────────────────────────────────
WORKDIR /app

# ── Cài đặt Python dependencies (layer riêng để tận dụng cache) ──
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Pre-download AI Models vào cache (build-time) ─────────────
# Làm điều này khi build để lúc startup không cần tải lại
RUN python -c " \
import sentence_transformers as st; \
print('Đang tải model Bi-Encoder (multilingual-e5-base)...'); \
st.SentenceTransformer('intfloat/multilingual-e5-base'); \
print('Đang tải model Cross-Encoder (ms-marco-MiniLM-L-6-v2)...'); \
st.CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2'); \
print('Tất cả model đã được tải thành công!')"

# ── Copy toàn bộ source code ───────────────────────────────────
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# ── Copy startup script và cấp quyền thực thi ─────────────────
COPY start.sh ./start.sh
RUN chmod +x ./start.sh

# ── Tạo thư mục data nếu chưa có ──────────────────────────────
RUN mkdir -p /app/backend/data

# ── Mở port HuggingFace Spaces ────────────────────────────────
EXPOSE 7860

# ── Lệnh khởi động ────────────────────────────────────────────
CMD ["/bin/bash", "/app/start.sh"]
