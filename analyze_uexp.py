import struct
import os

BASE = r'Octopath_Traveler0\Content\Paks\pakchunk0-Windows\Octopath_Traveler0\Content\Local\DataBase\GameText\Localize\EN-US'

# Start with a small file
for subdir in ['SystemText', 'TalkText']:
    full_dir = os.path.join(BASE, subdir)
    if not os.path.exists(full_dir):
        continue
    for fname in sorted(os.listdir(full_dir)):
        if not fname.endswith('.uexp'):
            continue
        fpath = os.path.join(full_dir, fname)
        fsize = os.path.getsize(fpath)
        print(f"\n{'='*70}")
        print(f"FILE: {fname} ({fsize:,} bytes)")
        print(f"{'='*70}")
        
        with open(fpath, 'rb') as f:
            data = f.read()
        
        # Hex dump first 256 bytes
        print(f"\nHex dump (first 320 bytes):")
        for i in range(0, min(320, len(data)), 16):
            hex_part = ' '.join(f'{b:02x}' for b in data[i:i+16])
            ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
            print(f'  {i:04x}: {hex_part:<48s}  {ascii_part}')
        
        # Find FString patterns (int32 length + UTF-8 data + null terminator)
        print(f"\nStrings found:")
        strings_found = []
        i = 0
        while i < len(data) - 4:
            str_len = struct.unpack_from('<i', data, i)[0]
            if 2 < str_len < 2000 and i + 4 + str_len <= len(data):
                try:
                    raw = data[i+4:i+4+str_len]
                    if raw[-1:] == b'\x00':  # null terminated
                        s = raw[:-1].decode('utf-8', errors='strict')
                        if len(s) > 1 and s.isprintable():
                            strings_found.append((i, s))
                            i += 4 + str_len
                            continue
                except:
                    pass
            i += 1
        
        for offset, s in strings_found[:50]:
            display = s[:100] + ('...' if len(s) > 100 else '')
            print(f'  0x{offset:04x}: "{display}"')
        
        if len(strings_found) > 50:
            print(f'  ... and {len(strings_found) - 50} more strings')
        print(f"  Total strings: {len(strings_found)}")
        
        # Only analyze first 2 files in detail
        if fsize > 10000:
            break
    break  # Only first subdir for now
