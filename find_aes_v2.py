"""
Improved AES Key Finder - validates against SHA1 hash of decrypted index.
This is the reliable way: decrypt with candidate key, check if SHA1 matches.
"""
import struct
import hashlib
import os
import sys
import re
from Crypto.Cipher import AES

PAK_PATH = r'Octopath_Traveler0\Content\Paks\pakchunk0-Windows.pak'
EXE_PATH = r'Octopath_Traveler0\Binaries\Win64\Octopath_Traveler0-Win64-Shipping.exe'

def read_pak_info(pak_path):
    with open(pak_path, 'rb') as f:
        f.seek(-300, 2)
        footer = f.read(300)
    
    magic_pos = footer.find(b'\xE1\x12\x6F\x5A')
    pos = magic_pos + 4
    version = struct.unpack_from('<I', footer, pos)[0]; pos += 4
    index_offset = struct.unpack_from('<Q', footer, pos)[0]; pos += 8
    index_size = struct.unpack_from('<Q', footer, pos)[0]; pos += 8
    index_hash = footer[pos:pos+20]
    
    with open(pak_path, 'rb') as f:
        f.seek(index_offset)
        # Read first 16 bytes (1 AES block) for quick test
        first_block = f.read(16)
        # Read full index for SHA1 verification
        f.seek(index_offset)
        full_index = f.read(index_size)
    
    return index_hash, first_block, full_index, index_size

def decrypt_block(key, block):
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.decrypt(block)

def decrypt_full(key, data):
    cipher = AES.new(key, AES.MODE_ECB)
    result = b''
    for i in range(0, len(data), 16):
        block = data[i:i+16]
        if len(block) == 16:
            result += cipher.decrypt(block)
        else:
            result += block
    return result

def quick_test(key, first_block):
    """Quick test: decrypt first block, check if it looks like a valid mount point."""
    dec = decrypt_block(key, first_block)
    str_len = struct.unpack('<i', dec[:4])[0]
    
    # Mount point: positive means UTF-8, negative means UTF-16
    if str_len > 0 and str_len < 512:
        # Check if remaining bytes are valid ASCII path chars
        remaining = dec[4:min(4 + str_len, 16)]
        if len(remaining) > 0 and all(b == 0 or (32 <= b < 127) for b in remaining):
            # Extra check: typical mount points start with "../../../" or "/"
            path_start = remaining.decode('ascii', errors='replace').rstrip('\x00')
            if path_start.startswith(('../', '/', '..\\')) or len(path_start) == 0:
                return True
    
    if str_len < 0 and str_len > -512:
        char_count = -str_len
        remaining = dec[4:min(4 + char_count * 2, 16)]
        try:
            text = remaining.decode('utf-16le', errors='strict')
            if all(c == '\x00' or (32 <= ord(c) < 127) for c in text):
                return True
        except:
            pass
    
    return False

def full_verify(key, full_index, index_size, expected_hash):
    """Full verification: decrypt entire index and check SHA1."""
    padded_size = ((len(full_index) + 15) // 16) * 16
    padded = full_index + b'\x00' * (padded_size - len(full_index))
    decrypted = decrypt_full(key, padded)
    actual_hash = hashlib.sha1(decrypted[:index_size]).digest()
    return actual_hash == expected_hash

def main():
    print("=" * 60)
    print("  Improved AES Key Finder (SHA1 Validated)")
    print("=" * 60)
    
    print("\nReading PAK file...")
    index_hash, first_block, full_index, index_size = read_pak_info(PAK_PATH)
    print(f"  Index Hash (target): {index_hash.hex()}")
    print(f"  Index Size: {index_size:,}")
    print(f"  First encrypted block: {first_block.hex()}")
    
    # Pad full index for AES
    padded_size = ((len(full_index) + 15) // 16) * 16
    full_index_padded = full_index + b'\x00' * (padded_size - len(full_index))
    
    exe_size = os.path.getsize(EXE_PATH)
    print(f"\nScanning {EXE_PATH} ({exe_size:,} bytes)...")
    print("Testing every possible 32-byte key with quick filter + SHA1 validation...")
    print("This may take 10-30 minutes for a 428MB file...\n")
    
    # Strategy: 
    # 1. Read exe in chunks
    # 2. For each 32-byte aligned candidate, do quick_test
    # 3. If quick_test passes, do full SHA1 verification
    
    candidates_tested = 0
    quick_passes = 0
    
    with open(EXE_PATH, 'rb') as f:
        # Read entire exe into memory (428MB should be fine)
        print("  Loading executable into memory...")
        exe_data = f.read()
    
    print(f"  Loaded {len(exe_data):,} bytes")
    print(f"  Scanning...\n")
    
    # Scan at every byte offset (thorough but slow)
    # Optimize: scan at 4-byte or 16-byte alignment first
    for alignment in [16, 4, 1]:
        if alignment == 1:
            print(f"\n  Phase 3: Scanning at every byte offset (this is slow)...")
        elif alignment == 4:
            print(f"\n  Phase 2: Scanning at 4-byte alignment...")
        else:
            print(f"  Phase 1: Scanning at 16-byte alignment...")
        
        for i in range(0, len(exe_data) - 31, alignment):
            if i % (10 * 1024 * 1024) == 0:
                pct = int(i / len(exe_data) * 100)
                print(f"\r    Progress: {pct}% (offset 0x{i:X}, {candidates_tested} tested, {quick_passes} quick passes)", end='', flush=True)
            
            candidate = exe_data[i:i+32]
            
            # Skip boring patterns
            if len(set(candidate)) < 8:
                continue
            
            candidates_tested += 1
            
            if quick_test(candidate, first_block):
                quick_passes += 1
                print(f"\n    Quick test passed at 0x{i:X}: {candidate.hex()}")
                print(f"    Verifying with SHA1 (decrypting {index_size:,} bytes)...")
                
                if full_verify(candidate, full_index_padded, index_size, index_hash):
                    print(f"\n    *** SHA1 VERIFIED! CORRECT KEY FOUND! ***")
                    print(f"\n{'='*60}")
                    print(f"  AES KEY: 0x{candidate.hex()}")
                    print(f"  Offset:  0x{i:X}")
                    print(f"{'='*60}")
                    print(f"\n  Use with repak:")
                    print(f'  .\\repak_cli\\repak.exe --aes-key 0x{candidate.hex()} unpack "Octopath_Traveler0\\Content\\Paks\\pakchunk0-Windows.pak" "extracted"')
                    
                    # Save key to file
                    with open('aes_key.txt', 'w') as kf:
                        kf.write(f'0x{candidate.hex()}\n')
                    print(f"\n  Key saved to aes_key.txt")
                    return
                else:
                    print(f"    SHA1 mismatch - false positive")
        
        print(f"\r    Phase complete. Tested: {candidates_tested}, Quick passes: {quick_passes}            ")
    
    print(f"\n\n  No valid AES key found in the executable.")
    print(f"  Total candidates tested: {candidates_tested}")
    print(f"  Quick test passes: {quick_passes}")
    print(f"\n  Suggestions:")
    print(f"  1. The key may be computed at runtime (not stored as-is)")
    print(f"  2. Try using FModel which can detect keys from its database")
    print(f"  3. Try AESDumpster on the game while it's running")

if __name__ == '__main__':
    main()
