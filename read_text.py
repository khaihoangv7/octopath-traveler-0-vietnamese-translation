import json, sys
files = ['GameTextPC', 'GameTextGraphic', 'GameTextMap', 'GameTextEnemy', 'GameTextItem', 'GameTextUI']
for name in files:
    try:
        data = json.load(open(f'extracted_text/{name}.json', 'r', encoding='utf-8'))
        print(f"\n=== {name} ({len(data)} entries) ===")
        for e in data[:60]:
            print(f"{e['id']}|{e['text_joined']}")
    except Exception as ex:
        print(f"Error: {name}: {ex}")
