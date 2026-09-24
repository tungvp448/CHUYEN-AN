import customtkinter as ctk
from typing import List
from src.config import (
    MAX_ATTEMPTS, WORD_LENGTH, 
    COLOR_CELL_EMPTY, COLOR_CELL_BORDER_EMPTY, COLOR_CELL_BORDER_ACTIVE,
    COLOR_CORRECT, COLOR_PRESENT, COLOR_ABSENT, COLOR_TEXT_PRIMARY
)
from src.game_engine import CellStatus

class GridView(ctk.CTkFrame):
    """Bảng 6 hàng ô chữ tự động co giãn theo số lượng chữ cái (word_length) của từng vụ án."""

    def __init__(self, master, default_word_length: int = WORD_LENGTH, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.word_length = default_word_length
        self.row_containers: List[ctk.CTkFrame] = []
        self.cell_frames: List[List[ctk.CTkFrame]] = []
        self.cell_labels: List[List[ctk.CTkLabel]] = []

        self._build_grid()

    def set_word_length(self, new_length: int):
        """Thay đổi độ dài từ khóa và tự động vẽ lại bảng với kích thước ô phù hợp."""
        if new_length == self.word_length and len(self.cell_frames) > 0:
            self.reset()
            return

        self.word_length = max(3, min(10, new_length))
        self._build_grid()

    def _build_grid(self):
        """Khởi tạo ma trận các ô chữ linh hoạt."""
        # Xóa các thành phần cũ nếu có
        for widget in self.winfo_children():
            widget.destroy()

        self.row_containers = []
        self.cell_frames = []
        self.cell_labels = []

        # Tự động tính kích thước ô chữ và font phù hợp theo độ dài từ
        # Giữ tổng chiều ngang khoảng 440px
        total_available = 440
        gap = 6
        cell_size = min(48, max(32, int((total_available - (self.word_length * gap)) / self.word_length)))
        font_size = max(13, int(cell_size * 0.45))

        for r in range(MAX_ATTEMPTS):
            row_frames = []
            row_labels = []
            row_container = ctk.CTkFrame(self, fg_color="transparent")
            row_container.pack(pady=gap // 2)
            self.row_containers.append(row_container)

            for c in range(self.word_length):
                frame = ctk.CTkFrame(
                    row_container,
                    width=cell_size,
                    height=cell_size,
                    corner_radius=6,
                    fg_color=COLOR_CELL_EMPTY,
                    border_width=2,
                    border_color=COLOR_CELL_BORDER_EMPTY
                )
                frame.pack_propagate(False)
                frame.pack(side="left", padx=gap // 2)

                label = ctk.CTkLabel(
                    frame,
                    text="",
                    font=ctk.CTkFont(family="Arial", size=font_size, weight="bold"),
                    text_color=COLOR_TEXT_PRIMARY
                )
                label.pack(expand=True, fill="both")

                row_frames.append(frame)
                row_labels.append(label)

            self.cell_frames.append(row_frames)
            self.cell_labels.append(row_labels)

    def update_grid(self, grid: List[List[str]], status_matrix: List[List[CellStatus]]):
        """Cập nhật chữ cái và màu sắc cho từng ô."""
        for r in range(MAX_ATTEMPTS):
            if r >= len(grid) or r >= len(self.cell_frames):
                continue
            for c in range(self.word_length):
                if c >= len(grid[r]) or c >= len(self.cell_frames[r]):
                    continue

                char = grid[r][c]
                status = status_matrix[r][c]
                label = self.cell_labels[r][c]
                frame = self.cell_frames[r][c]

                label.configure(text=char)

                if status == CellStatus.CORRECT:
                    frame.configure(fg_color=COLOR_CORRECT, border_width=0)
                elif status == CellStatus.PRESENT:
                    frame.configure(fg_color=COLOR_PRESENT, border_width=0)
                elif status == CellStatus.ABSENT:
                    frame.configure(fg_color=COLOR_ABSENT, border_width=0)
                elif status == CellStatus.FILLED:
                    frame.configure(fg_color=COLOR_CELL_EMPTY, border_width=2, border_color=COLOR_CELL_BORDER_ACTIVE)
                else: # EMPTY
                    frame.configure(fg_color=COLOR_CELL_EMPTY, border_width=2, border_color=COLOR_CELL_BORDER_EMPTY)

    def reset(self):
        """Đặt lại toàn bộ các ô về trạng thái rỗng."""
        for r in range(MAX_ATTEMPTS):
            if r >= len(self.cell_frames):
                continue
            for c in range(self.word_length):
                if c >= len(self.cell_frames[r]):
                    continue
                self.cell_labels[r][c].configure(text="")
                self.cell_frames[r][c].configure(
                    fg_color=COLOR_CELL_EMPTY, 
                    border_width=2, 
                    border_color=COLOR_CELL_BORDER_EMPTY
                )
