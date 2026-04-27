"""
Fix translation issues:
1. Remove debug/test entries (ボスシナリオテスト, テスト) - keep only first line (English name)
2. Fix </i> and </b> closing tags -> </>
3. Fix "không có dữ liệu" -> keep as "no data."
4. Fix Yusia (mother) dialogue pronouns
"""
import json
import os

# IDs that contain developer test strings (ボスシナリオテスト etc)
# These entries have format: "English Title\nTest(English)\nTest(American)\n..." 
# We only keep the first line (the real English title)
TEST_ENTRY_IDS = {
    # GameTextQuest
    90000000, 10100001,
    219104515, 219104740, 219104536, 219104448,
    919104604, 219104610, 219104457, 219104621,
    219104628, 219104639, 219104443, 219104652,
    219104661, 219104666, 919104510, 219104679,
    919104538, 219104688, 219104699, 219104710,
    919104557, 219104727,
    # GameTextEnemy
    49251,
    # GameTextUI
    11701, 62251,
}

# Yusia (mother) dialogue overrides - use "Con/Mẹ" pronouns
YUSIA_OVERRIDES = {
    412689: "...À, cuối cùng con cũng tỉnh rồi,\n<chara_name>.",
    412690: "Hehe... Con gặp ác mộng sao?",
    412691: "Con cứ trằn trọc mãi,\nvà còn gọi \"mẹ\" trong\nlúc ngủ nữa.",
    412692: "Con biết đấy, con không còn là\ntrẻ con nữa đâu.",
    412693: "Giờ thì, cha con đã ở ngoài kia,\nlàm công việc thường ngày của ông ấy rồi.",
    412694: "Con nên nhanh chân lên,\nđồ sâu ngủ à.",
    418005: "Ồ, <chara_name>.",
    418006: "Đây. Mẹ đã làm món con thích nhất—\n<favorite_dish_name>.",
    418007: "Con không thể chiến đấu\nvới cái bụng rỗng được đâu.",
    418008: "Giờ thì ăn đi rồi ra cho cha con thấy\nai mới là người giỏi nhất. Hê hê.",
}

def fix_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    modified = False
    
    if not isinstance(data, list):
        return
        
    for item in data:
        if 'vi' not in item:
            continue
            
        item_id = item.get('id')
        vi_text = item['vi']
        
        # 1. Fix test entries - revert to English original (don't translate)
        if item_id in TEST_ENTRY_IDS:
            if item.get('en'):
                # Keep only the first line of the English text (the real game text)
                first_line = item['en'].split('\n')[0]
                item['vi'] = first_line
                modified = True
                print(f"  Fixed test entry id={item_id}: '{first_line}'")
            continue
        
        # 2. Fix "không có dữ liệu"
        if vi_text.strip().lower() in ("không có dữ liệu.", "không có dữ liệu"):
            item['vi'] = item.get('en', 'no data.')
            modified = True
        
        # 3. Fix closing tags </i> -> </> and </b> -> </>
        if '</i>' in vi_text:
            item['vi'] = item['vi'].replace('</i>', '</>')
            modified = True
        if '</b>' in vi_text:
            item['vi'] = item['vi'].replace('</b>', '</>')
            modified = True
            
        # 4. Yusia overrides
        if item_id in YUSIA_OVERRIDES:
            item['vi'] = YUSIA_OVERRIDES[item_id]
            modified = True

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Fixed {filepath}")

if __name__ == '__main__':
    for file in os.listdir('translated_text'):
        if file.endswith('.json'):
            fix_json(os.path.join('translated_text', file))
    print("All fixes applied.")
