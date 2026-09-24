import os
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
from typing import Optional
from src.config import COLOR_CARD_BG, COLOR_TEXT_MUTED, COLOR_ACCENT

class ImageView(ctk.CTkFrame):
    """Khung hiển thị hình ảnh hiện trường / vật chứng của vụ án với cơ chế tự tạo placeholder an toàn."""

    def __init__(self, master, width: int = 480, height: int = 150, **kwargs):
        super().__init__(
            master, 
            width=width, 
            height=height, 
            fg_color=COLOR_CARD_BG, 
            corner_radius=12,
            border_width=2,
            border_color="#2c2c30",
            **kwargs
        )
        self.img_width = width
        self.img_height = height

        self.pack_propagate(False)

        self.label = ctk.CTkLabel(self, text="", fg_color="transparent")
        self.label.pack(expand=True, fill="both", padx=4, pady=4)

    def set_image(self, image_path: Optional[str], case_name: str = ""):
        """Hiển thị ảnh từ đường dẫn. Nếu chưa có ảnh, tự động vẽ placeholder trinh thám."""
        pil_img = None

        if image_path and os.path.exists(image_path):
            try:
                pil_img = Image.open(image_path)
            except Exception as e:
                print(f"[ImageView] Lỗi nạp ảnh {image_path}: {e}")
                pil_img = None

        # Nếu không có ảnh thật -> Tạo ảnh placeholder trinh thám bằng Pillow
        if pil_img is None:
            pil_img = self._create_placeholder(case_name)

        # Scale ảnh vừa vặn với khung
        pil_img.thumbnail((self.img_width, self.img_height), Image.Resampling.LANCZOS)
        
        # Tạo CTkImage
        ctk_img = ctk.CTkImage(
            light_image=pil_img, 
            dark_image=pil_img, 
            size=(self.img_width - 8, self.img_height - 8)
        )
        
        self.label.configure(image=ctk_img, text="")
        self.label.image = ctk_img

    def _create_placeholder(self, case_name: str) -> Image.Image:
        """Tạo ảnh đồ họa giả lập phong cách 'HỒ SƠ BẢO MẬT'."""
        w, h = self.img_width, self.img_height
        img = Image.new("RGB", (w, h), color=(26, 26, 29))
        draw = ImageDraw.Draw(img)

        # Vẽ khung viền vàng đồng phong cách mật thám
        draw.rectangle([6, 6, w - 7, h - 7], outline=(180, 130, 40), width=2)
        draw.rectangle([10, 10, w - 11, h - 11], outline=(50, 50, 55), width=1)

        # Viết chữ thông báo
        title_text = "🔒 VẬT CHỨNG ĐANG BẢO MẬT"
        sub_text = case_name if case_name else "Hồ sơ vụ án chưa nạp ảnh"
        hint_text = "(Thêm ảnh vào assets/images/ để mở khóa hình ảnh)"

        # Canh giữa chữ
        bbox_title = draw.textbbox((0, 0), title_text)
        t_w = bbox_title[2] - bbox_title[0]
        draw.text(((w - t_w) // 2, h // 2 - 32), title_text, fill=(230, 170, 50))

        bbox_sub = draw.textbbox((0, 0), sub_text)
        s_w = bbox_sub[2] - bbox_sub[0]
        draw.text(((w - s_w) // 2, h // 2 - 4), sub_text, fill=(240, 240, 240))

        bbox_hint = draw.textbbox((0, 0), hint_text)
        h_w = bbox_hint[2] - bbox_hint[0]
        draw.text(((w - h_w) // 2, h // 2 + 24), hint_text, fill=(120, 120, 125))

        return img
