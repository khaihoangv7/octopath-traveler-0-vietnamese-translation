import json

data = json.load(open('translated_text/GameTextNPC.json', 'r', encoding='utf-8'))
untranslated = [e for e in data if e['en'] == e['vi']]
print('--- GameTextNPC Untranslated ---')
for e in untranslated[:20]:
    en_text = e['en'].replace('\n', ' ')
    print(f"{e['id']}|{en_text}")
