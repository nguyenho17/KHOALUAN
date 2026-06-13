import os
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle

# --- ĐOẠN MỚI THÊM: Tính toán đường dẫn tuyệt đối ---
# File này nằm ở backend/app/services/embedding.py -> Lùi 3 cấp về thư mục backend
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Đảm bảo thư mục data luôn tồn tại trước khi lưu
os.makedirs(DATA_DIR, exist_ok=True)

INDEX_PATH = os.path.join(DATA_DIR, "vector_db.index")
METADATA_PATH = os.path.join(DATA_DIR, "metadata.pkl")
# ---------------------------------------------------

# 1. Khởi tạo mô hình Embedding (theo thiết kế RAG++)
# Sử dụng multilingual-e5-base để tối ưu cho tiếng Việt 
model = SentenceTransformer('intfloat/multilingual-e5-base')

def create_embeddings(chunks):
    texts = [c['content'] for c in chunks]
    # Thêm tiền tố 'query: ' hoặc 'passage: ' theo yêu cầu của dòng model E5
    embeddings = model.encode([f"passage: {t}" for t in texts], show_progress_bar=True)
    return np.array(embeddings).astype('float32')

def build_faiss_index(chunks):
    # Tạo vector từ các chunks đã tách ở bước trước
    embeddings = create_embeddings(chunks)
    
    # Khởi tạo Index FAISS (sử dụng IndexFlatL2 cho độ chính xác tuyệt đối)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    # Lưu Index và Metadata (để sau này truy xuất lại) -> Đã sửa thành đường dẫn tuyệt đối
    faiss.write_index(index, INDEX_PATH)
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(chunks, f)
        
    print(f"Đã Index thành công {len(chunks)} điều luật vào FAISS.")