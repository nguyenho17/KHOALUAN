import os
import re
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
import time

# 1. Tự động tìm và nạp các biến từ file .env
load_dotenv()

# =====================================================================
# HÀM TỰ ĐỘNG COMMENT (COMMIT) LẠI KEY HẾT HẠN TRÊN WEB SERVER
# =====================================================================
def disable_key_in_env(var_name):
    # Định vị file .env bằng cách quét ngược từ thư mục con lên thư mục gốc dự án
    current_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = None
    for _ in range(4):  # Quét tối đa 4 cấp cha để tìm chính xác file .env của backend
        possible_path = os.path.join(current_dir, ".env")
        if os.path.exists(possible_path):
            env_path = possible_path
            break
        current_dir = os.path.dirname(current_dir)
        
    if not env_path or not os.path.exists(env_path):
        return
    
    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    updated = False
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{var_name}="):
            lines[i] = f"# {line.strip()} # HẾT TOKEN HOẶC LỖI TRÊN WEB\n"
            updated = True
            break
            
    if updated:
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"📝 [WEB SERVER] Đã tự động comment vô hiệu hóa biến {var_name} trong file .env!")

# =====================================================================
# CLASS QUẢN LÝ XOAY VÒNG KEY ĐỘC LẬP CHO HỆ THỐNG FASTAPI
# =====================================================================
class APIKeyRotator:
    def __init__(self):
        self.keys = []  # Lưu danh sách tuple: [(TÊN_BIẾN, GIÁ_TRỊ_KEY)]
        self.current_index = 0
        
        # SỬA LỖI TẠI ĐÂY: Thay thế vòng lặp while dễ bị ngắt bằng vòng lặp quét diện rộng từ 1 đến 50
        # Cơ chế này giúp nạp chính xác các key_3, key_4, key_5 kể cả khi không có key_1 và key_2
        for i in range(1, 51):
            var_name = f"OPENROUTER_API_KEY_{i}"
            key_val = os.getenv(var_name)
            if key_val and key_val.strip():
                self.keys.append((var_name, key_val.strip()))
        
        # Phương án dự phòng nếu file .env của bạn đang để biến đơn lẻ dạng KEY_2 hoặc OPENROUTER_API_KEY
        if not self.keys:
            for alt_name in ["OPENROUTER_API_KEY_2", "OPENROUTER_API_KEY"]:
                fallback_key = os.getenv(alt_name)
                if fallback_key:
                    self.keys.append((alt_name, fallback_key.strip()))
                    break
        
        if not self.keys:
            print("⚠️ CẢNH BÁO: Hệ thống chưa nạp được API Key nào từ file .env!")
        else:
            print(f"🔑 [GENERATION SERVICE] Khởi tạo thành công: Đã tìm thấy {len(self.keys)} API Keys khả dụng.")

    def get_current_key(self):
        if not self.keys:
            return None
        return self.keys[self.current_index][1]

    def handle_expired_key(self):
        if not self.keys:
            return False
        
        var_name, _ = self.keys[self.current_index]
        print(f"\n⚠️ Biến {var_name} cạn kiệt token hoặc dính lỗi nghẽn băng thông trên Web App.")
        
        # Thực hiện đóng dấu comment trực tiếp vào file .env vật lý
        disable_key_in_env(var_name)
        
        # Xóa key lỗi ra khỏi bộ nhớ đệm RAM hiện tại của FastAPI
        self.keys.pop(self.current_index)
        
        if len(self.keys) == 0:
            print("\n❌ [NGUY CẤP] Toàn bộ danh sách API Keys dự phòng trên hệ thống đã cạn kiệt hoàn toàn!")
            return False
            
        if self.current_index >= len(self.keys):
            self.current_index = 0
            
        print(f"🔄 Web Server chuyển sang sử dụng biến dự phòng tiếp theo: {self.keys[self.current_index][0]}")
        return True

    def get_total_keys(self):
        return len(self.keys)


# Khởi tạo bộ xoay vòng Key chuyên dụng
rotator = APIKeyRotator()

# 3. Khởi tạo Client an toàn (Sử dụng chuỗi dự phòng để Uvicorn không bị crash lúc khởi động)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=rotator.get_current_key() or "EMPTY_KEY_FALLBACK",
)

class GenerationService:
    def __init__(self):
        # 🛠️ Chuyển đổi sang mô hình Llama 3.3 70B Instruct tốc độ cao và lập luận đanh thép
        self.model_name = "meta-llama/llama-3.3-70b-instruct"
        
    def generate_answer(self, question: str, retrieved_docs: list, history: list = None):
        context_items = []
        for doc in retrieved_docs:
            article = doc['metadata'].get('article', 'Không rõ')
            law_name_raw = doc['metadata'].get('law_name', 'Văn bản pháp luật')
            clean_law_name = re.sub(r'\b\d{5,}\b', '', law_name_raw).strip()
            year = doc['metadata'].get('year', 'Chưa rõ năm')
            content = doc['content']
            context_items.append(f"[{clean_law_name} (Năm {year}) - {article}]:\n{content}")
        
        context_text = "\n\n".join(context_items)

        # === ĐOẠN NÀY ĐỂ HIỆN TRONG TERMINAL (QUAN TRỌNG) ===
        print("\n" + "="*50)
        print("🔍 TÀI LIỆU RAG TRUY XUẤT ĐƯỢC TỪ DATABASE:")
        print("="*50)
        if not context_text:
            print("⚠️ KHÔNG CÓ DỮ LIỆU NÀO ĐƯỢC TRUY XUẤT!")
        else:
            print(context_text)
        print("="*50 + "\n")
        # =================================================

        # Xây dựng phần lịch sử hội thoại (multi-turn context)
        history_section = ""
        if history:
            history_lines = []
            for turn in history[-5:]:  # Chỉ lấy tối đa 5 lượt gần nhất
                q = turn.get('question', '')
                a = turn.get('answer', '')
                if q and a:
                    history_lines.append(f"Người dùng: {q}")
                    history_lines.append(f"Hệ thống: {a[:300]}...")  # Cắt ngắn tránh vượt context window
            if history_lines:
                history_section = (
                    "\n        LỊCH SỬ HỘI THOẠI TRƯỚC (để hiểu ngữ cảnh, KHÔNG lặp lại nội dung này):\n        "
                    + "\n        ".join(history_lines)
                    + "\n"
                )

        # PROMPT NÂNG CAO - YÊU CẦU TRÍCH DẪN ĐẦY ĐỦ SỐ ĐIỀU LUẬT ĐỂ CẢI THIỆN CITATION F1
        prompt = f"""
        Bạn là "Hệ thống Luật sư AI" - Chuyên gia tư vấn pháp luật cao cấp tại Việt Nam.
        Nhiệm vụ: Trình bày bản tư vấn pháp lý chính thống, đanh thép và có tính thuyết phục cao.

        YÊU CẦU VỀ ĐỊNH DẠNG:
        1. Tuyệt đối KHÔNG sử dụng các ký tự ngăn cách như "---", "===", hoặc dấu sao (*).
        2. Sử dụng VIẾT HOA các tiêu đề mục (PHẦN I, PHẦN II...) để phân tách không gian văn bản.
        3. Văn bản trình bày thuần túy, xuống dòng rõ ràng, mạch lạc giữa các đoạn văn.
        4. Mỗi luận điểm trong phần phân tích phải bắt đầu bằng số thứ tự (1. 2. 3.).
        5. TUYỆT ĐỐI KHÔNG in ra quá trình suy nghĩ (thinking process/scratchpad) hay bất kỳ văn bản tiếng Anh nào. CHỈ in ra kết quả tư vấn tiếng Việt cuối cùng bắt đầu bằng chữ "PHẦN I".

        CẤU TRÚC VĂN BẢN (BẮT BUỘC):
        PHẦN I: LỜI CHÀO VÀ XÁC NHẬN VẤN ĐỀ
        Xác nhận lại tình huống của khách hàng một cách thấu cảm và chuyên nghiệp.

        PHẦN II: CĂN CỨ PHÁP LÝ ÁP DỤNG
        [QUAN TRỌNG] Liệt kê ĐẦY ĐỦ và CHÍNH XÁC TẤT CẢ số hiệu Điều luật từ DANH SÁCH CĂN CỨ PHÁP LÝ bên dưới áp dụng cho tình huống này.
        Mỗi điều luật phải ghi đúng theo định dạng: "Điều X - [Tên văn bản pháp luật]".
        Ví dụ: "Điều 51 - Luật Hôn nhân và Gia đình 2014", "Điều 3 - Nghị quyết 01/2024/NQ-HĐTP".
        KHÔNG được bỏ sót bất kỳ Điều luật nào có trong DANH SÁCH CĂN CỨ PHÁP LÝ liên quan đến câu hỏi.

        PHẦN III: PHÂN TÍCH VÀ NỘI DUNG TƯ VẤN CHI TIẾT
        Sử dụng kỹ năng lập luận logic để giải quyết vấn đề. Phải phân tích rõ:
        - Bản chất pháp lý của tài sản/sự việc.
        - Mối quan hệ giữa căn cứ pháp luật và thực tế của khách hàng.
        - Kết luận đúng/sai hoặc chung/riêng một cách đanh thép.
        Trong phần này, khi nhắc đến điều luật phải viết đầy đủ số điều, ví dụ: "theo Điều 58 Luật Hôn nhân và Gia đình".

        PHẦN IV: LỜI KHUYÊN PHÁP LÝ VÀ KẾT LUẬN
        Đưa ra các bước hành động cụ thể để bảo vệ quyền lợi tối đa cho khách hàng.

        LƯU Ý KỶ LUẬT:
        - Chỉ tư vấn dựa trên "DANH SÁCH CĂN CỨ PHÁP LÝ" cung cấp bên dưới.
        - Nếu dữ liệu không đủ để kết luận, phải dùng MẪU TỪ CHỐI: "Dựa trên các quy định pháp luật được tra cứu hiện tại, hệ thống chưa có đủ thông tin để trả lời chính xác vấn đề này."
        {history_section}
        --- DANH SÁCH CĂN CỨ PHÁP LÝ ---
        {context_text}

        --- CÂU HỎI HIỆN TẠI CỦA NGƯỜI DÙNG ---
        "{question}"
        """

        
        # 🔄 LUỒNG TỰ ĐỘNG XOAY KEY VÀ RE-TRY TRỰC TIẾP KHI NGƯỜI DÙNG CHAT TRÊN GIAO DIỆN INTERFACE
        while rotator.get_total_keys() > 0:
            try:
                current_key = rotator.get_current_key()
                if not current_key:
                    return "Hệ thống phản hồi: Hiện tại không tìm thấy API Key khả dụng để xử lý yêu cầu."
                
                # Cập nhật chìa khóa mới cho luồng gọi hiện hành
                client.api_key = current_key
                
                response = client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0
                )
                
                answer = response.choices[0].message.content
                return answer.replace("*", "").strip()
                
            except Exception as e:
                err_str = str(e).lower()
                # Định vị chính xác nhóm mã lỗi tài khoản (401, 402, 429) để kích hoạt cơ chế xoay key bảo hiểm
                if any(code in err_str for code in ["401", "402", "429", "credit", "rate_limit", "payment"]):
                    success = rotator.handle_expired_key()
                    if not success:
                        return "Hệ thống phản hồi: Toàn bộ hạn mức API Key dự phòng của dịch vụ đã cạn kiệt. Vui lòng liên hệ quản trị viên."
                    time.sleep(1.0)
                    continue  # Quay ngược lại đầu vòng lặp để thực thi lại câu hỏi bằng Key mới
                else:
                    return f"Lỗi hệ thống sinh văn bản (OpenRouter API): {str(e)}"
                    
        return "Hệ thống phản hồi: Không tìm thấy tài nguyên API thích hợp để phản hồi câu hỏi này."

# Khởi tạo dịch vụ
generation_service = GenerationService()