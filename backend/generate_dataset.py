import os
import json
import re
import pandas as pd
from pypdf import PdfReader
from tqdm import tqdm
from openai import OpenAI
from dotenv import load_dotenv
import time

# Nạp biến môi trường từ file .env
load_dotenv()

# =====================================================================
# HÀM GHI ĐÈ FILE .ENV ĐỂ TỰ ĐỘNG COMMENT (COMMIT) LẠI KEY HẾT HẠN
# =====================================================================
def disable_key_in_env(var_name):
    # Tìm đường dẫn đến file .env ở cùng thư mục với file script này
    base_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(base_dir, ".env")
    
    if not os.path.exists(env_path):
        return
    
    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    updated = False
    for i, line in enumerate(lines):
        # Kiểm tra xem dòng đó có chứa biến tương ứng không (Ví dụ: OPENROUTER_API_KEY_1=)
        if line.strip().startswith(f"{var_name}="):
            # Thực hiện "commit" tự động bằng cách biến dòng đó thành bình luận (comment)
            lines[i] = f"# {line.strip()} # HẾT TOKEN HOẶC LỖI\n"
            updated = True
            break
            
    if updated:
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"📝 [HỆ THỐNG] Đã tự động comment lại và vô hiệu hóa biến {var_name} ngay trong file .env!")

# =====================================================================
# CLASS QUẢN LÝ XOAY VÒNG CÁC BIẾN API KEY ĐỘC LẬP (KEY_1, KEY_2, KEY_3...)
# =====================================================================
class APIKeyRotator:
    def __init__(self):
        self.keys = [] # Lưu danh sách tuple dưới dạng: [(TÊN_BIẾN, GIÁ_TRỊ_KEY)]
        self.current_index = 0
        
        # Quét tuần tự các biến từ OPENROUTER_API_KEY_1, _2, _3 cho đến khi không tìm thấy nữa
        i = 1
        while True:
            var_name = f"OPENROUTER_API_KEY_{i}"
            key_val = os.getenv(var_name)
            if not key_val:
                break
            self.keys.append((var_name, key_val.strip()))
            i += 1
            
        # Phương án dự phòng nếu bạn vẫn để 1 biến duy nhất là OPENROUTER_API_KEY
        if not self.keys:
            fallback_key = os.getenv("OPENROUTER_API_KEY")
            if fallback_key:
                self.keys.append(("OPENROUTER_API_KEY", fallback_key.strip()))
        
        if not self.keys:
            raise ValueError("❌ Lỗi: Không tìm thấy bất kỳ biến API Key nào (OPENROUTER_API_KEY_1, _2...) trong file .env!")
        
        print(f"🔑 Hệ thống khởi tạo thành công: Đã tìm thấy {len(self.keys)} API Keys độc lập.")

    def get_current_key(self):
        if not self.keys:
            return None
        return self.keys[self.current_index][1]

    def handle_expired_key(self):
        if not self.keys:
            return False
        
        var_name, _ = self.keys[self.current_index]
        print(f"\n⚠️ Biến {var_name} bị lỗi hoặc hết hạn.")
        
        # 1. Tự động commit/comment lại dòng key đó trực tiếp trong file .env
        disable_key_in_env(var_name)
        
        # 2. Xóa key hỏng này ra khỏi danh sách đang chạy trong bộ nhớ RAM
        self.keys.pop(self.current_index)
        
        if len(self.keys) == 0:
            print("\n❌ [CẢNH BÁO] Toàn bộ danh sách API Keys của bạn đã cạn kiệt hoặc bị lỗi!")
            return False
            
        # Điều chỉnh lại chỉ mục index sau khi xóa 1 phần tử của mảng
        if self.current_index >= len(self.keys):
            self.current_index = 0
            
        print(f"🔄 Đã chuyển sang sử dụng biến dự phòng tiếp theo: {self.keys[self.current_index][0]}")
        return True

    def get_total_keys(self):
        return len(self.keys)


# Khởi tạo bộ xoay vòng Key tách biệt
rotator = APIKeyRotator()

# Khởi tạo Client mặc định với Key đầu tiên khả dụng
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=rotator.get_current_key(),
)

# Giữ nguyên mô hình lớn ban đầu bạn chọn
ONLINE_MODEL = "meta-llama/llama-3.3-70b-instruct" 

def extract_and_chunk_pdf(pdf_path, chunk_size=1000, overlap=100):
    print(f"Đang đọc file PDF: {os.path.basename(pdf_path)}...")
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    print(f"-> Đã tạo được {len(chunks)} đoạn văn bản (chunks).")
    return chunks

def generate_qa_pairs_online(chunk, file_name):
    law_name = file_name.replace(".pdf", "").replace("_", " ")

    prompt = f"""
    Bạn là chuyên gia pháp lý cao cấp. Đọc đoạn luật từ {law_name} và tạo 2 cặp QA phục vụ đánh giá hệ thống RAG chuyên ngành.
    
    YÊU CẦU CÁC TRƯỜNG DỮ LIỆU:
    1. QUESTION: Câu hỏi tình huống thực tế của người dân.
    2. CONTEXT: Đoạn luật gốc đã được sửa sạch lỗi chính tả khoảng trắng.
    3. GROUND_TRUTH: Câu trả lời tư vấn hoàn chỉnh, chuẩn xác từ chuyên gia có trích dẫn điều luật rõ ràng làm đáp án gốc.
    4. KEYWORDS: Trích xuất 3-5 từ khóa pháp lý quan trọng nhất có trong câu trả lời chuyên gia.
    5. CONTEXT_ANSWER: Câu trả lời do Chatbot sinh ra dựa trên câu hỏi và đoạn ngữ cảnh này.

    Đoạn luật:
    "{chunk}"

    CHỈ TRẢ VỀ DUY NHẤT LỚP MẢNG JSON HỢP LỆ THEO ĐỊNH DẠNG SAU, KHÔNG VIẾT LỜI MỞ ĐẦU, KHÔNG GIẢI THÍCH GÌ THÊM:
    [
        {{
            "question": "...",
            "context": "...",
            "ground_truth": "...",
            "keywords": ["từ khóa 1", "từ khóa 2", "từ khóa 3"],
            "context_answer": "..."
        }}
    ]
    """
    
    while rotator.get_total_keys() > 0:
        try:
            current_key = rotator.get_current_key()
            if not current_key:
                return []
                
            client.api_key = current_key
            
            response = client.chat.completions.create(
                model=ONLINE_MODEL,
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.0,
                max_tokens=3000  # <--- ĐÃ TĂNG LÊN 3000 ĐỂ AI KHÔNG BỊ ĐỨT HƠI GIỮA CHỪNG
            )
            
            raw_content = response.choices[0].message.content
            if not raw_content or not raw_content.strip():
                continue
                
            # Tiền xử lý dữ liệu đầu vào chuỗi văn bản
            text_clean = raw_content.strip()
            text_clean = re.sub(r'^```json\s*', '', text_clean, flags=re.IGNORECASE)
            text_clean = re.sub(r'^```\s*', '', text_clean)
            text_clean = re.sub(r'\s*```$', '', text_clean).strip()
                
            # =====================================================================
            # BỘ TRÍCH XUẤT SỬA LỖI ĐỘC QUYỀN CHỐNG LỖI "EXPECTING VALUE: LINE 1"
            # =====================================================================
            json_array_match = re.search(r'\[\s*\{.*\}\s*\]', text_clean, re.DOTALL)
            
            if json_array_match:
                cleaned_content = json_array_match.group(0)
            else:
                json_dict_match = re.search(r'\{.*\}', text_clean, re.DOTALL)
                if json_dict_match:
                    cleaned_content = "[" + json_dict_match.group(0) + "]"
                else:
                    cleaned_content = text_clean
            
            cleaned_content = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', cleaned_content)
            
            qa_pairs = json.loads(cleaned_content, strict=False)
            if isinstance(qa_pairs, dict): 
                qa_pairs = [qa_pairs]
                
            return qa_pairs
            
        except json.JSONDecodeError as json_err:
            print(f"\n⚠️ Phát hiện lỗi cấu trúc phản hồi văn bản của {ONLINE_MODEL}: {json_err}")
            print("--- ĐOẠN TIN AI SINH BỊ TRÀO CHỮ THUẦN (RÁC HỘI THOẠI) ---")
            print(raw_content[:300])
            print("----------------------------------------------------------------")
            print("🔄 [TỰ ĐỘNG] Hệ thống bỏ qua chunk lỗi này để chuyển sang nạp đoạn tiếp theo...")
            return []
            
        except Exception as e:
            err_str = str(e).lower()
            if any(code in err_str for code in ["401", "402", "429", "credit", "rate_limit", "payment"]):
                success = rotator.handle_expired_key()
                if not success:
                    return []
                time.sleep(1.5)
                continue 
            else:
                print(f"⚠️ Lỗi phát sinh hệ thống: {e}")
                return []
                
    return []

def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(BASE_DIR, "data")
    if not os.path.exists(data_dir): 
        print(f"❌ Lỗi: Không tìm thấy thư mục {data_dir}")
        return

    pdf_files = [f for f in os.listdir(data_dir) if f.endswith('.pdf')]
    if not pdf_files:
        print("⚠️ Không có file PDF nào trong thư mục data.")
        return

    dataset = []
    output_csv = os.path.join(BASE_DIR, "golden_dataset_luat_1.csv")
    
    print(f"🚀 Khởi chạy hệ thống tự động sinh dataset với mô hình {ONLINE_MODEL}...")
    
    for filename in pdf_files:
        pdf_path = os.path.join(data_dir, filename)
        chunks = extract_and_chunk_pdf(pdf_path)
        
        for chunk in tqdm(chunks, desc=f"Sinh QA cho {filename}"): 
            if len(chunk.strip()) < 200: continue
            
            qa_pairs = generate_qa_pairs_online(chunk, filename)
            
            if qa_pairs:
                for pair in qa_pairs:
                    dataset.append({
                        "question": pair.get("question", ""),
                        "context": pair.get("context", ""),
                        "ground_truth": pair.get("ground_truth", ""),
                        "keywords": ", ".join(pair.get("keywords", [])),
                        "context_answer": pair.get("context_answer", "")
                    })
                
                df = pd.DataFrame(dataset)
                df.to_csv(output_csv, index=False, encoding="utf-8-sig")
            
            time.sleep(1.2) 
            
    print(f"\n✅ HOÀN THÀNH XUẤT SẮC! Dữ liệu đã được lưu trữ an toàn tại: {output_csv}")

if __name__ == "__main__":
    main()