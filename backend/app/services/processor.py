import os
import re
import time
from app.services.generation import client, rotator, _KEY_ERRORS, _TRANSIENT_ERRORS, MAX_TRANSIENT_RETRIES

# Sử dụng mô hình meta-llama/llama-3.3-70b-instruct để phân loại và viết lại câu hỏi tốc độ cao
MODEL_NAME = "meta-llama/llama-3.3-70b-instruct"

# =====================================================================
# PHÁT HIỆN LỜI CHÀO / SMALL TALK (Không cần gọi LLM, tiết kiệm API)
# =====================================================================
_GREETING_PATTERNS = re.compile(
    r"^("
    # Lời chào tiếng Việt
    r"xin\s*chào|chào\s*(bạn|anh|chị|em|mọi\s*người|buổi\s*(sáng|trưa|chiều|tối))|"
    r"hi|hello|hey|helo|hê\s*l+ô|"
    r"alo|ờ|ừ|uh|"
    r"good\s*(morning|afternoon|evening|night)|"
    r"chào\s*buổi|buổi\s*(sáng|trưa|chiều|tối)\s*(anh|chị|bạn|em)?|"
    # Hỏi thăm
    r"bạn\s*(có\s*)?(khỏe|ổn)\s*(không|ko|k)?|"
    r"(bạn|anh|chị)\s*(là|tên)\s*(gì|ai|nào)?|"
    r"how\s+are\s+you|what'?s?\s+up|"
    # Bắt đầu cuộc trò chuyện
    r"xin\s*hỏi$|cho\s*hỏi$|"
    r"cảm\s*ơn|thank(s|\s+you)?|cám\s*ơn|"
    r"ok(ay)?$|được\s*rồi$|hiểu\s*rồi$|"
    r"tạm\s*biệt|bye|goodbye"
    r")[\s!?.]*$",
    re.IGNORECASE | re.UNICODE
)

def is_greeting(query: str) -> bool:
    """
    Phát hiện nhanh lời chào hỏi và small talk bằng regex thuần Python.
    Trả về True nếu là lời chào (không cần gọi LLM).
    """
    if not query or not query.strip():
        return False
    text = query.strip()
    # Nếu quá ngắn (≤ 3 từ) → kiểm tra với pattern
    if len(text.split()) <= 3 and _GREETING_PATTERNS.search(text):
        return True
    # Kiểm tra toàn chuỗi với pattern
    if _GREETING_PATTERNS.match(text):
        return True
    return False


def is_out_of_scope(query: str) -> bool:
    """
    Kiểm tra xem câu hỏi có thuộc phạm vi Luật Hôn nhân và Gia đình Việt Nam hay không.
    Trả về True nếu ngoài phạm vi (Out of scope), False nếu đúng phạm vi (In scope).
    """
    if not query or not query.strip():
        return True

    prompt = f"""
    Bạn là bộ phân loại câu hỏi pháp lý chuyên nghiệp tại Việt Nam.
    Nhiệm vụ: Hãy xác định xem câu hỏi của người dùng dưới đây có liên quan đến chủ đề Luật Hôn nhân và Gia đình Việt Nam (như thủ tục đăng ký kết hôn, kết hôn cận huyết, đơn phương/thuận tình ly hôn, quyền nuôi con, tranh chấp chia tài sản chung/riêng vợ chồng, nghĩa vụ cấp dưỡng nuôi con/cha mẹ, quan hệ nhân thân giữa vợ chồng, di chúc thừa kế gia đình, kết hôn có yếu tố nước ngoài...) hay không.

    Câu hỏi của người dùng: "{query}"

    Quy tắc phân loại:
    - Trả về "IN_SCOPE" nếu câu hỏi liên quan đến chủ đề Luật Hôn nhân và Gia đình Việt Nam.
    - Trả về "OUT_OF_SCOPE" nếu câu hỏi liên quan đến các ngành luật khác (như hình sự, doanh nghiệp, thuế, lao động, giao thông, hành chính...) hoặc là câu hỏi trò chuyện phiếm, lập trình, nấu ăn, sức khỏe, khoa học... không thuộc phạm vi pháp lý gia đình.

    Yêu cầu định dạng: Chỉ trả về duy nhất một từ "IN_SCOPE" hoặc "OUT_OF_SCOPE". Tuyệt đối không giải thích hay thêm bớt bất kỳ từ nào khác.
    """
    
    transient_retries = 0

    while rotator.get_total_keys() > 0:
        try:
            current_key = rotator.get_current_key()
            if not current_key:
                break
            client.api_key = current_key
            
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=10
            )
            
            res_text = response.choices[0].message.content
            if not res_text or not res_text.strip():
                raise ValueError("empty response from API")
            res_text = res_text.strip().upper()
            print(f"👁️ [Out-of-scope Classifier] Phản hồi từ LLM: '{res_text}'")
            if "OUT_OF_SCOPE" in res_text:
                return True
            return False
            
        except Exception as e:
            err_str = str(e).lower()

            # 1️⃣ Lỗi key hết hạn / quota → xoay key
            if any(code in err_str for code in _KEY_ERRORS):
                success = rotator.handle_expired_key()
                if not success:
                    break
                time.sleep(1.0)
                transient_retries = 0
                continue

            # 2️⃣ Lỗi tạm thời (JSON parse, timeout, connection) → retry với delay tăng dần
            elif any(code in err_str for code in _TRANSIENT_ERRORS):
                transient_retries += 1
                wait_sec = transient_retries * 2.0
                print(f"⚠️ [OOS Classifier] Lỗi tạm thời lần {transient_retries}/{MAX_TRANSIENT_RETRIES}: {str(e)[:100]}")
                print(f"   → Retry sau {wait_sec:.0f}s...")
                if transient_retries >= MAX_TRANSIENT_RETRIES:
                    print("❌ [OOS Classifier] Đã retry tối đa, bỏ qua kiểm tra scope.")
                    break
                time.sleep(wait_sec)
                continue

            # 3️⃣ Lỗi không xác định
            else:
                print(f"⚠️ [OOS Classifier] Lỗi không xác định: {e}")
                break

    # Mặc định IN_SCOPE để tránh chặn oan câu hỏi người dùng khi API lỗi
    return False


def reformulate_query(query: str) -> str:
    """
    Viết lại câu hỏi thô thành câu truy vấn từ khóa pháp lý chuẩn để tối ưu hóa tìm kiếm FAISS & BM25.
    """
    if not query or not query.strip():
        return query

    # Nếu câu hỏi quá dài (ví dụ là một bài phân tích dài) thì giữ nguyên để tránh mất chi tiết
    if len(query.strip()) > 150:
        return query
        
    prompt = f"""
    Bạn là một trợ lý pháp lý chuyên nghiệp tại Việt Nam.
    Nhiệm vụ: Hãy viết lại câu hỏi ngắn, mang tính văn nói của người dùng dưới đây thành một câu truy vấn tìm kiếm ngắn gọn, chứa các từ khóa pháp lý chính xác của Luật Hôn nhân và Gia đình Việt Nam để phục vụ việc tra cứu cơ sở dữ liệu luật.

    Ví dụ:
    - "ly hôn cần những gì" -> "Thủ tục và điều kiện ly hôn theo Luật Hôn nhân và Gia đình"
    - "cho con bao nhiêu tiền một tháng" -> "Nghĩa vụ cấp dưỡng và mức cấp dưỡng nuôi con sau ly hôn"
    - "muốn chia đất khi ly hôn" -> "Phân chia tài sản chung là quyền sử dụng đất khi ly hôn"

    Câu hỏi gốc: "{query}"

    Yêu cầu: Chỉ trả về câu truy vấn được viết lại cuối cùng. Tuyệt đối không thêm lời dẫn, không giải thích gì thêm.
    """
    
    transient_retries = 0

    while rotator.get_total_keys() > 0:
        try:
            current_key = rotator.get_current_key()
            if not current_key:
                break
            client.api_key = current_key
            
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=60
            )
            
            res_text = response.choices[0].message.content
            if not res_text or not res_text.strip():
                raise ValueError("empty response from API")
            res_text = res_text.strip()
            # Loại bỏ dấu ngoặc kép nếu LLM tự động thêm vào
            res_text = re.sub(r'^["\']|["\']$', '', res_text)
            return res_text
            
        except Exception as e:
            err_str = str(e).lower()

            # 1️⃣ Lỗi key hết hạn / quota → xoay key
            if any(code in err_str for code in _KEY_ERRORS):
                success = rotator.handle_expired_key()
                if not success:
                    break
                time.sleep(1.0)
                transient_retries = 0
                continue

            # 2️⃣ Lỗi tạm thời → retry với delay tăng dần
            elif any(code in err_str for code in _TRANSIENT_ERRORS):
                transient_retries += 1
                wait_sec = transient_retries * 2.0
                print(f"⚠️ [Reformulate] Lỗi tạm thời lần {transient_retries}/{MAX_TRANSIENT_RETRIES}: {str(e)[:100]}")
                print(f"   → Retry sau {wait_sec:.0f}s...")
                if transient_retries >= MAX_TRANSIENT_RETRIES:
                    print("❌ [Reformulate] Đã retry tối đa, dùng câu hỏi gốc.")
                    break
                time.sleep(wait_sec)
                continue

            # 3️⃣ Lỗi không xác định
            else:
                print(f"⚠️ [Reformulate] Lỗi không xác định: {e}")
                break

    # Mặc định trả về câu hỏi gốc nếu lỗi API
    return query