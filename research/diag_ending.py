import json
with open('translated_text/GameTextEnding.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

problems = []
for x in data:
    en = x.get('en', '')
    vi = x.get('vi', '')
    if en and (not vi or vi == en) and en not in ['(Unlocalized)', 'no data.', '???', '......', '']:
        problems.append(x)

print(f"Missing: {len(problems)}")
if problems:
    print("Example 1:")
    print(f"  ID: {problems[0]['id']}")
    print(f"  EN: {problems[0]['en']}")
    print(f"  VI: {problems[0].get('vi', 'MISSING')}")
    print(f"  api_translated: {problems[0].get('api_translated', 'NOT_FOUND')}")

    print("\nExample 2:")
    print(f"  ID: {problems[1]['id']}")
    print(f"  EN: {problems[1]['en']}")
    print(f"  VI: {problems[1].get('vi', 'MISSING')}")
    print(f"  api_translated: {problems[1].get('api_translated', 'NOT_FOUND')}")
