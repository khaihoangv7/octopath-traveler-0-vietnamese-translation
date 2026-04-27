# Dự Án Việt Hóa Octopath Traveler 0

Dự án cung cấp bộ công cụ tự động hóa toàn bộ quy trình trích xuất, dịch thuật và đóng gói ngôn ngữ Tiếng Việt cho game Octopath Traveler (Unreal Engine 4).

---

## Dành Cho Người Chơi (Cài đặt nhanh)
Nếu bạn chỉ muốn chơi game bằng Tiếng Việt, hãy làm theo các bước sau:
1. Truy cập vào mục [Releases](https://github.com/khaihoangv7/octopath-traveler-0-vietnamese-translation/releases) (nếu có).
2. Tải file `pakchunk99-Vietnamese_P.pak` về máy.
3. Chép file vào thư mục cài đặt game theo đường dẫn:  
   `Octopath Traveler/Octopath_Traveler0/Content/Paks/`
4. Mở game và tận hưởng!

---

## Dành Cho Nhà Phát Triển (Sử dụng Tool)
Nếu bạn muốn tự dịch lại hoặc chỉnh sửa bản dịch, hãy làm theo quy trình dưới đây:

### 1. Yêu cầu hệ thống
* Cài đặt [Python 3.10+](https://www.python.org/).
* Cài đặt các thư viện cần thiết:
  ```bash
  pip install msgpack fonttools requests
  ```

### 2. Quy trình thực hiện (Pipeline)
Thực hiện theo đúng thứ tự các file script sau:

1. **Trích xuất Text:**  
   Chạy `extract_text.py` để lấy toàn bộ văn bản từ file `.uexp` của game ra định dạng JSON trong thư mục `extracted_text/`.
   
2. **Dịch thuật:**  
   Sử dụng `auto_translate.py` để dịch nội dung từ `extracted_text/` sang `translated_text/`. (Cần cấu hình Gemini API Key bên trong script).

3. **Sửa lỗi & Tối ưu:**  
   Chạy `fix_translations.py` để xử lý các lỗi xưng hô (Mẹ/Con), xóa các dòng debug "Kiểm thử" và fix lỗi hiển thị mã code.

4. **Đóng gói (Repack):**  
   Chạy `repack.py`. Script này sẽ bơm dữ liệu từ `translated_text/` ngược vào cấu hình binary của game và lưu vào thư mục `Mod_Vietnamese/`.

5. **Nén file .pak:**  
   Chạy lệnh sau trong Terminal để tạo file mod cuối cùng:
   ```bash
   python u4pak.py pack pakchunk99-Vietnamese_P.pak Octopath_Traveler0
   ```

---

## Cấu trúc thư mục
* `translated_text/`: Chứa toàn bộ nội dung đã dịch (Dạng JSON).
* `Mod_Vietnamese/`: Thư mục chứa các file đã được mod, sẵn sàng để đóng gói.
* `research/`: Chứa các script nghiên cứu, tìm AES key và phân tích cấu trúc file.
* `u4pak.py`: Công cụ nén/giải nén file `.pak` của Unreal Engine 4.

---

## Lỗi Hiện Tại (Known Issues)
* **Khoảng cách dòng:** Một số ô hội thoại có thể hiển thị các dòng văn bản quá sát nhau (do giới hạn khung hình của game gốc). Chúng tôi đang nghiên cứu giải pháp tối ưu hơn cho font chữ để khắc phục triệt để vấn đề này.

---

## Tính năng nổi bật
- [x] **Tự động hóa 90%**: Từ trích xuất đến đóng gói.
- [x] **Hỗ trợ Font Tiếng Việt**: Đã cấu hình font Segoe UI hiển thị đẹp, không lỗi dấu.
- [x] **Xử lý ngữ cảnh**: Sửa lỗi xưng hô nhân vật theo quan hệ gia đình (Yusia).
- [x] **Dọn dẹp rác**: Tự động loại bỏ các dòng test kịch bản của nhà phát triển.

---

## Đóng góp
Mọi đóng góp về bản dịch hoặc cải tiến công cụ đều được hoan nghênh. Vui lòng mở `Issue` hoặc tạo `Pull Request`.

**License:** MIT
