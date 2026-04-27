import json
import os

INPUT_FILE = 'translated_text/GameTextEvent.json'

# Đoạn hội thoại mở đầu cốt truyện Herminia
STORY_TRANSLATION = {
    112158: "Có",
    112159: "Không",
    413302: "Ngươi cũng định chống lại mụ phù thủy sao?",
    413303: "Thôi, quên chuyện đó đi.",
    413304: "Mặc kệ người ta có căm ghét mụ thế nào — tài sản của mụ ta chỉ có tăng lên thôi.",
    413305: "Tại sao ư? Chà, để ta nói cho mà nghe...",
    1: "Các người đã nghe tin đồn về Quý bà Herminia chưa?",
    2: "Nghe nói mụ ta sẵn sàng tàn sát cả con ruột của mình vì tiền đấy!",
    3: "Ta nghe nói chính mụ đã tận diệt những người rừng cuối cùng!",
    4: "Thật kinh khủng... Một mụ phù thủy không biết gì ngoài lòng tham của bản thân.",
    5: "Và bất cứ thứ gì mụ muốn... mụ đều đoạt được.",
    976: "Mụ ta là",
    977: "kẻ giàu có nhất vương quốc.",
    978: "Quý bà Herminia, \"Phù Thủy Tham Lam.\"",
    979: "Tàn nhẫn nghiền nát bất cứ ai ngáng đường,",
    980: "mụ đã tích lũy được một khối tài sản vô tận.",
    981: "Người đời sợ hãi rỉ tai nhau rằng...",
    983: "\"Mụ phù thủy đó thậm chí",
    984: "có thể mua được cả linh hồn con người.\"",
    12: "Thưa Quý bà Herminia. Khâu chuẩn bị cho buổi vũ hội đã hoàn tất.",
    13: "...Tốt lắm.",
    415467: "Ngươi thực sự định một mình đối đầu với mụ ta sao?",
    415468: "Thật ngu ngốc...",
    415469: "Thật ra, một đám ngốc nghếch giống như ngươi đang tập trung ở con phố chính đấy.",
    415470: "Ngươi nên đến gia nhập cùng bọn chúng đi, tất nhiên là nếu chúng chịu nhận ngươi.",
    14: "...Ngươi đến rồi. Tốt.",
    15: "Hôm nay thời vận của chúng ta sẽ thay đổi. Ta đảm bảo điều đó.",
    16: "Ngươi định thực hiện kế hoạch này thế nào?",
    17: "Chúng ta thậm chí sẽ chẳng lọt nổi qua cái cổng chính đâu!"
}

data = json.load(open(INPUT_FILE, 'r', encoding='utf-8'))
translated_count = 0

for e in data:
    if e['id'] in STORY_TRANSLATION:
        e['vi'] = STORY_TRANSLATION[e['id']]
        translated_count += 1

with open(INPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("=" * 60)
print(f"Bản demo dịch thuật AI: Cập nhật thành công {translated_count} dòng hội thoại vào GameTextEvent.json")
print("=" * 60)
for eid, text in STORY_TRANSLATION.items():
    print(f"{eid} | {text}")
