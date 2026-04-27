import struct
import re

exe_path = r'Octopath_Traveler0\Binaries\Win64\Octopath_Traveler0-Win64-Shipping.exe'

print(f"Scanning {exe_path} for encryption-related strings...")

chunk_size = 64 * 1024 * 1024  # 64MB chunks

with open(exe_path, 'rb') as f:
    offset = 0
    results = []
    while True:
        data = f.read(chunk_size)
        if not data:
            break
        
        for pattern in [b'encrypt', b'Encrypt', b'ENCRYPT', b'aes', b'AES', 
                        b'DecryptionKey', b'PakEncryptionKey', b'FPakPlatformFile',
                        b'CryptoKeys', b'EncryptionKey']:
            idx = 0
            while True:
                idx = data.find(pattern, idx)
                if idx < 0:
                    break
                ctx_start = max(0, idx - 30)
                ctx_end = min(len(data), idx + 120)
                ctx = data[ctx_start:ctx_end]
                printable = ''.join(chr(b) if 32 <= b < 127 else '.' for b in ctx)
                results.append(f"  Found '{pattern.decode()}' at 0x{offset + idx:X}: ...{printable}...")
                idx += len(pattern)
        
        offset += len(data)

print(f"Found {len(results)} references")
for r in results[:50]:
    print(r)

# Also try to find UE version string
print("\n--- Searching for engine version ---")
with open(exe_path, 'rb') as f:
    offset = 0
    while True:
        data = f.read(chunk_size)
        if not data:
            break
        
        for pattern in [b'+UE4', b'4.1', b'4.2', b'4.3', b'EngineVersion', b'CottonGame']:
            idx = 0
            while True:
                idx = data.find(pattern, idx)
                if idx < 0:
                    break
                ctx_start = max(0, idx - 10)
                ctx_end = min(len(data), idx + 80)
                ctx = data[ctx_start:ctx_end]
                printable = ''.join(chr(b) if 32 <= b < 127 else '.' for b in ctx)
                print(f"  '{pattern.decode()}' at 0x{offset + idx:X}: ...{printable}...")
                idx += len(pattern)
                break  # Just first occurrence per chunk
        
        offset += len(data)
