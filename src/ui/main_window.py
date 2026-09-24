import customtkinter as ctk
from typing import Optional

from src.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_BG, COLOR_CARD_BG,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_MUTED, COLOR_ACCENT, COLOR_ACCENT_HOVER,
    COLOR_BTN_CLUE, COLOR_BTN_CLUE_HOVER
)
from src.game_engine import GameEngine, GameStatus
from src.data_manager import DataManager
from src.sound_manager import SoundManager
from src.ui.image_view import ImageView
from src.ui.grid_view import GridView
from src.ui.keyboard_view import KeyboardView

class MainWindow(ctk.CTk):
    """Cửa sổ ứng dụng chính kết nối toàn bộ thành phần giao diện, logic và âm thanh."""

    def __init__(self):
        super().__init__()

        # Cấu hình cửa sổ
        self.title("CHUYÊN ÁN - Mật mã Wordle")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_BG)

        # Khởi tạo các thành phần quản lý
        self.data_manager = DataManager()
        self.game_engine = GameEngine()
        self.sound_manager = SoundManager()

        self.current_case_idx = 0

        # Xây dựng giao diện
        self._build_ui()

        # Bắt sự kiện bàn phím máy tính
        self.bind("<Key>", self._on_physical_key)

        # Khởi động ván chơi đầu tiên
        self._load_case(self.current_case_idx)

        # Phát nhạc nền
        self.after(500, self.sound_manager.play_bgm)

    def _build_ui(self):
        """Tạo layout giao diện người dùng."""
        # 1. HEADER (Thanh tiêu đề trên cùng)
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header_frame.pack(fill="x", padx=16, pady=(12, 6))

        # Tiêu đề game bên trái
        self.title_label = ctk.CTkLabel(
            header_frame,
            text="🕵️ CHUYÊN ÁN #1",
            font=ctk.CTkFont(family="Arial", size=18, weight="bold"),
            text_color=COLOR_ACCENT
        )
        self.title_label.pack(side="left")

        # Nút chuyển vụ án tiếp theo
        self.btn_next_case = ctk.CTkButton(
            header_frame,
            text="Vụ án tiếp ➔",
            width=90,
            height=30,
            corner_radius=6,
            fg_color="#27272a",
            hover_color="#3f3f46",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._next_case
        )
        self.btn_next_case.pack(side="right", padx=(6, 0))

        # Nút bật/tắt nhạc nền (BGM)
        self.btn_music = ctk.CTkButton(
            header_frame,
            text="🎵",
            width=36,
            height=30,
            corner_radius=6,
            fg_color="#27272a",
            hover_color="#3f3f46",
            font=ctk.CTkFont(size=14),
            command=self._toggle_music
        )
        self.btn_music.pack(side="right", padx=(6, 0))

        # Nút bật/tắt hiệu ứng âm thanh (SFX)
        self.btn_sound = ctk.CTkButton(
            header_frame,
            text="🔊",
            width=36,
            height=30,
            corner_radius=6,
            fg_color="#27272a",
            hover_color="#3f3f46",
            font=ctk.CTkFont(size=14),
            command=self._toggle_sound
        )
        self.btn_sound.pack(side="right")

        # 2. TÊN VỤ ÁN
        self.case_name_label = ctk.CTkLabel(
            self,
            text="Đang nạp hồ sơ...",
            font=ctk.CTkFont(family="Arial", size=14, weight="normal"),
            text_color=COLOR_TEXT_MUTED
        )
        self.case_name_label.pack(pady=(0, 6))

        # 3. KHUNG ẢNH VẬT CHỨNG / HIỆN TRƯỜNG
        self.image_view = ImageView(self, width=480, height=190)
        self.image_view.pack(pady=4)

        # 4. KHUNG HIỂN THỊ MANH MỐI (CLUE BOX)
        self.clue_frame = ctk.CTkFrame(self, fg_color=COLOR_CARD_BG, corner_radius=8, height=45, width=480)
        self.clue_frame.pack_propagate(False)
        self.clue_frame.pack(pady=(6, 4))

        self.clue_label = ctk.CTkLabel(
            self.clue_frame,
            text="💡 Bấm 'Xem Manh Mối' để mở gợi ý giải mã vụ án",
            font=ctk.CTkFont(family="Arial", size=12, slant="italic"),
            text_color=COLOR_TEXT_MUTED,
            wraplength=460
        )
        self.clue_label.pack(expand=True, fill="both", padx=8)

        # Nút bấm xem manh mối
        self.btn_clue = ctk.CTkButton(
            self,
            text="🔍 XEM MANH MỐI (0/3)",
            width=200,
            height=30,
            corner_radius=6,
            fg_color=COLOR_BTN_CLUE,
            hover_color=COLOR_BTN_CLUE_HOVER,
            font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
            command=self._on_clue_click
        )
        self.btn_clue.pack(pady=(0, 6))

        # 5. DÒNG THÔNG BÁO TRẠNG THÁI (STATUS / MESSAGE BAR)
        self.status_label = ctk.CTkLabel(
            self,
            text="Nhập 5 chữ cái để giải mã hung khí / tang vật",
            font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
            text_color="#e4e4e7"
        )
        self.status_label.pack(pady=(2, 6))

        # 6. BẢNG 6 HÀNG Ô CHỮ WORDLE
        self.grid_view = GridView(self)
        self.grid_view.pack(pady=4)

        # 7. BÀN PHÍM ẢO
        self.keyboard_view = KeyboardView(self, on_key_click=self._handle_input)
        self.keyboard_view.pack(pady=(8, 12))

    def _load_case(self, index: int):
        """Tải dữ liệu của một vụ án lên giao diện."""
        # Dừng âm thanh thắng/thua của ván trước đó
        self.sound_manager.stop_all_sfx()

        case_data = self.data_manager.get_case(index)
        if not case_data:
            return

        self.game_engine.start_case(case_data)

        # Cập nhật thông tin Header
        total_cases = self.data_manager.get_total_cases()
        self.title_label.configure(text=f"🕵️ CHUYÊN ÁN #{case_data.get('id', index + 1)}/{total_cases}")
        case_name = case_data.get("case_name", f"Vụ án số {index + 1}")
        self.case_name_label.configure(text=case_name)

        # Tải ảnh hoặc placeholder
        img_path = self.data_manager.resolve_image_path(case_data.get("image", ""))
        self.image_view.set_image(img_path, case_name)

        # Đặt lại manh mối
        clues_count = len(case_data.get("clues", []))
        self.btn_clue.configure(text=f"🔍 XEM MANH MỐI (0/{clues_count})", state="normal")
        self.clue_label.configure(
            text="💡 Bấm 'Xem Manh Mối' để mở gợi ý giải mã vụ án",
            text_color=COLOR_TEXT_MUTED
        )

        # Đặt lại bảng ô chữ theo đúng độ dài từ của vụ án này
        self.grid_view.set_word_length(self.game_engine.word_length)
        self.status_label.configure(
            text=f"Nhập {self.game_engine.word_length} chữ cái để giải mã hung khí / tang vật",
            text_color="#e4e4e7"
        )
        self.keyboard_view.reset()

    def _handle_input(self, key: str):
        """Xử lý ký tự người chơi nhập (từ bàn phím ảo hoặc phím vật lý)."""
        if self.game_engine.game_status != GameStatus.PLAYING:
            return

        if key == "ENTER":
            success, msg, _ = self.game_engine.submit_guess()
            if success:
                # Cập nhật giao diện
                self.grid_view.update_grid(self.game_engine.grid, self.game_engine.grid_status)
                self.keyboard_view.update_keys(self.game_engine.keyboard_status)
                
                # Kiểm tra trạng thái ván
                if self.game_engine.game_status == GameStatus.WON:
                    self.sound_manager.play_sfx("win")
                    self.status_label.configure(text=msg, text_color="#4ade80")
                    # Hiển thị ảnh mở khóa nếu có
                    case_data = self.game_engine.current_case or {}
                    reveal_path = case_data.get("reveal_image") or case_data.get("correct_image") or case_data.get("solved_image")
                    if reveal_path:
                        real_img_path = self.data_manager.resolve_image_path(reveal_path)
                        self.image_view.set_image(real_img_path, "VẬT CHỨNG ĐÃ ĐƯỢC GIẢI MÃ!")
                elif self.game_engine.game_status == GameStatus.LOST:
                    self.sound_manager.play_sfx("lose")
                    self.status_label.configure(text=msg, text_color="#f87171")
                else:
                    self.sound_manager.play_sfx("submit")
                    self.status_label.configure(text=msg, text_color="#e4e4e7")
            else:
                self.sound_manager.play_sfx("error")
                self.status_label.configure(text=f"⚠️ {msg}", text_color="#facc15")

        elif key == "BACKSPACE":
            if self.game_engine.remove_letter():
                self.sound_manager.play_sfx("type")
                self.grid_view.update_grid(self.game_engine.grid, self.game_engine.grid_status)

        elif len(key) == 1 and key.isalpha():
            if self.game_engine.add_letter(key):
                self.sound_manager.play_sfx("type")
                self.grid_view.update_grid(self.game_engine.grid, self.game_engine.grid_status)

    def _on_physical_key(self, event):
        """Xử lý khi người chơi bấm phím cứng trên bàn phím máy tính."""
        keysym = event.keysym.upper()
        if keysym == "RETURN":
            self._handle_input("ENTER")
        elif keysym == "BACKSPACE":
            self._handle_input("BACKSPACE")
        elif len(keysym) == 1 and keysym.isalpha():
            self._handle_input(keysym)

    def _on_clue_click(self):
        """Mở manh mối tiếp theo."""
        has_clue, clue_text = self.game_engine.reveal_next_clue()
        if has_clue:
            self.sound_manager.play_sfx("clue")
            self.clue_label.configure(text=clue_text, text_color="#38bdf8")
            
            # Cập nhật số lượng manh mối trên nút
            total_clues = len(self.game_engine.current_case.get("clues", []))
            self.btn_clue.configure(text=f"🔍 XEM MANH MỐI ({self.game_engine.revealed_clues}/{total_clues})")
        else:
            self.sound_manager.play_sfx("error")
            self.status_label.configure(text=f"ℹ️ {clue_text}", text_color="#facc15")

    def _next_case(self):
        """Chuyển sang vụ án tiếp theo hoặc quay vòng lại từ đầu."""
        total = self.data_manager.get_total_cases()
        if total > 0:
            self.current_case_idx = (self.current_case_idx + 1) % total
            self._load_case(self.current_case_idx)

    def _toggle_music(self):
        """Bật/tắt nhạc nền."""
        is_on = self.sound_manager.toggle_music()
        self.btn_music.configure(text="🎵" if is_on else "🔇")

    def _toggle_sound(self):
        """Bật/tắt hiệu ứng âm thanh."""
        is_on = self.sound_manager.toggle_sound()
        self.btn_sound.configure(text="🔊" if is_on else "🔕")
