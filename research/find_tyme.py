import json
with open('translated_text/GameTextEvent.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

search_text = "Here you go, Tyme."
matches = [d for d in data if d.get('en') == search_text]

print(f"Found {len(matches)} matches for '{search_text}':")
for m in matches:
    print(f"ID {m['id']}: VI='{m.get('vi', 'MISSING')}' | api_translated={m.get('api_translated', False)}")
