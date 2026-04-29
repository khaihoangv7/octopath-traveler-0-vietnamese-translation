import json
with open('translated_text/GameTextCharacter.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

api_true = sum(1 for x in data if x.get('api_translated'))
vi_translated = sum(1 for x in data if x.get('vi') and x['vi'] != x['en'])
total = len(data)

print(f"Total: {total}")
print(f"api_translated=True: {api_true}")
print(f"vi != en: {vi_translated}")
print(f"Missing (by script logic): {total - api_true - vi_translated}")
