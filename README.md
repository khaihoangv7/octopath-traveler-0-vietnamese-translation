# Việt Hóa Game (Unreal Engine 4 & General)

Tài liệu này ghi lại toàn bộ quy trình chuẩn để Việt hóa một tựa game (đặc biệt là các game dùng Unreal Engine 4/5 như Octopath Traveler). Bạn có thể lưu lại và gửi cho AI (như Gemini) trong các dự án sau để nó hiểu ngay bối cảnh và tự động code các tool cần thiết.

---

## Bước 1: Khảo sát & Vượt rào bảo mật (Unpacking)
Hầu hết các game hiện đại đều mã hóa hoặc nén dữ liệu. Đối với Unreal Engine, dữ liệu nằm trong các file `.pak`.
1. **Tìm AES Key:** Nếu file `.pak` bị khóa (mã hóa), cần phải tìm chuỗi khóa AES (ví dụ: `0x14A2B...`).
   - *Kỹ thuật:* Dùng phần mềm giả lập hoặc yêu cầu AI viết script Python đọc trực tiếp bộ nhớ RAM (Memory Dump) khi game đang chạy để moi key ra (như file `dump_aes_key.py` chúng ta đã làm).
2. **Giải nén (Unpack):** Dùng công cụ giải nén chuyên dụng (như `repak_cli` hoặc `UnrealPak.exe` của Epic Games) truyền AES Key vào để xả toàn bộ dữ liệu từ `.pak` ra thư mục con.

## Bước 2: Phân tích cấu trúc & Trích xuất Text (Extraction)
1. **Định vị file Text:** Tìm đến thư mục chứa ngôn ngữ gốc của game (thường là `Content/Local/EN-US` hoặc `Localization`). Các file chữ thường có đuôi `.uexp`, `.uasset` hoặc `.locres`.
2. **Phân tích nhị phân (Binary Analysis):** Mở thử file bằng Hex Editor (HxD) để xem cấu trúc bên trong. 
   - Với Octopath Traveler, chữ không nằm trần trụi mà bị gói trong định dạng **MessagePack** (một dạng cấu trúc siêu nén).
3. **Viết Script trích xuất:** Yêu cầu AI viết một script Python (`extract.py`) để:
   - Cắt bỏ phần đầu (Header) và phần đuôi (Footer) của hệ thống Unreal Engine.
   - Dùng thư viện (như `msgpack`) để dịch ngược cục dữ liệu ở giữa thành file `.json` hoặc `.csv` để con người có thể mở ra đọc được.

## Bước 3: Dịch thuật quy mô lớn (Mass Translation bằng AI)
Khi game có quá nhiều chữ (ví dụ 50.000 dòng), dịch bằng tay hoặc copy-paste là bất khả thi.
1. **Chuẩn bị API Key:** Đăng ký lấy API Key miễn phí từ Google AI Studio (Gemini).
2. **Viết Auto-Translator Tool:** Yêu cầu AI viết script Python (`auto_translate.py`) tự động hóa việc dịch:
   - Đọc từng dòng từ file JSON gốc.
   - Gửi lên API dịch theo từng cụm (batch) 100 câu/lần để không bị nghẽn mạng.
   - Truyền "Ngữ cảnh" (Prompt) cực kỳ nghiêm ngặt: *Đây là game RPG, xưng hô ta-ngươi, giữ nguyên các mã code {0}, <color>...*
   - Xử lý lỗi Quota: Thêm lệnh đếm ngược thời gian chờ (time.sleep) nếu gọi quá giới hạn miễn phí để tool không bị đứng giữa chừng. Thêm cờ đánh dấu (`api_translated`) để tránh bị lặp lại các câu đã dịch.

## Bước 4: Đóng gói ngược lại (Repacking)
Đây là khâu kỹ thuật phức tạp nhất để đánh lừa Engine game.
1. **Chuyển về Binary:** Viết script Python (`repack.py`) đọc các file JSON đã dịch, nén chúng lại thành định dạng gốc (MessagePack).
2. **Ghép nối (Inject):** Bơm đoạn dữ liệu nhị phân mới này vào giữa Header và Footer của file `.uexp` ban đầu. 
   - *Lưu ý sống còn:* Phải tính toán lại kích thước file (Size) và chèn lại vào đúng vị trí byte kích thước trong Header của Unreal Engine.
3. **Tạo File Mod (.pak):** Tạo cây thư mục giả lập y hệt thư mục gốc của game (vd: `Octopath_Traveler0\Content\Local\DataBase\...`). Đặt các file `.uexp` vừa tạo vào đúng thư mục đó. 
   - Sau đó dùng tool `u4pak.py` hoặc `repak_cli` nén lại thành file `pakchunk99-Vietnamese_P.pak`. (Chữ `_P` mang ý nghĩa Patch, giúp game ưu tiên đọc file này đè lên file tiếng Anh gốc).

## Bước 5: Thay Font Tiếng Việt (Font Modding)
Text tiếng Việt có dấu (ư, ơ, ê...) sẽ bị ô vuông nếu font chữ của game không hỗ trợ Unicode.
1. **Test trước:** Cứ bỏ file Mod Text (pakchunk99) vào thư mục `Paks` của game chạy thử. Nếu game của hãng lớn có "Fallback Font" (như Arial/NotoSans ẩn bên trong) thì chữ sẽ tự hiển thị đẹp.
2. **Can thiệp Font:** Nếu bị lỗi ô vuông, dùng phần mềm chuyên dụng **UAssetGUI** mở file font `.uasset` của game ra, đổi đường dẫn (font face) sang một font chữ khác, hoặc dùng Unreal Engine Editor render (chế) một file `.ufont` tương đồng chép đè vào.

