import json, os

files = [
    ('GameTextUI', 200),
    ('GameTextSkill', 100),
    ('GameTextQuest', 100),
    ('GameTextCharacterCreate', 200),
    ('GameTextVillage', 100),
    ('GameTextScenarioReplay', 100),
    ('GameTextNPC', 80),
    ('GameTextEvent', 80),
    ('GameTextFC', 80),
]

for name, limit in files:
    data = json.load(open(f'extracted_text/{name}.json', 'r', encoding='utf-8'))
    print(f"\n########## {name} ({len(data)} entries) ##########")
    for e in data[:limit]:
        t = e['text_joined'].replace('\n', '\\n')[:150]
        print(f"{e['id']}|{t}")
    if len(data) > limit:
        print(f"... +{len(data)-limit} more")
