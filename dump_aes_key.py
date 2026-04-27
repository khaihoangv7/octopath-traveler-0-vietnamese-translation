"""
AES Key Dumper v3 - FAST version.
Uses a 2-step filter: 
  1. Quick: decrypt 1 block (16 bytes), check mount point format
  2. Full: only if quick passes, decrypt all 3.8MB and verify SHA1
This is ~1000x faster than checking SHA1 for every candidate.
"""
import ctypes
import ctypes.wintypes
import struct
import hashlib
import sys
import os
import time
from Crypto.Cipher import AES

PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400
MEM_COMMIT = 0x1000
PAGE_READWRITE = 0x04
PAGE_READONLY = 0x02
PAGE_EXECUTE_READ = 0x20
PAGE_EXECUTE_READWRITE = 0x40
PAGE_WRITECOPY = 0x08
PAGE_EXECUTE_WRITECOPY = 0x80
READABLE_PAGES = (PAGE_READWRITE, PAGE_READONLY, PAGE_EXECUTE_READ, 
                  PAGE_EXECUTE_READWRITE, PAGE_WRITECOPY, PAGE_EXECUTE_WRITECOPY)

class MEMORY_BASIC_INFORMATION64(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_uint64),
        ("AllocationBase", ctypes.c_uint64),
        ("AllocationProtect", ctypes.wintypes.DWORD),
        ("__alignment1", ctypes.wintypes.DWORD),
        ("RegionSize", ctypes.c_uint64),
        ("State", ctypes.wintypes.DWORD),
        ("Protect", ctypes.wintypes.DWORD),
        ("Type", ctypes.wintypes.DWORD),
        ("__alignment2", ctypes.wintypes.DWORD),
    ]

PAK_PATH = r'D:\Game\Steam\steamapps\common\Octopath_Traveler0\Octopath_Traveler0\Content\Paks\pakchunk0-Windows.pak'

def get_pak_info():
    with open(PAK_PATH, 'rb') as f:
        f.seek(-300, 2)
        footer = f.read(300)
    magic_pos = footer.find(b'\xE1\x12\x6F\x5A')
    pos = magic_pos + 4
    version = struct.unpack_from('<I', footer, pos)[0]; pos += 4
    index_offset = struct.unpack_from('<Q', footer, pos)[0]; pos += 8
    index_size = struct.unpack_from('<Q', footer, pos)[0]; pos += 8
    index_hash = footer[pos:pos+20]
    with open(PAK_PATH, 'rb') as f:
        f.seek(index_offset)
        first_block = f.read(16)
        f.seek(index_offset)
        full_index = f.read(index_size)
    padded_size = ((len(full_index) + 15) // 16) * 16
    full_index += b'\x00' * (padded_size - len(full_index))
    return index_hash, first_block, full_index, index_size

def find_process(name):
    import subprocess
    result = subprocess.run(['tasklist', '/FI', f'IMAGENAME eq {name}', '/FO', 'CSV', '/NH'],
                          capture_output=True, text=True)
    for line in result.stdout.strip().split('\n'):
        if name.lower() in line.lower():
            parts = line.strip('"').split('","')
            if len(parts) >= 2:
                return int(parts[1])
    return None

def quick_check(key_bytes, first_encrypted_block):
    """FAST check: decrypt just 16 bytes, see if it looks like a mount point."""
    try:
        cipher = AES.new(key_bytes, AES.MODE_ECB)
        dec = cipher.decrypt(first_encrypted_block)
        val = struct.unpack('<i', dec[:4])[0]
        # Mount point string length: positive=UTF8, negative=UTF16
        if val > 0 and val < 512:
            remaining = dec[4:min(4 + val, 16)]
            if len(remaining) > 0 and all(b == 0 or (32 <= b < 127) for b in remaining):
                return True
        elif val < 0 and val > -512:
            return True
    except:
        pass
    return False

def full_verify(key_bytes, full_index, index_size, index_hash):
    """SLOW but definitive: decrypt full index and check SHA1."""
    cipher = AES.new(key_bytes, AES.MODE_ECB)
    decrypted = b''
    for i in range(0, len(full_index), 16):
        block = full_index[i:i+16]
        if len(block) == 16:
            decrypted += cipher.decrypt(block)
    actual_hash = hashlib.sha1(decrypted[:index_size]).digest()
    return actual_hash == index_hash

def scan_memory(pid, first_block, full_index, index_size, index_hash):
    kernel32 = ctypes.windll.kernel32
    kernel32.OpenProcess.restype = ctypes.wintypes.HANDLE
    kernel32.OpenProcess.argtypes = [ctypes.wintypes.DWORD, ctypes.wintypes.BOOL, ctypes.wintypes.DWORD]
    kernel32.VirtualQueryEx.restype = ctypes.c_size_t
    kernel32.VirtualQueryEx.argtypes = [ctypes.wintypes.HANDLE, ctypes.c_uint64,
                                        ctypes.POINTER(MEMORY_BASIC_INFORMATION64), ctypes.c_size_t]
    kernel32.ReadProcessMemory.restype = ctypes.wintypes.BOOL
    kernel32.ReadProcessMemory.argtypes = [ctypes.wintypes.HANDLE, ctypes.c_uint64,
                                           ctypes.c_void_p, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]

    process = kernel32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, pid)
    if not process:
        print(f"  ERROR: Cannot open process. Run as Administrator!")
        return None

    print(f"  Opened process {pid}")
    mbi = MEMORY_BASIC_INFORMATION64()
    addr = 0
    regions = 0
    total_mb = 0
    candidates = 0
    quick_hits = 0
    start_time = time.time()

    try:
        while True:
            ret = kernel32.VirtualQueryEx(process, ctypes.c_uint64(addr),
                                         ctypes.byref(mbi), ctypes.sizeof(mbi))
            if ret == 0:
                break

            base = mbi.BaseAddress
            size = mbi.RegionSize
            if size == 0:
                break

            if (mbi.State == MEM_COMMIT and mbi.Protect in READABLE_PAGES
                    and 0 < size < 256 * 1024 * 1024):
                try:
                    buf = (ctypes.c_char * size)()
                    n = ctypes.c_size_t(0)
                    ok = kernel32.ReadProcessMemory(process, ctypes.c_uint64(base),
                                                    buf, size, ctypes.byref(n))
                    if ok and n.value > 31:
                        data = bytes(buf[:n.value])
                        regions += 1
                        total_mb += len(data) / (1024 * 1024)

                        elapsed = time.time() - start_time
                        if regions % 20 == 0:
                            print(f"\r    [{elapsed:.0f}s] {regions} regions, {total_mb:.0f} MB scanned, {candidates} candidates, {quick_hits} quick hits", end='', flush=True)

                        for i in range(0, len(data) - 31, 16):
                            cand = data[i:i+32]
                            if len(set(cand)) < 8:
                                continue
                            candidates += 1

                            # FAST check first (microseconds)
                            if quick_check(cand, first_block):
                                quick_hits += 1
                                elapsed = time.time() - start_time
                                print(f"\n    [{elapsed:.0f}s] Quick hit #{quick_hits} at 0x{base+i:X}: {cand.hex()}")
                                print(f"    Verifying SHA1 (this takes a few seconds)...")

                                if full_verify(cand, full_index, index_size, index_hash):
                                    print(f"    SHA1 VERIFIED!")
                                    return cand.hex()
                                else:
                                    print(f"    False positive, continuing...")
                except Exception as e:
                    pass

            next_addr = base + size
            if next_addr <= addr:
                break
            addr = next_addr

    finally:
        kernel32.CloseHandle(process)

    elapsed = time.time() - start_time
    print(f"\n    Done in {elapsed:.0f}s: {regions} regions, {total_mb:.0f} MB, {candidates} candidates, {quick_hits} quick hits")
    return None

def main():
    print("=" * 60)
    print("  AES Key Memory Dumper v3 (FAST)")
    print("=" * 60)

    for name in ['Octopath_Traveler0-Win64-Shipping.exe', 'Octopath_Traveler0.exe']:
        pid = find_process(name)
        if pid:
            print(f"\nFound: {name} (PID {pid})")
            break
    else:
        print("\nGame is not running! Start the game first.")
        sys.exit(1)

    print("\nReading PAK info...")
    index_hash, first_block, full_index, index_size = get_pak_info()
    print(f"  Target SHA1: {index_hash.hex()}")

    print(f"\nScanning memory (should take 1-3 minutes)...\n")
    key = scan_memory(pid, first_block, full_index, index_size, index_hash)

    if key:
        print(f"\n{'='*60}")
        print(f"  SUCCESS! Key: 0x{key}")
        print(f"{'='*60}")
        with open('aes_key.txt', 'w') as f:
            f.write(f'0x{key}\n')
        print(f"  Saved to aes_key.txt")
        print(f"\n  Extract with:")
        print(f'  .\\repak_cli\\repak.exe --aes-key 0x{key} unpack "Octopath_Traveler0\\Content\\Paks\\pakchunk0-Windows.pak" "extracted"')
    else:
        print("\n  Key not found. Make sure game is fully loaded and run as Admin.")

if __name__ == '__main__':
    main()
