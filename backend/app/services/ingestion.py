import re
import os # Thêm thư viện os vì bên dưới code cũ của bạn có gọi os.path.basename
from PyPDF2 import PdfReader
# Thay đổi nếu lệnh import cũ vẫn lỗi sau khi cài package
from langchain_text_splitters import RecursiveCharacterTextSplitter

class IngestionService:
    def __init__(self):
        # Tách văn bản dựa trên các ký hiệu pháp lý
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["Điều ", "\n\n", "\n", ". "]
        )

    def process_pdf(self, file_path: str):
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content
        
        # Làm sạch văn bản sơ bộ (loại bỏ khoảng trắng thừa)
        text = re.sub(r'\s+', ' ', text)
        
        # Tách nhỏ văn bản
        chunks = self.splitter.split_text(text)
        
        processed_data = []
        for i, chunk in enumerate(chunks):
            # --- CHỈNH SỬA: Thêm dấu chấm (\.) để chỉ bắt tiêu đề Điều ---
            match = re.search(r'Điều (\d+)\.', chunk)
            article_no = match.group(1) if match else "Unknown"
            
            # --- PHẦN NÂNG CẤP: XÁC ĐỊNH HIỆU LỰC LUẬT ---
            # Trong thực tế, bạn có thể truyền status này từ giao diện Admin
            # Ở đây, mình gán mặc định là 'active' (còn hiệu lực). 
            current_status = 'active'
            # ----------------------------------------------
            
            processed_data.append({
                "id": f"chunk_{i}",
                "content": chunk,
                "metadata": {
                    "article": article_no,
                    "source": os.path.basename(file_path),
                    "type": "Law",
                    "status": current_status 
                }
            })
        return processed_data

ingestion_service = IngestionService()