"""
AES Key Finder for Unreal Engine games.
Scans the game executable for potential AES-256 keys by looking for
byte patterns that could be encryption keys and testing them against
the PAK file's encrypted index.
"""
import struct
import hashlib
import os
import sys

try:
    from Crypto.Cipher import AES
    HAS_CRYPTO = True
except ImportError:
    try:
        from Cryptodome.Cipher import AES
        HAS_CRYPTO = True
    except ImportError:
        HAS_CRYPTO = False

PAK_PATH = r'Octopath_Traveler0\Content\Paks\pakchunk0-Windows.pak'
EXE_PATH = r'Octopath_Traveler0\Binaries\Win64\Octopath_Traveler0-Win64-Shipping.exe'

def read_pak_footer(pak_path):
    """Read PAK v11 footer to get index info for key validation."""
    with open(pak_path, 'rb') as f:
        f.seek(-300, 2)
        data = f.read(300)
    
    magic_pos = data.find(b'\xE1\x12\x6F\x5A')
    if magic_pos < 0:
        print("ERROR: PAK magic not found")
        sys.exit(1)
    
    pos = magic_pos + 4  # skip magic
    version = struct.unpack_from('<I', data, pos)[0]; pos += 4
    index_offset = struct.unpack_from('<Q', data, pos)[0]; pos += 8
    index_size = struct.unpack_from('<Q', data, pos)[0]; pos += 8
    index_hash = data[pos:pos+20]; pos += 20
    
    # IsEncrypted is 1 byte before magic, enc_guid is 16 bytes before that
    is_encrypted = data[magic_pos - 1]
    enc_guid = data[magic_pos - 17:magic_pos - 1]
    
    print(f"PAK Version: {version}")
    print(f"Index Offset: {index_offset}")
    print(f"Index Size: {index_size}")
    print(f"Index Hash (SHA1): {index_hash.hex()}")
    print(f"IsEncrypted: {is_encrypted}")
    print(f"Encryption GUID: {enc_guid.hex()}")
    
    return {
        'version': version,
        'index_offset': index_offset,
        'index_size': index_size,
        'index_hash': index_hash,
        'is_encrypted': is_encrypted,
    }

def read_encrypted_index(pak_path, footer):
    """Read the first block of the encrypted index for key testing."""
    with open(pak_path, 'rb') as f:
        f.seek(footer['index_offset'])
        # Read first 16 bytes (one AES block) for testing
        encrypted_block = f.read(min(footer['index_size'], 256))
    return encrypted_block

def test_aes_key(key_bytes, encrypted_data, footer):
    """Test if an AES key can decrypt the index correctly."""
    if not HAS_CRYPTO:
        return False
    
    try:
        cipher = AES.new(key_bytes, AES.MODE_ECB)
        decrypted = cipher.decrypt(encrypted_data[:16])
        
        # In UE4 PAK, the decrypted index starts with the mount point string
        # First 4 bytes = string length (little-endian int32)
        str_len = struct.unpack('<i', decrypted[:4])[0]
        
        # Valid mount point length should be reasonable (1-1024)
        if 1 <= str_len <= 1024:
            # Check if remaining bytes look like ASCII path characters
            remaining = decrypted[4:min(4+str_len, 16)]
            if all(32 <= b < 127 or b == 0 for b in remaining):
                return True
        
        # Also check for negative (UTF-16 indicator)
        if -1024 <= str_len <= -1:
            return True
            
    except Exception:
        pass
    
    return False

def scan_exe_for_keys(exe_path, encrypted_data, footer):
    """Scan exe for potential 32-byte AES keys."""
    file_size = os.path.getsize(exe_path)
    chunk_size = 64 * 1024 * 1024  # 64MB
    overlap = 32  # overlap to catch keys at chunk boundaries
    
    print(f"\nScanning {exe_path} ({file_size:,} bytes)...")
    print("This will take a few minutes...\n")
    
    found_keys = []
    
    with open(exe_path, 'rb') as f:
        offset = 0
        prev_tail = b''
        
        while offset < file_size:
            data = prev_tail + f.read(chunk_size)
            if not data:
                break
            
            progress = min(100, int((offset / file_size) * 100))
            print(f"\r  Progress: {progress}% ({offset:,} / {file_size:,})", end='', flush=True)
            
            # Strategy 1: Look for 32-byte sequences aligned to common boundaries
            # UE4 typically stores keys at aligned addresses
            for i in range(0, len(data) - 31, 1):
                candidate = data[i:i+32]
                
                # Skip all-zero or all-FF sequences
                if candidate == b'\x00' * 32 or candidate == b'\xFF' * 32:
                    continue
                
                # AES keys typically have high entropy
                # Quick entropy check: count unique bytes
                unique_bytes = len(set(candidate))
                if unique_bytes < 10:
                    continue
                
                if test_aes_key(candidate, encrypted_data, footer):
                    actual_offset = offset + i - len(prev_tail)
                    key_hex = candidate.hex()
                    print(f"\n\n*** FOUND AES KEY at offset 0x{actual_offset:X} ***")
                    print(f"  Hex:    0x{key_hex}")
                    
                    # Verify by decrypting more data
                    cipher = AES.new(candidate, AES.MODE_ECB)
                    full_decrypt = b''
                    for block_start in range(0, min(len(encrypted_data), 256), 16):
                        block = encrypted_data[block_start:block_start+16]
                        if len(block) == 16:
                            full_decrypt += cipher.decrypt(block)
                    
                    str_len = struct.unpack('<i', full_decrypt[:4])[0]
                    if str_len > 0:
                        mount_point = full_decrypt[4:4+str_len]
                        mount_str = mount_point.decode('utf-8', errors='replace').rstrip('\x00')
                        print(f"  Mount Point: '{mount_str}'")
                    
                    found_keys.append((actual_offset, key_hex))
                    
                    # Usually only one key, but keep scanning briefly
                    if len(found_keys) >= 3:
                        return found_keys
            
            prev_tail = data[-overlap:] if len(data) > overlap else data
            offset += chunk_size
    
    print(f"\r  Progress: 100%                              ")
    return found_keys

def main():
    print("=" * 60)
    print("  AES Key Finder for Octopath Traveler")
    print("=" * 60)
    
    if not HAS_CRYPTO:
        print("\nERROR: pycryptodome is required!")
        print("Install it with: pip install pycryptodome")
        sys.exit(1)
    
    print("\n--- PAK Footer Analysis ---")
    footer = read_pak_footer(PAK_PATH)
    
    if not footer['is_encrypted']:
        print("\nPAK is NOT encrypted! No AES key needed.")
        sys.exit(0)
    
    print("\n--- Reading Encrypted Index ---")
    encrypted_data = read_encrypted_index(PAK_PATH, footer)
    print(f"Read {len(encrypted_data)} bytes of encrypted index")
    print(f"First 16 bytes (encrypted): {encrypted_data[:16].hex()}")
    
    print("\n--- Scanning Executable for AES Keys ---")
    keys = scan_exe_for_keys(EXE_PATH, encrypted_data, footer)
    
    if keys:
        print(f"\n{'=' * 60}")
        print(f"  FOUND {len(keys)} KEY(S)!")
        print(f"{'=' * 60}")
        for offset, key_hex in keys:
            print(f"\n  Key: 0x{key_hex}")
            print(f"  Offset: 0x{offset:X}")
            print(f"\n  Use with repak:")
            print(f'  repak.exe --aes-key 0x{key_hex} list "path\\to\\pakchunk0-Windows.pak"')
    else:
        print("\n  No AES keys found in the executable.")
        print("  The key might be obfuscated or stored differently.")
        print("  Try using FModel which has a community key database.")

if __name__ == '__main__':
    main()
