"""
Translate all Octopath Traveler text from English to Vietnamese.
Processes each JSON file and creates translated versions.
"""
import json
import os
import re

INPUT_DIR = 'extracted_text'
OUTPUT_DIR = 'translated_text'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# TRANSLATION DICTIONARIES
# ============================================================

# GameTextPC - Job/Class names
TRANSLATE_PC = {
    0: "(Chưa dịch)",
    1: "Chiến Binh",
    2: "Dược Sư",
    3: "Đạo Tặc",
    4: "Học Giả",
    5: "Giáo Sĩ",
    6: "Thợ Săn",
    7: "Thương Nhân",
    8: "Vũ Công",
    11: "Lãnh Chúa",
    12: "Nữ Hoàng",
    13: "Quốc Vương",
    14: "Hiền Vương",
    15: "Đội Trưởng",
    16: "Kỵ Sĩ Ardante",
    17: "Hoàng Hậu",
    18: "Kiến Trúc Sư",
    19: "Học Giả Cait",
    20: "Lính Canh Lửa",
    21: "Tân Binh Tuần Tra",
    22: "Kiến Trúc Sư Tập Sự",
}

# GameTextGraphic - Battle/UI Graphics text
TRANSLATE_GRAPHIC = {
    1: "Kết Quả",
    2: "Lên Cấp",
    3: "Chí Mạng",
    4: "Trượt",
    5: "YẾU",
    6: "Hạ Gục",
    7: "Khiên Chắn",
    8: "BP",
    9: "SP",
    10: "PHÁ VỠ",
    11: "Kết Thúc",
    12: "Cấp Thị Trấn",
    13: "Danh Tiếng",
    14: "Tài Sản",
    15: "Sức Mạnh",
    18: "TẤT CẢ",
    19: "TẤT CẢ",
    20: "Hoàn Thành",
    21: "Đang tải...",
    22: "Thăng Hạng",
    23: "Hết",
    24: "Cảm ơn bạn đã đồng hành cùng chúng tôi.",
    25: "Ngươi - kẻ tìm kiếm tài sản - sẽ bắt đầu\nhành trình tại những cánh rừng xanh tươi của Vùng Rừng.\n\nTại đó, ngươi sẽ gặp gỡ\nHerminia, \"Phù Thủy Tham Lam.\"\n\nLòng tham vô đáy của bà ta đã nhuộm\nthị trấn Valore trong bóng tối và sa đọa.",
    26: "Ngươi - kẻ tìm kiếm danh tiếng - sẽ bắt đầu\nhành trình tại những đồng cỏ của Vùng Bằng.\n\nTại đó, ngươi sẽ gặp gỡ\nAuguste, nhà soạn kịch thiên tài.\n\nTại Theatropolis, thành phố nghệ thuật, biết bao linh hồn\nđã bị dẫn lối bởi những lời mê hoặc của hắn.",
    27: "Ngươi - kẻ tìm kiếm sức mạnh - sẽ bắt đầu\nhành trình tại vùng biên giới tuyết phủ của Vùng Băng.\n\nTại đó, ngươi sẽ gặp gỡ\nTytos, người anh hùng.\n\nThủ lĩnh của Đôi Cánh Đỏ Thắm, một băng nhóm\ncựu tội phạm, hắn cai trị Emberglow bằng bàn tay sắt.",
    28: "Không",
    29: "Quay Ước Nguyện",
}

# GameTextMap - Region and location names
TRANSLATE_MAP = {
    3101: "Vùng Băng Giá",
    3102: "Vùng Bằng Phẳng",
    3103: "Vùng Duyên Hải",
    3104: "Vùng Cao Nguyên",
    3105: "Vùng Sa Mạc",
    3106: "Vùng Sông Ngòi",
    3107: "Vùng Vách Đá",
    3108: "Vùng Rừng Rậm",
    16269: "Cổng Tận Thế",
    16270: "Thiên Giới",
    90097: "???",
    3201: "Đèo Cragspear",
    3202: "Cragspear",
    3203: "Cragspear: Khu Ổ Chuột",
    3204: "Lâu Đài Edoras: Ngục Tối",
    3205: "Hang Động Xám",
    3206: "Hang Động Xám: Sâu Thẳm",
    3207: "Đèo Cragspear Nam",
    3208: "Hẻm Núi Geist: Phía Nam",
    3209: "Hẻm Núi Geist",
    3210: "Đường Đến Lâu Đài Edoras",
    3211: "Cổng Lâu Đài Edoras",
    3212: "Lâu Đài Edoras",
    3213: "Lâu Đài Edoras: Tầng Trên",
    3214: "Lâu Đài Edoras: Sân Trong",
    3215: "Lâu Đài Edoras: Phòng Công Chúa",
    3216: "Lâu Đài Edoras: Phòng Ngai Vàng",
    3222: "Rippletide",
    3223: "Bờ Biển Rippletide",
    3224: "Bờ Biển Rippletide Bắc",
    3225: "Đảo Orsa",
    3226: "Đảo Orsa: Sâu Thẳm",
    3363: "Đảo Orsa: Bàn Thờ",
    3227: "Sunshade",
    3228: "Cát Sunshade",
    3229: "Cát Sunshade Đông",
    3237: "Đèo Shepherds Rock",
    3238: "Đèo Shepherds Rock Bắc",
    3239: "Thung Lũng Tử Thần: Phía Đông",
    3240: "Thung Lũng Tử Thần",
    3241: "Thung Lũng Tử Thần: Phía Tây",
    3247: "Valore",
    3248: "Valore: Đại Lộ Chính",
    3249: "Đường Mòn Valore",
    3250: "Đường Mòn Valore Tây",
    3251: "Đường Đến Dinh Thự Herminia",
    3252: "Dinh Thự Herminia: Lối Vào",
    3253: "Dinh Thự Herminia",
    3254: "Dinh Thự Herminia: Hầm Rượu",
    3255: "Biệt Thự Auguste: Lối Vào",
    3256: "Biệt Thự Auguste",
    3257: "Emberglow",
    3258: "Emberglow: Khu Đông",
    3259: "Hoang Dã Emberglow",
    3260: "Hoang Dã Emberglow Tây",
    3261: "Phòng Thí Nghiệm Emberglow: Lối Vào",
    3262: "Phòng Thí Nghiệm Emberglow",
    3263: "Quảng Trường Nghi Lễ",
    3264: "Giáo Đường Tytos",
    16060: "Giáo Đường Tytos: Lối Vào",
}

def translate_file_direct(name, translation_dict):
    """Translate a file using a pre-built dictionary."""
    input_path = os.path.join(INPUT_DIR, f'{name}.json')
    output_path = os.path.join(OUTPUT_DIR, f'{name}.json')
    
    with open(input_path, 'r', encoding='utf-8') as f:
        entries = json.load(f)
    
    translated = []
    for entry in entries:
        eid = entry['id']
        if eid in translation_dict:
            vi_text = translation_dict[eid]
        else:
            vi_text = entry['text_joined']  # Keep original if not translated
        
        translated.append({
            'id': eid,
            'en': entry['text_joined'],
            'vi': vi_text,
        })
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(translated, f, ensure_ascii=False, indent=2)
    
    count_translated = sum(1 for t in translated if t['en'] != t['vi'])
    print(f"  {name}: {count_translated}/{len(translated)} translated")
    return translated

# Common UI translations
UI_TRANSLATIONS = {
    0: "Không có dữ liệu.",
    7: "Đang giữ",
    32: "Không có",
    33: "Bật",
    34: "Tắt",
    52: "đã nhận được.",
    56: "Nguy Hiểm",
    58: "Cấp đề xuất",
    67: "Tên",
    68: "Thuộc tính",
    64992: "Người Sống",
    64993: "Người Chết",
    65000: "Trò Chơi Mới",
    65001: "Tiếp Tục",
    65002: "Cài Đặt",
    65003: "Thoát Game",
    96681: "Tải Dữ Liệu Demo",
    96682: "Tải Dữ Liệu PlayStation®4",
    97248: "Tải Dữ Liệu Nintendo Switch™",
    96683: "Nhấn Phím Bất Kỳ",
    96824: "NHẤN NÚT BẤT KỲ",
    96825: "NHẤN NÚT BẤT KỲ",
    96826: "NHẤN NÚT BẤT KỲ",
    96827: "NHẤN NÚT BẤT KỲ",
    96828: "NHẤN PHÍM BẤT KỲ",
    65006: "Thoát game?",
    511: "Cài Đặt",
    535: "Menu",
    536: "Nhiệm Vụ",
    537: "Bản Đồ Thế Giới",
    542: "Vật Phẩm",
    545: "Khác",
    566: "Theo Dõi",
    95503: "Di Chuyển",
    95504: "Hủy",
    95505: "Theo Dõi Nhiệm Vụ",
    95506: "Hủy",
    95507: "Không thể di chuyển nhanh đến địa điểm này.",
    95508: "Theo Dõi Nhiệm Vụ",
    95509: "Hủy",
    651: "Về Màn Hình Chính",
    62753: "Đã trang bị",
    902: "Trạng Thái",
    79: "Chọn một tùy chọn.",
    62864: "???",
}

# Common item type translations
ITEM_WORD_MAP = {
    "Sword": "Kiếm", "Spear": "Thương", "Dagger": "Dao Găm", "Axe": "Rìu",
    "Bow": "Cung", "Staff": "Trượng", "Shield": "Khiên", "Helm": "Mũ",
    "Armor": "Giáp", "Robe": "Áo Choàng", "Hat": "Nón", "Ring": "Nhẫn",
    "Necklace": "Vòng Cổ", "Bracelet": "Vòng Tay", "Belt": "Thắt Lưng",
    "Healing Grape": "Nho Hồi Phục", "Plum": "Mận", "Herb": "Thảo Dược",
    "Pomegranate": "Lựu", "Olive": "Ô Liu",
    "Makeshift": "Tạm Thời", "Iron": "Sắt", "Silver": "Bạc", "Gold": "Vàng",
    "Platinum": "Bạch Kim", "Divine": "Thần Thánh", "Sacred": "Linh Thiêng",
    "Enchanted": "Ma Thuật", "Guardian": "Hộ Vệ", "Forbidden": "Cấm Kỵ",
    "Battle-Tested": "Trận Mạc",
    "Long Sword": "Trường Kiếm", "Broadsword": "Đại Kiếm",
    "Greatsword": "Cự Kiếm", "Heavy Blade": "Trọng Kiếm",
    "Bastard Sword": "Kiếm Lai",
}

# Enemy name translations  
ENEMY_WORD_MAP = {
    "Marmot": "Sóc Đất", "Viper": "Rắn Độc", "Howler": "Kẻ Hú",
    "Wolf": "Sói", "Bat": "Dơi", "Fox": "Cáo", "Mushroom": "Nấm",
    "Spider": "Nhện", "Rat": "Chuột", "Snake": "Rắn", "Bear": "Gấu",
    "Lizardman": "Người Thằn Lằn", "Skeleton": "Bộ Xương",
    "Sentinel": "Lính Canh", "Guardian": "Hộ Vệ", "Soldier": "Lính",
    "Guard Dog": "Chó Canh", "Bodyguard": "Vệ Sĩ",
    "Menacing": "Hung Dữ", "Majestic": "Oai Phong",
    "Ice": "Băng", "Flame": "Lửa", "Thunder": "Sấm", "Dark": "Bóng Tối",
    "Shadow": "Bóng Tối", "Snow": "Tuyết", "Frost": "Sương Giá",
    "Forest": "Rừng", "Ash": "Tro", "White": "Trắng",
    "Remnant": "Tàn Dư", "Wisp": "Ma Trơi",
    "Researcher": "Nghiên Cứu Viên", "Believer": "Tín Đồ",
    "Shambling Weed": "Cỏ Dại Lê Bước", "Rampant Weed": "Cỏ Dại Hoành Hành",
    "Spud Bug": "Bọ Khoai", "Mossy Meep": "Meep Rêu Phong",
    "Mortal Mushroom": "Nấm Tử Thần", "Vampire Bat": "Dơi Ma Cà Rồng",
    "Gabbrodillo": "Gabbrodillo",
    "Scaled Viper": "Rắn Vảy Độc",
}

def translate_items(entries):
    """Translate item names using word map."""
    results = []
    for entry in entries:
        en = entry['text_joined']
        vi = en  # default: keep original
        
        # Try direct word replacement for common patterns
        for eng_word, vi_word in ITEM_WORD_MAP.items():
            if eng_word in en:
                vi = vi.replace(eng_word, vi_word)
        
        results.append({
            'id': entry['id'],
            'en': en,
            'vi': vi,
        })
    return results

def translate_enemies(entries):
    """Translate enemy names."""
    results = []
    for entry in entries:
        en = entry['text_joined']
        vi = en
        
        for eng_word, vi_word in ENEMY_WORD_MAP.items():
            if eng_word in en:
                vi = vi.replace(eng_word, vi_word)
        
        results.append({
            'id': entry['id'],
            'en': en,
            'vi': vi,
        })
    return results

# ============================================================
# MAIN PROCESSING
# ============================================================
print("=" * 60)
print("  Octopath Traveler - English to Vietnamese Translation")
print("=" * 60)

# 1. Direct dictionary translations
print("\n--- Direct translations ---")
translate_file_direct('GameTextPC', TRANSLATE_PC)
translate_file_direct('GameTextGraphic', TRANSLATE_GRAPHIC)
translate_file_direct('GameTextMap', TRANSLATE_MAP)
translate_file_direct('GameTextUI', UI_TRANSLATIONS)

# 2. Item translations
print("\n--- Item translations ---")
with open(os.path.join(INPUT_DIR, 'GameTextItem.json'), 'r', encoding='utf-8') as f:
    item_entries = json.load(f)
translated_items = translate_items(item_entries)
with open(os.path.join(OUTPUT_DIR, 'GameTextItem.json'), 'w', encoding='utf-8') as f:
    json.dump(translated_items, f, ensure_ascii=False, indent=2)
count = sum(1 for t in translated_items if t['en'] != t['vi'])
print(f"  GameTextItem: {count}/{len(translated_items)} translated")

# 3. Enemy translations
print("\n--- Enemy translations ---")
with open(os.path.join(INPUT_DIR, 'GameTextEnemy.json'), 'r', encoding='utf-8') as f:
    enemy_entries = json.load(f)
translated_enemies = translate_enemies(enemy_entries)
with open(os.path.join(OUTPUT_DIR, 'GameTextEnemy.json'), 'w', encoding='utf-8') as f:
    json.dump(translated_enemies, f, ensure_ascii=False, indent=2)
count = sum(1 for t in translated_enemies if t['en'] != t['vi'])
print(f"  GameTextEnemy: {count}/{len(translated_enemies)} translated")

# 4. Copy remaining files as-is (need more context for dialogue)
print("\n--- Files needing manual/contextual translation ---")
remaining_files = [
    'GameTextCharacter', 'GameTextCharacterCreate', 'GameTextEnding',
    'GameTextFC', 'GameTextPartVoice', 'GameTextQuest',
    'GameTextScenarioReplay', 'GameTextSkill', 'GameTextVillage',
    'GameTextEvent', 'GameTextNPC'
]
for name in remaining_files:
    input_path = os.path.join(INPUT_DIR, f'{name}.json')
    if os.path.exists(input_path):
        with open(input_path, 'r', encoding='utf-8') as f:
            entries = json.load(f)
        # Create template with en/vi fields
        template = [{'id': e['id'], 'en': e['text_joined'], 'vi': ''} for e in entries]
        with open(os.path.join(OUTPUT_DIR, f'{name}.json'), 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        print(f"  {name}: {len(entries)} entries (template created, needs translation)")

# Summary
print(f"\n{'='*60}")
print(f"  Output directory: {OUTPUT_DIR}/")
print(f"  Files with translations: GameTextPC, GameTextGraphic, GameTextMap, GameTextUI, GameTextItem, GameTextEnemy")
print(f"  Files needing translation: {', '.join(remaining_files)}")
print(f"{'='*60}")
