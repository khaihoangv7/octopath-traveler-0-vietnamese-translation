"""Find where MessagePack data starts in the .uexp file."""
import struct
import msgpack

path = r'Octopath_Traveler0\Content\Paks\pakchunk0-Windows\Octopath_Traveler0\Content\Local\DataBase\GameText\Localize\EN-US\SystemText\GameTextPC.uexp'

with open(path, 'rb') as f:
    data = f.read()

print(f"File size: {len(data)} bytes")
print(f"\nFull hex dump (file is only {len(data)} bytes):")
for i in range(0, min(len(data), 900), 16):
    hex_part = ' '.join(f'{b:02x}' for b in data[i:i+16])
    ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
    print(f'  {i:04x}: {hex_part:<48s}  {ascii_part}')

# Try msgpack at every offset
print(f"\nTrying msgpack.unpackb at every offset 0-100:")
for offset in range(0, min(100, len(data))):
    try:
        result = msgpack.unpackb(data[offset:], raw=False, strict_map_key=False)
        print(f"  SUCCESS at offset {offset}!")
        print(f"  Type: {type(result).__name__}")
        if isinstance(result, dict):
            print(f"  Keys: {list(result.keys())[:10]}")
        elif isinstance(result, list):
            print(f"  Length: {len(result)}")
            if len(result) > 0:
                print(f"  First item type: {type(result[0]).__name__}")
                if isinstance(result[0], dict):
                    print(f"  First item keys: {list(result[0].keys())}")
        break
    except Exception as e:
        if offset < 10:
            print(f"  offset {offset}: {type(e).__name__}: {str(e)[:60]}")

# Also try: maybe the header is a UE4 custom serialization header
# Let's look at what bytes 0-3 mean
print(f"\nFirst 4 bytes as int32: {struct.unpack_from('<I', data, 0)[0]}")
print(f"Bytes 4-7 as int32: {struct.unpack_from('<I', data, 4)[0]}")

# The hex dump showed: 00 00 00 00 00 03 f6 5c
# First 4 bytes = 0 (could be UE4 None export)
# Bytes 4-7 = 0x005cf603 = could be size or tag

# Look for msgpack map marker (0x80-0x8f = fixmap, 0xde = map16, 0xdf = map32)
print(f"\nSearching for msgpack markers:")
for i in range(len(data)):
    b = data[i]
    if b == 0x82:  # fixmap with 2 entries (m_DataList structure has 2 keys often)
        # Check if next bytes could be a key string
        if i+1 < len(data) and (0xa0 <= data[i+1] <= 0xbf):  # fixstr
            str_len = data[i+1] - 0xa0
            if i+2+str_len <= len(data):
                try:
                    key = data[i+2:i+2+str_len].decode('ascii')
                    if key.startswith('m_'):
                        print(f"  Offset 0x{i:04x}: fixmap(2) with key '{key}'")
                        # Try parsing from here
                        try:
                            result = msgpack.unpackb(data[i:], raw=False, strict_map_key=False)
                            print(f"    -> PARSED! Type: {type(result).__name__}")
                            if isinstance(result, dict):
                                for k, v in result.items():
                                    if isinstance(v, list):
                                        print(f"    -> {k}: list of {len(v)} items")
                                        if len(v) > 0 and isinstance(v[0], dict):
                                            print(f"       First item: {v[0]}")
                                    else:
                                        print(f"    -> {k}: {type(v).__name__}")
                            break
                        except Exception as e:
                            print(f"    -> Parse failed: {e}")
                except:
                    pass
