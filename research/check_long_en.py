import json
with open('translated_text/GameTextEvent.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

SKIP_TEXTS = ['(Unlocalized)', 'no data.', '???', '......', '', None]
long_english = [d for d in data if d.get('en') not in SKIP_TEXTS and (not d.get('vi') or d.get('vi') == d.get('en')) and len(d.get('en', '').split()) >= 3]

print(f"Long sentences missing: {len(long_english)}")
for d in long_english[:20]:
    print(f"ID {d['id']}: {d['en']}")
