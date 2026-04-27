import json

data = json.load(open('translated_text/GameTextEvent.json', 'r', encoding='utf-8'))
print('--- GameTextEvent (Story Dialogue) First 30 lines ---')
for e in data[:30]:
    en_text = e['en'].replace('\n', ' ')
    if en_text and en_text != '(Unlocalized)' and en_text != 'no data.':
        print(f"{e['id']}|{en_text}")
