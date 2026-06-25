#!/bin/bash
# ==============================================================
# start.sh — Script khởi động hệ thống ChatBot AI LexRAG++
# Chạy trong Docker container trên HuggingFace Spaces
# ==============================================================

set -e  # Dừng ngay nếu có lỗi

echo ""
echo "============================================================"
echo "  🚀 KHỞI ĐỘNG CHATBOT AI LUẬT HÔN NHÂN & GIA ĐÌNH"
echo "  🏷️  LexRAG++ | HuggingFace Spaces Deployment"
echo "============================================================"
echo ""

# ── Bước 1: Kiểm tra biến môi trường bắt buộc ─────────────────
echo "⚙️  [1/4] Kiểm tra cấu hình môi trường..."

if [ -z "$DATABASE_URL" ]; then
    echo "⚠️  CẢNH BÁO: DATABASE_URL chưa được đặt!"
    echo "   → Hệ thống sẽ dùng SQLite tại /app/backend/data/chatbot.db"
    export DATABASE_URL="sqlite:////app/backend/data/chatbot.db"
fi

if [ -z "$JWT_SECRET_KEY" ]; then
    echo "⚠️  CẢNH BÁO: JWT_SECRET_KEY chưa được đặt, dùng giá trị mặc định!"
    export JWT_SECRET_KEY="khoaluan_chatbot_bi_mat_hf_2026"
fi

echo "✅ Cấu hình môi trường OK"
echo "   DATABASE: $(echo $DATABASE_URL | sed 's|://.*@|://***@|g')"
echo ""

# ── Bước 2: Build FAISS index nếu chưa có ─────────────────────
echo "🧠 [2/4] Kiểm tra FAISS Vector Database..."

FAISS_INDEX="/app/backend/data/vector_db.index"
METADATA="/app/backend/data/metadata.pkl"

if [ -f "$FAISS_INDEX" ] && [ -f "$METADATA" ]; then
    echo "✅ Đã tìm thấy FAISS index sẵn có. Bỏ qua bước build."
else
    echo "📚 Chưa có FAISS index. Bắt đầu nạp dữ liệu từ PDF..."
    echo "   Quá trình này mất khoảng 2-5 phút lần đầu..."
    
    cd /app/backend
    python scripts/ingest_law.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Đã build FAISS index thành công!"
    else
        echo "❌ LỖI khi build FAISS index. Kiểm tra file PDF trong /app/backend/data/"
        exit 1
    fi
fi
echo ""

# ── Bước 3: Khởi động FastAPI Server ──────────────────────────
echo "🌐 [3/4] Khởi động FastAPI Backend..."
echo "   Host : 0.0.0.0"
echo "   Port : ${PORT:-7860}"
echo "   Docs : http://localhost:${PORT:-7860}/docs"
echo ""

echo "🎯 [4/4] Hệ thống sẵn sàng phục vụ!"
echo "============================================================"
echo ""

cd /app/backend
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-7860} \
    --workers 1 \
    --log-level info \
    --timeout-keep-alive 75
