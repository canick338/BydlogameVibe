"""
Менеджер спрайтов врагов
"""
from game.sprites.sprite_sheet import SpriteSheet


class EnemySpriteManager:
    """Менеджер спрайтов врагов"""
    _instance = None
    _sprites_loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._sprites_loaded:
            self.sprites = {}
            self.load_sprites()
            self._sprites_loaded = True
            print(f"Загружено спрайтов: {len(self.sprites)}")
            for key in self.sprites:
                print(f"  {key}: {len(self.sprites[key])} кадров")
    
    def load_sprites(self):
        # Загружаем спрайты ментов
        ment_paths = [
            ("Idle", "assets/police-character-sprites-pixel-art/Policeman_Patrolman/Idle.png"),
            ("Walk", "assets/police-character-sprites-pixel-art/Policeman_Patrolman/Walk.png"),
            ("Run", "assets/police-character-sprites-pixel-art/Policeman_Patrolman/Run.png"),
            ("Shot", "assets/police-character-sprites-pixel-art/Policeman_Patrolman/Shot_1.png"),
            ("Hurt", "assets/police-character-sprites-pixel-art/Policeman_Patrolman/Hurt.png"),
            ("Dead", "assets/police-character-sprites-pixel-art/Policeman_Patrolman/Dead.png")
        ]
        
        # Загружаем спрайты боссов
        boss_paths = [
            ("Idle", "assets/police-character-sprites-pixel-art/Capitan/Idle.png"),
            ("Walk", "assets/police-character-sprites-pixel-art/Capitan/Walk.png"),
            ("Run", "assets/police-character-sprites-pixel-art/Capitan/Run.png"),
            ("Shot", "assets/police-character-sprites-pixel-art/Capitan/Shot.png"),
            ("Hurt", "assets/police-character-sprites-pixel-art/Capitan/Hurt.png"),
            ("Dead", "assets/police-character-sprites-pixel-art/Capitan/Dead.png")
        ]
        
        # Загружаем спрайты для других типов (используем полицейских)
        other_paths = [
            ("Idle", "assets/police-character-sprites-pixel-art/Policewoman/Idle.png"),
            ("Walk", "assets/police-character-sprites-pixel-art/Policewoman/Walk.png"),
            ("Run", "assets/police-character-sprites-pixel-art/Policewoman/Run.png"),
            ("Shot", "assets/police-character-sprites-pixel-art/Policewoman/Shot.png"),
            ("Hurt", "assets/police-character-sprites-pixel-art/Policewoman/Hurt.png"),
            ("Dead", "assets/police-character-sprites-pixel-art/Policewoman/Dead.png")
        ]
        
        # Загружаем спрайты с правильными размерами
        for state, path in ment_paths:
            try:
                # Пробуем загрузить без указания размера - пусть определит автоматически
                sheet = SpriteSheet(path)
                if sheet.frames and len(sheet.frames) > 0 and len(sheet.frames) < 20:
                    self.sprites[f"мент_{state}"] = sheet.frames
                    print(f"✓ Загружено {len(sheet.frames)} кадров для мент_{state}")
                else:
                    # Пробуем с конкретным размером
                    sheet = SpriteSheet(path, frame_width=38, frame_height=64)
                    if sheet.frames and len(sheet.frames) > 0 and len(sheet.frames) < 20:
                        self.sprites[f"мент_{state}"] = sheet.frames
                        print(f"✓ Загружено {len(sheet.frames)} кадров для мент_{state} (38x64)")
                    else:
                        print(f"✗ Не удалось загрузить кадры из {path} (кадров: {len(sheet.frames) if sheet.frames else 0})")
            except Exception as e:
                print(f"✗ Ошибка загрузки {path}: {e}")
        
        for state, path in boss_paths:
            try:
                sheet = SpriteSheet(path)
                if sheet.frames and len(sheet.frames) > 0 and len(sheet.frames) < 20:
                    self.sprites[f"босс_{state}"] = sheet.frames
                    print(f"✓ Загружено {len(sheet.frames)} кадров для босс_{state}")
                else:
                    sheet = SpriteSheet(path, frame_width=38, frame_height=64)
                    if sheet.frames and len(sheet.frames) > 0 and len(sheet.frames) < 20:
                        self.sprites[f"босс_{state}"] = sheet.frames
                        print(f"✓ Загружено {len(sheet.frames)} кадров для босс_{state} (38x64)")
                    else:
                        print(f"✗ Не удалось загрузить кадры из {path}")
            except Exception as e:
                print(f"✗ Ошибка загрузки {path}: {e}")
        
        for state, path in other_paths:
            try:
                sheet = SpriteSheet(path)
                if sheet.frames and len(sheet.frames) > 0 and len(sheet.frames) < 20:
                    self.sprites[f"другой_{state}"] = sheet.frames
                    print(f"✓ Загружено {len(sheet.frames)} кадров для другой_{state}")
                else:
                    sheet = SpriteSheet(path, frame_width=38, frame_height=64)
                    if sheet.frames and len(sheet.frames) > 0 and len(sheet.frames) < 20:
                        self.sprites[f"другой_{state}"] = sheet.frames
                        print(f"✓ Загружено {len(sheet.frames)} кадров для другой_{state} (38x64)")
                    else:
                        print(f"✗ Не удалось загрузить кадры из {path}")
            except Exception as e:
                print(f"✗ Ошибка загрузки {path}: {e}")
    
    def get_sprite(self, enemy_type, state="Idle", frame=0):
        key = f"{enemy_type}_{state}"
        if key in self.sprites and self.sprites[key]:
            frames = self.sprites[key]
            if frames and len(frames) > 0:
                frame_index = frame % len(frames)
                sprite = frames[frame_index]
                # Проверяем что спрайт не пустой
                if sprite:
                    try:
                        w, h = sprite.get_size()
                        if w > 0 and h > 0:
                            return sprite
                    except:
                        pass
        # Пробуем альтернативные ключи
        alt_key = f"{enemy_type}_Idle"
        if alt_key in self.sprites and self.sprites[alt_key]:
            frames = self.sprites[alt_key]
            if frames and len(frames) > 0:
                sprite = frames[0]
                if sprite:
                    try:
                        w, h = sprite.get_size()
                        if w > 0 and h > 0:
                            return sprite
                    except:
                        pass
        return None

