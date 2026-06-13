import os
import re
import requests
import sys

# Đảm bảo console Windows in tiếng Việt và emoji không bị lỗi
sys.stdout.reconfigure(encoding='utf-8')

# Đường dẫn đến file .env của backend
ENV_PATH = ".env"

if not os.path.exists(ENV_PATH):
    print("❌ Lỗi: Không tìm thấy file .env ở thư mục hiện tại!")
    print("Vui lòng chạy script này từ thư mục C:\\KHOALUAN\\backend")
    sys.exit(1)

# Biểu thức chính quy phát hiện API Key OpenRouter (bao gồm cả dòng chứa dấu #)
pattern = re.compile(r'^(#\s*)?(OPENROUTER_API_KEY_\d+)\s*=\s*(sk-or-v1-[a-f0-9]+)')

keys_to_check = []

with open(ENV_PATH, "r", encoding="utf-8") as f:
    for line in f:
        match = pattern.match(line.strip())
        if match:
            is_commented = match.group(1) is not None
            key_name = match.group(2)
            key_value = match.group(3)
            keys_to_check.append({
                "name": key_name,
                "value": key_value,
                "status": "🔴 Đã tắt (#)" if is_commented else "🟢 Đang bật"
            })

if not keys_to_check:
    print("⚠️ Không tìm thấy API Key OpenRouter nào trong file .env!")
    sys.exit(0)

print("=" * 95)
print(f"📊 KIỂM TRA HẠN MỨC QUOTA CỦA {len(keys_to_check)} OPENROUTER KEYS TRONG FILE .ENV")
print("=" * 95)
print(f"{'Tên API Key':<25} | {'Trạng Thái':<12} | {'Đã Dùng (USD)':<15} | {'Hạn Mức (USD)':<15} | {'Hạn Mức Còn Lại (%)':<20}")
print("-" * 95)

for k in keys_to_check:
    key_name = k["name"]
    key_val = k["value"]
    status = k["status"]
    
    url = "https://openrouter.ai/api/v1/key"
    headers = {"Authorization": f"Bearer {key_val}"}
    
    try:
        # Gửi request lên OpenRouter API kiểm tra trạng thái key trực tiếp
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            res_data = response.json().get("data", {})
            usage = res_data.get("usage", 0.0)
            limit = res_data.get("limit")
            
            # Tính toán phần trăm còn lại
            if limit is not None and limit > 0:
                remaining_usd = max(0.0, limit - usage)
                remaining_pct = (remaining_usd / limit) * 100
                remaining_str = f"{remaining_pct:.1f}% còn lại"
                limit_str = f"${limit:.4f}"
            else:
                remaining_str = "Không giới hạn"
                limit_str = "Unlimited"
                
            usage_str = f"${usage:.4f}"
            print(f"{key_name:<25} | {status:<12} | {usage_str:<15} | {limit_str:<15} | {remaining_str:<20}")
            
        elif response.status_code == 401:
            print(f"{key_name:<25} | {status:<12} | {'Lỗi 401':<15} | {'Key không hợp lệ':<15} | {'0.0% (Đã hết hạn/Sai key)':<20}")
        elif response.status_code == 402:
            print(f"{key_name:<25} | {status:<12} | {'Lỗi 402':<15} | {'Hết số dư tài khoản':<15} | {'0.0% (Hết số dư)':<20}")
        elif response.status_code == 429:
            print(f"{key_name:<25} | {status:<12} | {'Lỗi 429':<15} | {'Rate limit':<15} | {'Nghẽn băng thông tạm thời':<20}")
        else:
            print(f"{key_name:<25} | {status:<12} | {f'Lỗi HTTP {response.status_code}':<15} | {'-':<15} | {'-':<20}")
            
    except Exception as e:
        print(f"{key_name:<25} | {status:<12} | {'Lỗi kết nối':<15} | {'-':<15} | {'-':<20}")

print("=" * 95)
