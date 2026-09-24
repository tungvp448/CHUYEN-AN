import customtkinter as ctk
from typing import Callable, Dict
from src.config import (
    COLOR_KEY_DEFAULT, COLOR_KEY_TEXT,
    COLOR_CORRECT, COLOR_PRESENT, COLOR_ABSENT
)
from src.game_engine import CellStatus

KEYBOARD_LAYOUT = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
    ["ENTER", "Z", "X", "C", "V", "B", "N", "M", "⌫"]
]

class KeyboardView(ctk.CTkFrame):
    """Bàn phím ảo trực quan dạng QWERTY, cập nhật màu theo tiến trình đoán."""

    def __init__(self, master, on_key_click: Callable[[str], None], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.on_key_click = on_key_click
        self.buttons: Dict[str, ctk.CTkButton] = {}

        self._build_keyboard()

    def _build_keyboard(self):
        """Khởi tạo các hàng phím bấm."""
        for row in KEYBOARD_LAYOUT:
            row_frame = ctk.CTkFrame(self, fg_color="transparent")
            row_frame.pack(pady=3)

            for key in row:
                btn_width = 38
                btn_text = key
                if key == "ENTER":
                    btn_width = 62
                elif key == "⌫":
                    btn_width = 46

                btn = ctk.CTkButton(
                    row_frame,
                    text=btn_text,
                    width=btn_width,
                    height=44,
                    corner_radius=6,
                    fg_color=COLOR_KEY_DEFAULT,
                    hover_color="#52525b",
                    text_color=COLOR_KEY_TEXT,
                    font=ctk.CTkFont(family="Arial", size=13, weight="bold"),
                    command=lambda k=key: self._handle_click(k)
                )
                btn.pack(side="left", padx=2)
                
                # Lưu tham chiếu để sau này đổi màu
                dict_key = "BACKSPACE" if key == "⌫" else key
                self.buttons[dict_key] = btn

    def _handle_click(self, key: str):
        if key == "⌫":
            self.on_key_click("BACKSPACE")
        else:
            self.on_key_click(key)

    def update_keys(self, keyboard_status: Dict[str, CellStatus]):
        """Cập nhật màu sắc các phím theo trạng thái xanh/vàng/xám."""
        for char, status in keyboard_status.items():
            btn = self.buttons.get(char)
            if not btn:
                continue

            if status == CellStatus.CORRECT:
                btn.configure(fg_color=COLOR_CORRECT, hover_color="#44733e")
            elif status == CellStatus.PRESENT:
                btn.configure(fg_color=COLOR_PRESENT, hover_color="#9c872f")
            elif status == CellStatus.ABSENT:
                btn.configure(fg_color=COLOR_ABSENT, hover_color="#27272a")

    def reset(self):
        """Đặt lại màu tất cả các phím về mặc định."""
        for btn in self.buttons.values():
            btn.configure(fg_color=COLOR_KEY_DEFAULT, hover_color="#52525b")
