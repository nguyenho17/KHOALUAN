from datasets import load_dataset
import pandas as pd

print("Bước 1: Đang tải toàn bộ dataset từ Hugging Face (vui lòng đợi)...")
# Tải dataset từ Hugging Face
dataset = load_dataset("adamwhite625/vietnam-legal-qa")

print("Bước 2: Đang xử lý dữ liệu...")
# Chuyển dữ liệu sang dạng DataFrame để lọc
df = dataset['train'].to_pandas()

# Lọc đúng phân đoạn Luật Hôn nhân và Gia đình 2014
df_hngd = df[df['law_name'] == 'Luật Hôn nhân và Gia đình 2014']

print(f"Bước 3: Đã lọc được {len(df_hngd)} câu hỏi. Đang xuất ra file CSV...")
# Lưu thành file CSV (mã hóa utf-8-sig để không lỗi font tiếng Việt khi mở bằng Excel)
df_hngd.to_csv("benchmark_hngd.csv", index=False, encoding="utf-8-sig")

print("=== HOÀN THÀNH ===")
print("File 'benchmark_hngd.csv' đã được lưu thành công trong cùng thư mục!")