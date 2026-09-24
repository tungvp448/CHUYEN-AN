import os
from src.config import SOUNDS_DIR

class SoundManager:
    """Quản lý toàn bộ hiệu ứng âm thanh và nhạc nền xuyên suốt."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        self.is_music_on = True
        self.is_sound_on = True
        self.mixer_ready = False
        self.sfx_cache = {}

        # Thử khởi tạo pygame mixer
        try:
            import pygame
            pygame.mixer.init()
            self.mixer_ready = True
        except Exception as e:
            print(f"[SoundManager] Không thể khởi tạo âm thanh: {e}")
            self.mixer_ready = False

    def play_bgm(self):
        """Phát nhạc nền lặp vô tận (loop=-1)."""
        if not self.mixer_ready or not self.is_music_on:
            return
        
        # Tìm file bgm.mp3 hoặc bgm.wav
        bgm_candidates = ["bgm.mp3", "bgm.wav", "theme.mp3", "theme.wav"]
        bgm_path = None
        for candidate in bgm_candidates:
            p = os.path.join(SOUNDS_DIR, candidate)
            if os.path.exists(p):
                bgm_path = p
                break
        
        if not bgm_path:
            return # Chưa có file nhạc nền thì chạy im lặng, không lỗi

        try:
            import pygame
            pygame.mixer.music.load(bgm_path)
            pygame.mixer.music.set_volume(0.4) # Âm lượng vừa phải
            pygame.mixer.music.play(-1) # Lặp vô tận
        except Exception as e:
            print(f"[SoundManager] Lỗi phát BGM: {e}")

    def stop_bgm(self):
        """Dừng nhạc nền."""
        if self.mixer_ready:
            try:
                import pygame
                pygame.mixer.music.stop()
            except Exception:
                pass

    def toggle_music(self) -> bool:
        """Bật/Tắt nhạc nền, trả về trạng thái mới (True/False)."""
        self.is_music_on = not self.is_music_on
        if self.is_music_on:
            self.play_bgm()
        else:
            self.stop_bgm()
        return self.is_music_on

    def toggle_sound(self) -> bool:
        """Bật/Tắt hiệu ứng âm thanh (SFX)."""
        self.is_sound_on = not self.is_sound_on
        return self.is_sound_on

    def play_sfx(self, sfx_name: str):
        """
        Phát hiệu ứng âm thanh theo tên:
        'type', 'submit', 'clue', 'win', 'lose', 'error'
        """
        if not self.mixer_ready or not self.is_sound_on:
            return

        import pygame

        if sfx_name not in self.sfx_cache:
            # Tìm file âm thanh .wav hoặc .mp3
            file_found = None
            for ext in [".wav", ".mp3", ".ogg"]:
                candidate = os.path.join(SOUNDS_DIR, f"{sfx_name}{ext}")
                if os.path.exists(candidate):
                    file_found = candidate
                    break

            if file_found:
                try:
                    sound = pygame.mixer.Sound(file_found)
                    sound.set_volume(0.7)
                    self.sfx_cache[sfx_name] = sound
                except Exception as e:
                    print(f"[SoundManager] Lỗi tải SFX {sfx_name}: {e}")
                    self.sfx_cache[sfx_name] = None
            else:
                self.sfx_cache[sfx_name] = None

        sound = self.sfx_cache.get(sfx_name)
        if sound:
            try:
                sound.play()
            except Exception as e:
                print(f"[SoundManager] Lỗi phát SFX {sfx_name}: {e}")

    def stop_all_sfx(self):
        """Dừng ngay lập tức các hiệu ứng âm thanh SFX đang phát (win, lose...)."""
        if self.mixer_ready:
            try:
                import pygame
                pygame.mixer.stop()
            except Exception:
                pass
