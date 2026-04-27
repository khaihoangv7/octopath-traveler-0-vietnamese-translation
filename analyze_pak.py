import struct

pak_path = r'Octopath_Traveler0\Content\Paks\pakchunk0-Windows.pak'

with open(pak_path, 'rb') as f:
    file_size = f.seek(0, 2)
    print(f"PAK file size: {file_size:,} bytes")
    
    # V11 footer is at the very end. The footer format is:
    # EncryptionKeyGuid (16 bytes)
    # IsEncrypted (1 byte) 
    # Magic (4 bytes) = 0x5A6F12E1
    # Version (4 bytes) = 11
    # IndexOffset (8 bytes)
    # IndexSize (8 bytes) 
    # IndexHash (20 bytes)
    # FrozenIndex (1 byte) - v9+
    # CompressionMethods (string array) - v8a+
    # Total footer = 16 + 1 + 4 + 4 + 8 + 8 + 20 + 1 + ... 
    
    # Read last 300 bytes to be safe
    f.seek(-300, 2)
    data = f.read(300)
    
    # Find magic
    magic_pos = data.find(b'\xE1\x12\x6F\x5A')
    if magic_pos < 0:
        print("Magic not found!")
        exit()
    
    print(f"\nMagic found at position {magic_pos} (from end: {300 - magic_pos})")
    
    # Parse V11 footer structure starting from magic
    pos = magic_pos
    magic = struct.unpack_from('<I', data, pos)[0]
    pos += 4
    version = struct.unpack_from('<I', data, pos)[0]
    pos += 4
    index_offset = struct.unpack_from('<Q', data, pos)[0]
    pos += 8
    index_size = struct.unpack_from('<Q', data, pos)[0]
    pos += 8
    index_hash = data[pos:pos+20]
    pos += 20
    
    print(f"Magic: 0x{magic:08X}")
    print(f"Version: {version}")
    print(f"Index Offset: {index_offset}")
    print(f"Index Size: {index_size}")
    print(f"Index Hash: {index_hash.hex()}")
    
    # What's before magic in V11:
    # FrozenIndex (1 byte) - for v9+
    # CompressionMethods - for v8a+
    # IsEncrypted (1 byte) - for v3+
    # EncryptionKeyGuid (16 bytes) - for v7+
    
    # Let's look at what's before magic
    print(f"\n--- Data before magic ---")
    before = data[:magic_pos]
    print(f"Bytes before magic ({len(before)} bytes):")
    print(f"Hex: {before.hex()}")
    
    # Typically: ...compression_methods... | enc_guid(16) | is_encrypted(1) | magic
    if len(before) >= 17:
        is_encrypted = before[-1]
        enc_guid = before[-17:-1]
        print(f"\nEncryption GUID (last 16 before flag): {enc_guid.hex()}")
        print(f"IsEncrypted flag: {is_encrypted}")
        
        # What's even before that?
        remaining = before[:-17]
        print(f"\nRemaining bytes before guid ({len(remaining)}):")
        print(f"Hex: {remaining.hex()}")
        
    # After index_hash, check for frozen index and compression methods
    rest = data[pos:]
    print(f"\n--- Data after index_hash ({len(rest)} bytes) ---")
    print(f"Hex: {rest.hex()}")
    
    # For V8A+, after the standard footer we have:
    # FrozenIndex (1 byte)
    # CompressionMethodNames - 32*5 bytes = 160 bytes for V11
    
    if len(rest) > 0:
        frozen_index = rest[0]
        print(f"\nFrozenIndex: {frozen_index}")
        
    if len(rest) > 1:
        compression_data = rest[1:]
        # Compression methods are stored as 32-byte strings, up to 5
        print(f"\nCompression method data ({len(compression_data)} bytes):")
        for i in range(0, min(len(compression_data), 160), 32):
            chunk = compression_data[i:i+32]
            name = chunk.split(b'\x00')[0].decode('ascii', errors='replace')
            if name:
                print(f"  Method {i//32}: '{name}'")
