import customtkinter as ctk
from src.ui.main_window import MainWindow

def main():
    # Thiết lập giao diện tối (Dark mode) chuẩn phong cách điều tra
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    # Khởi động ứng dụng Chuyên Án
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
