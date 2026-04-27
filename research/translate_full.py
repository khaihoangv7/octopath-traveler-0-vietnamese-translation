"""
FULL Vietnamese Translation for Octopath Traveler.
Translates ALL entries across all files.
"""
import json, os, re

INPUT_DIR = 'extracted_text'
OUTPUT_DIR = 'translated_text'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================
# COMPREHENSIVE TRANSLATION DICTIONARY
# ============================================================
# Common words/phrases that appear across ALL files
COMMON = {
    # Basic UI
    "Yes": "Có", "No": "Không", "OK": "Đồng ý", "Cancel": "Hủy",
    "Confirm": "Xác nhận", "Back": "Quay lại", "Close": "Đóng",
    "Help": "Trợ giúp", "Save": "Lưu", "Load": "Tải", "None": "Không có",
    "On": "Bật", "Off": "Tắt", "Quit": "Thoát", "Exit": "Thoát",
    "obtained.": "đã nhận được.", "Equipped": "Đã trang bị",
    "No data.": "Không có dữ liệu.", "no data.": "không có dữ liệu.",
    "(Unlocalized)": "(Chưa dịch)", "???": "???",
    "Danger": "Nguy hiểm", "Name": "Tên", "Attributes": "Thuộc tính",
    "Status": "Trạng thái",

    # Menu
    "New Game": "Trò Chơi Mới", "Continue": "Tiếp Tục",
    "Options": "Cài Đặt", "Settings": "Cài Đặt",
    "Quit Game": "Thoát Game", "Quit game?": "Thoát game?",
    "Menu": "Menu", "Quests": "Nhiệm Vụ", "World Map": "Bản Đồ Thế Giới",
    "Items": "Vật Phẩm", "Other": "Khác", "Track": "Theo Dõi",
    "Travel": "Di Chuyển", "Track Quest": "Theo Dõi Nhiệm Vụ",
    "Return to Title": "Về Màn Hình Chính",
    "Press Any Key": "Nhấn Phím Bất Kỳ",
    "PRESS ANY BUTTON": "NHẤN NÚT BẤT KỲ",
    "PRESS ANY KEY": "NHẤN PHÍM BẤT KỲ",
    "The Living": "Người Sống", "The Dead": "Người Chết",
    "Form Party": "Thành Lập Đội", "Optimize": "Tối Ưu Hóa",
    "Unequip All": "Tháo Tất Cả", "Support Skills": "Kỹ Năng Hỗ Trợ",
    "Fast Travel": "Di Chuyển Nhanh",
    "An Encounter Awaits": "Một Cuộc Chiến Đang Chờ",
    "Zoom Out": "Thu Nhỏ", "Zoom In": "Phóng To",
    "Wishvale": "Wishvale", "Hell": "Địa Ngục", "The World": "Thế Giới",
    "The Middlesea": "Trung Hải", "The Outersea": "Ngoại Hải",
    "Next Destination": "Điểm Đến Tiếp Theo",
    "Side Story": "Câu Chuyện Phụ",

    # Battle
    "Results": "Kết Quả", "Level Up": "Lên Cấp", "Critical": "Chí Mạng",
    "Miss": "Trượt", "WEAK": "YẾU", "Overkill": "Hạ Gục",
    "Shield Guard": "Khiên Chắn", "BREAK": "PHÁ VỠ", "Game Over": "Kết Thúc",
    "Complete": "Hoàn Thành", "Loading...": "Đang tải...",
    "Rank Up": "Thăng Hạng", "Fin": "Hết",

    # Stats
    "HP": "HP", "SP": "SP", "BP": "BP", "JP": "JP",
    "Phys. Atk.": "Tấn Công V.Lý", "Phys. Def.": "Phòng Thủ V.Lý",
    "Elem. Atk.": "Tấn Công N.Tố", "Elem. Def.": "Phòng Thủ N.Tố",
    "Speed": "Tốc Độ", "Crit.": "Chí Mạng",
    "Accuracy": "Chính Xác", "Evasion": "Né Tránh",
    "Max. HP": "HP Tối Đa", "Max. SP": "SP Tối Đa",
    "Front Row": "Hàng Trước", "Back Row": "Hàng Sau",
    "SP Cost": "SP Tiêu Hao", "Cannot Equip": "Không Thể Trang Bị",
    "Influence": "Ảnh Hưởng", "Wealth": "Tài Sản",
    "Power": "Sức Mạnh", "Fame": "Danh Tiếng",
    "Town Level": "Cấp Thị Trấn",

    # Items categories
    "Valuables": "Vật Quý", "Weapons": "Vũ Khí",
    "Accessories": "Phụ Kiện", "Consumables": "Tiêu Hao",
    "Sword": "Kiếm", "Axe": "Rìu", "Dagger": "Dao Găm",
    "Tome": "Sách Phép", "Staff": "Trượng", "Bow": "Cung",
    "Polearm": "Thương", "Fan": "Quạt",
    "Headgear": "Mũ", "Body Armor": "Giáp Thân",
    "Ultimate Technique": "Tuyệt Kỹ",
    "Status Boost": "Tăng Chỉ Số", "Shield": "Khiên",
    "Dishes": "Món Ăn", "Music": "Âm Nhạc",

    # Path Actions
    "Path Actions": "Hành Động Đường", "Inquire": "Tra Hỏi",
    "Inquire Further": "Tra Hỏi Thêm", "Purchase": "Mua",
    "Hire": "Thuê", "Haggle": "Mặc Cả",
    "Contend": "Thách Đấu", "Impress": "Gây Ấn Tượng",
    "Entreat": "Cầu Xin", "Recruit": "Chiêu Mộ",
    "Invite": "Mời", "Illuminate": "Soi Sáng",
    "Possessions": "Tài Sản", "Part Ways": "Chia Tay",
    "Strength": "Sức Mạnh", "Skill": "Kỹ Năng", "Uses": "Số Lần Dùng",

    # Quest related
    "Prologue": "Mở Đầu", "Finale": "Chung Kết",
    "A New Tale": "Một Câu Chuyện Mới",
    "Ch. 1": "Ch. 1", "Ch. 2": "Ch. 2", "Ch. 3": "Ch. 3",
    "Ch. 4": "Ch. 4", "Ch. 5": "Ch. 5", "Ch. 6": "Ch. 6",
    "Ch. 7": "Ch. 7", "Ch. 8": "Ch. 8",

    # Village
    "Facilities": "Công Trình", "Man-Made Decorations": "Trang Trí Nhân Tạo",
    "Natural Decorations": "Trang Trí Thiên Nhiên",
    "Decorations (Special)": "Trang Trí (Đặc Biệt)",
    "Ground Tiles": "Gạch Nền", "Residents": "Cư Dân",
    "Grade": "Hạng", "Size": "Kích Thước",
    "Other Features": "Tính Năng Khác",
    "Select a style.": "Chọn một kiểu.", "Outside": "Bên Ngoài",
    "Grass": "Cỏ", "Dirt": "Đất", "Cobblestone": "Đá Cuội",
    "Sand": "Cát", "Snow": "Tuyết", "Volcanic Soil": "Đất Núi Lửa",
    "Workshop": "Xưởng", "Hub": "Trung Tâm", "Shop": "Cửa Hàng",
    "Church": "Nhà Thờ", "Ranch": "Trang Trại",
    "Training Ground": "Bãi Tập", "Salon": "Tiệm",
    "Museum": "Bảo Tàng", "Strange House": "Nhà Kỳ Lạ",
    "Monster Arena": "Đấu Trường Quái Vật", "Fields": "Cánh Đồng",
    "House": "Nhà", "House (Large)": "Nhà (Lớn)", "House (Grand)": "Nhà (Hoành Tráng)",
    "Well": "Giếng", "Fountain": "Đài Phun Nước",
    "Small Fountain": "Đài Phun Nhỏ", "Grand Fountain": "Đài Phun Lớn",
    "Bench": "Ghế Dài", "Table": "Bàn", "Chair": "Ghế",
    "Pot": "Chậu", "Rope": "Dây Thừng", "Bottle": "Chai",
    "Firewood": "Củi", "Cart": "Xe Kéo", "Wagon": "Xe Ngựa",

    # Jobs
    "Warrior": "Chiến Binh", "Apothecary": "Dược Sư", "Thief": "Đạo Tặc",
    "Scholar": "Học Giả", "Cleric": "Giáo Sĩ", "Hunter": "Thợ Săn",
    "Merchant": "Thương Nhân", "Dancer": "Vũ Công",

    # Character Create
    "Learned Skill": "Kỹ Năng Đã Học", "Favorite Dish": "Món Ăn Yêu Thích",
    "Belongings": "Hành Trang", "Job": "Nghề Nghiệp",
    "Mastery": "Tinh Thông", "Memory": "Ký Ức",
    "Formation": "Đội Hình", "Party": "Đội",
    "Change Equipment": "Thay Đổi Trang Bị",
    "Change Skills": "Thay Đổi Kỹ Năng",
    "Final Confirmation": "Xác Nhận Cuối",
    "Confirm Settings": "Xác Nhận Cài Đặt",
    "Change Appearance": "Thay Đổi Ngoại Hình",
    "Change Learned Skill": "Thay Đổi Kỹ Năng Đã Học",
    "Change Favorite Dish": "Thay Đổi Món Ăn Yêu Thích",
    "Change Belongings": "Thay Đổi Hành Trang",
    "Change Name": "Đổi Tên", "Change Job": "Đổi Nghề",
    "Change Mastery": "Thay Đổi Tinh Thông",
    "Begin Story": "Bắt Đầu Câu Chuyện",
    "Continue Story": "Tiếp Tục Câu Chuyện",
    "Attack Skill": "Kỹ Năng Tấn Công",
    "Recovery Skill": "Kỹ Năng Hồi Phục",
    "Enfeebling Skill": "Kỹ Năng Suy Yếu",
    "Support Skill": "Kỹ Năng Hỗ Trợ",

    # Scenario chapters
    "Kindlers of the Flame": "Những Người Giữ Lửa",
    "Master of Wealth": "Bậc Thầy Tài Sản",
    "Master of Power": "Bậc Thầy Sức Mạnh",
    "Master of Fame": "Bậc Thầy Danh Tiếng",
    "Master of All": "Bậc Thầy Vạn Sự",
    "Bestower of Wealth": "Đấng Ban Tài Sản",
    "Bestower of Power": "Đấng Ban Sức Mạnh",
    "Bestower of Fame": "Đấng Ban Danh Tiếng",
    "Bestower of All": "Đấng Ban Vạn Sự",
    "All": "Tất Cả",
}

# Longer sentences - UI
SENTENCES = {
    "Select an option.": "Chọn một tùy chọn.",
    "Cannot fast travel to this location.": "Không thể di chuyển nhanh đến đây.",
    "Cannot fast travel to places you haven't visited.": "Không thể di chuyển nhanh đến nơi chưa đến.",
    "Cannot fast travel to this location at this time.": "Không thể di chuyển nhanh đến đây lúc này.",
    "You feel rested and fully recovered!": "Bạn cảm thấy được nghỉ ngơi và hồi phục hoàn toàn!",
    "Confirm party?": "Xác nhận đội hình?",
    "Hold to Skip": "Giữ để Bỏ Qua",
    "All enemies defeated!": "Đã đánh bại tất cả kẻ địch!",
    "The treasure chest is locked.": "Rương báu bị khóa.",
    "Optimize Equipment": "Tối Ưu Trang Bị",
    "It seems to be locked.": "Có vẻ như nó bị khóa.",
    "A dark mist blocks the way forward.": "Sương đen ngăn cản đường phía trước.",
    "A thick fog blocks the way forward.": "Sương mù dày đặc chắn đường phía trước.",
    "It seems you can't go any further.": "Có vẻ không thể đi xa hơn nữa.",
    "This area is off-limits.": "Khu vực này bị cấm.",
    "What do you want to ask about?": "Bạn muốn hỏi về điều gì?",
    "Do you want to ask anything else?": "Bạn muốn hỏi thêm gì không?",
    "I'm done here.": "Tôi xong rồi.",
    "Return to town?": "Quay về thị trấn?",
    "Begin this quest?": "Bắt đầu nhiệm vụ này?",
    "Halt. Who goes there?": "Dừng lại. Ai đó?",
    "Haven't seen you around before.": "Chưa thấy ngươi quanh đây bao giờ.",
    "Hey, I've been waiting for you.": "Này, ta đã đợi ngươi.",
    "Abandon changes?": "Bỏ thay đổi?",
    "Please enter your name.": "Hãy nhập tên của bạn.",
    "Please enter the name of your favorite dish.": "Hãy nhập tên món ăn yêu thích.",
    "Select the skill you learned when you were young.": "Chọn kỹ năng bạn đã học khi còn nhỏ.",
    "Select your favorite dish.": "Chọn món ăn yêu thích.",
    "Enter the name of your favorite dish.": "Nhập tên món ăn yêu thích.",
    "Select 3 belongings.": "Chọn 3 hành trang.",
    "Finally, enter your name.": "Cuối cùng, nhập tên của bạn.",
    "Select your job.": "Chọn nghề nghiệp.",
    "Select the mastery you achieved from training.": "Chọn tinh thông đạt được từ luyện tập.",
    "Select your appearance.": "Chọn ngoại hình.",
    "Proceed with this appearance?": "Tiếp tục với ngoại hình này?",
    "Proceed with this learned skill?": "Tiếp tục với kỹ năng này?",
    "Proceed with this favorite dish?": "Tiếp tục với món ăn này?",
    "Proceed with these belongings?": "Tiếp tục với hành trang này?",
    "Proceed with this job?": "Tiếp tục với nghề này?",
    "Proceed with this mastery?": "Tiếp tục với tinh thông này?",
    "Track this quest?": "Theo dõi nhiệm vụ này?",
    "Thank you for traveling with us.": "Cảm ơn bạn đã đồng hành cùng chúng tôi.",
    "Rec. Level": "Cấp Đề Xuất",
    "Held": "Đang Giữ",
}

# Template patterns with {0}, {1}, etc
TEMPLATES = {
    "Lv. {0}": "Cấp {0}",
    "Obtained {0}.": "Nhận được {0}.",
    "{0} Left": "{0} Còn Lại",
    "Travel to {1}\n({0})?": "Di chuyển đến {1}\n({0})?",
    "Placed: {0}/{1}": "Đã đặt: {0}/{1}",
    "Danger Lv. {0}": "Mức Nguy Hiểm {0}",
    "Success Rate: {0}%": "Tỷ Lệ Thành Công: {0}%",
    "Part ways with {0}?": "Chia tay {0}?",
    "Parted ways with {0}.": "Đã chia tay {0}.",
    "{0} has become a helper.": "{0} đã trở thành trợ thủ.",
    "Invite them to Wishvale?": "Mời họ đến Wishvale?",
    "You must inquire first.": "Bạn cần tra hỏi trước.",
    "Began \"{0}.\"": "Bắt đầu \"{0}.\"",
    "Finished \"{0}.\"": "Hoàn thành \"{0}.\"",
    "Play \"{0}\"?": "Phát \"{0}\"?",
    "Quit game?": "Thoát game?",
}

def translate_text(text):
    """Translate a single text entry."""
    if not text or not text.strip():
        return text
    
    # Exact match in sentences
    stripped = text.strip()
    if stripped in SENTENCES:
        return SENTENCES[stripped]
    if stripped in COMMON:
        return COMMON[stripped]
    if stripped in TEMPLATES:
        return TEMPLATES[stripped]
    
    # Check for template patterns
    for en_tmpl, vi_tmpl in TEMPLATES.items():
        # Simple check: if the static parts match
        if '{0}' in en_tmpl:
            static_parts = en_tmpl.split('{0}')[0]
            if text.startswith(static_parts) and len(static_parts) > 3:
                return text.replace(static_parts, vi_tmpl.split('{0}')[0])
    
    # For short texts (< 50 chars), try word-by-word
    if len(stripped) < 50 and stripped in COMMON:
        return COMMON[stripped]
    
    # Return original if no translation found
    return text

def process_all_files():
    """Process ALL json files in extracted_text."""
    stats = {'total': 0, 'translated': 0}
    
    for fname in sorted(os.listdir(INPUT_DIR)):
        if not fname.endswith('.json'):
            continue
        
        name = fname.replace('.json', '')
        input_path = os.path.join(INPUT_DIR, fname)
        output_path = os.path.join(OUTPUT_DIR, fname)
        
        with open(input_path, 'r', encoding='utf-8') as f:
            entries = json.load(f)
        
        results = []
        file_translated = 0
        
        for entry in entries:
            en = entry['text_joined']
            vi = translate_text(en)
            
            if vi != en:
                file_translated += 1
            
            results.append({
                'id': entry['id'],
                'en': en,
                'vi': vi,
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        stats['total'] += len(results)
        stats['translated'] += file_translated
        print(f"  {name}: {file_translated}/{len(results)} translated")
    
    return stats

print("=" * 60)
print("  Full Translation Pass")
print("=" * 60)
stats = process_all_files()

# Create final CSV
csv_path = os.path.join(OUTPUT_DIR, 'all_translations.csv')
total = 0
done = 0
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
                done += 1

print(f"\n{'='*60}")
print(f"  FINAL SUMMARY")
print(f"  Total: {total}")
print(f"  Translated: {done} ({done*100//max(total,1)}%)")
print(f"  TODO: {total-done}")
print(f"  CSV: {csv_path}")
print(f"{'='*60}")
