from enum import Enum
from typing import List, Dict, Tuple, Optional
from collections import Counter
from src.config import MAX_ATTEMPTS, WORD_LENGTH, MAX_CLUES

class CellStatus(Enum):
    EMPTY = "empty"
    FILLED = "filled"
    CORRECT = "correct"   # Xanh lá (đúng chữ, đúng vị trí)
    PRESENT = "present"   # Vàng (có chữ, sai vị trí)
    ABSENT = "absent"     # Xám (không có chữ trong từ)

class GameStatus(Enum):
    PLAYING = "playing"
    WON = "won"
    LOST = "lost"

class GameEngine:
    """Xử lý logic cốt lõi của trò chơi: so khớp chữ, tính lượt, quản lý manh mối."""

    def __init__(self):
        self.current_case: Optional[Dict] = None
        self.target_word: str = ""
        self.word_length: int = WORD_LENGTH
        self.current_row: int = 0
        self.current_col: int = 0
        self.grid: List[List[str]] = [["" for _ in range(WORD_LENGTH)] for _ in range(MAX_ATTEMPTS)]
        self.grid_status: List[List[CellStatus]] = [[CellStatus.EMPTY for _ in range(WORD_LENGTH)] for _ in range(MAX_ATTEMPTS)]
        self.keyboard_status: Dict[str, CellStatus] = {}
        self.revealed_clues: int = 0
        self.game_status: GameStatus = GameStatus.PLAYING

    def start_case(self, case_data: Dict):
        """Khởi động ván chơi mới với một vụ án cụ thể."""
        self.current_case = case_data
        self.target_word = case_data.get("word", "").strip().upper()
        self.word_length = len(self.target_word) if self.target_word else WORD_LENGTH
        self.current_row = 0
        self.current_col = 0
        self.grid = [["" for _ in range(self.word_length)] for _ in range(MAX_ATTEMPTS)]
        self.grid_status = [[CellStatus.EMPTY for _ in range(self.word_length)] for _ in range(MAX_ATTEMPTS)]
        self.keyboard_status = {}
        self.revealed_clues = 0
        self.game_status = GameStatus.PLAYING

    def add_letter(self, letter: str) -> bool:
        """Thêm 1 chữ cái vào hàng hiện tại."""
        if self.game_status != GameStatus.PLAYING:
            return False
        if self.current_col < self.word_length:
            char = letter.upper()
            self.grid[self.current_row][self.current_col] = char
            self.grid_status[self.current_row][self.current_col] = CellStatus.FILLED
            self.current_col += 1
            return True
        return False

    def remove_letter(self) -> bool:
        """Xóa 1 chữ cái vừa gõ (Backspace)."""
        if self.game_status != GameStatus.PLAYING:
            return False
        if self.current_col > 0:
            self.current_col -= 1
            self.grid[self.current_row][self.current_col] = ""
            self.grid_status[self.current_row][self.current_col] = CellStatus.EMPTY
            return True
        return False

    def submit_guess(self) -> Tuple[bool, str, List[CellStatus]]:
        """
        Nộp từ đoán (Enter).
        Áp dụng thuật toán so khớp chuẩn 2 lượt của Wordle (xử lý chính xác chữ cái lặp lại).
        """
        if self.game_status != GameStatus.PLAYING:
            return False, "Ván chơi đã kết thúc!", []

        if self.current_col < self.word_length:
            return False, f"Chưa đủ {self.word_length} chữ cái!", []

        guess = "".join(self.grid[self.current_row])
        result_status = [CellStatus.ABSENT] * self.word_length
        
        # Đếm tần suất các chữ cái trong từ mục tiêu
        target_counts = Counter(self.target_word)

        # Lượt 1: Xác định tất cả các chữ cái ĐÚNG VỊ TRÍ (Xanh lá - CORRECT)
        for i in range(self.word_length):
            if guess[i] == self.target_word[i]:
                result_status[i] = CellStatus.CORRECT
                target_counts[guess[i]] -= 1

        # Lượt 2: Xác định các chữ cái CÓ TRONG TỪ NHƯNG SAI VỊ TRÍ (Vàng - PRESENT)
        for i in range(self.word_length):
            if result_status[i] != CellStatus.CORRECT:
                char = guess[i]
                if target_counts.get(char, 0) > 0:
                    result_status[i] = CellStatus.PRESENT
                    target_counts[char] -= 1
                else:
                    result_status[i] = CellStatus.ABSENT

        # Cập nhật trạng thái lưới
        self.grid_status[self.current_row] = result_status

        # Cập nhật trạng thái bàn phím ảo (ưu tiên CORRECT > PRESENT > ABSENT)
        for char, status in zip(guess, result_status):
            old_status = self.keyboard_status.get(char)
            if old_status == CellStatus.CORRECT:
                continue # Đã xanh rồi thì giữ nguyên
            elif old_status == CellStatus.PRESENT and status == CellStatus.ABSENT:
                continue # Đã vàng rồi thì không bị hạ xuống xám
            self.keyboard_status[char] = status

        # Kiểm tra điều kiện thắng
        if guess == self.target_word:
            self.game_status = GameStatus.WON
            return True, "🎉 PHÁ ÁN THÀNH CÔNG! BẠN ĐÃ TÌM RA TỪ KHÓA!", result_status

        # Sang hàng tiếp theo
        self.current_row += 1
        self.current_col = 0

        # Kiểm tra điều kiện hết lượt (thua)
        if self.current_row >= MAX_ATTEMPTS:
            self.game_status = GameStatus.LOST
            return True, f"💀 CHUYÊN ÁN BẾ TẮC! TỪ KHÓA LÀ: {self.target_word}", result_status

        return True, "Tiếp tục giải mã...", result_status

    def reveal_next_clue(self) -> Tuple[bool, str]:
        """Lấy manh mối tiếp theo của vụ án."""
        if not self.current_case:
            return False, "Không có dữ liệu vụ án."

        clues = self.current_case.get("clues", [])
        if self.revealed_clues < len(clues):
            clue_text = clues[self.revealed_clues]
            self.revealed_clues += 1
            return True, f"🔍 Manh mối {self.revealed_clues}/{len(clues)}: {clue_text}"
        else:
            return False, "Đã hết manh mối cho vụ án này!"
