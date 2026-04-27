import os
import struct

# Check file sizes
pak = r'Octopath_Traveler0\Content\Paks\pakchunk0-Windows.pak'
exe = r'Octopath_Traveler0.exe'
print(f'PAK size: {os.path.getsize(pak):,} bytes')
print(f'EXE size: {os.path.getsize(exe):,} bytes')

# Check the exe for game name strings
with open(exe, 'rb') as f:
    data = f.read()
    for pattern in [b'Octopath', b'OCTOPATH', b'CottonGame', b'4.18', b'4.25', b'4.26', b'4.27', b'UE4', b'EngineVersion']:
        idx = data.find(pattern)
        if idx >= 0:
            context = data[max(0,idx-20):idx+60]
            printable = ''.join(chr(b) if 32 <= b < 127 else '.' for b in context)
            print(f'Found "{pattern.decode()}" at offset {idx}: ...{printable}...')

# Read PAK footer more carefully
print('\n--- PAK Footer Analysis ---')
with open(pak, 'rb') as f:
    # Try footer at -221 (v11 with encryption guid + frozen index)
    for offset in [-44, -45, -204, -205, -221, -222, -225]:
        f.seek(offset, 2)
        footer = f.read(-offset)
        magic_pos = footer.find(b'\xE1\x12\x6F\x5A')
        if magic_pos >= 0:
            version = struct.unpack_from('<I', footer, magic_pos + 4)[0]
            idx_offset = struct.unpack_from('<Q', footer, magic_pos + 8)[0] if len(footer) > magic_pos + 16 else None
            idx_size = struct.unpack_from('<Q', footer, magic_pos + 16)[0] if len(footer) > magic_pos + 24 else None
            sha1 = footer[magic_pos + 24:magic_pos + 44].hex() if len(footer) > magic_pos + 44 else None
            
            # Check for encryption guid before magic
            if magic_pos >= 20:
                enc_guid = footer[magic_pos-20:magic_pos-4].hex()
                enc_flag = footer[magic_pos-4] if magic_pos >= 4 else None
                print(f'Footer offset {offset}: magic at pos {magic_pos}')
                print(f'  Version: {version}')
                print(f'  Index offset: {idx_offset}')
                print(f'  Index size: {idx_size}')
                print(f'  Possible enc_guid before magic: {enc_guid}')
                print(f'  Possible enc_flag: {enc_flag}')
            else:
                print(f'Footer offset {offset}: magic at pos {magic_pos}, version {version}')
