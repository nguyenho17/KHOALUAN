import os
import faiss
import pickle
import numpy as np
import datetime
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, CrossEncoder
from pyvi import ViTokenizer

class RetrievalService:
    def __init__(self):
        print("Đang khởi động Bộ truy xuất RAG++ (FAISS + BM25 + Cross-Encoder)...")

        # -------------------------------------------------------
        # 1. Load model Bi-Encoder để tạo vector embedding
        # -------------------------------------------------------
        self.model = SentenceTransformer('intfloat/multilingual-e5-base')

        # -------------------------------------------------------
        # 2. Load Cross-Encoder để rerank (giai đoạn cuối)
        #    Model nhỏ gọn, hỗ trợ đa ngôn ngữ tốt với văn bản pháp lý
        # -------------------------------------------------------
        print("-> Đang nạp Cross-Encoder (ms-marco-MiniLM-L-6-v2)...")
        self.cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        print("-> Cross-Encoder đã sẵn sàng.")

        # -------------------------------------------------------
        # 3. Tính đường dẫn tuyệt đối đến thư mục data
        # -------------------------------------------------------
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        index_path = os.path.join(BASE_DIR, "data", "vector_db.index")
        metadata_path = os.path.join(BASE_DIR, "data", "metadata.pkl")

        # -------------------------------------------------------
        # 4. Nạp FAISS index và metadata
        # -------------------------------------------------------
        if os.path.exists(index_path) and os.path.exists(metadata_path):
            self.index = faiss.read_index(index_path)

            with open(metadata_path, "rb") as f:
                self.metadata = pickle.load(f)

            # 5. Khởi tạo BM25 với tách từ tiếng Việt
            tokenized_corpus = [
                ViTokenizer.tokenize(doc['content'].lower()).split()
                for doc in self.metadata
            ]
            self.bm25 = BM25Okapi(tokenized_corpus)
            print(f"-> Đã tải thành công {len(self.metadata)} đoạn luật vào hệ thống tìm kiếm.")
        else:
            self.index = None
            self.metadata = []
            self.bm25 = None
            print("⚠️ CẢNH BÁO: Chưa tìm thấy dữ liệu luật. Vui lòng chạy file ingest_law.py!")

    def hybrid_search(self, query: str, top_k: int = 7):
        """
        Pipeline truy xuất 4 giai đoạn:
          Giai đoạn 1: FAISS dense semantic search
          Giai đoạn 2: BM25 sparse keyword search (có ViTokenizer)
          Giai đoạn 3: Reciprocal Rank Fusion (RRF) + Temporal Decay Penalty
          Giai đoạn 4: Cross-Encoder Reranking (mới)
        Trả về top_k=7 tài liệu tốt nhất (tăng từ 5 lên 7 để cải thiện Completeness).
        """
        if not self.metadata or not self.bm25:
            return []

        # ═══════════════════════════════════════════════════════
        # GIAI ĐOẠN 1: FAISS DENSE SEARCH
        # Tăng pool lên top_k * 5 để Cross-Encoder có nhiều ứng viên hơn
        # ═══════════════════════════════════════════════════════
        search_pool = top_k * 5   # = 35 ứng viên ban đầu

        query_vector = self.model.encode([f"query: {query}"]).astype('float32')
        _, faiss_indices = self.index.search(query_vector, search_pool)
        faiss_results = faiss_indices[0].tolist()

        # ═══════════════════════════════════════════════════════
        # GIAI ĐOẠN 2: BM25 SPARSE SEARCH (có tách từ tiếng Việt)
        # ═══════════════════════════════════════════════════════
        tokenized_query = ViTokenizer.tokenize(query.lower()).split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        bm25_results = np.argsort(bm25_scores)[::-1][:search_pool].tolist()

        # Lọc các kết quả BM25 có điểm = 0 (không khớp từ khóa nào)
        valid_bm25_results = [idx for idx in bm25_results if bm25_scores[idx] > 0]

        # ═══════════════════════════════════════════════════════
        # GIAI ĐOẠN 3: RECIPROCAL RANK FUSION + TEMPORAL DECAY
        # ═══════════════════════════════════════════════════════
        rrf_scores = {}
        k_rrf = 60  # Hằng số làm mượt chuẩn RRF

        # Trọng số FAISS = 1.5 (ưu tiên ngữ nghĩa)
        for rank, idx in enumerate(faiss_results):
            if idx == -1:
                continue
            rrf_scores[idx] = rrf_scores.get(idx, 0) + 1.5 / (k_rrf + rank + 1)

        # Trọng số BM25 = 1.5 (cân bằng)
        for rank, idx in enumerate(valid_bm25_results):
            rrf_scores[idx] = rrf_scores.get(idx, 0) + 1.5 / (k_rrf + rank + 1)

        # Temporal Decay Penalty: phạt 20%/năm tuổi văn bản
        current_year = datetime.date.today().year
        for idx in list(rrf_scores.keys()):
            doc = self.metadata[idx]
            doc_year = doc.get("metadata", {}).get("year", 2000)
            age = current_year - doc_year
            if age > 0:
                decay_factor = max(0.01, 1.0 - (age * 0.20))
                rrf_scores[idx] *= decay_factor

        # Lấy top 20 ứng viên tốt nhất sau RRF để đưa vào Cross-Encoder
        rerank_pool_size = min(20, len(rrf_scores))
        sorted_by_rrf = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
        rrf_top_candidates = sorted_by_rrf[:rerank_pool_size]

        # ═══════════════════════════════════════════════════════
        # GIAI ĐOẠN 4: CROSS-ENCODER RERANKING  ← MỚI THÊM
        # Cross-Encoder đọc cặp (query, document) và cho điểm relevance chính xác hơn
        # ═══════════════════════════════════════════════════════
        if len(rrf_top_candidates) > 1:
            # Tạo danh sách cặp [query, nội_dung_điều_luật] cho Cross-Encoder chấm điểm
            cross_pairs = [
                [query, self.metadata[idx]['content'][:512]]   # Giới hạn 512 ký tự để tiết kiệm tốc độ
                for idx in rrf_top_candidates
            ]

            # Cross-Encoder chấm điểm relevance từng cặp (điểm cao = liên quan hơn)
            cross_scores = self.cross_encoder.predict(cross_pairs)

            # Kết hợp điểm Cross-Encoder với RRF bằng phép cộng có trọng số
            # Alpha = 0.7 ưu tiên Cross-Encoder (chính xác hơn), 0.3 giữ tín hiệu RRF
            alpha = 0.7
            rrf_max = max([rrf_scores[idx] for idx in rrf_top_candidates]) or 1.0
            cs_min = float(np.min(cross_scores))
            cs_max = float(np.max(cross_scores))
            cs_range = (cs_max - cs_min) if (cs_max - cs_min) > 0 else 1.0

            final_scores = {}
            for i, idx in enumerate(rrf_top_candidates):
                rrf_norm = rrf_scores[idx] / rrf_max
                cs_norm  = (cross_scores[i] - cs_min) / cs_range
                final_scores[idx] = alpha * cs_norm + (1 - alpha) * rrf_norm

            # Sắp xếp lại theo điểm kết hợp
            sorted_indices = sorted(final_scores.keys(), key=lambda x: final_scores[x], reverse=True)

            print(f"\n🔍 [Cross-Encoder] Top-{min(top_k, len(sorted_indices))} tài liệu sau reranking:")
            for rank, idx in enumerate(sorted_indices[:top_k]):
                doc = self.metadata[idx]
                article = doc.get('metadata', {}).get('article', '?')
                law    = doc.get('metadata', {}).get('law_name', '?')[:40]
                score  = final_scores[idx]
                print(f"  [{rank+1}] {article} | {law} | score={score:.4f}")
        else:
            # Nếu chỉ có 1 ứng viên thì trả thẳng, không cần rerank
            sorted_indices = rrf_top_candidates

        # ═══════════════════════════════════════════════════════
        # TRẢ VỀ KẾT QUẢ: top_k=7 tài liệu tốt nhất
        # ═══════════════════════════════════════════════════════
        final_results = [self.metadata[i] for i in sorted_indices[:top_k]]
        return final_results


retrieval_service = RetrievalService()