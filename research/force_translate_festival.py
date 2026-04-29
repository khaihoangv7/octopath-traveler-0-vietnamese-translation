import json
import os
import time
from google import genai

client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

def translate_batch(texts):
    prompt = "Translate these Octopath Traveler RPG game lines into Vietnamese. Keep placeholders like <chara_name> or <VAR> exactly as they are. Output only the translated Vietnamese lines, one per line.\n\n" + "\n".join(texts)
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=prompt
    )
    return response.text.strip().split('\n')

with open('translated_text/GameTextEvent.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find missing in range
missing = [d for d in data if 412000 <= d['id'] <= 416000 and not d.get('api_translated')]

if not missing:
    print("No missing strings in festival range.")
    exit()

print(f"Translating {len(missing)} missing strings in festival range...")

# Small batch translate
batch_size = 20
for i in range(0, len(missing), batch_size):
    batch = missing[i:i+batch_size]
    ens = [b['en'] for b in batch]
    try:
        vis = translate_batch(ens)
        if len(vis) >= len(ens):
            for j, b in enumerate(batch):
                b['vi'] = vis[j].strip()
                b['api_translated'] = True
            print(f"Translated batch {i//batch_size + 1}")
        else:
            print(f"Warning: Batch {i//batch_size + 1} returned {len(vis)} results for {len(ens)} inputs.")
    except Exception as e:
        print(f"Error in batch {i//batch_size + 1}: {e}")
    time.sleep(2)

with open('translated_text/GameTextEvent.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Festival range translation COMPLETE.")
