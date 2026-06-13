import os
import re
import sys
import datetime # Thêm thư viện để lấy năm hiện tại
import pdfplumber # Đã thay thế PyPDF2 bằng pdfplumber để đọc tiếng Việt chuẩn hơn

# Thêm thư mục gốc (backend) vào đường dẫn hệ thống để import được module app
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from app.services.vector_store import vector_service

def process_all_pdfs_in_directory(directory_path: str):
    if not os.path.exists(directory_path):
        print(f"❌ Lỗi: Không tìm thấy thư mục tại đường dẫn: {directory_path}")
        return

    # 1. Quét tìm tất cả các file có đuôi .pdf trong thư mục
    pdf_files = [f for f in os.listdir(directory_path) if f.endswith('.pdf')]
    
    if not pdf_files:
        print(f"⚠️ Không có file PDF nào trong thư mục '{directory_path}'.")
        return

    print(f"🔍 Tìm thấy {len(pdf_files)} file PDF. Bắt đầu xử lý...\n")
    
    all_chunks = [] # Danh sách chứa dữ liệu của TẤT CẢ các file
    current_year = datetime.date.today().year # Lấy năm hiện tại

    # 2. Lặp qua từng file để xử lý
    for filename in pdf_files:
        pdf_path = os.path.join(directory_path, filename)
        
        law_name_auto = filename.replace(".pdf", "").replace("_", " ")
        
        # TÌM NĂM BAN HÀNH TỪ TÊN FILE
        year_match = re.search(r'(19|20)\d{2}', filename)
        year_issued = int(year_match.group(0)) if year_match else current_year
        
        print(f"--- Đang xử lý: {filename} (Năm: {year_issued}) ---")
        
        full_text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + " "

        if not full_text.strip():
            print(f"⚠️ Bỏ qua {filename}: File trống hoặc là ảnh chụp.")
            continue

        full_text = full_text.replace('\n', ' ')
        full_text = re.sub(r'\s+', ' ', full_text)

        # --- CHỈNH SỬA: Thêm \. vào re.split để tránh cắt nhầm Điều tham chiếu trong câu ---
        raw_chunks = re.split(r'(?i)(?=Điều\s+\d+\.)', full_text)
        
        file_chunk_count = 0
        for chunk in raw_chunks:
            chunk = chunk.strip()
            if len(chunk) < 20: 
                continue
                
            # --- CHỈNH SỬA: Thêm \. để ép lấy đúng số Điều của tiêu đề ---
            match = re.search(r'(?i)Điều\s+(\d+)\.', chunk)
            article_num = match.group(1) if match else "Khác"
            
            all_chunks.append({
                "content": chunk,
                "metadata": {
                    "article": f"Điều {article_num}",
                    "law_name": law_name_auto, 
                    "year": year_issued,      
                    "status": "active" 
                }
            })
            file_chunk_count += 1
            
        print(f"-> Đã bóc tách thành công {file_chunk_count} đoạn từ {filename}.\n")

    # 3. Nhúng và lưu toàn bộ data vào FAISS một lần
    if all_chunks:
        print(f"🚀 Bắt đầu nhúng (Embedding) tổng cộng {len(all_chunks)} đoạn vào FAISS...")
        
        vector_service.index = None
        vector_service.metadata = []
        
        vector_service.add_to_index(all_chunks)
        print("✅ HOÀN TẤT! Toàn bộ dữ liệu SẠCH đã được cập nhật vào metadata.pkl và vector_db.index.")
    else:
        print("⚠️ Không có đoạn văn bản nào hợp lệ để nhúng.")

if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_directory = os.path.join(BASE_DIR, "data") 
    process_all_pdfs_in_directory(target_directory)