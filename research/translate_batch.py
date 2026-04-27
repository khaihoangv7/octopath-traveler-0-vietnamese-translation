"""
Batch translate remaining Octopath Traveler files EN -> VI.
For 56K entries, we use pattern-based + dictionary translation.
"""
import json, os, re

INPUT_DIR = 'extracted_text'
OUTPUT_DIR = 'translated_text'

# ============================================================
# CHARACTER NAMES
# ============================================================
CHAR_NAMES = {
    28600: "Cậu bé", 28500: "không có dữ liệu.", 28565: "???", 28566: "Mọi người",
    116414: "Chủ quán", 28592: "Cậu bé", 28567: "Băng đảng Bargello",
    28568: "Bargello", 28569: "Tiziano", 28570: "Pierro Della", 28571: "Fra",
    28572: "Quý bà Herminia", 28573: "Thị nữ", 28574: "Sonia",
    28575: "Lãnh chúa Taviani", 28577: "Trưởng lão tàn phế", 28578: "Hắc bào",
    28579: "???", 28580: "Đội trưởng Tristan", 28583: "Cô gái bán hoa",
    28584: "Herminia Nữ Thợ Săn", 28588: "Rosso", 28589: "Tomazzo",
    28590: "Gastone", 28988: "???", 28989: "Tư lệnh Tytos", 28991: "Hầu cận",
    28994: "Velnorte", 28995: "Jurgen", 28996: "Rinyuu", 28997: "Linh mục",
    28998: "Phina", 29000: "Tên côn đồ bất thường", 29005: "Hầu cận Al",
    29006: "Kỵ sĩ Ardante", 29009: "Giám mục", 29014: "Thợ săn Dmitri",
    116284: "Chủ trọ", 116285: "Cánh Đỏ Thắm", 116288: "Tytos Lưỡi Kiếm Sấm",
    116362: "Chủ quán", 116366: "Tytos của Kỵ Đoàn Ardante", 116367: "Giáo hoàng",
    116368: "Vua xứ Edoras", 116369: "Vua xứ Hornburg",
    28963: "Nữ diễn viên", 28965: "\"Jana\"", 28966: "\"Françoise\"",
    28967: "\"Anna\"", 28970: "\"Rafael\"", 28971: "Nữ diễn viên Francesca",
    28972: "\"Margretta\"", 28973: "Kịch tác gia Auguste", 28974: "Schwartz",
    28975: "Mikhail", 28976: "Hầu gái", 28977: "Sư phụ Dorteau",
    28978: "Thi sĩ Simeon", 116359: "\"Auguste\"", 116386: "\"Schwartz\"",
    116387: "Auguste Hoàng Tử Đạo Tặc", 118110: "\"Đứa trẻ\"",
    116289: "Tướng quân Mahrez", 116290: "Công chúa Elrica",
    116291: "Công chúa Alaune", 116292: "Nữ hoàng Alaune",
    116293: "Tư lệnh Krauser", 116294: "Tướng quân Krauser",
    116295: "Quốc vương Solon", 116296: "Tùy tùng Lebrandt",
    116297: "Kiếm sĩ El", 116298: "Lữ khách Charles",
    116299: "Tùy tùng Mendoza", 116300: "Đội trưởng Barnes",
    116301: "Vua xứ Riven", 116302: "Tể tướng Raum",
    116303: "Sư phụ Helgenish", 116304: "Vũ công Primrose",
    116305: "Thương nhân Trompeur", 116306: "Tộc trưởng Kanzas",
}

# ============================================================
# SKILL KEYWORDS
# ============================================================
SKILL_KEYWORDS = {
    "Strike": "Đòn Chém", "Slash": "Chém", "Attack": "Tấn Công",
    "Defend": "Phòng Thủ", "Guard": "Đỡ", "Heal": "Hồi Phục",
    "Cure": "Chữa Trị", "Revive": "Hồi Sinh", "Fire": "Hỏa",
    "Ice": "Băng", "Thunder": "Sấm", "Wind": "Phong", "Light": "Quang",
    "Dark": "Ám", "Holy": "Thánh", "Cross": "Chéo",
    "Boost": "Tăng Cường", "Break": "Phá Vỡ", "Counter": "Phản Đòn",
    "Shield": "Khiên", "Blade": "Kiếm", "Arrow": "Mũi Tên",
    "Steal": "Trộm", "Flee": "Chạy Trốn", "Analyze": "Phân Tích",
    "Capture": "Bắt Giữ", "Summon": "Triệu Hồi", "Dance": "Vũ Điệu",
    "Song": "Bài Ca", "Prayer": "Cầu Nguyện", "Blessing": "Ban Phước",
    "Curse": "Nguyền Rủa", "Poison": "Độc", "Sleep": "Ngủ",
    "Silence": "Câm Lặng", "Blind": "Mù", "Confuse": "Hỗn Loạn",
    "Stun": "Choáng", "Freeze": "Đóng Băng",
    "All Allies": "Toàn Đồng Đội", "All Foes": "Toàn Kẻ Địch",
    "Single Foe": "Một Kẻ Địch", "Single Ally": "Một Đồng Đội",
    "Self": "Bản Thân",
    "Damage": "Sát thương", "Physical": "Vật lý", "Elemental": "Nguyên tố",
    "HP": "HP", "SP": "SP", "BP": "BP",
    "Restore": "Hồi phục", "Reduce": "Giảm", "Increase": "Tăng",
    "turns": "lượt", "turn": "lượt",
    "Deals": "Gây", "to": "lên", "and": "và",
    "for": "trong", "with": "với",
}

# ============================================================
# UI EXTENDED  
# ============================================================
UI_EXTENDED = {
    "Yes": "Có", "No": "Không", "OK": "Đồng ý", "Cancel": "Hủy",
    "Confirm": "Xác nhận", "Back": "Quay lại", "Save": "Lưu",
    "Load": "Tải", "Quit": "Thoát", "Exit": "Thoát",
    "Attack": "Tấn Công", "Defend": "Phòng Thủ", "Flee": "Chạy Trốn",
    "Items": "Vật Phẩm", "Skills": "Kỹ Năng", "Magic": "Ma Thuật",
    "Equip": "Trang Bị", "Status": "Trạng Thái", "Formation": "Đội Hình",
    "Party": "Đội", "Battle": "Chiến Đấu", "Victory": "Chiến Thắng",
    "Defeat": "Thất Bại", "Experience": "Kinh Nghiệm",
    "Level": "Cấp Độ", "HP": "HP", "SP": "SP", "BP": "BP",
    "Strength": "Sức Mạnh", "Defense": "Phòng Thủ",
    "Intelligence": "Trí Tuệ", "Speed": "Tốc Độ", "Luck": "May Mắn",
    "Evasion": "Né Tránh", "Accuracy": "Chính Xác",
    "Critical": "Chí Mạng", "Physical": "Vật Lý", "Elemental": "Nguyên Tố",
    "Weapon": "Vũ Khí", "Armor": "Giáp", "Accessory": "Phụ Kiện",
    "Consumable": "Tiêu Hao", "Key Item": "Vật Phẩm Quan Trọng",
    "Quest": "Nhiệm Vụ", "Main Story": "Cốt Truyện Chính",
    "Side Story": "Câu Chuyện Phụ", "Travel": "Du Hành",
    "Inn": "Nhà Trọ", "Shop": "Cửa Hàng", "Tavern": "Quán Rượu",
    "Church": "Nhà Thờ", "Save Point": "Điểm Lưu",
    "Obtained": "Nhận được", "Lost": "Mất", "Learned": "Đã học",
    "Equipped": "Đã trang bị", "Unequipped": "Đã tháo",
    "bought": "đã mua", "sold": "đã bán",
    "Danger Level": "Mức Nguy Hiểm", "Recommended Level": "Cấp Đề Xuất",
    "New Game": "Trò Chơi Mới", "Continue": "Tiếp Tục",
    "Options": "Cài Đặt", "Quit Game": "Thoát Game",
    "Game Over": "Kết Thúc", "Loading": "Đang Tải",
}

# ============================================================
# COMMON DIALOGUE PATTERNS
# ============================================================
def translate_dialogue(text):
    """Translate common dialogue patterns."""
    result = text
    
    # Common short phrases
    patterns = {
        "It seems to be locked.": "Có vẻ như nó bị khóa.",
        "A dark mist blocks the way forward.": "Một làn sương đen ngăn cản đường phía trước.",
        "A thick fog blocks the way forward.": "Sương mù dày đặc ngăn cản đường phía trước.",
        "no data.": "không có dữ liệu.",
        "(Unlocalized)": "(Chưa dịch)",
        "Track this quest?": "Theo dõi nhiệm vụ này?",
        "Prologue": "Mở Đầu",
        "Chapter": "Chương",
        "Epilogue": "Vĩ Thanh",
        "Final Chapter": "Chương Cuối",
    }
    
    if result in patterns:
        return patterns[result]
    
    return result

def translate_generic(text):
    """Generic translation using keyword replacement for short texts."""
    if not text or len(text) > 200:
        return text  # Skip long texts (need contextual translation)
    
    result = text
    
    # Direct matches for common UI/short texts
    if result in UI_EXTENDED:
        return UI_EXTENDED[result]
    
    return result

# ============================================================
# PROCESS ALL REMAINING FILES
# ============================================================
def process_file(name, translate_fn=None):
    input_path = os.path.join(INPUT_DIR, f'{name}.json')
    output_path = os.path.join(OUTPUT_DIR, f'{name}.json')
    
    with open(input_path, 'r', encoding='utf-8') as f:
        entries = json.load(f)
    
    results = []
    translated_count = 0
    
    for entry in entries:
        eid = entry['id']
        en = entry['text_joined']
        vi = ''
        
        # Check character names dict
        if eid in CHAR_NAMES:
            vi = CHAR_NAMES[eid]
        elif translate_fn:
            vi = translate_fn(en)
        else:
            vi = translate_generic(en)
        
        if not vi:
            vi = en  # Fallback to English
        
        results.append({
            'id': eid,
            'en': en,
            'vi': vi
        })
        
        if vi != en:
            translated_count += 1
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"  {name}: {translated_count}/{len(results)} translated")
    return results

print("=" * 60)
print("  Batch Translation - Remaining Files")
print("=" * 60)

# Character names
process_file('GameTextCharacter')

# Character creation
process_file('GameTextCharacterCreate', translate_generic)

# Scenario replay
process_file('GameTextScenarioReplay', translate_dialogue)

# Quest text
process_file('GameTextQuest', translate_dialogue)

# NPC dialogue
process_file('GameTextNPC', translate_dialogue)

# Village
process_file('GameTextVillage', translate_generic)

# Skills (use keyword replacement)
process_file('GameTextSkill', translate_generic)

# FC content
process_file('GameTextFC', translate_dialogue)

# Event dialogue (largest file)
process_file('GameTextEvent', translate_dialogue)

# Part voice
process_file('GameTextPartVoice', translate_generic)

# Ending
process_file('GameTextEnding', translate_generic)

# Create master CSV for review
print("\n--- Creating master translation CSV ---")
csv_path = os.path.join(OUTPUT_DIR, 'all_translations.csv')
total = 0
translated = 0
with open(csv_path, 'w', encoding='utf-8-sig') as f:
    f.write("File,ID,English,Vietnamese,Status\n")
    for fname in sorted(os.listdir(OUTPUT_DIR)):
        if not fname.endswith('.json'):
            continue
        name = fname.replace('.json', '')
        data = json.load(open(os.path.join(OUTPUT_DIR, fname), 'r', encoding='utf-8'))
        for entry in data:
            en = entry.get('en', '')
            vi = entry.get('vi', '')
            status = 'DONE' if vi and vi != en else 'TODO'
            en_esc = en.replace('"', '""').replace('\n', '\\n')
            vi_esc = vi.replace('"', '""').replace('\n', '\\n')
            f.write(f'{name},{entry["id"]},"{en_esc}","{vi_esc}",{status}\n')
            total += 1
            if status == 'DONE':
                translated += 1

print(f"\n{'='*60}")
print(f"  TRANSLATION SUMMARY")
print(f"  Total entries: {total}")
print(f"  Translated: {translated} ({translated*100//total}%)")
print(f"  Remaining: {total - translated}")
print(f"  Master CSV: {csv_path}")
print(f"{'='*60}")
