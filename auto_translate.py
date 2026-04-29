import json
import os
import time
from google import genai

# API KEY
API_KEY = ""

INPUT_DIR = 'extracted_text'
OUTPUT_DIR = 'translated_text'
os.makedirs(OUTPUT_DIR, exist_ok=True)

SYSTEM_INSTRUCTION = """
You are a professional video game localizer translating an RPG from English to Vietnamese.
Context: The game is a medieval fantasy RPG (Octopath Traveler).
Rules:
1. Maintain an RPG fantasy tone (e.g. use "ngươi", "ta", "bệ hạ", "quái vật", "ma thuật"... where appropriate based on context).
2. Keep all special tags like {0}, <chara_name>, \\n exactly as they are.
3. Do NOT translate character names (e.g. Herminia, Bargello, Tytos).
4. I will give you a JSON array of strings. You MUST return ONLY a valid JSON array of the translated strings in the EXACT SAME ORDER, with nothing else outside the JSON.
"""

def setup_client():
    client = genai.Client(api_key=API_KEY)
    return client

def translate_batch(client, texts):
    if not texts:
        return []
    
    prompt = json.dumps(texts, ensure_ascii=False)
    
    try:
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite-preview',
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.3,
                response_mime_type="application/json",
            )
        )
        
        result_text = response.text
        translated_texts = json.loads(result_text)
        
        if len(translated_texts) != len(texts):
            print(f"  WARNING: Got {len(translated_texts)} results for {len(texts)} inputs")
            return texts
            
        return translated_texts
        
    except Exception as e:
        error_msg = str(e)
        print(f"  API Error: {error_msg[:200]}")
        if "429" in error_msg or "Quota" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            print("  Rate limited. Waiting 35s...")
            time.sleep(35)
        else:
            print("  Waiting 10s before retry...")
            time.sleep(10)
        return None

def process_file(filename, client):
    input_path = os.path.join(INPUT_DIR, filename)
    output_path = os.path.join(OUTPUT_DIR, filename)
    
    with open(input_path, 'r', encoding='utf-8') as f:
        entries = json.load(f)
        
    if os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as f:
            completed_entries = json.load(f)
    else:
        completed_entries = []
        for e in entries:
            completed_entries.append({
                'id': e['id'],
                'en': e['text_joined'],
                'vi': ''
            })
    
    # Count missing
    missing_count = sum(1 for item in completed_entries 
                       if not item.get('api_translated', False) 
                       and (not item.get('vi') or item.get('vi') == item.get('en',''))
                       and item.get('en','') not in ["(Unlocalized)", "no data.", "???", "......", ""])
    
    if missing_count == 0:
        print(f"  {filename}: ALL DONE")
        return
    
    print(f"\n--- {filename}: {missing_count} entries to translate ---")
    
    BATCH_SIZE = 30  # Smaller batches for better stability and accuracy
    
    for i in range(0, len(completed_entries), BATCH_SIZE):
        batch = completed_entries[i:i+BATCH_SIZE]
        
        needs_translation = [
            item for item in batch 
            if not item.get('api_translated', False) and (not item.get('vi') or item.get('vi') == item.get('en',''))
        ]
        
        skip_texts = ["(Unlocalized)", "no data.", "???", "......", ""]
        texts_to_translate = [item['en'] for item in needs_translation if item.get('en','') not in skip_texts]
        
        if not texts_to_translate:
            # Mark skippable items
            for item in needs_translation:
                if item.get('en','') in skip_texts:
                    item['api_translated'] = True
                    item['vi'] = item.get('en','')
            continue
            
        print(f"  Translating {len(texts_to_translate)} texts (batch {i//BATCH_SIZE + 1})...")
        
        translated_texts = None
        retries = 5
        while translated_texts is None and retries > 0:
            translated_texts = translate_batch(client, texts_to_translate)
            retries -= 1
            if translated_texts is None:
                time.sleep(4)
            
        if translated_texts:
            idx = 0
            for item in needs_translation:
                item['api_translated'] = True
                if item.get('en','') in skip_texts:
                    item['vi'] = item.get('en','')
                else:
                    item['vi'] = translated_texts[idx]
                    idx += 1
                    
        # Save after each batch
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(completed_entries, f, ensure_ascii=False, indent=2)
        
        time.sleep(2)  # Rate limiting

if __name__ == "__main__":
    print("Starting AI Translator (google-genai SDK)...")
    client = setup_client()
    
    files_to_translate = sorted([f for f in os.listdir(INPUT_DIR) if f.endswith('.json')])
    
    for filename in files_to_translate:
        process_file(filename, client)
        
    print("\nDONE! All translations complete.")
