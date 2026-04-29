"""Quick check: are the remaining 'long' lines actually long, or just tag-inflated?"""
import sys, io, json, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TAG_PATTERN = re.compile(r'(<[^>]+>|\{[^}]+\})')
TRANSLATED_DIR = r'd:\Game\Steam\steamapps\common\Octopath_Traveler0\translated_text'

truly_long = 0
tag_inflated = 0

for f in sorted(os.listdir(TRANSLATED_DIR)):
    if not f.endswith('.json'): continue
    data = json.load(open(os.path.join(TRANSLATED_DIR, f), 'r', encoding='utf-8'))
    for item in data:
        vi = item.get('vi', '')
        if not vi or vi == item.get('en', ''): continue
        for line in vi.split('\n'):
            raw_len = len(line)
            visible_len = len(TAG_PATTERN.sub('', line))
            if raw_len > 45:
                if visible_len > 35:
                    truly_long += 1
                    if truly_long <= 10:
                        print(f"  TRULY LONG (visible={visible_len}, raw={raw_len}): {repr(line[:80])}")
                else:
                    tag_inflated += 1

print(f"\nTruly long (visible > 35): {truly_long}")
print(f"Tag-inflated only (visible <= 35, raw > 45): {tag_inflated}")
