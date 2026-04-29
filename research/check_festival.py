import json
with open('translated_text/GameTextEvent.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

count_missing = 0
count_translated = 0
for d in data:
    if 412000 <= d['id'] <= 416000:
        if d.get('api_translated'):
            count_translated += 1
        else:
            count_missing += 1
            if count_missing <= 10:
                print(f"Missing ID {d['id']}: {d.get('en')}")

print(f"\nRange 412000-416000: {count_translated} translated, {count_missing} missing.")
