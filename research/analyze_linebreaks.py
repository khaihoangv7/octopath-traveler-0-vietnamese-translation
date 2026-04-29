"""
Analyze line break patterns in translated text to find:
1. Lines that are too long (causing overlap in game)
2. Unnecessary line breaks (mid-word or mid-sentence breaks)
3. Compare EN vs VI line break patterns
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import json
import os

TRANSLATED_DIR = r'd:\Game\Steam\steamapps\common\Octopath_Traveler0\translated_text'

def analyze_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    filename = os.path.basename(filepath)
    issues = []
    
    for item in data:
        vi = item.get('vi', '')
        en = item.get('en', '')
        item_id = item.get('id', '?')
        
        if not vi or vi == en:
            continue
        
        # Check for \n in Vietnamese text
        if '\n' in vi:
            vi_lines = vi.split('\n')
            en_lines = en.split('\n') if '\n' in en else [en]
            
            # Count line breaks
            vi_breaks = vi.count('\n')
            en_breaks = en.count('\n')
            
            # Check for very long lines (>40 chars - typical game dialog width)
            long_lines = [l for l in vi_lines if len(l) > 45]
            
            # Check for unnecessary breaks (very short fragments)
            short_fragments = [l for l in vi_lines if 0 < len(l.strip()) < 5]
            
            # Check if VI has MORE line breaks than EN
            extra_breaks = vi_breaks > en_breaks
            
            if long_lines or short_fragments or extra_breaks:
                issue = {
                    'id': item_id,
                    'file': filename,
                    'en': en[:150],
                    'vi': vi[:150],
                    'vi_breaks': vi_breaks,
                    'en_breaks': en_breaks,
                    'long_lines': long_lines,
                    'short_fragments': short_fragments,
                    'extra_breaks': extra_breaks,
                }
                issues.append(issue)
    
    return issues

# Analyze all files
all_issues = []
stats = {
    'total_translated': 0,
    'with_newlines': 0,
    'extra_breaks': 0,
    'long_lines': 0,
    'short_fragments': 0,
}

for f in sorted(os.listdir(TRANSLATED_DIR)):
    if not f.endswith('.json'):
        continue
    filepath = os.path.join(TRANSLATED_DIR, f)
    
    with open(filepath, 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    
    for item in data:
        vi = item.get('vi', '')
        en = item.get('en', '')
        if vi and vi != en:
            stats['total_translated'] += 1
            if '\n' in vi:
                stats['with_newlines'] += 1
                if vi.count('\n') > en.count('\n'):
                    stats['extra_breaks'] += 1
    
    issues = analyze_file(filepath)
    all_issues.extend(issues)

print("=" * 70)
print("TRANSLATION LINE BREAK ANALYSIS")
print("=" * 70)
print(f"\nTotal translated entries: {stats['total_translated']}")
print(f"Entries with newlines in VI: {stats['with_newlines']}")
print(f"Entries where VI has MORE breaks than EN: {stats['extra_breaks']}")
print()

# Show examples of extra breaks
extra = [i for i in all_issues if i['extra_breaks']]
print(f"\n--- EXTRA LINE BREAKS (VI has more \\n than EN): {len(extra)} cases ---")
for issue in extra[:20]:
    print(f"\n  File: {issue['file']}, ID: {issue['id']}")
    print(f"  EN ({issue['en_breaks']} breaks): {repr(issue['en'][:100])}")
    print(f"  VI ({issue['vi_breaks']} breaks): {repr(issue['vi'][:100])}")

# Show examples of long lines
long = [i for i in all_issues if i['long_lines']]
print(f"\n\n--- LONG LINES (>45 chars): {len(long)} cases ---")
for issue in long[:20]:
    print(f"\n  File: {issue['file']}, ID: {issue['id']}")
    for ll in issue['long_lines'][:3]:
        print(f"  LONG ({len(ll)} chars): {repr(ll[:80])}")

# Analyze the EN original line lengths to understand game limits
print("\n\n--- EN ORIGINAL LINE LENGTH DISTRIBUTION ---")
en_line_lengths = []
for f in sorted(os.listdir(TRANSLATED_DIR)):
    if not f.endswith('.json'):
        continue
    filepath = os.path.join(TRANSLATED_DIR, f)
    with open(filepath, 'r', encoding='utf-8') as fh:
        data = json.load(fh)
    for item in data:
        en = item.get('en', '')
        if '\n' in en:
            for line in en.split('\n'):
                if line.strip():
                    en_line_lengths.append(len(line))

if en_line_lengths:
    en_line_lengths.sort()
    print(f"  Total EN lines: {len(en_line_lengths)}")
    print(f"  Min: {min(en_line_lengths)}, Max: {max(en_line_lengths)}")
    print(f"  Median: {en_line_lengths[len(en_line_lengths)//2]}")
    print(f"  90th percentile: {en_line_lengths[int(len(en_line_lengths)*0.9)]}")
    print(f"  95th percentile: {en_line_lengths[int(len(en_line_lengths)*0.95)]}")
    
    # Distribution
    buckets = [20, 25, 30, 35, 40, 45, 50, 55, 60]
    for b in buckets:
        count = sum(1 for l in en_line_lengths if l <= b)
        print(f"  <= {b} chars: {count} ({count*100//len(en_line_lengths)}%)")
