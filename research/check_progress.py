import json
import os

INPUT_DIR = 'translated_text'

total_lines = 0
translated_lines = 0
files_fully_done = 0

# Danh sách các chuỗi hệ thống không cần dịch
SKIP_TEXTS = ["(Unlocalized)", "no data.", "???", "......", "", None]

files = sorted([f for f in os.listdir(INPUT_DIR) if f.endswith('.json')])
total_files = len(files)

for filename in files:
    path = os.path.join(INPUT_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    file_total_to_translate = 0
    file_done = 0
    
    for item in data:
        en = item.get('en', '')
        vi = item.get('vi', '')
        
        # Bỏ qua các dòng hệ thống/rỗng khỏi tổng số cần dịch
        if en in SKIP_TEXTS:
            continue
            
        file_total_to_translate += 1
        total_lines += 1
        
        # Chỉ tính là đã dịch nếu vi có nội dung và khác en
        if vi and vi != en:
            file_done += 1
            translated_lines += 1
            
    if file_total_to_translate > 0 and file_done == file_total_to_translate:
        files_fully_done += 1

percent = (translated_lines / total_lines) * 100 if total_lines > 0 else 0

print("=" * 60)
print("        TIẾN ĐỘ DỊCH THUẬT THỰC TẾ (CHỈ TÍNH TIẾNG VIỆT)")
print("=" * 60)
print(f"Tổng số câu cần dịch : {total_lines}")
print(f"Số câu đã dịch xong  : {translated_lines}")
print(f"Còn thiếu            : {total_lines - translated_lines}")
print(f"Phần trăm thực tế    : {percent:.2f}%")
print(f"Số File hoàn tất     : {files_fully_done} / {total_files}")
print("=" * 60)
bar_len = 40
filled = int(percent / 100 * bar_len)
print("Tiến độ: [" + "#" * filled + "-" * (bar_len - filled) + "]")
print("=" * 60)
