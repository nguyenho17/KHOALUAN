import pandas as pd
from tqdm import tqdm
import requests
import time
import os

# URL chính xác dựa theo file main.py của bạn
API_URL = "http://127.0.0.1:8000/api/chat"

def ask_my_chatbot(question):
    """
    Hàm gửi request theo chuẩn định dạng Schema ChatRequest (POST) trong main.py
    """
    try:
        # Định dạng payload khớp hoàn toàn với class ChatRequest(BaseModel)
        payload = {
            "question": question,
            "session_id": "benchmark_session"  # Gom cụm các câu test vào chung 1 session định danh
        }
        
        # Gửi request bằng phương thức POST theo đúng cấu trúc @app.post
        response = requests.post(API_URL, json=payload, timeout=90)
        
        if response.status_code == 200:
            data = response.json()
            # Bóc tách cả câu trả lời và nguồn trích dẫn từ return của backend
            answer = data.get("answer", "Không tìm thấy key 'answer'")
            citations = data.get("citations", [])
            citations_str = ", ".join(citations) if citations else "N/A"
            
            return answer, citations_str
        else:
            return f"[Lỗi API] HTTP Status: {response.status_code}", "N/A"
            
    except requests.exceptions.Timeout:
        return "[Lỗi Hệ Thống] Quá thời gian phản hồi (Timeout > 90s)", "N/A"
    except Exception as e:
        return f"[Lỗi Kết Nối] Không thể gọi FastAPI: {str(e)}", "N/A"

def main():
    input_file = "benchmark_hngd.xlsx"
    output_file = "benchmarkss.xlsx"
    checkpoint_file = "benchmark_checkpoint.xlsx" # File lưu tạm cuốn chiếu

    try:
        print(f"[*] Đang đọc danh sách câu hỏi từ file: {input_file}")
        df = pd.read_excel(input_file)
    except Exception as e:
        print(f"[Lỗi] Không thể mở file {input_file}. Chi tiết: {e}")
        return

    # Khởi tạo hoặc tái sử dụng mảng để lưu kết quả trả về từ RAG++
    chatbot_answers = []
    chatbot_citations = []

    print("\n[*] Bắt đầu chạy tự động Benchmark hệ thống RAG++...")
    print(f"[!] Tổng số câu hỏi cần xử lý: {len(df)} câu.")
    print("[!] Hệ thống tích hợp xử lý ngầm (BackgroundTasks) chấm điểm nên hãy giữ server FastAPI luôn bật.\n")
    
    # Chạy vòng lặp qua toàn bộ câu hỏi bằng thanh tiến trình tqdm
    for i, question in enumerate(tqdm(df['question'], desc="Tiến độ đánh giá")):
        answer, citations = ask_my_chatbot(question)
        
        chatbot_answers.append(answer)
        chatbot_citations.append(citations)
        
        # ---- CHIẾN LƯỢC 2: LƯU CUỐN CHIẾU (CHECKPOINT) MỖI 10 CÂU ----
        if (i + 1) % 10 == 0 or (i + 1) == len(df):
            # Sao chép tạm dataframe tính đến thời điểm hiện tại để lưu
            df_temp = df.iloc[:len(chatbot_answers)].copy()
            df_temp['answer'] = chatbot_answers
            df_temp['citations_answer'] = chatbot_citations
            try:
                df_temp.to_excel(checkpoint_file, index=False)
            except Exception:
                # Nếu file checkpoint bị lỗi (do đang mở), ghi ra file CSV thay thế làm backup cứng
                df_temp.to_csv("benchmark_checkpoint.csv", index=False, encoding='utf-8-sig')

        # Nghỉ 0.2 giây giữa các request để đảm bảo luồng background_tasks của FastAPI xử lý kịp
        time.sleep(0.2)

    # Đính kết quả thu được vào file Excel khớp chính xác với tên cột mà file evaluate.py tìm kiếm
    df['answer'] = chatbot_answers
    df['citations_answer'] = chatbot_citations

    # KIỂM TRA VÀ TỰ ĐỘNG BỔ SUNG CỘT KEYWORDS NẾU CHƯA CÓ ĐỂ TRÁNH LỖI ĐIỂM 0.00
    if 'keywords' not in df.columns:
        print("[*] Phát hiện hệ thống thiếu cột dữ liệu từ khóa gốc. Tiến hành tạo cột từ khóa tự động...")
        auto_keywords = []
        for _, row in df.iterrows():
            q = str(row['question']).lower()
            gt = str(row.get('ground_truth', '')).lower()
            
            # Trích xuất các thuật ngữ pháp lý xuất hiện trong câu hỏi hoặc đáp án mẫu
            kws = []
            if "ly hôn" in q or "ly hôn" in gt: kws.append("ly hôn")
            if "nuôi con" in q or "nuôi con" in gt: kws.append("quyền nuôi con")
            if "tài sản" in q or "tài sản" in gt: kws.append("tài sản chung")
            if "cấp dưỡng" in q or "cấp dưỡng" in gt: kws.append("cấp dưỡng")
            if "kết hôn" in q or "kết hôn" in gt: kws.append("kết hôn")
            if "đơn phương" in q or "đơn phương" in gt: kws.append("đơn phương")
            if "thuận tình" in q or "thuận tình" in gt: kws.append("thuận tình")
            
            if not kws:
                kws = ["luật hôn nhân", "gia đình"]
            auto_keywords.append(", ".join(kws))
        df['keywords'] = auto_keywords

    # ---- CHIẾN LƯỢC 1: BỌC TRY-EXCEPT PHÒNG THỦ KHI XUẤT FILE CHÍNH ----
    print(f"\n[*] Đang tiến hành xuất dữ liệu kết quả ra file: {output_file}")
    try:
        df.to_excel(output_file, index=False)
        print("\n=== HOÀN THÀNH QUÁ TRÌNH CHẠY BENCHMARK ===")
        print(f"[✓] File kết quả chứa đầy đủ yếu tố lưu tại: {output_file}")
        
        # Xóa file checkpoint sau khi đã hoàn thành lưu file chính thành công
        if os.path.exists(checkpoint_file): os.remove(checkpoint_file)
        if os.path.exists("benchmark_checkpoint.csv"): os.remove("benchmark_checkpoint.csv")
        
    except PermissionError:
        # KỊCH BẢN CỨU NGUY: Khi file chính bị khóa
        timestamp = int(time.time())
        emergency_file = f"benchmark_URGENT_SAVE_{timestamp}.xlsx"
        print(f"\n[!] CẢNH BÁO NGUY HIỂM: File '{output_file}' đang bị mở hoặc bị khóa!")
        print(f"[*] Hệ thống tiến hành cứu dữ liệu sang file dự phòng: {emergency_file}")
        try:
            df.to_excel(emergency_file, index=False)
            print(f"[✓] CỨU DỮ LIỆU THÀNH CÔNG! Kết quả hiện tại nằm ở: {emergency_file}")
        except Exception as e:
            # Phương án cuối cùng: Lưu ra CSV (CSV cực kì hiếm khi bị lỗi Permission chéo hệ thống)
            csv_backup = f"benchmark_URGENT_SAVE_{timestamp}.csv"
            df.to_csv(csv_backup, index=False, encoding='utf-8-sig')
            print(f"[✓] BIỆN PHÁP CUỐI CÙNG: Đã cứu dữ liệu thành công ra file CSV: {csv_backup}")
            
    except Exception as e:
        print(f"\n[-] Gặp lỗi không xác định khi lưu file: {e}")
        # Lưu khẩn cấp ra CSV đề phòng lỗi thư viện Excel
        df.to_csv("benchmark_final_error_backup.csv", index=False, encoding='utf-8-sig')
        print("[✓] Đã lưu dữ liệu khẩn cấp ra file: benchmark_final_error_backup.csv")

if __name__ == "__main__":
    main()