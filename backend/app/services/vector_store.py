import faiss
import pickle
import numpy as np
import os # Thêm thư viện os để xử lý đường dẫn
from sentence_transformers import SentenceTransformer

# 1. Tính toán đường dẫn tuyệt đối về thư mục gốc (backend)
# File này nằm ở backend/app/services/vector_store.py -> Lùi 3 cấp
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")

# 2. Đảm bảo thư mục data luôn tồn tại, tránh lỗi báo không tìm thấy thư mục
os.makedirs(DATA_DIR, exist_ok=True)

# 3. Tạo đường dẫn chính xác tuyệt đối tới 2 file
INDEX_PATH = os.path.join(DATA_DIR, "vector_db.index")
METADATA_PATH = os.path.join(DATA_DIR, "metadata.pkl")

class VectorStoreService:
    def __init__(self):
        # Sử dụng model multilingual-e5-base như đề cương
        self.model = SentenceTransformer('intfloat/multilingual-e5-base')
        self.index = None
        self.metadata = []

        # --- ĐOẠN CODE THÊM MỚI ---
        # Tự động tải dữ liệu lên RAM khi Server khởi động (để Chatbot có thể tìm kiếm)
        if os.path.exists(INDEX_PATH) and os.path.exists(METADATA_PATH):
            self.index = faiss.read_index(INDEX_PATH)
            with open(METADATA_PATH, "rb") as f:
                self.metadata = pickle.load(f)
            print(f"[VectorStore] Đã tải thành công {len(self.metadata)} chunks vào bộ nhớ.")
        # --------------------------

    def encode_text(self, text: str):
        # Format cho model E5: thêm "passage: " cho tài liệu
        return self.model.encode([f"passage: {text}"])[0]

    def add_to_index(self, chunks):
        embeddings = []
        for chunk in chunks:
            embeddings.append(self.encode_text(chunk['content']))
            self.metadata.append(chunk)
            
        embeddings = np.array(embeddings).astype('float32')
        dimension = embeddings.shape[1]
        
        if self.index is None:
            self.index = faiss.IndexFlatL2(dimension)
            
        self.index.add(embeddings)
        
        # Lưu index và metadata (Đã thay bằng đường dẫn tuyệt đối)
        faiss.write_index(self.index, INDEX_PATH)
        with open(METADATA_PATH, "wb") as f:
            pickle.dump(self.metadata, f)

    def search(self, query: str, top_k=5):
        # Chặn lỗi nếu chưa có dữ liệu nào trong Database
        if self.index is None or len(self.metadata) == 0:
            return []

        # Format cho model E5: thêm "query: " cho câu hỏi
        query_vector = self.model.encode([f"query: {query}"]).astype('float32')
        distances, indices = self.index.search(query_vector, top_k)
        
        return [self.metadata[i] for i in indices[0] if i != -1]

vector_service = VectorStoreService()