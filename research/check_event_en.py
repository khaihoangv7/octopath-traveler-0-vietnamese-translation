import json
with open('translated_text/GameTextEvent.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

SKIP_TEXTS = ['(Unlocalized)', 'no data.', '???', '......', '', None]
still_english = [d for d in data if d.get('en') not in SKIP_TEXTS and (not d.get('vi') or d.get('vi') == d.get('en'))]

print(f"Total potential English: {len(still_english)}")
for d in still_english[:20]:
    print(f"ID {d['id']}: {d['en']}")
