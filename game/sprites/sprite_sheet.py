"""
Класс для работы со спрайт-листами
"""
import pygame


class SpriteSheet:
    """Класс для работы со спрайт-листами"""
    def __init__(self, image_path, frame_width=None, frame_height=None):
        try:
            # Пробуем разные пути
            paths_to_try = [
                image_path,
                image_path.replace('/', '\\'),
                image_path.replace('\\', '/'),
            ]
            
            self.image = None
            for path in paths_to_try:
                try:
                    loaded_image = pygame.image.load(path)
                    # Убеждаемся что изображение конвертировано правильно
                    if loaded_image.get_flags() & pygame.SRCALPHA:
                        self.image = loaded_image
                    else:
                        self.image = loaded_image.convert_alpha()
                    break
                except Exception as e:
                    print(f"Не удалось загрузить {path}: {e}")
                    continue
            
            if self.image is None:
                self.frames = []
                return
                
            img_width = self.image.get_width()
            img_height = self.image.get_height()
            
            # Если размеры не указаны, пытаемся определить автоматически
            if frame_width is None or frame_height is None:
                # Для полицейских спрайтов: обычно идут в одну строку
                # Пробуем разные варианты количества кадров
                test_frame_counts = [6, 4, 8, 3, 2, 1]
                
                for frame_count in test_frame_counts:
                    tw = img_width // frame_count
                    th = img_height
                    if tw > 0 and th > 0 and img_width % frame_count == 0:
                        frame_width = tw
                        frame_height = th
                        print(f"Определен размер кадра: {frame_width}x{frame_height} ({frame_count} кадров)")
                        break
                
                # Если не нашли, используем размер всего изображения
                if frame_width is None:
                    frame_width = img_width
                    frame_height = img_height
            
            self.frame_width = frame_width
            self.frame_height = frame_height
            self.frames = []
            self.load_frames()
        except Exception as e:
            print(f"Ошибка загрузки спрайта {image_path}: {e}")
            self.image = None
            self.frames = []
    
    def load_frames(self):
        if self.image is None:
            return
        
        img_width = self.image.get_width()
        img_height = self.image.get_height()
        
        # Проверяем что размеры кадра разумные
        if self.frame_width <= 0 or self.frame_height <= 0:
            print(f"Ошибка: неверный размер кадра {self.frame_width}x{self.frame_height}")
            return
        
        # Автоматически определяем количество кадров
        cols = max(1, img_width // self.frame_width)
        rows = max(1, img_height // self.frame_height)
        
        # Ограничиваем количество кадров (обычно спрайты идут в одну строку)
        if cols > 20:  # Если слишком много колонок, значит размер кадра неправильный
            # Пробуем определить размер автоматически
            # Обычно спрайты идут по горизонтали, пробуем разные размеры
            for test_w in [img_width // 6, img_width // 4, img_width // 3, img_width // 2]:
                if test_w > 0 and img_width % test_w == 0:
                    self.frame_width = test_w
                    self.frame_height = img_height
                    cols = img_width // self.frame_width
                    rows = 1
                    print(f"Автоопределение: размер кадра {self.frame_width}x{self.frame_height}, кадров: {cols}")
                    break
        
        for row in range(rows):
            for col in range(cols):
                x = col * self.frame_width
                y = row * self.frame_height
                if x + self.frame_width <= img_width and y + self.frame_height <= img_height:
                    try:
                        frame = self.image.subsurface((x, y, self.frame_width, self.frame_height))
                        # Убеждаемся что кадр имеет правильный формат
                        if not (frame.get_flags() & pygame.SRCALPHA):
                            frame = frame.convert_alpha()
                        self.frames.append(frame)
                    except Exception as e:
                        print(f"Ошибка извлечения кадра {col},{row}: {e}")
                        pass
    
    def get_frame(self, index):
        if self.frames and 0 <= index < len(self.frames):
            return self.frames[index]
        elif self.frames:
            return self.frames[0]  # Возвращаем первый кадр если индекс вне диапазона
        return None

