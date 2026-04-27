import json
import os

INPUT_DIR = 'translated_text'

total_lines = 0
translated_lines = 0
files_processed = 0
total_files = len([f for f in os.listdir(INPUT_DIR) if f.endswith('.json')])

for filename in os.listdir(INPUT_DIR):
    if not filename.endswith('.json'):
        continue
        
    path = os.path.join(INPUT_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    file_total = len(data)
    file_translated = 0
    
    for item in data:
        total_lines += 1
        # Đếm các dòng đã được AI xử lý hoặc có chữ tiếng Việt khác tiếng Anh
        if item.get('api_translated', False) or (item.get('vi') and item.get('vi') != item.get('en')):
            file_translated += 1
            translated_lines += 1
            
    if file_translated == file_total:
        files_processed += 1

percent = (translated_lines / total_lines) * 100 if total_lines > 0 else 0

print("=" * 60)
print("             TIẾN ĐỘ DỊCH THUẬT OCTOPATH TRAVELER")
print("=" * 60)
print(f"Tổng số dòng đã dịch : {translated_lines} / {total_lines}")
print(f"Phần trăm hoàn thành : {percent:.2f}%")
print(f"Số File hoàn tất     : {files_processed} / {total_files}")
print("=" * 60)
print("Tiến độ: [" + "#" * int(percent/2) + "-" * (50 - int(percent/2)) + "]")
print("=" * 60)
