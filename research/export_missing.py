import json
with open('translated_text/GameTextEvent.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
missing = [d for d in data if 412000 <= d['id'] <= 416000 and not d.get('api_translated')]
with open('research/missing_festival.txt', 'w', encoding='utf-8') as f:
    for d in missing:
        f.write(f"{d['id']}|{d['en']}\n")
