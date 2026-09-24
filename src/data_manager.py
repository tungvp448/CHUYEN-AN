import json
import os
from typing import List, Dict, Optional
from src.config import CASES_FILE, BASE_DIR, IMAGES_DIR

class DataManager:
    """Quản lý nạp và trích xuất dữ liệu hồ sơ các vụ án."""

    def __init__(self):
        self.cases: List[Dict] = []
        self.load_cases()

    def load_cases(self):
        """Đọc danh sách các vụ án từ file cases.json."""
        if os.path.exists(CASES_FILE):
            try:
                with open(CASES_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        self.cases = data
                        return
            except Exception as e:
                print(f"[DataManager] Lỗi đọc {CASES_FILE}: {e}")

        # Trường hợp file trống hoặc lỗi, cung cấp vụ án mặc định dự phòng
        self.cases = [
            {
                "id": 1,
                "case_name": "Vụ án: Hung khí trong bếp",
                "word": "KNIFE",
                "image": "assets/images/knife.png",
                "clues": [
                    "Vật chứng sắc nhọn bằng kim loại thường thấy ở hiện trường nhà bếp.",
                    "Thường được dùng làm vật dụng ăn uống đi đôi với nĩa (dĩa).",
                    "Từ gồm 5 chữ cái tiếng Anh, bắt đầu bằng 'K' và kết thúc bằng 'E'."
                ]
            }
        ]

    def get_case(self, index: int) -> Optional[Dict]:
        """Lấy vụ án theo số thứ tự (index bắt đầu từ 0)."""
        if 0 <= index < len(self.cases):
            return self.cases[index]
        return None

    def get_total_cases(self) -> int:
        """Tổng số vụ án hiện có."""
        return len(self.cases)

    def resolve_image_path(self, image_rel_path: str) -> Optional[str]:
        """
        Tìm kiếm đường dẫn ảnh thực tế trên ổ đĩa.
        Tự động tìm kiếm trong BASE_DIR, assets/images và assests/images.
        """
        if not image_rel_path:
            return None

        # 1. Thử đường dẫn tuyệt đối hoặc tương đối trực tiếp
        direct_path = os.path.join(BASE_DIR, image_rel_path)
        if os.path.exists(direct_path):
            return direct_path

        # 2. Thử tìm theo tên file trong IMAGES_DIR
        filename = os.path.basename(image_rel_path)
        img_in_dir = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(img_in_dir):
            return img_in_dir

        # 3. Thử tìm trong thư mục assests/images nếu có
        alt_path = os.path.join(BASE_DIR, "assests", "images", filename)
        if os.path.exists(alt_path):
            return alt_path

        return None
