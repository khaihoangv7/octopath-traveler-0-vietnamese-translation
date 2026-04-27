import json
import os
import time
import google.generativeai as genai

# 1. ĐIỀN API KEY CỦA BẠN VÀO ĐÂY (Giữ nguyên dấu ngoặc kép)
API_KEY = "AIzaSyCQSciKFvGMkBg2WnkS6mfJMpv9fhsIzjg"

INPUT_DIR = 'extracted_text'
OUTPUT_DIR = 'translated_text'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def setup_gemini():
    genai.configure(api_key=API_KEY)
    # Dùng model gemini-3.1-flash-lite-preview để không bị vướng giới hạn 20 lần/ngày của các bản chính thức mới
    model = genai.GenerativeModel(
        model_name='gemini-3.1-flash-lite-preview',
        system_instruction="""
        You are a professional video game localizer translating an RPG from English to Vietnamese.
        Context: The game is a medieval fantasy RPG (Octopath Traveler).
        Rules:
        1. Maintain an RPG fantasy tone (e.g. use "ngươi", "ta", "bệ hạ", "quái vật", "ma thuật"... where appropriate based on context).
        2. Keep all special tags like {0}, <chara_name>, \n exactly as they are.
        3. Do NOT translate character names (e.g. Herminia, Bargello, Tytos).
        4. I will give you a JSON array of strings. You MUST return ONLY a valid JSON array of the translated strings in the EXACT SAME ORDER, with nothing else outside the JSON.
        """
    )
    return model

def translate_batch(model, texts):
    if not texts:
        return []
    
    # Gom các câu cần dịch thành JSON để gửi đi
    prompt = json.dumps(texts, ensure_ascii=False)
    
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3, # Nhiệt độ thấp để dịch chính xác, không chế từ
                response_mime_type="application/json", # Ép AI trả về chuẩn JSON
            )
        )
        
        # Đọc kết quả JSON trả về
        result_text = response.text
        translated_texts = json.loads(result_text)
        
        if len(translated_texts) != len(texts):
            print(f"Lỗi: Số lượng câu trả về ({len(translated_texts)}) không khớp với số lượng gửi đi ({len(texts)})")
            return texts # Lỗi thì giữ nguyên tiếng Anh
            
        return translated_texts
        
    except Exception as e:
        error_msg = str(e)
        print(f"Lỗi khi gọi API: {error_msg}")
        if "429" in error_msg or "Quota" in error_msg:
            print("Đã đạt giới hạn số lần gọi API miễn phí mỗi phút. Đang chờ 35 giây để hồi phục...")
            time.sleep(35)
        else:
            print("Đang chờ 10 giây rồi thử lại...")
            time.sleep(10)
        return None # Trả về None để vòng lặp bên ngoài thử lại

def process_file(filename, model):
    input_path = os.path.join(INPUT_DIR, filename)
    output_path = os.path.join(OUTPUT_DIR, filename)
    
    with open(input_path, 'r', encoding='utf-8') as f:
        entries = json.load(f)
        
    # Nếu file đã dịch một phần, đọc nó lên để không dịch lại từ đầu
    if os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as f:
            completed_entries = json.load(f)
    else:
        completed_entries = []
        for e in entries:
            completed_entries.append({
                'id': e['id'],
                'en': e['text_joined'],
                'vi': '' # Rỗng nghĩa là chưa dịch
            })
            
    print(f"\n--- Đang xử lý file: {filename} ({len(entries)} dòng) ---")
    
    BATCH_SIZE = 100 # Dịch 100 câu mỗi lần để tiết kiệm số lần gọi API
    
    for i in range(0, len(completed_entries), BATCH_SIZE):
        batch = completed_entries[i:i+BATCH_SIZE]
        
        # Chỉ dịch những câu chưa có cờ 'api_translated' VÀ (vi đang trống HOẶC vi giống en)
        needs_translation = [
            item for item in batch 
            if not item.get('api_translated', False) and (not item.get('vi') or item.get('vi') == item.get('en'))
        ]
        
        # Loại bỏ các câu quá ngắn hoặc mang tính hệ thống không cần dịch
        texts_to_translate = [item['en'] for item in needs_translation if item['en'] not in ["(Unlocalized)", "no data.", "???"]]
        
        if not texts_to_translate:
            continue # Cụm này đã dịch xong hết, bỏ qua
            
        print(f"  Đang dịch {len(texts_to_translate)} câu mới (từ dòng {i} đến {i+len(batch)})...")
        
        # Gửi lên AI (có cơ chế thử lại nếu bị lỗi mạng/quá tải)
        translated_texts = None
        retries = 100 # Cho phép thử lại nhiều lần nếu bị kẹt
        while translated_texts is None and retries > 0:
            translated_texts = translate_batch(model, texts_to_translate)
            retries -= 1
            time.sleep(4) # Nghỉ 4s giữa các lần gọi API để tránh bị chặn spam (Google miễn phí cho 15 lần/phút)
            
        if translated_texts:
            # Ráp bản dịch vào dữ liệu
            idx = 0
            for item in needs_translation:
                item['api_translated'] = True # Đánh dấu là đã qua AI xử lý để không bao giờ dịch lại câu này nữa
                if item['en'] in ["(Unlocalized)", "no data.", "???"]:
                    item['vi'] = item['en']
                else:
                    item['vi'] = translated_texts[idx]
                    idx += 1
                    
        # LƯU NGAY LẬP TỨC SAU MỖI CỤM (Chống mất dữ liệu nếu cúp điện)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(completed_entries, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    if API_KEY == "ĐIỀN_API_KEY_CỦA_BẠN_VÀO_ĐÂY":
        print("LỖI: Bạn chưa điền API Key!")
        print("Mở file auto_translate.py bằng Notepad và dán mã API Key của bạn vào biến API_KEY ở dòng số 6.")
        exit(1)
        
    print("Khởi động AI Translator...")
    model = setup_gemini()
    
    # Lấy danh sách các file JSON cần dịch
    files_to_translate = sorted([f for f in os.listdir(INPUT_DIR) if f.endswith('.json')])
    
    for filename in files_to_translate:
        process_file(filename, model)
        
    print("\nHOÀN TẤT DỊCH TOÀN BỘ GAME!")
