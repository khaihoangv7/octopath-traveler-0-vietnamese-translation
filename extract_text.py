"""
Extract all game text from Octopath Traveler's .uexp files.
Format: UE4 header (variable) + MessagePack data + UE4 footer (8 bytes)
"""
import msgpack
import struct
import os
import json

BASE = r'Octopath_Traveler0\Content\Paks\pakchunk0-Windows\Octopath_Traveler0\Content\Local\DataBase\GameText\Localize\EN-US'
OUTPUT_DIR = 'extracted_text'

os.makedirs(OUTPUT_DIR, exist_ok=True)

def find_msgpack_start(data):
    """Find the start of MessagePack data by looking for root map marker."""
    # Look for 0x81 (fixmap with 1 entry) followed by 0xaa 0x6d 0x5f... ("m_")
    for i in range(min(30, len(data))):
        if data[i] == 0x81:  # fixmap(1)
            if i + 2 < len(data) and data[i+1] >= 0xa0:  # fixstr
                str_len = data[i+1] - 0xa0
                if i + 2 + str_len <= len(data):
                    try:
                        key = data[i+2:i+2+str_len].decode('ascii')
                        if key == 'm_DataList':
                            return i
                    except:
                        pass
    return -1

def extract_text_from_uexp(filepath):
    """Read .uexp file and parse MessagePack data."""
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Find msgpack start
    start = find_msgpack_start(data)
    if start < 0:
        return None
    
    # Strip UE4 footer (last 4-8 bytes are usually UE4 export footer)
    # Try stripping last 8 bytes, then 4
    for footer_size in [8, 4, 0]:
        end = len(data) - footer_size
        try:
            result = msgpack.unpackb(data[start:end], raw=False, strict_map_key=False)
            return result
        except Exception:
            continue
    
    # Try with Unpacker (streaming)
    try:
        unpacker = msgpack.Unpacker(raw=False, strict_map_key=False)
        unpacker.feed(data[start:])
        result = next(iter(unpacker))
        return result
    except:
        pass
    
    return None

def extract_entries(parsed):
    """Extract text entries from parsed data."""
    entries = []
    
    if isinstance(parsed, dict) and 'm_DataList' in parsed:
        data_list = parsed['m_DataList']
        if isinstance(data_list, list):
            for item in data_list:
                if isinstance(item, dict) and 'm_id' in item and 'm_gametext' in item:
                    entry_id = item['m_id']
                    gametext = item['m_gametext']
                    
                    # gametext is typically a fixarray of strings
                    if isinstance(gametext, list):
                        text_lines = []
                        for s in gametext:
                            if isinstance(s, str):
                                stripped = s.strip()
                                if stripped:
                                    text_lines.append(stripped)
                        if text_lines:
                            entries.append({
                                'id': entry_id,
                                'text': text_lines,
                                'text_joined': '\n'.join(text_lines)
                            })
                    elif isinstance(gametext, str) and gametext.strip():
                        entries.append({
                            'id': entry_id,
                            'text': [gametext.strip()],
                            'text_joined': gametext.strip()
                        })
    
    return entries

# Process all EN-US files
all_texts = {}
total_entries = 0
total_strings = 0

for subdir in ['SystemText', 'TalkText']:
    full_dir = os.path.join(BASE, subdir)
    if not os.path.exists(full_dir):
        continue
    
    for fname in sorted(os.listdir(full_dir)):
        if not fname.endswith('.uexp'):
            continue
        
        fpath = os.path.join(full_dir, fname)
        name = fname.replace('.uexp', '')
        
        parsed = extract_text_from_uexp(fpath)
        
        if parsed is None:
            print(f"  ERROR: {fname}")
            continue
        
        entries = extract_entries(parsed)
        total_entries += len(entries)
        total_strings += sum(len(e['text']) for e in entries)
        
        # Save to JSON
        output_file = os.path.join(OUTPUT_DIR, f"{name}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
        
        # Print summary
        print(f"  {subdir}/{fname}: {len(entries)} entries")
        for entry in entries[:3]:
            preview = entry['text_joined'][:70]
            print(f"    ID {entry['id']}: \"{preview}\"")
        if len(entries) > 3:
            print(f"    ... +{len(entries)-3} more")
        
        all_texts[name] = entries

# Create translation template CSV
csv_file = os.path.join(OUTPUT_DIR, 'translation_template.csv')
with open(csv_file, 'w', encoding='utf-8-sig') as f:
    f.write("File,ID,English,Vietnamese\n")
    for name, entries in all_texts.items():
        for entry in entries:
            text = entry['text_joined'].replace('"', '""').replace('\n', '\\n')
            f.write(f'{name},{entry["id"]},"{text}",""\n')

print(f"\n{'='*60}")
print(f"  EXTRACTION COMPLETE")
print(f"  Total files: {len(all_texts)}")
print(f"  Total entries: {total_entries}")
print(f"  Total text lines: {total_strings}")
print(f"  Output: {OUTPUT_DIR}/")
print(f"  Translation template: {csv_file}")
print(f"{'='*60}")
