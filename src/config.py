import os

# --- THƯ MỤC DỰ ÁN ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Hỗ trợ cả 2 cách đặt tên thư mục tài nguyên: assets và assests
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
if not os.path.exists(ASSETS_DIR):
    ALT_ASSETS = os.path.join(BASE_DIR, "assests")
    if os.path.exists(ALT_ASSETS):
        ASSETS_DIR = ALT_ASSETS

IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
DATA_DIR = os.path.join(BASE_DIR, "data")
CASES_FILE = os.path.join(DATA_DIR, "cases.json")

# --- LUẬT GAME ---
MAX_ATTEMPTS = 6
WORD_LENGTH = 5
MAX_CLUES = 3

# --- KÍCH THƯỚC CỬA SỔ ---
WINDOW_WIDTH = 560
WINDOW_HEIGHT = 860
IMAGE_HEIGHT = 160

# --- BẢNG MÃ MÀU CHUYÊN ÁN (DARK MODE WORDLE THEME) ---
COLOR_BG = "#121213"              # Nền cửa sổ chính
COLOR_CARD_BG = "#1a1a1d"         # Nền các khung thẻ / card
COLOR_TEXT_PRIMARY = "#FFFFFF"     # Chữ màu trắng
COLOR_TEXT_MUTED = "#8e8e93"       # Chữ mờ / phụ đề

# Màu ô chữ Wordle
COLOR_CELL_EMPTY = "#18181b"       # Ô trống
COLOR_CELL_BORDER_EMPTY = "#3f3f46" # Viền ô trống
COLOR_CELL_BORDER_ACTIVE = "#71717a" # Viền ô đang nhập
COLOR_CORRECT = "#538d4e"          # Xanh lá: Đúng chữ, đúng vị trí
COLOR_PRESENT = "#b59f3b"          # Vàng: Có chữ, sai vị trí
COLOR_ABSENT = "#3a3a3c"           # Xám tối: Chữ không có trong từ

# Màu bàn phím ảo
COLOR_KEY_DEFAULT = "#404045"
COLOR_KEY_TEXT = "#FFFFFF"

# Màu chủ đề trinh thám (Detective Accent)
COLOR_ACCENT = "#d97706"           # Màu vàng đồng / huy hiệu thám tử
COLOR_ACCENT_HOVER = "#b45309"
COLOR_BTN_CLUE = "#0284c7"         # Nút mở manh mối (Xanh biển)
COLOR_BTN_CLUE_HOVER = "#0369a1"
