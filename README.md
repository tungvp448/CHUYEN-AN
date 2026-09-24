# 🕵️ CHUYÊN ÁN - Đấu Trường Wordle Trinh Thám

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/CustomTkinter-5.x-blue?style=for-the-badge" alt="CustomTkinter" />
  <img src="https://img.shields.io/badge/Status-Completed-success?style=for-the-badge" alt="Status" />
</p>

> **CHUYÊN ÁN** là trò chơi giải đố mật mã trinh thám dựa trên cơ chế Wordle kinh điển kết hợp phong cách đấu trường thi đấu lập trình (Competitive Programming). Người chơi quan sát vật chứng tại hiện trường, mở khóa các manh mối điều tra và có tối đa 6 lượt để giải mã từ khóa bí mật.

---

## ✨ Tính Năng Nổi Bật

* 🧩 **Wordle Độ Dài Linh Hoạt (Dynamic Word Length):** Không bị giới hạn ở 5 chữ cái. Mỗi vụ án có thể có độ dài từ khóa bất kỳ (4, 5, 6, 7... chữ cái). Bảng ô chữ tự động co giãn thông minh theo từng vụ án.
* 🖼️ **Cơ Chế Mở Khóa Ảnh Thật (Reveal Image):**
  * Trong lúc phá án: Hiển thị ảnh vật chứng gợi ý ban đầu (ảnh 8-bit, ảnh bóng mờ...).
  * Khi đoán đúng từ khóa: Hệ thống tự động hoán đổi sang bức ảnh đáp án thật sắc nét!
* 🎵 **Hệ Thống Âm Thanh & Nhạc Nền Trinh Thám:**
  * Nhạc nền `bgm.mp3` tự động phát lặp vô tận khi bắt đầu chuyên án.
  * 6 hiệu ứng âm thanh SFX (`type`, `submit`, `clue`, `win`, `lose`, `error`).
  * Cơ chế ngắt âm thanh thông minh khi chuyển sang vụ án mới hoặc bấm "Thi đấu lại".
* 🏆 **Bảng Xếp Hạng Chuẩn Thi Đấu CP (ICPC / Codeforces):**
  * Đồng hồ đếm thời gian trực tiếp `⏱️ Live Timer`.
  * Thanh chọn vụ án hiển thị huy hiệu `AC (+2)` hoặc `Failed (-6)`.
  * Hệ thống tính điểm: Điểm cơ bản - Phạt số lượt đoán - Phạt số manh mối - Phạt thời gian giải.
  * Bảng xếp hạng Standings lưu trữ vĩnh viễn trong `data/leaderboard.json` với huy chương 🥇 🥈 🥉.
* 📱 **Hỗ Trợ Đa Nền Tảng (Cross-Platform):**
  * **Bản Web (`app.py`):** Giao diện Dark Noir Responsive tối ưu tuyệt đối cho cả máy tính và màn hình điện thoại cảm ứng.
  * **Bản Desktop (`main.py`):** Ứng dụng máy tính mượt mà với CustomTkinter.
  * Cả hai nền tảng dùng chung 100% kho dữ liệu `cases.json` và thư mục tài nguyên `assets/`.

---

## 📂 Cấu Trúc Thư Mục Dự Án

```text
CHUYÊN ÁN/
│
├── assets/                  # Tài nguyên dùng chung
│   ├── images/              # Ảnh vật chứng gợi ý và ảnh thật reveal (.png, .jpg)
│   └── sounds/              # Toàn bộ 7 file âm thanh (bgm.mp3, type.wav, win.wav...)
│
├── data/
│   ├── cases.json           # Dữ liệu hồ sơ vụ án, từ khóa và các manh mối
│   └── leaderboard.json     # Bảng xếp hạng thành tích các thám tử
│
├── static/                  # Tài nguyên cho Bản Web
│   ├── css/style.css        # Giao diện Dark Noir & Animation lật ô, rung lắc
│   └── js/game.js           # Điều khiển thi đấu, đồng hồ, âm thanh và bảng xếp hạng
│
├── templates/
│   └── index.html           # Khung giao diện Web Contest
│
├── src/                     # Mã nguồn cho Bản Desktop
│   ├── config.py            # Cài đặt hằng số, màu sắc, kích thước
│   ├── game_engine.py       # Thuật toán so khớp Wordle 2 lượt chuẩn xác
│   ├── data_manager.py      # Bộ nạp dữ liệu hồ sơ vụ án an toàn
│   ├── sound_manager.py     # Quản lý phát nhạc nền & SFX trên máy tính
│   └── ui/                  # Giao diện CustomTkinter (Grid, Keyboard, ImageView)
│
├── app.py                   # Điểm khởi chạy BẢN WEB (Flask Server)
├── main.py                  # Điểm khởi chạy BẢN DESKTOP
├── requirements.txt         # Danh sách thư viện phụ thuộc
├── .gitignore               # Cấu hình bỏ qua file rác của Git
└── README.md                # Tài liệu hướng dẫn dự án
```

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy Cục Bộ (Local)

### 1. Cài đặt môi trường
Yêu cầu máy tính đã cài đặt **Python 3.10** trở lên. Mở Terminal / PowerShell tại thư mục dự án và chạy:
```bash
pip install -r requirements.txt
```

### 2. Khởi chạy Bản WEB (Khuyên dùng)
```bash
python app.py
```
👉 Mở trình duyệt truy cập: **`http://localhost:5000`**  
*(Nếu muốn chơi trên điện thoại cùng mạng Wi-Fi, truy cập theo địa chỉ IP LAN hiển thị trên Terminal, ví dụ: `http://192.168.1.X:5000`)*

### 3. Khởi chạy Bản DESKTOP
```bash
python main.py
```

---

## 🌐 Hướng Dẫn Deploy Chạy Server Online 24/24

Để bạn bè ở bất kỳ đâu cũng có thể vào chơi qua đường link công khai mọi lúc mà không cần bạn bật máy tính:

### Cách triển khai lên [Render.com](https://render.com) (Dễ nhất):
1. Đẩy mã nguồn dự án lên một kho chứa (Repository) trên **GitHub**.
2. Đăng ký/Đăng nhập vào **Render.com** bằng tài khoản GitHub.
3. Bấm nút **New +** ➔ Chọn **Web Service** ➔ Chọn Repository `CHUYÊN ÁN`.
4. Cấu hình thông số:
   * **Name:** `chuyen-an`
   * **Region:** `Singapore` (để người chơi ở Việt Nam có tốc độ nhanh nhất)
   * **Runtime:** `Python 3`
   * **Build Command:** `pip install -r requirements.txt`
   * **Start Command:** `gunicorn app:app`
   * **Instance Type:** Chọn gói `Free` (hoặc `Starter $7/tháng` để server chạy 24/24 không bao giờ ngủ).
5. Bấm **Deploy Web Service** ➔ Render sẽ cấp cho bạn một đường link HTTPS (ví dụ: `https://chuyen-an.onrender.com`) để chia sẻ cho mọi người!

---

## 📝 Cách Thêm Vụ Án Mới

Mở file [`data/cases.json`](data/cases.json) và thêm một đối tượng vụ án mới:

```json
{
  "id": 3,
  "case_name": "Tên vụ án hiển thị",
  "word": "MẬT_MÃ",
  "image": "assets/images/anh_goi_y.png",
  "reveal_image": "assets/images/anh_that.png",
  "clues": [
    "Manh mối gợi ý số 1",
    "Manh mối gợi ý số 2",
    "Manh mối gợi ý số 3"
  ]
}
```

* **`word`:** Từ khóa bí mật người chơi phải đoán (độ dài linh hoạt tùy ý).
* **`image`:** Ảnh gợi ý ban đầu đặt trong `assets/images/`.
* **`reveal_image`:** Ảnh thật xuất hiện ngay khi người chơi đoán đúng.
* Cả bản Web lẫn Desktop đều sẽ tự động nhận diện câu đố mới ngay lập tức mà không cần khởi động lại code!

---

## 📜 Giấy Phép (License)
Dự án được phát triển nhằm mục đích học tập, giải trí và thi đấu suy luận logic. Hoàn toàn mã nguồn mở theo giấy phép MIT.
