"""
Decrypt PAK index and extract file list manually.
Since repak crashes on UTF-16, we'll handle it ourselves.
"""
import struct
from Crypto.Cipher import AES
import hashlib

PAK_PATH = r'Octopath_Traveler0\Content\Paks\pakchunk0-Windows.pak'

# Keys found
KEYS = [
    bytes.fromhex('4863c9c5fa11748e04f6c2200f8475fdffffc4e37916e9014863c9c4e3791774'),
    bytes.fromhex('c4e2352c0c02c4e27d185f04c4e275b8d3c4c27d1823f6851006000001c5fc29'),
]

def decrypt_ecb(key, data):
    """Decrypt data using AES-256-ECB."""
    cipher = AES.new(key, AES.MODE_ECB)
    result = b''
    for i in range(0, len(data), 16):
        block = data[i:i+16]
        if len(block) == 16:
            result += cipher.decrypt(block)
        else:
            result += block
    return result

def read_fstring(data, pos):
    """Read UE4 FString from binary data."""
    str_len = struct.unpack_from('<i', data, pos)[0]
    pos += 4
    if str_len == 0:
        return '', pos
    
    if str_len < 0:
        # UTF-16 encoded
        char_count = -str_len
        raw = data[pos:pos + char_count * 2]
        text = raw.decode('utf-16le', errors='replace').rstrip('\x00')
        pos += char_count * 2
    else:
        # UTF-8/ASCII
        raw = data[pos:pos + str_len]
        text = raw.decode('utf-8', errors='replace').rstrip('\x00')
        pos += str_len
    
    return text, pos

def main():
    # Read PAK footer
    with open(PAK_PATH, 'rb') as f:
        f.seek(-300, 2)
        footer_data = f.read(300)
    
    magic_pos = footer_data.find(b'\xE1\x12\x6F\x5A')
    pos = magic_pos + 4
    version = struct.unpack_from('<I', footer_data, pos)[0]; pos += 4
    index_offset = struct.unpack_from('<Q', footer_data, pos)[0]; pos += 8
    index_size = struct.unpack_from('<Q', footer_data, pos)[0]; pos += 8
    index_hash = footer_data[pos:pos+20]
    
    print(f"PAK Version: {version}")
    print(f"Index Offset: {index_offset}")
    print(f"Index Size: {index_size}")
    
    # Read encrypted index
    with open(PAK_PATH, 'rb') as f:
        f.seek(index_offset)
        encrypted_index = f.read(index_size)
    
    print(f"Read {len(encrypted_index)} bytes of encrypted index")
    
    # Pad to 16 byte boundary for AES
    padded_size = ((len(encrypted_index) + 15) // 16) * 16
    if len(encrypted_index) < padded_size:
        encrypted_index += b'\x00' * (padded_size - len(encrypted_index))
    
    for key_idx, key in enumerate(KEYS):
        print(f"\n{'='*60}")
        print(f"Testing Key {key_idx + 1}: 0x{key.hex()}")
        print(f"{'='*60}")
        
        decrypted = decrypt_ecb(key, encrypted_index)
        
        # Verify SHA1
        actual_hash = hashlib.sha1(decrypted[:index_size]).digest()
        if actual_hash == index_hash:
            print("✅ SHA1 MATCH! This is the correct key!")
        else:
            print(f"❌ SHA1 mismatch")
            print(f"  Expected: {index_hash.hex()}")
            print(f"  Got:      {actual_hash.hex()}")
        
        # Try to parse the mount point
        print(f"\nFirst 64 bytes (hex): {decrypted[:64].hex()}")
        print(f"First 64 bytes (raw): {decrypted[:64]}")
        
        try:
            mount_point, pos = read_fstring(decrypted, 0)
            print(f"\nMount Point: '{mount_point}'")
            
            # Next should be the record count
            record_count = struct.unpack_from('<I', decrypted, pos)[0]
            pos += 4
            print(f"Record Count: {record_count}")
            
            if record_count > 0 and record_count < 1000000:
                print(f"\nFirst 20 files:")
                files_found = []
                for i in range(min(record_count, 20)):
                    try:
                        filename, pos = read_fstring(decrypted, pos)
                        files_found.append(filename)
                        
                        # Skip record data (offset, size, uncomp_size, compr_method, hash, etc.)
                        # V11 record: offset(8) + comp_size(8) + uncomp_size(8) + compr_method(4) + sha1(20) = 48
                        # Plus possible compression blocks + encrypted flag(1) + block_size(4)
                        
                        # Read the record header inline
                        rec_offset = struct.unpack_from('<Q', decrypted, pos)[0]; pos += 8
                        comp_size = struct.unpack_from('<Q', decrypted, pos)[0]; pos += 8
                        uncomp_size = struct.unpack_from('<Q', decrypted, pos)[0]; pos += 8
                        compr_method = struct.unpack_from('<I', decrypted, pos)[0]; pos += 4
                        sha1 = decrypted[pos:pos+20]; pos += 20
                        
                        if compr_method != 0:
                            block_count = struct.unpack_from('<I', decrypted, pos)[0]; pos += 4
                            pos += block_count * 16  # skip blocks
                        
                        encrypted_flag = decrypted[pos]; pos += 1
                        block_size = struct.unpack_from('<I', decrypted, pos)[0]; pos += 4
                        
                        print(f"  {i+1}. {filename} (size: {uncomp_size:,}, compr: {compr_method})")
                        
                    except Exception as e:
                        print(f"  Error parsing record {i}: {e}")
                        # Show hex around current position
                        print(f"  Hex at pos {pos}: {decrypted[pos:pos+32].hex()}")
                        break
                        
        except Exception as e:
            print(f"Parse error: {e}")
            # Dump more raw data for analysis
            for off in range(0, min(256, len(decrypted)), 16):
                hex_str = decrypted[off:off+16].hex()
                ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in decrypted[off:off+16])
                print(f"  {off:4X}: {hex_str}  {ascii_str}")

if __name__ == '__main__':
    main()
