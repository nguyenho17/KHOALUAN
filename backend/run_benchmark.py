import os
import json
import re
import pandas as pd
from tqdm import tqdm
import requests
import time

# URL chính xác dựa theo cấu trúc cổng backend của bạn
API_URL = "http://127.0.0.1:8000/api/chat"

def clean_citation_string(text):
    """
    Hàm xử lý triệt để lỗi vỡ font hoặc nhân bản chuỗi như 'Điều Điều ...' thành 'Điều ...'
    """
    if not text or pd.isna(text):
        return "N/A"
    text_str = str(text).strip()
    # Sử dụng biểu thức chính quy để gom cụm các chữ 'Điều' bị lặp lại liên tiếp
    text_str = re.sub(r'(Điều\s+){2,}', 'Điều ', text_str)
    text_str = re.sub(r'(điều\s+){2,}', 'điều ', text_str)
    return text_str

def ask_my_chatbot(question):
    """
    Hàm gửi request theo chuẩn định dạng Schema ChatRequest (POST) trong hệ thống
    """
    try:
        payload = {
            "question": question,
            "session_id": "benchmark_session"
        }
        
        response = requests.post(API_URL, json=payload, timeout=90)
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "")
            citations = data.get("citations", [])
            
            # Khôi phục hoặc bóc tách trường ngữ cảnh phục vụ phép đo @5 nếu backend trả về
            contexts = data.get("contexts", "")
            if isinstance(contexts, list):
                contexts_str = "\n".join(contexts)
            else:
                contexts_str = str(contexts) if contexts else ""
                
            citations_str = ", ".join(citations) if citations else "N/A"
            # Làm sạch chuỗi trích dẫn ngay tại tầng thu nhận đầu vào
            citations_str = clean_citation_string(citations_str)
            
            return answer, citations_str, contexts_str
        else:
            return f"[Lỗi API] HTTP Status: {response.status_code}", "N/A", ""
            
    except requests.exceptions.Timeout:
        return "[Lỗi Hệ Thống] Quá thời gian phản hồi (Timeout > 90s)", "N/A", ""
    except Exception as e:
        return f"[Lỗi Kết Nối] Không thể gọi FastAPI: {str(e)}", "N/A", ""

def main():
    input_file = "benchmark_hngd.xlsx"
    output_file = "benchmarkss.xlsx"
    checkpoint_file = "benchmark_checkpoint.xlsx"

    try:
        print(f"[*] Đang tiến hành đọc tập dữ liệu gốc từ tệp: {input_file}")
        df = pd.read_excel(input_file)
    except Exception as e:
        print(f"[Lỗi] Không thể mở file {input_file}. Chi tiết: {e}")
        return

    chatbot_answers = []
    chatbot_citations = []
    retrieved_contexts = []

    print("\n[*] Bắt đầu khởi chạy tự động Benchmark hệ thống RAG++...")
    print(f"[!] Tổng số tình huống pháp lý cần giải nghĩa: {len(df)} câu.")
    
    for i, question in enumerate(tqdm(df['question'], desc="Tiến độ đánh giá")):
        answer, citations, contexts = ask_my_chatbot(question)
        
        chatbot_answers.append(answer)
        chatbot_citations.append(citations)
        retrieved_contexts.append(contexts)
        
        # Chiến lược lưu cuốn chiếu checkpoint phòng ngừa sự cố máy tính
        if (i + 1) % 10 == 0 or (i + 1) == len(df):
            df_temp = df.iloc[:len(chatbot_answers)].copy()
            df_temp['answer'] = chatbot_answers
            df_temp['chatbot_answer'] = chatbot_answers
            df_temp['chatbot_citations'] = chatbot_citations
            df_temp['contexts_answer'] = retrieved_contexts
            try:
                df_temp.to_excel(checkpoint_file, index=False)
            except Exception:
                df_temp.to_csv("benchmark_checkpoint.csv", index=False, encoding='utf-8-sig')

        time.sleep(0.2)

    # Đính kết quả đồng bộ vào DataFrame chính theo đúng Schema yêu cầu
    df['chatbot_answer'] = chatbot_answers
    df['answer'] = chatbot_answers
    df['chatbot_citations'] = chatbot_citations
    df['contexts_answer'] = retrieved_contexts
    
    # Thiết lập cột ngữ cảnh chuẩn của Ground Truth dựa trên nội dung luật gốc có sẵn
    df['context_ground_truth'] = df.get('law_content', df.get('ground_truth', ''))

    # Kiểm tra và tự động bổ sung cột keywords từ khóa pháp lý nếu file gốc thiếu sót
    if 'keywords' not in df.columns:
        auto_keywords = []
        for _, row in df.iterrows():
            q = str(row['question']).lower()
            gt = str(row.get('ground_truth', '')).lower()
            kws = []
            if "ly hôn" in q or "ly hôn" in gt: kws.append("ly hôn")
            if "nuôi con" in q or "nuôi con" in gt: kws.append("quyền nuôi con")
            if "tài sản" in q or "tài sản" in gt: kws.append("tài sản chung")
            if "cấp dưỡng" in q or "cấp dưỡng" in gt: kws.append("cấp dưỡng")
            if "kết hôn" in q or "kết hôn" in gt: kws.append("kết hôn")
            auto_keywords.append(", ".join(kws) if kws else "luật hôn nhân, gia đình")
        df['keywords'] = auto_keywords

    # Sắp xếp và lọc chính xác các cột đầu ra theo đúng thứ tự cấu trúc nhóm yêu cầu
    target_columns = [
        'question', 'law_content', 'law_id', 'law_name', 
        'chatbot_answer', 'chatbot_citations', 'keywords', 
        'ground_truth', 'answer', 'contexts_answer', 'context_ground_truth'
    ]
    
    # Giữ lại các cột đích, nếu cột nào không tồn tại thì tự khởi tạo rỗng để tránh lỗi sập luồng
    for col in target_columns:
        if col not in df.columns:
            df[col] = ""
            
    df_final_output = df[target_columns]

    print(f"\n[*] Đang kết xuất dữ liệu cấu trúc sạch ra file: {output_file}")
    try:
        df_final_output.to_excel(output_file, index=False)
        print(f"[✓] QUÁ TRÌNH HOÀN THÀNH KHOA HỌC! Tập tệp lưu tại: {output_file}")
        if os.path.exists(checkpoint_file): os.remove(checkpoint_file)
    except PermissionError:
        timestamp = int(time.time())
        emergency_file = f"benchmark_URGENT_SAVE_{timestamp}.xlsx"
        df_final_output.to_excel(emergency_file, index=False)
        print(f"[✓] FILE BỊ KHÓA - ĐÃ CỨU DỮ LIỆU SANG FILE DỰ PHÒNG: {emergency_file}")
    except Exception as e:
        df_final_output.to_csv("benchmark_final_error_backup.csv", index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    main()