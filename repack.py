import json
import os
import struct
import msgpack
import shutil

INPUT_JSON_DIR = 'translated_text'
ORIGINAL_UEXP_BASE = r'Octopath_Traveler0\Content\Paks\pakchunk0-Windows\Octopath_Traveler0\Content\Local\DataBase\GameText\Localize\EN-US'
OUTPUT_MOD_DIR = r'Mod_Vietnamese\Octopath_Traveler0\Content\Local\DataBase\GameText\Localize\EN-US'

os.makedirs(OUTPUT_MOD_DIR, exist_ok=True)

def find_msgpack_start(data):
    for i in range(30):
        if data[i] == 0x81 and data[i+1] >= 0xa0:
            return i
    return -1

def repack_file(json_filename):
    json_path = os.path.join(INPUT_JSON_DIR, json_filename)
    if not os.path.exists(json_path):
        return
        
    with open(json_path, 'r', encoding='utf-8') as f:
        translations = json.load(f)
        
    # Create lookup dictionary
    trans_map = {}
    for t in translations:
        if t.get('vi') and t.get('vi') != t.get('en'):
            trans_map[t['id']] = t['vi']
            
    # Find original uexp
    basename = json_filename.replace('.json', '')
    original_uexp = None
    original_uasset = None
    rel_path = ''
    
    for subdir in ['SystemText', 'TalkText']:
        p = os.path.join(ORIGINAL_UEXP_BASE, subdir, basename + '.uexp')
        if os.path.exists(p):
            original_uexp = p
            original_uasset = p.replace('.uexp', '.uasset')
            rel_path = subdir
            break
            
    if not original_uexp:
        print(f"Could not find original uexp for {basename}")
        return
        
    # Read original
    with open(original_uexp, 'rb') as f:
        data = f.read()
        
    start = find_msgpack_start(data)
    header_start = data[:start]
    footer = data[-4:]
    
    msgpack_start_data = data[start:]
    unpacker = msgpack.Unpacker(raw=False, strict_map_key=False)
    unpacker.feed(msgpack_start_data)
    
    try:
        parsed = next(iter(unpacker))
    except StopIteration:
        print(f"Could not parse msgpack in {basename}")
        return
        
    bytes_consumed = unpacker.tell()
    footer = msgpack_start_data[bytes_consumed:]
    
    # Replace text
    replaced_count = 0
    if 'm_DataList' in parsed:
        for item in parsed['m_DataList']:
            if 'm_id' in item and 'm_gametext' in item:
                m_id = item['m_id']
                if m_id in trans_map:
                    new_text = trans_map[m_id]
                    # Check original type
                    if isinstance(item['m_gametext'], list):
                        # Preserve original array structure and length (e.g. 12 elements)
                        for i, s in enumerate(item['m_gametext']):
                            if isinstance(s, str) and s.strip():
                                item['m_gametext'][i] = new_text
                                break
                    else:
                        item['m_gametext'] = new_text
                    replaced_count += 1
                    
    # Repack msgpack
    new_msgpack = msgpack.packb(parsed, use_bin_type=False)
    
    # Calculate new header
    # size = len(msgpack) - 4
    # Construct new uexp WITH the original footer (which contains 4 padding bytes + 4 magic bytes)
    new_size = len(new_msgpack)
    new_header = header_start[:6] + struct.pack('<I', new_size)
    new_data = new_header + new_msgpack + footer
    
    # Save files
    out_dir = os.path.join(OUTPUT_MOD_DIR, rel_path)
    os.makedirs(out_dir, exist_ok=True)
    
    out_uexp = os.path.join(out_dir, basename + '.uexp')
    with open(out_uexp, 'wb') as f:
        f.write(new_data)
        
    # Patch and copy uasset
    out_uasset = os.path.join(out_dir, basename + '.uasset')
    if os.path.exists(original_uasset):
        with open(original_uasset, 'rb') as f:
            uasset_data = f.read()
            
        old_size_packed = struct.pack('<Q', len(data) - 4)
        new_size_packed = struct.pack('<Q', len(new_data) - 4)
        
        # Replace the size in the uasset (should be exactly 1 occurrence)
        new_uasset_data = uasset_data.replace(old_size_packed, new_size_packed)
        
        with open(out_uasset, 'wb') as f:
            f.write(new_uasset_data)
        
    print(f"Repacked {basename}: {replaced_count} strings replaced. Size changed from {len(data)} to {len(new_data)}")

if __name__ == '__main__':
    print("Starting repack...")
    for f in os.listdir(INPUT_JSON_DIR):
        if f.endswith('.json'):
            repack_file(f)
    print("Repack complete. Output saved to Mod_Vietnamese/")
