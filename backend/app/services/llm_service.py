import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Nạp API Key từ file .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# 2. Cấu hình Google Gemini
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("⚠️ CẢNH BÁO: Chưa có GEMINI_API_KEY trong file .env")

def generate_legal_answer(context, question):
    # Sử dụng model gemini-1.5-flash để tốc độ trả lời nhanh nhất
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Prompt tinh chỉnh cực mạnh để chống bịa đặt và đảm bảo tính chính xác
    prompt = f"""
    Bạn là "Luật sư AI" chuyên nghiệp tại Việt Nam. 
    Nhiệm vụ của bạn là tư vấn cho người dùng CHỈ DỰA VÀO Căn cứ pháp lý được cung cấp.

    DANH SÁCH CĂN CỨ PHÁP LÝ: 
    {context}

    CÂU HỎI CỦA NGƯỜI DÙNG: 
    {question}

    YÊU CẦU BẮT BUỘC (QUY TẮC KỶ LUẬT):
    1. VĂN PHONG: Trả lời bằng văn bản thuần túy, KHÔNG DÙNG DẤU SAO (*), KHÔNG DÙNG Markdown, KHÔNG IN ĐẬM.
    2. CẤU TRÚC: Dùng số thứ tự 1. 2. 3. để liệt kê các luận điểm pháp lý.
    3. ƯU TIÊN LUẬT MỚI: Nếu trong căn cứ pháp lý có nhiều văn bản khác năm, bạn PHẢI lấy số liệu từ văn bản có NĂM BAN HÀNH MỚI NHẤT.
    4. CẤM BỊA ĐẶT: 
       - Tuyệt đối copy chính xác 100% mức tiền phạt từ tài liệu. 
       - Không tự ý chế tên Luật hay Nghị định. 
       - Nếu tài liệu không ghi mức phạt, hãy nói: "Tài liệu hiện tại chưa cung cấp mức phạt cụ thể cho hành vi này."
    5. THẤU CẢM: Nếu câu hỏi liên quan đến tình huống nhạy cảm (mang thai, trẻ em, bạo lực), hãy kết thúc bằng một lời nhắn nhủ thấu cảm "LỜI KHUYÊN TỪ LUẬT SƯ AI" ấm áp.
    """
    
    try:
        # Gọi API Gemini
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(temperature=0.1)
        )
        answer = response.text
        
        # Hậu xử lý dọn dẹp các dấu sao thừa (nếu AI quên)
        return answer.replace("*", "").strip()
        
    except Exception as e:
        print(f"Lỗi gọi API: {e}")
        return "Xin lỗi, hệ thống chưa thể xử lý yêu cầu này lúc này do lỗi kết nối API."