import pygame
import sys
import random
import math
from enum import Enum
import os

"""
БРАТВА: УЛИЦЫ СТОЛИЦЫ - ЭПИЧЕСКИЙ РЕМАСТЕР!
Шедевральная игра про настоящих пацанов и их борьбу за район.

Особенности:
- 5 уникальных локаций с разными атмосферами
- 8 видов оружия с уникальными характеристиками
- Система магазина для покупки патронов и улучшений
- Система навыков и уровней
- 5 эпических миссий с сюжетом
- Система достижений
- Мини-карта для навигации
- Комбо система для бонусов
- Разнообразные враги: менты, быдло, крысы, боссы, снайперы, танки
- Взрывные пули и визуальные эффекты
- Регенерация здоровья и броня
"""

# Инициализация для настоящих пацанов
pygame.init()
pygame.font.init()
pygame.mixer.init()  # Инициализация звуковой системы

# Константы
SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768
FPS = 60

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 120, 255)
GOLD = (255, 215, 0)
DARK_GREY = (40, 40, 40)
LIGHT_GREY = (100, 100, 100)
ASPHALT = (30, 30, 40)
BUILDING_COLORS = [(80, 80, 100), (60, 60, 80), (100, 100, 120)]

# Шрифты
title_font = pygame.font.SysFont('arial', 72, bold=True)
menu_font = pygame.font.SysFont('arial', 36)
dialog_font = pygame.font.SysFont('arial', 24)
small_font = pygame.font.SysFont('arial', 18)


class GameState(Enum):
    MAIN_MENU = 0
    PLAYING = 1
    CUTSCENE = 2
    GAME_OVER = 3
    WIN = 4
    PAUSE = 5
    MISSION_START = 6
    CONTROLS = 7
    SHOP = 8
    LOCATION_SELECT = 9
    SKILLS = 10


class Weapon:
    def __init__(self, name, damage, fire_rate, ammo, color, spread=0.1):
        self.name = name
        self.damage = damage
        self.fire_rate = fire_rate
        self.max_ammo = ammo
        self.ammo = ammo
        self.color = color
        self.spread = spread
        self.last_shot = 0

    def can_shoot(self):
        current_time = pygame.time.get_ticks()
        return current_time - self.last_shot > 1000 / self.fire_rate and self.ammo > 0

    def shoot(self, direction, x, y):
        if self.can_shoot():
            self.ammo -= 1
            self.last_shot = pygame.time.get_ticks()

            # Добавляем разброс в зависимости от оружия
            spread_angle = random.uniform(-self.spread, self.spread)
            actual_direction = direction + spread_angle

            bullet_type = "normal"
            if self.name == "ГРАНАТОМЁТ":
                bullet_type = "explosive"
            
            return Bullet(
                x + math.cos(direction) * 30,
                y + math.sin(direction) * 30,
                actual_direction,
                15 if bullet_type == "normal" else 12,
                self.damage,
                bullet_type
            )
        return None


class Achievement:
    def __init__(self, name, description, condition_func):
        self.name = name
        self.description = description
        self.condition_func = condition_func
        self.unlocked = False
        self.show_time = 0

    def check(self, player, game):
        if not self.unlocked and self.condition_func(player, game):
            self.unlocked = True
            self.show_time = 180
            return True
        return False


class Particle:
    def __init__(self, x, y, color, velocity_x, velocity_y, lifetime=30):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.lifetime = lifetime
        self.max_lifetime = lifetime

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_x *= 0.95
        self.velocity_y *= 0.95
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, screen):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        size = max(1, int(3 * (self.lifetime / self.max_lifetime)))
        if size > 0:
            # Свечение частицы
            if size > 2:
                glow_surface = pygame.Surface((size * 2 + 4, size * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*self.color[:3], alpha // 2), (size + 2, size + 2), size + 2)
                screen.blit(glow_surface, (int(self.x) - size - 2, int(self.y) - size - 2))
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)
            pygame.draw.circle(screen, tuple(min(255, c + 50) for c in self.color), (int(self.x), int(self.y)), size - 1)


class BloodParticle(Particle):
    def __init__(self, x, y, velocity_x, velocity_y):
        super().__init__(x, y, (150, 0, 0), velocity_x, velocity_y, 60)
    
    def draw(self, screen):
        size = max(1, int(4 * (self.lifetime / self.max_lifetime)))
        if size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)


class DamageNumber:
    def __init__(self, x, y, damage, is_critical=False):
        self.x = x
        self.y = y
        self.damage = damage
        self.is_critical = is_critical
        self.lifetime = 60
        self.velocity_y = -2
        self.alpha = 255

    def update(self):
        self.y += self.velocity_y
        self.velocity_y *= 0.95
        self.lifetime -= 1
        self.alpha = int(255 * (self.lifetime / 60))
        return self.lifetime > 0

    def draw(self, screen):
        if self.lifetime > 0:
            color = (255, 255, 0) if self.is_critical else (255, 100, 100)
            size = 24 if self.is_critical else 18
            
            # Свечение текста
            if self.is_critical:
                glow_text = small_font.render(f"-{self.damage}", True, (255, 200, 0))
                for offset in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
                    screen.blit(glow_text, (int(self.x) + offset[0], int(self.y) + offset[1]))
            
            text = small_font.render(f"-{self.damage}", True, color)
            screen.blit(text, (int(self.x), int(self.y)))
            
            # Эффект для крита
            if self.is_critical:
                crit_glow = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(crit_glow, (255, 255, 0, self.alpha // 2), (size, size), size)
                screen.blit(crit_glow, (int(self.x) - size, int(self.y) - size))


class KillFeedEntry:
    def __init__(self, enemy_type):
        self.enemy_type = enemy_type
        self.lifetime = 180
        self.alpha = 255

    def update(self):
        self.lifetime -= 1
        if self.lifetime < 60:
            self.alpha = int(255 * (self.lifetime / 60))
        return self.lifetime > 0

    def draw(self, screen, y_pos):
        if self.lifetime > 0:
            text = small_font.render(f"Убит: {self.enemy_type.upper()}", True, (200, 200, 200))
            screen.blit(text, (10, y_pos))


class Bullet:
    def __init__(self, x, y, direction, speed, damage, bullet_type="normal"):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = speed
        self.damage = damage
        self.lifetime = 90
        self.type = bullet_type
        self.explosion_radius = 0
        if bullet_type == "explosive":
            self.lifetime = 120
            self.explosion_radius = 50

    def update(self, world_size=5000):
        self.x += math.cos(self.direction) * self.speed
        self.y += math.sin(self.direction) * self.speed
        self.lifetime -= 1
        return self.lifetime > 0 and 0 < self.x < world_size and 0 < self.y < world_size

    def draw(self, screen):
        if self.type == "explosive":
            # Взрывной снаряд с улучшенным эффектом
            start_pos = (int(self.x), int(self.y))
            end_pos = (int(self.x - math.cos(self.direction) * 8),
                       int(self.y - math.sin(self.direction) * 8))
            
            # Огненный след
            for i in range(5):
                trail_x = self.x - math.cos(self.direction) * (8 + i * 4)
                trail_y = self.y - math.sin(self.direction) * (8 + i * 4)
                size = 5 - i
                if size > 0:
                    trail_color = (255, 200 - i * 40, 0)
                    pygame.draw.circle(screen, trail_color, (int(trail_x), int(trail_y)), size)
            
            pygame.draw.line(screen, (255, 100, 0), start_pos, end_pos, 5)
            pygame.draw.circle(screen, (255, 200, 0), start_pos, 5)
            pygame.draw.circle(screen, (255, 255, 150), start_pos, 3)
            pygame.draw.circle(screen, (255, 255, 255), start_pos, 1)
        else:
            # Эффект трассера с улучшениями
            start_pos = (int(self.x), int(self.y))
            end_pos = (int(self.x - math.cos(self.direction) * 10),
                       int(self.y - math.sin(self.direction) * 10))
            
            # Свечение пули
            bullet_glow = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(bullet_glow, (*GOLD[:3], 100), (5, 5), 5)
            screen.blit(bullet_glow, (int(self.x) - 5, int(self.y) - 5))
            
            # Трассер
            pygame.draw.line(screen, (255, 255, 150), start_pos, end_pos, 4)
            pygame.draw.line(screen, GOLD, start_pos, end_pos, 2)
            pygame.draw.circle(screen, (255, 255, 255), start_pos, 3)
            pygame.draw.circle(screen, (255, 255, 200), start_pos, 2)
            pygame.draw.circle(screen, GOLD, start_pos, 1)


class Player:
    def __init__(self):
        # Начальная позиция будет установлена в start_game
        self.x = 2500  # Центр мира по умолчанию
        self.y = 2500
        self.width = 40
        self.height = 60
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.money = 1000
        self.reputation = 5
        self.direction = 0

        # Оружие
        self.weapons = [
            Weapon("ПИСТОЛЕТ", 25, 3, 30, (180, 180, 180), 0.05),
            Weapon("АВТОМАТ", 15, 10, 60, (100, 150, 200), 0.15),
            Weapon("ДРОБОВИК", 40, 1.5, 12, (200, 100, 50), 0.3),
            Weapon("СНАЙПЕРКА", 60, 1, 10, (150, 200, 150), 0.02),
            Weapon("ПУЛЕМЁТ", 20, 15, 100, (200, 150, 100), 0.2),
            Weapon("ГРАНАТОМЁТ", 80, 0.5, 5, (255, 100, 0), 0.1),
            Weapon("РЕВОЛЬВЕР", 35, 2, 18, (200, 200, 200), 0.03),
            Weapon("АВТОМАТ-2", 18, 12, 80, (120, 180, 220), 0.12)
        ]

        self.current_weapon = 0
        self.kills = 0
        self.completed_missions = 0
        self.total_missions = 5
        self.mission_kills = 0
        self.auto_fire = False
        self.total_damage_dealt = 0
        self.headshots = 0
        self.bosses_killed = 0
        self.time_played = 0
        self.armor = 0
        self.damage_multiplier = 1.0
        self.speed_multiplier = 1.0
        self.regen_timer = 0
        self.last_damage_time = 0
        self.combo = 0
        self.combo_timer = 0
        self.level = 1
        self.experience = 0
        self.experience_to_next = 100
        self.skill_points = 0
        self.skills = {
            "damage": 0,
            "health": 0,
            "speed": 0,
            "ammo": 0,
            "regen": 0
        }

    def move(self, dx, dy, world_size=5000):
        # Движение в открытом мире
        self.x += dx * self.speed
        self.y += dy * self.speed

        # Границы открытого мира
        self.x = max(self.width // 2, min(world_size - self.width // 2, self.x))
        self.y = max(self.height // 2, min(world_size - self.height // 2, self.y))

    def update_direction(self, target_x, target_y):
        self.direction = math.atan2(target_y - self.y, target_x - self.x)

    def shoot(self):
        return self.weapons[self.current_weapon].shoot(self.direction, self.x, self.y)

    def switch_weapon(self, direction):
        self.current_weapon = (self.current_weapon + direction) % len(self.weapons)

    def draw(self, screen):
        # Тень персонажа
        shadow_surface = pygame.Surface((self.width + 10, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 100), (0, 0, self.width + 10, 20))
        screen.blit(shadow_surface, (self.x - (self.width + 10) // 2, self.y + self.height // 2))
        
        # Тело пацана с градиентом
        body_color = (180, 80, 80) if self.health > 50 else (200, 50, 50)
        body_rect = pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)
        
        # Градиент тела
        for i in range(self.height):
            grad_factor = i / self.height
            grad_color = tuple(int(c * (0.85 + grad_factor * 0.15)) for c in body_color)
            pygame.draw.line(screen, grad_color, 
                           (self.x - self.width // 2, self.y - self.height // 2 + i),
                           (self.x + self.width // 2, self.y - self.height // 2 + i))
        
        # Обводка
        pygame.draw.rect(screen, tuple(min(255, c + 40) for c in body_color), body_rect, 2)

        # Голова с эффектом
        head_radius = 16
        head_x = self.x + math.cos(self.direction) * 25
        head_y = self.y + math.sin(self.direction) * 25
        
        # Свечение головы
        head_glow = pygame.Surface((head_radius * 2 + 6, head_radius * 2 + 6), pygame.SRCALPHA)
        pygame.draw.circle(head_glow, (240, 200, 160, 50), (head_radius + 3, head_radius + 3), head_radius + 3)
        screen.blit(head_glow, (int(head_x) - head_radius - 3, int(head_y) - head_radius - 3))
        
        pygame.draw.circle(screen, (240, 200, 160), (int(head_x), int(head_y)), head_radius)
        pygame.draw.circle(screen, (255, 230, 200), (int(head_x), int(head_y)), head_radius, 2)

        # Глаза с эффектом
        eye_offset = 6
        eye1_x = head_x + math.cos(self.direction) * 8 + math.cos(self.direction - math.pi / 2) * eye_offset
        eye1_y = head_y + math.sin(self.direction) * 8 + math.sin(self.direction - math.pi / 2) * eye_offset
        eye2_x = head_x + math.cos(self.direction) * 8 + math.cos(self.direction + math.pi / 2) * eye_offset
        eye2_y = head_y + math.sin(self.direction) * 8 + math.sin(self.direction + math.pi / 2) * eye_offset

        pygame.draw.circle(screen, (30, 30, 100), (int(eye1_x), int(eye1_y)), 5)
        pygame.draw.circle(screen, (30, 30, 100), (int(eye2_x), int(eye2_y)), 5)
        pygame.draw.circle(screen, (100, 150, 255), (int(eye1_x), int(eye1_y)), 3)
        pygame.draw.circle(screen, (100, 150, 255), (int(eye2_x), int(eye2_y)), 3)
        pygame.draw.circle(screen, (0, 0, 0), (int(eye1_x), int(eye1_y)), 2)
        pygame.draw.circle(screen, (0, 0, 0), (int(eye2_x), int(eye2_y)), 2)

        # Оружие с эффектом
        weapon = self.weapons[self.current_weapon]
        weapon_x = self.x + math.cos(self.direction) * 35
        weapon_y = self.y + math.sin(self.direction) * 35
        
        # Металлический эффект оружия
        weapon_rect = pygame.Rect(weapon_x - 8, weapon_y - 4, 25, 8)
        pygame.draw.rect(screen, tuple(int(c * 0.7) for c in weapon.color), weapon_rect)
        pygame.draw.rect(screen, weapon.color, (weapon_x - 7, weapon_y - 3, 23, 6))
        pygame.draw.rect(screen, tuple(min(255, c + 50) for c in weapon.color), (weapon_x - 6, weapon_y - 2, 21, 2))
        pygame.draw.rect(screen, (50, 50, 50), weapon_rect, 1)


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
                if sheet.frames and len(sheet.frames) > 0 and len(sheet.frames) < 20:  # Разумное количество кадров
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


class Enemy:
    def __init__(self, x, y, enemy_type, level=1):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.level = level
        self.max_health = 80 + level * 20
        self.health = self.max_health
        self.direction = random.uniform(0, 2 * math.pi)
        self.attack_cooldown = 0
        self.speed_modifier = 0.8 + level * 0.1
        self.stun_timer = 0
        self.flash_timer = 0
        self.last_damage_time = 0
        self.pathfinding_timer = 0
        self.aggro_range = 400
        
        # Анимация
        self.sprite_manager = EnemySpriteManager()
        self.animation_state = "Idle"
        self.animation_frame = 0
        self.animation_timer = 0
        self.is_moving = False
        self.is_dead = False
        self.is_hurt = False
        self.shot_animation_timer = 0  # Таймер для анимации выстрела
        
        # Размер спрайта
        self.sprite_size = 64
        self.last_x = x
        self.last_y = y
        self.animation_state_prev = "Idle"
        self.sprite_available = False  # Флаг доступности спрайтов
        self.check_sprite_availability()

        if enemy_type == "мент":
            self.color = (70, 70, 200)
            self.size = 38
            self.speed = 2.2 * self.speed_modifier
            self.damage = 3
            self.attack_range = 85
            self.bounty = 200
        elif enemy_type == "быдло":
            self.color = (160, 100, 60)
            self.size = 42
            self.speed = 1.8 * self.speed_modifier
            self.damage = 2
            self.attack_range = 70
            self.bounty = 100
        elif enemy_type == "босс":
            self.color = (200, 0, 0)
            self.size = 55
            self.speed = 1.5 * self.speed_modifier
            self.damage = 5
            self.attack_range = 100
            self.bounty = 500
            self.aggro_range = 600
        elif enemy_type == "снайпер":
            self.color = (100, 150, 100)
            self.size = 30
            self.speed = 1.2 * self.speed_modifier
            self.damage = 8
            self.attack_range = 300
            self.bounty = 300
            self.aggro_range = 500
        elif enemy_type == "танк":
            self.color = (80, 80, 80)
            self.size = 50
            self.speed = 0.8 * self.speed_modifier
            self.damage = 4
            self.attack_range = 90
            self.bounty = 400
            self.max_health = 150 + level * 30
            self.health = self.max_health
        else:  # крыса
            self.color = (120, 120, 120)
            self.size = 25
            self.speed = 2.8 * self.speed_modifier
            self.damage = 1
            self.attack_range = 50
            self.bounty = 50
        
        # Проверяем доступность спрайтов один раз при создании
        self.check_sprite_availability()
    
    def check_sprite_availability(self):
        """Проверяет доступность спрайтов для этого врага"""
        sprite_type = self.type if self.type in ["мент", "босс"] else "другой"
        test_sprite = self.sprite_manager.get_sprite(sprite_type, "Idle", 0)
        if test_sprite:
            try:
                w, h = test_sprite.get_size()
                self.sprite_available = w > 0 and h > 0
            except:
                self.sprite_available = False
        else:
            self.sprite_available = False

    def update(self, player_x, player_y):
        if self.is_dead:
            self.animation_state = "Dead"
            return 0
            
        if self.stun_timer > 0:
            self.stun_timer -= 1
            return 0
        
        dx = player_x - self.x
        dy = player_y - self.y
        distance = max(0.1, math.sqrt(dx * dx + dy * dy))
        
        # Обновление таймеров
        if self.flash_timer > 0:
            self.flash_timer -= 1
            self.is_hurt = True
        else:
            self.is_hurt = False
        
        # Определяем движение
        moved = abs(self.x - self.last_x) > 0.1 or abs(self.y - self.last_y) > 0.1
        self.last_x = self.x
        self.last_y = self.y
        
        # Обновление анимации
        self.animation_timer += 1
        self.is_moving = moved
        
        # Обновление таймера анимации выстрела
        if self.shot_animation_timer > 0:
            self.shot_animation_timer -= 1
            if self.shot_animation_timer == 0:
                # Возвращаемся к обычной анимации после выстрела
                if self.is_moving:
                    self.animation_state = "Run" if self.speed > 2 else "Walk"
                else:
                    self.animation_state = "Idle"
        
        # Снайпер стреляет издалека
        if self.type == "снайпер" and distance < self.aggro_range:
            self.direction = math.atan2(dy, dx)
            self.attack_cooldown -= 1
            if self.attack_cooldown <= 0 and distance > 150:
                self.attack_cooldown = 60
                self.animation_state = "Shot"
                self.shot_animation_timer = 15  # Показываем анимацию выстрела 15 кадров
                return self.damage
            if self.shot_animation_timer == 0:
                self.animation_state = "Idle"
            return 0

        if distance < self.attack_range:
            # Атака вблизи
            self.direction = math.atan2(dy, dx)
            self.attack_cooldown -= 1
            if self.attack_cooldown <= 0:
                self.attack_cooldown = 25 if self.type != "танк" else 35
                self.animation_state = "Shot"
                self.shot_animation_timer = 15  # Показываем анимацию выстрела 15 кадров
                return self.damage
            if self.shot_animation_timer == 0:
                self.animation_state = "Idle"
        elif distance < self.aggro_range:
            # Преследование с улучшенным ИИ
            self.pathfinding_timer += 1
            if self.pathfinding_timer > 30:
                self.direction = math.atan2(dy, dx) + random.uniform(-0.15, 0.15)
                self.pathfinding_timer = 0
            else:
                self.direction = math.atan2(dy, dx) + random.uniform(-0.1, 0.1)
            
            if self.stun_timer == 0:
                self.x += math.cos(self.direction) * self.speed
                self.y += math.sin(self.direction) * self.speed
                self.is_moving = True
                self.animation_state = "Run" if self.speed > 2 else "Walk"
        else:
            self.animation_state = "Idle"
        
        # Обновление кадра анимации
        # Сбрасываем кадр при смене состояния
        if self.animation_state != self.animation_state_prev:
            self.animation_frame = 0
            self.animation_state_prev = self.animation_state
        
        # Скорость анимации зависит от состояния
        if self.animation_state == "Shot":
            anim_speed = 4  # Быстрая анимация выстрела
        elif self.animation_state == "Hurt":
            anim_speed = 3  # Быстрая анимация получения урона
        elif self.animation_state == "Dead":
            anim_speed = 8  # Медленная анимация смерти
        elif self.is_moving:
            anim_speed = 6  # Анимация движения
        else:
            anim_speed = 12  # Анимация покоя
        
        if self.animation_timer >= anim_speed:
            self.animation_timer = 0
            # Определяем количество кадров в зависимости от состояния
            sprite_type = self.type if self.type in ["мент", "босс"] else "другой"
            key = f"{sprite_type}_{self.animation_state}"
            frames = self.sprite_manager.sprites.get(key, [])
            max_frames = len(frames) if frames else 1
            if max_frames > 0:
                # Для анимации выстрела и смерти не зацикливаем
                if self.animation_state in ["Shot", "Dead"]:
                    if self.animation_frame < max_frames - 1:
                        self.animation_frame += 1
                    # Для выстрела возвращаемся к первому кадру если таймер истек
                    if self.animation_state == "Shot" and self.shot_animation_timer == 0:
                        self.animation_frame = 0
                else:
                    self.animation_frame = (self.animation_frame + 1) % max_frames

        return 0

    def take_damage(self, damage):
        self.health -= damage
        self.flash_timer = 10
        self.is_hurt = True
        self.animation_state = "Hurt"
        self.last_damage_time = pygame.time.get_ticks()
        # Критический урон может оглушить
        if damage > 50 and random.random() < 0.3:
            self.stun_timer = 30
        if self.health <= 0:
            self.is_dead = True
            self.animation_state = "Dead"
        return self.health <= 0

    def draw(self, screen):
        # Тень врага
        shadow_surface = pygame.Surface((self.sprite_size + 10, 15), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 120), (0, 0, self.sprite_size + 10, 15))
        screen.blit(shadow_surface, (int(self.x) - self.sprite_size // 2 - 5, int(self.y) + self.sprite_size // 2))
        
        # Используем спрайты только если они доступны
        if self.sprite_available:
            # Получаем спрайт
            sprite_type = self.type if self.type in ["мент", "босс"] else "другой"
            sprite = None
            
            # Пробуем получить спрайт для текущего состояния
            sprite = self.sprite_manager.get_sprite(sprite_type, self.animation_state, self.animation_frame)
            
            # Если спрайт не найден, пробуем Idle
            if not sprite:
                sprite = self.sprite_manager.get_sprite(sprite_type, "Idle", 0)
            
            # Проверяем что спрайт действительно загружен и видимый
            sprite_loaded = sprite is not None
            if sprite_loaded:
                try:
                    orig_width, orig_height = sprite.get_size()
                    sprite_loaded = orig_width > 0 and orig_height > 0
                except:
                    sprite_loaded = False
        else:
            sprite_loaded = False
            sprite = None
        
        if sprite_loaded and sprite is not None:
            # Масштабируем спрайт в зависимости от типа врага
            if self.type == "босс":
                scale = 1.8
            elif self.type == "танк":
                scale = 1.5
            elif self.type == "снайпер":
                scale = 1.0
            else:
                scale = 1.6  # Увеличиваем размер для лучшей видимости
            
            # Используем реальный размер спрайта для масштабирования
            orig_width, orig_height = sprite.get_size()
            
            # Проверяем что размеры разумные
            if orig_width > 0 and orig_height > 0:
                scaled_width = max(30, int(orig_width * scale))
                scaled_height = max(40, int(orig_height * scale))
                
                # Масштабируем спрайт с сглаживанием
                scaled_sprite = pygame.transform.scale(sprite, (scaled_width, scaled_height))
                
                # Отражаем спрайт в зависимости от направления
                if math.cos(self.direction) < 0:
                    scaled_sprite = pygame.transform.flip(scaled_sprite, True, False)
                
                # Мигание при получении урона
                if self.flash_timer > 0:
                    # Создаем белый оттенок
                    flash_sprite = scaled_sprite.copy()
                    white_overlay = pygame.Surface(scaled_sprite.get_size(), pygame.SRCALPHA)
                    white_overlay.fill((255, 255, 255, 150))
                    flash_sprite.blit(white_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                    scaled_sprite = flash_sprite
                
                # Эффект свечения при выстреле
                if self.animation_state == "Shot" and self.shot_animation_timer > 0:
                    glow_surface = pygame.Surface((scaled_width + 10, scaled_height + 10), pygame.SRCALPHA)
                    for radius in range(15, 0, -2):
                        alpha = int(100 * (1 - radius / 15))
                        pygame.draw.circle(glow_surface, (255, 200, 0, alpha), 
                                         (scaled_width // 2 + 5, scaled_height // 2 + 5), radius)
                    screen.blit(glow_surface, (int(self.x) - scaled_width // 2 - 5, int(self.y) - scaled_height // 2 - 15))
                
                # Рисуем спрайт с небольшим смещением вверх (чтобы ноги были на земле)
                sprite_rect = scaled_sprite.get_rect(center=(int(self.x), int(self.y) - 15))
                screen.blit(scaled_sprite, sprite_rect)
        else:
            # Fallback - рисуем простую форму если спрайт не загрузился
            draw_color = self.color
            if self.flash_timer > 0:
                draw_color = tuple(min(255, c + 100) for c in self.color)
            
            for radius in range(self.size, 0, -2):
                grad_factor = radius / self.size
                grad_color = tuple(int(c * (0.7 + grad_factor * 0.3)) for c in draw_color)
                pygame.draw.circle(screen, grad_color, (int(self.x), int(self.y)), radius)
            pygame.draw.circle(screen, tuple(min(255, c + 30) for c in draw_color), (int(self.x), int(self.y)), self.size, 2)
        
        # Индикатор оглушения с эффектом
        if self.stun_timer > 0:
            stun_glow = pygame.Surface((self.size * 2 + 20, self.size * 2 + 20), pygame.SRCALPHA)
            for radius in range(self.size + 10, 0, -3):
                alpha = int(150 * (1 - radius / (self.size + 10)))
                pygame.draw.circle(stun_glow, (255, 255, 0, alpha), (self.size + 10, self.size + 10), radius)
            screen.blit(stun_glow, (int(self.x) - self.size - 10, int(self.y) - self.size - 10))
            pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), self.size + 5, 3)

        # Полоска здоровья
        health_width = (self.health / self.max_health) * (self.size * 2)
        pygame.draw.rect(screen, RED, (self.x - self.size, self.y - self.size - 20, self.size * 2, 6))
        pygame.draw.rect(screen, GREEN, (self.x - self.size, self.y - self.size - 20, health_width, 6))
        
        # Индикатор типа для босса
        if self.type == "босс":
            crown_y = self.y - self.size - 25
            pygame.draw.polygon(screen, GOLD, [
                (self.x - self.size // 2, crown_y),
                (self.x - self.size // 4, crown_y - 8),
                (self.x, crown_y),
                (self.x + self.size // 4, crown_y - 8),
                (self.x + self.size // 2, crown_y)
            ])


class Mission:
    def __init__(self, title, description, target, reward, mission_type, cutscene_texts):
        self.title = title
        self.description = description
        self.target = target
        self.current = 0
        self.reward = reward
        self.completed = False
        self.type = mission_type  # "kill", "collect", "survive"
        self.timer = 0
        self.cutscene_texts = cutscene_texts

    def update(self, value=1):
        if not self.completed:
            self.current += value
            if self.current >= self.target:
                self.completed = True
                return True
        return False

    def update_timer(self, dt):
        if self.type == "survive":
            self.timer += dt
            self.current = self.timer
            if self.timer >= self.target:
                self.completed = True
                return True
        return False


class HotlineCutscene:
    def __init__(self):
        self.car_image = None
        self.music = None
        self.load_assets()
        self.phase = 0  # 0 - машина подъезжает, 1 - выход персонажа, 2 - менты подходят, 3 - диалог
        self.car_x = -300
        self.car_y = SCREEN_HEIGHT // 2 - 50
        self.car_speed = 3
        self.player_exit_x = SCREEN_WIDTH // 2
        self.player_exit_y = SCREEN_HEIGHT // 2 + 50
        self.player_exit_progress = 0
        self.ment_x = SCREEN_WIDTH + 100
        self.ment_y = SCREEN_HEIGHT // 2
        self.ment_speed = 2
        self.dialog_active = False
        self.dialog_text = ""
        self.timer = 0
        self.music_playing = False
        self.waiting_for_input = False  # Ожидание нажатия для продолжения
        self.dialog_index = 0
        self.dialogs = [
            "МЕНТ: Э, шкет, куда прешь? Это наша территория!",
            "СЕРЁГА: Ваша? С какого хрена? Я тут 10 лет отсидел,\nа вы тут за неделю всё захватили?",
            "МЕНТ: А тебе чё, пацан? Хочешь проблем? Мы тебя щас\nпо статье отправим!",
            "СЕРЁГА: Попробуйте, мусора... Только троньте -\nваши семьи завтра хоронить будут!",
            "МЕНТ: Ах ты гангстер малолетний! Ребята, взять его!\nПокажем кто в районе хозяин!",
            "СЕРЁГА: ИДИ НАХУЙ, МУСОР! Я покажу вам кто тут\nнастоящий хозяин!"
        ]
        
    def load_assets(self):
        # Пробуем разные пути для спрайта машины
        car_paths = ["sprite/car.png", "sprite\\car.png", ".venv/sprite/car.png", "sprite/car.PNG"]
        self.car_image = None
        for path in car_paths:
            try:
                self.car_image = pygame.image.load(path)
                self.car_image = pygame.transform.scale(self.car_image, (200, 100))
                break
            except:
                continue
        
        if self.car_image is None:
            # Если спрайт не загрузился, создаем красивую машину
            self.car_image = pygame.Surface((200, 100), pygame.SRCALPHA)
            # Кузов
            pygame.draw.rect(self.car_image, (100, 150, 200), (20, 20, 160, 60))
            # Окна
            pygame.draw.rect(self.car_image, (200, 200, 200), (40, 30, 50, 40))
            pygame.draw.rect(self.car_image, (200, 200, 200), (110, 30, 50, 40))
            # Колёса
            pygame.draw.circle(self.car_image, (30, 30, 30), (50, 85), 15)
            pygame.draw.circle(self.car_image, (30, 30, 30), (150, 85), 15)
            # Фары
            pygame.draw.circle(self.car_image, (255, 255, 200), (180, 50), 8)
        
        # Пробуем разные пути для музыки
        music_paths = ["music/musicingame.ogg", "music\\musicingame.ogg", ".venv/music/musicingame.ogg", 
                      "music/musicingame.OGG", "music/musicingame.wav", "music/musicingame.mp3"]
        self.music_loaded = False
        for path in music_paths:
            try:
                pygame.mixer.music.load(path)
                self.music_loaded = True
                break
            except:
                continue
    
    def update(self, skip=False):
        if not skip:
            self.timer += 1
        
        if self.phase == 0:  # Машина подъезжает
            if not skip:
                self.car_x += self.car_speed * 0.5  # Замедлили
            if self.car_x >= SCREEN_WIDTH // 2 - 100:
                self.car_x = SCREEN_WIDTH // 2 - 100
                if self.timer > 120:  # Пауза 2 секунды перед выходом
                    self.phase = 1
                    self.timer = 0
        
        elif self.phase == 1:  # Выход персонажа
            if not skip:
                self.player_exit_progress += 0.008  # Замедлили анимацию
            if self.player_exit_progress >= 1.0:
                self.player_exit_progress = 1.0
                if self.timer > 180:  # Пауза 3 секунды после выхода
                    self.phase = 2
                    self.timer = 0
                    # Начинаем музыку
                    if not self.music_playing and self.music_loaded:
                        try:
                            pygame.mixer.music.set_volume(0.7)
                            pygame.mixer.music.play(-1)
                            self.music_playing = True
                        except:
                            pass
        
        elif self.phase == 2:  # Менты подходят
            if not skip:
                self.ment_x -= self.ment_speed * 0.5  # Замедлили
            if self.ment_x <= SCREEN_WIDTH // 2 + 150:
                self.ment_x = SCREEN_WIDTH // 2 + 150
                if self.timer > 120:  # Пауза перед диалогом
                    self.phase = 3
                    self.dialog_active = True
                    self.dialog_text = self.dialogs[0]
                    self.dialog_index = 0
                    self.waiting_for_input = True
                    self.timer = 0
        
        elif self.phase == 3:  # Диалог с выбором
            if skip and self.waiting_for_input:
                # Переход к следующему диалогу
                self.dialog_index += 1
                if self.dialog_index >= len(self.dialogs):
                    return True  # Катсцена завершена
                self.dialog_text = self.dialogs[self.dialog_index]
                self.timer = 0
                self.waiting_for_input = True
        
        return False
    
    def draw(self, screen):
        # Фон улицы ночью
        screen.fill((20, 20, 30))
        
        # Здания на фоне
        for i in range(5):
            x = i * 200
            height = 200 + (i % 3) * 50
            pygame.draw.rect(screen, (40, 40, 50), (x, SCREEN_HEIGHT - height, 150, height))
            # Окна
            for wy in range(SCREEN_HEIGHT - height + 20, SCREEN_HEIGHT - 40, 30):
                for wx in range(x + 20, x + 130, 40):
                    lit = random.random() > 0.5
                    color = (255, 255, 150) if lit else (60, 60, 80)
                    pygame.draw.rect(screen, color, (wx, wy, 25, 20))
        
        # Дорога
        pygame.draw.rect(screen, (30, 30, 40), (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
        # Разметка (анимированная)
        offset = (self.timer * 2) % 80
        for i in range(-80, SCREEN_WIDTH + 80, 80):
            pygame.draw.rect(screen, (200, 200, 100), (i + offset, SCREEN_HEIGHT - 50, 40, 4))
        
        # Фонари на столбах
        for i in range(0, SCREEN_WIDTH, 250):
            # Столб
            pygame.draw.rect(screen, (60, 60, 60), (i, SCREEN_HEIGHT - 200, 8, 100))
            # Фонарь
            light_intensity = 0.7 + 0.3 * math.sin(self.timer * 0.1)
            light_color = tuple(int(255 * light_intensity) for _ in range(3))
            pygame.draw.circle(screen, light_color, (i + 4, SCREEN_HEIGHT - 200), 15)
            # Свет от фонаря
            light_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
            for radius in range(50, 0, -5):
                alpha = int(30 * (1 - radius / 50))
                pygame.draw.circle(light_surface, (*light_color[:3], alpha), (50, 50), radius)
            screen.blit(light_surface, (i - 50, SCREEN_HEIGHT - 250))
        
        # Машина
        if self.car_image:
            # Дым от выхлопа когда машина останавливается
            if self.phase >= 1:
                for i in range(3):
                    smoke_x = self.car_x + 180 + random.randint(-10, 10)
                    smoke_y = self.car_y + 80 + i * 5
                    smoke_size = 10 + i * 3
                    smoke_alpha = 100 - i * 20
                    smoke_surface = pygame.Surface((smoke_size * 2, smoke_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(smoke_surface, (80, 80, 80, smoke_alpha), (smoke_size, smoke_size), smoke_size)
                    screen.blit(smoke_surface, (smoke_x - smoke_size, smoke_y - smoke_size))
            
            screen.blit(self.car_image, (self.car_x, self.car_y))
            
            # Фары машины
            if self.phase == 0:
                # Свет фар
                headlight_surface = pygame.Surface((300, 200), pygame.SRCALPHA)
                for radius in range(150, 0, -10):
                    alpha = int(50 * (1 - radius / 150))
                    pygame.draw.circle(headlight_surface, (255, 255, 200, alpha), (150, 100), radius)
                screen.blit(headlight_surface, (self.car_x + 200, self.car_y - 50))
        
        # Персонаж выходит из машины
        if self.phase >= 1:
            # Плавная анимация выхода
            exit_offset = math.sin(self.player_exit_progress * math.pi) * 50
            player_x = self.player_exit_x + exit_offset
            player_y = self.player_exit_y - self.player_exit_progress * 40
            
            # Тело персонажа
            body_color = (180, 80, 80)
            body_rect = pygame.Rect(player_x - 20, player_y - 30, 40, 60)
            pygame.draw.rect(screen, body_color, body_rect)
            
            # Голова
            head_radius = 16
            head_y = player_y - 40
            pygame.draw.circle(screen, (240, 200, 160), (int(player_x), int(head_y)), head_radius)
            
            # Глаза (смотрят на ментов когда они подходят)
            if self.phase >= 2:
                eye_direction = 1 if self.ment_x < player_x else -1
            else:
                eye_direction = 0
            pygame.draw.circle(screen, (50, 50, 150), (int(player_x - 6 + eye_direction * 2), int(head_y - 2)), 4)
            pygame.draw.circle(screen, (50, 50, 150), (int(player_x + 6 + eye_direction * 2), int(head_y - 2)), 4)
            
            # Оружие в руке (когда выходит)
            if self.player_exit_progress > 0.5:
                weapon_x = player_x + 25
                weapon_y = player_y - 10
                pygame.draw.rect(screen, (180, 180, 180), (weapon_x, weapon_y, 20, 6))
        
        # Менты подходят (с использованием спрайтов)
        if self.phase >= 2:
            # Загружаем спрайты для ментов в катсцене
            if not hasattr(self, 'ment_sprite_manager'):
                self.ment_sprite_manager = EnemySpriteManager()
            
            # Анимация подхода ментов
            ment_offset = 0
            if self.phase == 2:
                ment_offset = math.sin(self.timer * 0.1) * 3  # Небольшая тряска при ходьбе
            
            # Определяем состояние анимации
            ment_anim_state = "Walk" if self.phase == 2 else "Idle"
            ment_anim_frame = (self.timer // 8) % 6  # 6 кадров в анимации
            
            # Мент 1
            ment1_x = self.ment_x + ment_offset
            ment1_y = self.ment_y
            
            # Пробуем загрузить спрайт
            ment_sprite = self.ment_sprite_manager.get_sprite("мент", ment_anim_state, ment_anim_frame)
            
            # Проверяем что спрайт загружен и видимый
            sprite_ok = False
            if ment_sprite:
                try:
                    w, h = ment_sprite.get_size()
                    sprite_ok = w > 0 and h > 0
                except:
                    sprite_ok = False
            
            if sprite_ok:
                # Масштабируем спрайт (увеличиваем для видимости)
                orig_w, orig_h = ment_sprite.get_size()
                scaled_w = max(76, int(orig_w * 2.0))
                scaled_h = max(128, int(orig_h * 2.0))
                scaled_ment = pygame.transform.scale(ment_sprite, (scaled_w, scaled_h))
                # Отражаем (менты идут слева направо)
                scaled_ment = pygame.transform.flip(scaled_ment, True, False)
                ment_rect = scaled_ment.get_rect(center=(int(ment1_x), int(ment1_y)))
                screen.blit(scaled_ment, ment_rect)
            else:
                # Fallback - старый способ (всегда видимый)
                pygame.draw.circle(screen, (70, 70, 200), (int(ment1_x), int(ment1_y)), 38)
                pygame.draw.rect(screen, (60, 60, 180), (ment1_x - 20, ment1_y, 40, 50))
                pygame.draw.rect(screen, (200, 200, 200), (ment1_x - 19, ment1_y - 33, 38, 8))
                pygame.draw.circle(screen, RED, (int(ment1_x + 8), int(ment1_y - 5)), 6)
                pygame.draw.circle(screen, RED, (int(ment1_x - 8), int(ment1_y - 5)), 6)
            
            # Руки (указывают на персонажа)
            if self.phase == 3:
                pygame.draw.line(screen, (240, 200, 160), (ment1_x - 15, ment1_y + 10), 
                               (self.player_exit_x - 30, self.player_exit_y - 20), 3)
            
            # Мент 2
            ment2_x = self.ment_x + 60 + ment_offset
            ment2_y = self.ment_y
            
            ment_sprite2 = self.ment_sprite_manager.get_sprite("мент", ment_anim_state, ment_anim_frame)
            
            sprite2_ok = False
            if ment_sprite2:
                try:
                    w, h = ment_sprite2.get_size()
                    sprite2_ok = w > 0 and h > 0
                except:
                    sprite2_ok = False
            
            if sprite2_ok:
                orig_w, orig_h = ment_sprite2.get_size()
                scaled_w = max(76, int(orig_w * 2.0))
                scaled_h = max(128, int(orig_h * 2.0))
                scaled_ment2 = pygame.transform.scale(ment_sprite2, (scaled_w, scaled_h))
                scaled_ment2 = pygame.transform.flip(scaled_ment2, True, False)
                ment_rect2 = scaled_ment2.get_rect(center=(int(ment2_x), int(ment2_y)))
                screen.blit(scaled_ment2, ment_rect2)
            else:
                # Fallback
                pygame.draw.circle(screen, (70, 70, 200), (int(ment2_x), int(ment2_y)), 38)
                pygame.draw.rect(screen, (60, 60, 180), (ment2_x - 20, ment2_y, 40, 50))
                pygame.draw.rect(screen, (200, 200, 200), (ment2_x - 19, ment2_y - 33, 38, 8))
                pygame.draw.circle(screen, RED, (int(ment2_x + 8), int(ment2_y - 5)), 6)
                pygame.draw.circle(screen, RED, (int(ment2_x - 8), int(ment2_y - 5)), 6)
        
        # Диалоговое окно
        if self.dialog_active and self.phase == 3:
            dialog_width = 800
            dialog_height = 150
            dialog_x = SCREEN_WIDTH // 2 - dialog_width // 2
            dialog_y = SCREEN_HEIGHT - 200
            
            # Фон диалога с эффектом свечения
            glow_surface = pygame.Surface((dialog_width + 20, dialog_height + 20), pygame.SRCALPHA)
            for i in range(3):
                alpha = 50 - i * 15
                pygame.draw.rect(glow_surface, (*GOLD[:3], alpha), 
                               (i, i, dialog_width + 20 - i*2, dialog_height + 20 - i*2), 2)
            screen.blit(glow_surface, (dialog_x - 10, dialog_y - 10))
            
            # Основной фон диалога
            pygame.draw.rect(screen, (10, 10, 20), (dialog_x, dialog_y, dialog_width, dialog_height))
            pygame.draw.rect(screen, GOLD, (dialog_x, dialog_y, dialog_width, dialog_height), 3)
            
            # Имя говорящего
            speaker = "МЕНТ" if "МЕНТ:" in self.dialog_text else "СЕРЁГА"
            speaker_color = (200, 100, 100) if "МЕНТ:" in self.dialog_text else (100, 200, 100)
            speaker_text = menu_font.render(speaker, True, speaker_color)
            screen.blit(speaker_text, (dialog_x + 20, dialog_y + 10))
            
            # Текст диалога
            lines = self.dialog_text.split('\n')
            for i, line in enumerate(lines):
                if ":" in line:
                    line = line.split(":", 1)[1].strip()  # Убираем имя говорящего из текста
                text = dialog_font.render(line, True, WHITE)
                screen.blit(text, (dialog_x + 20, dialog_y + 50 + i * 35))
        
        # Подсказка для продолжения
        if self.waiting_for_input and self.phase == 3:
            if pygame.time.get_ticks() % 1000 < 500:
                hint = small_font.render("Нажми ПРОБЕЛ чтобы продолжить", True, GOLD)
                screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 50))
        
        # Индикатор музыки
        if not self.music_loaded:
            music_hint = small_font.render("Музыка не найдена (music/musicingame.ogg)", True, LIGHT_GREY)
            screen.blit(music_hint, (10, SCREEN_HEIGHT - 30))


class Cutscene:
    def __init__(self, texts, background_color=DARK_GREY, mission_complete=False):
        self.texts = texts
        self.current_text = 0
        self.background_color = background_color
        self.timer = 0
        self.mission_complete = mission_complete

    def update(self, dt):
        self.timer += dt
        if self.timer > 4000:  # 4 секунды на кадр
            self.timer = 0
            self.current_text += 1
            return self.current_text >= len(self.texts)
        return False

    def draw(self, screen):
        screen.fill(self.background_color)

        if self.current_text < len(self.texts):
            lines = self.texts[self.current_text].split('\n')
            for i, line in enumerate(lines):
                text = dialog_font.render(line, True, WHITE)
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2,
                                   SCREEN_HEIGHT // 2 - len(lines) * 20 + i * 40))

        # Индикатор продолжения
        if pygame.time.get_ticks() % 1000 < 500:
            hint_text = "Нажми ПРОБЕЛ чтобы продолжить" if not self.mission_complete else "Нажми ПРОБЕЛ для завершения миссии"
            hint = small_font.render(hint_text, True, LIGHT_GREY)
            screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 100))


class Location:
    def __init__(self, name, description, color_modifier=(1.0, 1.0, 1.0), world_pos=(0, 0)):
        self.name = name
        self.description = description
        self.color_modifier = color_modifier
        self.world_x, self.world_y = world_pos
        self.buildings = []
        self.shop_pos = None
        self.generate_buildings()

    def generate_buildings(self):
        # Улучшенная генерация зданий с правильным расположением
        building_positions = [
            # Левая сторона
            (80, 150, 120, 200), (80, 400, 120, 180), (80, 620, 120, 140),
            # Центр-лево
            (250, 100, 140, 250), (250, 400, 140, 200), (250, 650, 140, 100),
            # Центр-право
            (650, 120, 150, 280), (650, 450, 150, 220), (650, 700, 150, 60),
            # Правая сторона
            (820, 180, 130, 200), (820, 430, 130, 180), (820, 650, 130, 110),
        ]
        
        for x, y, width, height in building_positions:
            color = random.choice(BUILDING_COLORS)
            # Применяем модификатор цвета локации
            color = tuple(int(c * self.color_modifier[i]) for i, c in enumerate(color))
            windows = []

            # Генерация окон
            for wx in range(x + 15, x + width - 15, 25):
                for wy in range(y + 15, y + height - 15, 30):
                    if random.random() > 0.4:
                        lit = random.random() > 0.3
                        windows.append((wx, wy, lit))

            self.buildings.append((x, y, width, height, color, windows))
        
        # Магазин всегда в центре
        self.shop_pos = (SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 - 40, 80, 80)

    def draw(self, screen):
        # Здания
        for x, y, width, height, color, windows in self.buildings:
            # Основное здание
            pygame.draw.rect(screen, color, (x, y, width, height))

            # Тень
            pygame.draw.polygon(screen, (20, 20, 30), [
                (x + width, y),
                (x + width + 10, y - 10),
                (x + width + 10, y + height - 10),
                (x + width, y + height)
            ])

            # Окна
            for wx, wy, lit in windows:
                window_color = (255, 255, 150) if lit else (80, 80, 120)
                pygame.draw.rect(screen, window_color, (wx, wy, 18, 22))

            # Дверь
            door_x = x + width // 2 - 15
            door_y = y + height - 50
            pygame.draw.rect(screen, (40, 30, 20), (door_x, door_y, 30, 50))
        
        # Магазин
        if self.shop_pos:
            sx, sy, sw, sh = self.shop_pos
            # Здание магазина
            pygame.draw.rect(screen, (150, 100, 50), (sx, sy, sw, sh))
            pygame.draw.rect(screen, GOLD, (sx, sy, sw, sh), 3)
            # Вывеска
            sign_text = small_font.render("МАГАЗИН", True, GOLD)
            screen.blit(sign_text, (sx + sw // 2 - sign_text.get_width() // 2, sy - 20))


class Shop:
    def __init__(self):
        self.items = [
            {"name": "ПАТРОНЫ ПИСТОЛЕТ", "price": 50, "type": "ammo", "weapon_index": 0, "amount": 30},
            {"name": "ПАТРОНЫ АВТОМАТ", "price": 80, "type": "ammo", "weapon_index": 1, "amount": 60},
            {"name": "ПАТРОНЫ ДРОБОВИК", "price": 120, "type": "ammo", "weapon_index": 2, "amount": 12},
            {"name": "ПАТРОНЫ СНАЙПЕРКА", "price": 200, "type": "ammo", "weapon_index": 3, "amount": 10},
            {"name": "ПАТРОНЫ ПУЛЕМЁТ", "price": 150, "type": "ammo", "weapon_index": 4, "amount": 100},
            {"name": "АПТЕЧКА", "price": 300, "type": "health", "amount": 50},
            {"name": "УЛУЧШЕНИЕ УРОНА", "price": 2000, "type": "upgrade", "stat": "damage"},
            {"name": "УЛУЧШЕНИЕ СКОРОСТИ", "price": 1500, "type": "upgrade", "stat": "speed"},
            {"name": "УЛУЧШЕНИЕ ЗДОРОВЬЯ", "price": 2500, "type": "upgrade", "stat": "health"},
            {"name": "ПАТРОНЫ ГРАНАТОМЁТ", "price": 500, "type": "ammo", "weapon_index": 5, "amount": 5},
            {"name": "ПАТРОНЫ РЕВОЛЬВЕР", "price": 100, "type": "ammo", "weapon_index": 6, "amount": 18},
            {"name": "ПАТРОНЫ АВТОМАТ-2", "price": 120, "type": "ammo", "weapon_index": 7, "amount": 80},
            {"name": "БОЛЬШАЯ АПТЕЧКА", "price": 600, "type": "health", "amount": 100},
            {"name": "УЛУЧШЕНИЕ СКОРОСТИ СТРЕЛЬБЫ", "price": 3000, "type": "upgrade", "stat": "firerate"},
            {"name": "УЛУЧШЕНИЕ ТОЧНОСТИ", "price": 2500, "type": "upgrade", "stat": "accuracy"},
            {"name": "БРОНЯ", "price": 4000, "type": "upgrade", "stat": "armor"},
        ]
        self.selected_item = 0

    def buy_item(self, item, player):
        if player.money >= item["price"]:
            player.money -= item["price"]
            if item["type"] == "ammo":
                weapon = player.weapons[item["weapon_index"]]
                weapon.ammo = min(weapon.max_ammo, weapon.ammo + item["amount"])
                return True, f"Куплено: {item['name']}"
            elif item["type"] == "health":
                player.health = min(player.max_health, player.health + item["amount"])
                return True, f"Восстановлено {item['amount']} здоровья"
            elif item["type"] == "upgrade":
                if item["stat"] == "damage":
                    for weapon in player.weapons:
                        weapon.damage = int(weapon.damage * 1.2)
                    return True, "Урон всех оружий увеличен на 20%"
                elif item["stat"] == "speed":
                    player.speed = min(8, player.speed + 0.5)
                    return True, "Скорость увеличена"
                elif item["stat"] == "health":
                    player.max_health += 20
                    player.health += 20
                    return True, "Максимальное здоровье +20"
                elif item["stat"] == "firerate":
                    for weapon in player.weapons:
                        weapon.fire_rate = weapon.fire_rate * 1.15
                    return True, "Скорострельность всех оружий +15%"
                elif item["stat"] == "accuracy":
                    for weapon in player.weapons:
                        weapon.spread = max(0.01, weapon.spread * 0.8)
                    return True, "Точность всех оружий +20%"
                elif item["stat"] == "armor":
                    player.armor = getattr(player, 'armor', 0) + 10
                    return True, "Броня +10 (снижение урона)"
        return False, "Недостаточно денег!"

    def draw(self, screen, player):
        # Фон магазина
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        # Заголовок
        title = title_font.render("МАГАЗИН ОРУЖИЯ", True, GOLD)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

        # Деньги игрока
        money_text = menu_font.render(f"БАБЛО: {player.money} РУБ.", True, GOLD)
        screen.blit(money_text, (SCREEN_WIDTH // 2 - money_text.get_width() // 2, 120))

        # Список товаров
        start_y = 180
        item_height = 50
        visible_items = 8
        start_index = max(0, self.selected_item - visible_items // 2)
        end_index = min(len(self.items), start_index + visible_items)

        for i in range(start_index, end_index):
            item = self.items[i]
            y_pos = start_y + (i - start_index) * item_height
            
            # Выделение выбранного товара
            if i == self.selected_item:
                pygame.draw.rect(screen, GOLD, (200, y_pos - 5, SCREEN_WIDTH - 400, item_height), 3)
            
            # Название товара
            item_text = dialog_font.render(item["name"], True, WHITE)
            screen.blit(item_text, (220, y_pos))
            
            # Цена
            price_text = dialog_font.render(f"{item['price']} РУБ.", True, GOLD)
            screen.blit(price_text, (SCREEN_WIDTH - 300, y_pos))

        # Подсказки
        hint1 = small_font.render("СТРЕЛКИ ВВЕРХ/ВНИЗ - ВЫБОР | ENTER - КУПИТЬ | ESC - ВЫХОД", True, LIGHT_GREY)
        screen.blit(hint1, (SCREEN_WIDTH // 2 - hint1.get_width() // 2, SCREEN_HEIGHT - 80))

        # Информация о выбранном товаре
        selected = self.items[self.selected_item]
        info_y = SCREEN_HEIGHT - 150
        if selected["type"] == "ammo":
            weapon = player.weapons[selected["weapon_index"]]
            info_text = small_font.render(f"Текущие патроны: {weapon.ammo}/{weapon.max_ammo}", True, WHITE)
            screen.blit(info_text, (SCREEN_WIDTH // 2 - info_text.get_width() // 2, info_y))
        elif selected["type"] == "health":
            info_text = small_font.render(f"Текущее здоровье: {player.health}/{player.max_health}", True, WHITE)
            screen.blit(info_text, (SCREEN_WIDTH // 2 - info_text.get_width() // 2, info_y))


class City:
    def __init__(self):
        self.locations = []
        self.current_location_index = 0
        self.world_size = 5000  # Размер открытого мира
        self.camera_x = 0
        self.camera_y = 0
        self.init_locations()
        self.transition_points = []  # Точки перехода между локациями
        self.init_transition_points()

    def init_locations(self):
        self.locations = [
            Location("ЦЕНТРАЛЬНЫЙ РАЙОН", "Богатый район с высокими зданиями", (1.2, 1.1, 1.0), (2500, 2500)),
            Location("ПРОМЗОНА", "Заброшенные заводы и склады", (0.7, 0.7, 0.8), (1000, 1000)),
            Location("СТАРЫЙ ГОРОД", "Узкие улочки и старые дома", (0.9, 0.85, 0.9), (1500, 3500)),
            Location("ПОРТОВАЯ ЗОНА", "Доки и причалы", (0.8, 0.9, 1.1), (4000, 2000)),
            Location("ЭЛИТНЫЙ КВАРТАЛ", "Роскошные особняки", (1.3, 1.2, 1.1), (3500, 1000)),
            Location("ГЕТТО", "Опасные улицы, полные бандитов", (0.6, 0.5, 0.6), (500, 3000)),
            Location("ПРОМЫШЛЕННЫЙ РАЙОН", "Заводы и фабрики", (0.8, 0.8, 0.9), (4500, 4000)),
            Location("ТОРГОВЫЙ ЦЕНТР", "Магазины и рынки", (1.1, 1.0, 0.9), (2000, 1500))
        ]

    def init_transition_points(self):
        # Создаём точки перехода между локациями
        for i, loc in enumerate(self.locations):
            for j, other_loc in enumerate(self.locations):
                if i != j:
                    # Создаём переходы между соседними локациями
                    dist = math.sqrt((loc.world_x - other_loc.world_x)**2 + (loc.world_y - other_loc.world_y)**2)
                    if dist < 2000:  # Только близкие локации
                        mid_x = (loc.world_x + other_loc.world_x) // 2
                        mid_y = (loc.world_y + other_loc.world_y) // 2
                        self.transition_points.append({
                            'x': mid_x, 'y': mid_y,
                            'from': i, 'to': j,
                            'radius': 100
                        })

    def get_current_location(self):
        return self.locations[self.current_location_index]
    
    def update_camera(self, player_x, player_y):
        # Камера следует за игроком в открытом мире
        self.camera_x = player_x - SCREEN_WIDTH // 2
        self.camera_y = player_y - SCREEN_HEIGHT // 2
        
        # Ограничиваем камеру границами мира
        self.camera_x = max(0, min(self.world_size - SCREEN_WIDTH, self.camera_x))
        self.camera_y = max(0, min(self.world_size - SCREEN_HEIGHT, self.camera_y))
    
    def check_location_transition(self, player_x, player_y):
        # Проверяем переходы между локациями
        for tp in self.transition_points:
            dist = math.sqrt((player_x - tp['x'])**2 + (player_y - tp['y'])**2)
            if dist < tp['radius']:
                self.current_location_index = tp['to']
                return True
        return False

    def draw(self, screen, player_x=0, player_y=0):
        # Фон открытого мира с улучшенным градиентом
        for y in range(0, SCREEN_HEIGHT, 10):
            color_factor = y / SCREEN_HEIGHT
            # Более насыщенный градиент
            color = (
                int(10 + color_factor * 15),
                int(12 + color_factor * 18),
                int(20 + color_factor * 25)
            )
            pygame.draw.rect(screen, color, (0, y, SCREEN_WIDTH, 10))
        
        # Рисуем улучшенную сетку с эффектом глубины
        grid_color = (30, 30, 40)
        grid_bright = (40, 40, 50)
        for x in range(int(self.camera_x % 200), SCREEN_WIDTH + 200, 200):
            screen_x = x - int(self.camera_x % 200)
            pygame.draw.line(screen, grid_bright, (screen_x, 0), (screen_x, SCREEN_HEIGHT), 2)
        for y in range(int(self.camera_y % 200), SCREEN_HEIGHT + 200, 200):
            screen_y = y - int(self.camera_y % 200)
            pygame.draw.line(screen, grid_bright, (0, screen_y), (SCREEN_WIDTH, screen_y), 2)
        
        # Мелкая сетка
        for x in range(int(self.camera_x % 50), SCREEN_WIDTH + 50, 50):
            screen_x = x - int(self.camera_x % 50)
            pygame.draw.line(screen, grid_color, (screen_x, 0), (screen_x, SCREEN_HEIGHT), 1)
        for y in range(int(self.camera_y % 50), SCREEN_HEIGHT + 50, 50):
            screen_y = y - int(self.camera_y % 50)
            pygame.draw.line(screen, grid_color, (0, screen_y), (SCREEN_WIDTH, screen_y), 1)
        
        # Добавляем случайные объекты на карте (деревья, столбы, мусор)
        for i in range(20):
            obj_x = (self.camera_x + i * 300) % (self.world_size - 200) + 100
            obj_y = (self.camera_y + i * 250) % (self.world_size - 200) + 100
            screen_x = obj_x - self.camera_x
            screen_y = obj_y - self.camera_y
            
            if -50 < screen_x < SCREEN_WIDTH + 50 and -50 < screen_y < SCREEN_HEIGHT + 50:
                obj_type = i % 4
                if obj_type == 0:  # Дерево
                    # Ствол
                    pygame.draw.rect(screen, (60, 40, 20), (screen_x - 5, screen_y, 10, 30))
                    # Крона
                    pygame.draw.circle(screen, (20, 80, 20), (int(screen_x), int(screen_y - 10)), 20)
                    pygame.draw.circle(screen, (30, 100, 30), (int(screen_x), int(screen_y - 10)), 15)
                elif obj_type == 1:  # Столб
                    pygame.draw.rect(screen, (50, 50, 50), (screen_x - 3, screen_y, 6, 40))
                    # Фонарь
                    pygame.draw.circle(screen, (200, 200, 150), (int(screen_x), int(screen_y - 5)), 8)
                elif obj_type == 2:  # Мусорный бак
                    pygame.draw.rect(screen, (40, 40, 50), (screen_x - 8, screen_y, 16, 20))
                    pygame.draw.rect(screen, (60, 60, 70), (screen_x - 8, screen_y, 16, 5))
                elif obj_type == 3:  # Камень/препятствие
                    pygame.draw.circle(screen, (70, 70, 80), (int(screen_x), int(screen_y)), 12)
                    pygame.draw.circle(screen, (50, 50, 60), (int(screen_x), int(screen_y)), 8)
        
        # Рисуем все локации в открытом мире
        for i, loc in enumerate(self.locations):
            # Позиция локации относительно камеры
            loc_screen_x = loc.world_x - self.camera_x
            loc_screen_y = loc.world_y - self.camera_y
            
            # Рисуем только видимые локации
            if -500 < loc_screen_x < SCREEN_WIDTH + 500 and -500 < loc_screen_y < SCREEN_HEIGHT + 500:
                # Мини-индикатор локации с эффектом свечения
                if i == self.current_location_index:
                    # Свечение
                    glow_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
                    for radius in range(60, 0, -5):
                        alpha = int(100 * (1 - radius / 60))
                        pygame.draw.circle(glow_surface, (*GOLD[:3], alpha), (60, 60), radius)
                    screen.blit(glow_surface, (int(loc_screen_x) - 60, int(loc_screen_y) - 60))
                    
                    pygame.draw.circle(screen, GOLD, (int(loc_screen_x), int(loc_screen_y)), 50, 4)
                    pygame.draw.circle(screen, (255, 255, 150), (int(loc_screen_x), int(loc_screen_y)), 45, 2)
                    name_text = small_font.render(loc.name, True, GOLD)
                    screen.blit(name_text, (int(loc_screen_x) - name_text.get_width() // 2, int(loc_screen_y) - 70))
                else:
                    pygame.draw.circle(screen, LIGHT_GREY, (int(loc_screen_x), int(loc_screen_y)), 30, 2)
                    pygame.draw.circle(screen, (60, 60, 70), (int(loc_screen_x), int(loc_screen_y)), 25, 1)
        
        # Рисуем точки перехода с эффектом
        for tp in self.transition_points:
            tp_screen_x = tp['x'] - self.camera_x
            tp_screen_y = tp['y'] - self.camera_y
            if -100 < tp_screen_x < SCREEN_WIDTH + 100 and -100 < tp_screen_y < SCREEN_HEIGHT + 100:
                # Пульсирующее свечение
                pulse = math.sin(pygame.time.get_ticks() * 0.005) * 0.3 + 0.7
                glow_radius = int(tp['radius'] * pulse)
                glow_surface = pygame.Surface((glow_radius * 2 + 10, glow_radius * 2 + 10), pygame.SRCALPHA)
                for radius in range(glow_radius, 0, -5):
                    alpha = int(80 * (1 - radius / glow_radius))
                    pygame.draw.circle(glow_surface, (*BLUE[:3], alpha), (glow_radius + 5, glow_radius + 5), radius)
                screen.blit(glow_surface, (int(tp_screen_x) - glow_radius - 5, int(tp_screen_y) - glow_radius - 5))
                pygame.draw.circle(screen, BLUE, (int(tp_screen_x), int(tp_screen_y)), tp['radius'], 3)
                pygame.draw.circle(screen, (100, 150, 255), (int(tp_screen_x), int(tp_screen_y)), tp['radius'] - 5, 1)
        
        # Дороги между локациями с улучшенной графикой
        for i in range(len(self.locations)):
            for j in range(i + 1, len(self.locations)):
                loc1 = self.locations[i]
                loc2 = self.locations[j]
                dist = math.sqrt((loc1.world_x - loc2.world_x)**2 + (loc1.world_y - loc2.world_y)**2)
                if dist < 2000:
                    x1 = loc1.world_x - self.camera_x
                    y1 = loc1.world_y - self.camera_y
                    x2 = loc2.world_x - self.camera_x
                    y2 = loc2.world_y - self.camera_y
                    if (x1 > -200 and x1 < SCREEN_WIDTH + 200 and y1 > -200 and y1 < SCREEN_HEIGHT + 200) or \
                       (x2 > -200 and x2 < SCREEN_WIDTH + 200 and y2 > -200 and y2 < SCREEN_HEIGHT + 200):
                        # Тень дороги
                        pygame.draw.line(screen, (20, 20, 25), (int(x1), int(y1) + 1), (int(x2), int(y2) + 1), 5)
                        # Основная дорога
                        pygame.draw.line(screen, (50, 50, 60), (int(x1), int(y1)), (int(x2), int(y2)), 4)
                        # Разметка
                        steps = int(dist / 50)
                        for step in range(0, steps, 2):
                            t = step / steps
                            mark_x = int(x1 + (x2 - x1) * t)
                            mark_y = int(y1 + (y2 - y1) * t)
                            pygame.draw.circle(screen, (180, 180, 100), (mark_x, mark_y), 3)
        
        # Отрисовка текущей локации (детали)
        current_loc = self.get_current_location()
        loc_screen_x = current_loc.world_x - self.camera_x
        loc_screen_y = current_loc.world_y - self.camera_y
        
        # Если игрок в текущей локации, рисуем детали (увеличиваем радиус)
        dist_to_loc = math.sqrt((player_x - current_loc.world_x)**2 + (player_y - current_loc.world_y)**2)
        if dist_to_loc < 1200:  # Увеличили радиус отрисовки
            # Смещаем отрисовку зданий
            offset_x = loc_screen_x - SCREEN_WIDTH // 2
            offset_y = loc_screen_y - SCREEN_HEIGHT // 2
            
            # Асфальт с текстурой
            for i in range(0, SCREEN_WIDTH, 40):
                for j in range(SCREEN_HEIGHT - 100, SCREEN_HEIGHT, 40):
                    if (i + j) % 80 < 40:
                        pygame.draw.rect(screen, (25, 25, 35), (offset_x + i, offset_y + j, 40, 40))
            pygame.draw.rect(screen, ASPHALT, (offset_x, offset_y + SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
            
            # Дороги с разметкой и эффектом
            road_color = (35, 35, 45)
            for i in range(0, SCREEN_WIDTH, 120):
                # Тень дороги
                pygame.draw.rect(screen, (20, 20, 30), (offset_x + i - 1, offset_y + SCREEN_HEIGHT // 2 - 3, 62, 6))
                pygame.draw.rect(screen, road_color, (offset_x + i, offset_y + SCREEN_HEIGHT // 2 - 2, 60, 4))
                # Разметка с эффектом
                mark_offset = int((self.camera_x + self.camera_y) % 80)
                if i + mark_offset < SCREEN_WIDTH:
                    pygame.draw.rect(screen, (200, 200, 100), (offset_x + i + mark_offset, offset_y + SCREEN_HEIGHT // 2 - 1, 40, 2))
            
            for i in range(0, SCREEN_HEIGHT, 120):
                pygame.draw.rect(screen, (20, 20, 30), (offset_x + SCREEN_WIDTH // 2 - 3, offset_y + i - 1, 6, 62))
                pygame.draw.rect(screen, road_color, (offset_x + SCREEN_WIDTH // 2 - 2, offset_y + i, 4, 60))
                mark_offset = int((self.camera_x + self.camera_y) % 80)
                if i + mark_offset < SCREEN_HEIGHT:
                    pygame.draw.rect(screen, (200, 200, 100), (offset_x + SCREEN_WIDTH // 2 - 1, offset_y + i + mark_offset, 2, 40))
            
            # Дополнительные объекты на локации (машины, фонари, мусор)
            for i in range(8):
                obj_x = offset_x + random.randint(50, SCREEN_WIDTH - 50)
                obj_y = offset_y + SCREEN_HEIGHT - 120 + random.randint(-20, 20)
                
                if -100 < obj_x < SCREEN_WIDTH + 100 and -100 < obj_y < SCREEN_HEIGHT + 100:
                    obj_type = i % 3
                    if obj_type == 0:  # Машина
                        car_color = random.choice([(100, 150, 200), (200, 100, 100), (150, 150, 150), (200, 200, 100)])
                        pygame.draw.rect(screen, car_color, (obj_x - 25, obj_y - 15, 50, 30))
                        pygame.draw.rect(screen, (200, 200, 200), (obj_x - 20, obj_y - 12, 18, 20))
                        pygame.draw.rect(screen, (200, 200, 200), (obj_x + 2, obj_y - 12, 18, 20))
                        pygame.draw.circle(screen, (30, 30, 30), (int(obj_x - 15), int(obj_y + 12)), 6)
                        pygame.draw.circle(screen, (30, 30, 30), (int(obj_x + 15), int(obj_y + 12)), 6)
                    elif obj_type == 1:  # Фонарь
                        pygame.draw.rect(screen, (60, 60, 60), (obj_x - 2, obj_y - 30, 4, 30))
                        light_intensity = 0.7 + 0.3 * math.sin(pygame.time.get_ticks() * 0.01 + i)
                        light_color = tuple(int(255 * light_intensity) for _ in range(3))
                        pygame.draw.circle(screen, light_color, (int(obj_x), int(obj_y - 30)), 8)
                        # Свет от фонаря
                        light_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
                        for radius in range(30, 0, -5):
                            alpha = int(40 * (1 - radius / 30))
                            pygame.draw.circle(light_surf, (*light_color[:3], alpha), (30, 30), radius)
                        screen.blit(light_surf, (obj_x - 30, obj_y - 60))
                    elif obj_type == 2:  # Мусорный бак
                        pygame.draw.rect(screen, (40, 40, 50), (obj_x - 8, obj_y - 20, 16, 20))
                        pygame.draw.rect(screen, (60, 60, 70), (obj_x - 8, obj_y - 20, 16, 4))
            
            # Здания текущей локации с улучшенной графикой
            for x, y, width, height, color, windows in current_loc.buildings:
                screen_x = offset_x + x
                screen_y = offset_y + y
                
                # Проверяем видимость здания
                if screen_x + width < 0 or screen_x > SCREEN_WIDTH or screen_y + height < 0 or screen_y > SCREEN_HEIGHT:
                    continue
                
                # Основа здания с градиентом
                for i in range(height):
                    gradient_factor = i / height
                    grad_color = tuple(int(c * (0.8 + gradient_factor * 0.2)) for c in color)
                    pygame.draw.line(screen, grad_color, (screen_x, screen_y + i), (screen_x + width, screen_y + i))
                
                # Тень с эффектом
                shadow_points = [
                    (screen_x + width, screen_y),
                    (screen_x + width + 15, screen_y - 15),
                    (screen_x + width + 15, screen_y + height - 15),
                    (screen_x + width, screen_y + height)
                ]
                pygame.draw.polygon(screen, (10, 10, 15), shadow_points)
                
                # Обводка здания
                pygame.draw.rect(screen, tuple(min(255, c + 30) for c in color), (screen_x, screen_y, width, height), 2)
                
                # Окна с эффектом свечения
                for wx, wy, lit in windows:
                    win_screen_x = offset_x + wx
                    win_screen_y = offset_y + wy
                    
                    if lit:
                        # Свечение окна
                        glow_surface = pygame.Surface((25, 25), pygame.SRCALPHA)
                        for radius in range(12, 0, -2):
                            alpha = int(80 * (1 - radius / 12))
                            pygame.draw.circle(glow_surface, (255, 255, 150, alpha), (12, 12), radius)
                        screen.blit(glow_surface, (win_screen_x - 3, win_screen_y - 3))
                    
                    window_color = (255, 255, 180) if lit else (60, 60, 80)
                    pygame.draw.rect(screen, window_color, (win_screen_x, win_screen_y, 18, 22))
                    pygame.draw.rect(screen, (40, 40, 50), (win_screen_x, win_screen_y, 18, 22), 1)
                    
                    # Отражение в окнах
                    if lit and random.random() > 0.7:
                        pygame.draw.line(screen, (255, 255, 255), 
                                       (win_screen_x + 2, win_screen_y + 2), 
                                       (win_screen_x + 16, win_screen_y + 20), 1)
                
                # Крыша здания
                roof_color = tuple(int(c * 0.7) for c in color)
                pygame.draw.polygon(screen, roof_color, [
                    (screen_x, screen_y),
                    (screen_x + width // 2, screen_y - 20),
                    (screen_x + width, screen_y)
                ])
                
                # Дверь с деталями
                door_x = screen_x + width // 2 - 15
                door_y = screen_y + height - 50
                pygame.draw.rect(screen, (30, 20, 15), (door_x, door_y, 30, 50))
                pygame.draw.rect(screen, (50, 40, 30), (door_x, door_y, 30, 50), 2)
                # Ручка двери
                pygame.draw.circle(screen, (150, 150, 150), (door_x + 25, door_y + 25), 3)
            
            # Магазин с улучшенной графикой
            if current_loc.shop_pos:
                sx, sy, sw, sh = current_loc.shop_pos
                shop_world_x = current_loc.world_x - SCREEN_WIDTH // 2 + sx + sw // 2
                shop_world_y = current_loc.world_y - SCREEN_HEIGHT // 2 + sy + sh // 2
                shop_screen_x = shop_world_x - self.camera_x
                shop_screen_y = shop_world_y - self.camera_y
                
                # Свечение магазина
                shop_glow = pygame.Surface((sw + 40, sh + 40), pygame.SRCALPHA)
                for radius in range(40, 0, -5):
                    alpha = int(60 * (1 - radius / 40))
                    pygame.draw.circle(shop_glow, (*GOLD[:3], alpha), (sw // 2 + 20, sh // 2 + 20), radius)
                screen.blit(shop_glow, (shop_screen_x - sw // 2 - 20, shop_screen_y - sh // 2 - 20))
                
                # Здание магазина с градиентом
                shop_color = (150, 100, 50)
                for i in range(sh):
                    grad_factor = i / sh
                    grad_color = tuple(int(c * (0.9 + grad_factor * 0.1)) for c in shop_color)
                    pygame.draw.line(screen, grad_color, 
                                   (shop_screen_x - sw // 2, shop_screen_y - sh // 2 + i),
                                   (shop_screen_x + sw // 2, shop_screen_y - sh // 2 + i))
                
                pygame.draw.rect(screen, GOLD, (shop_screen_x - sw // 2, shop_screen_y - sh // 2, sw, sh), 4)
                pygame.draw.rect(screen, (255, 255, 200), (shop_screen_x - sw // 2, shop_screen_y - sh // 2, sw, sh), 2)
                
                # Вывеска с эффектом
                sign_y = shop_screen_y - sh // 2 - 25
                sign_bg = pygame.Surface((sw + 20, 30), pygame.SRCALPHA)
                sign_bg.fill((0, 0, 0, 200))
                screen.blit(sign_bg, (shop_screen_x - sw // 2 - 10, sign_y))
                sign_text = small_font.render("МАГАЗИН", True, GOLD)
                screen.blit(sign_text, (shop_screen_x - sign_text.get_width() // 2, sign_y + 5))
                
                # Окна магазина
                for i in range(2):
                    win_x = shop_screen_x - sw // 2 + 15 + i * 35
                    win_y = shop_screen_y - sh // 2 + 15
                    pygame.draw.rect(screen, (255, 255, 200), (win_x, win_y, 20, 25))
                    pygame.draw.rect(screen, GOLD, (win_x, win_y, 20, 25), 2)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("БРАТВА: УЛИЦЫ СТОЛИЦЫ - ЭПИЧЕСКИЙ РЕМАСТЕР!")
        self.clock = pygame.time.Clock()
        self.state = GameState.MAIN_MENU
        self.player = Player()
        self.city = City()
        self.enemies = []
        self.bullets = []
        self.particles = []
        self.damage_numbers = []
        self.missions = []
        self.current_mission_index = 0
        self.cutscene = None
        self.hotline_cutscene = None
        self.score = 0
        self.wave = 1
        self.enemy_spawn_timer = 0
        self.mission_start_time = 0
        self.shop = Shop()
        self.shop_message = ""
        self.shop_message_timer = 0
        self.achievements = []
        self.current_achievement_notification = None
        self.achievement_notification_timer = 0
        self.kill_feed = []
        self.damage_numbers = []
        self.screen_shake = 0
        self.screen_shake_intensity = 0

        self.init_missions()
        self.init_achievements()
    
    def init_achievements(self):
        self.achievements = [
            Achievement("ПЕРВАЯ КРОВЬ", "Убей первого врага", 
                       lambda p, g: p.kills >= 1),
            Achievement("МАССОВЫЙ УБИЙЦА", "Убей 50 врагов", 
                       lambda p, g: p.kills >= 50),
            Achievement("БОСС УБИЙЦА", "Убей 10 боссов", 
                       lambda p, g: p.bosses_killed >= 10),
            Achievement("МИЛЛИОНЕР", "Заработай 10000 рублей", 
                       lambda p, g: p.money >= 10000),
            Achievement("НЕУЯЗВИМЫЙ", "Пройди миссию без потери здоровья", 
                       lambda p, g: False),  # Специальная проверка
            Achievement("МАСТЕР СТРЕЛЬБЫ", "Сделай 100 убийств", 
                       lambda p, g: p.kills >= 100),
            Achievement("ЛЕГЕНДА", "Пройди все миссии", 
                       lambda p, g: p.completed_missions >= len(self.missions)),
            Achievement("ВОЛНА УЖАСА", "Достигни 10 волны", 
                       lambda p, g: g.wave >= 10),
        ]

    def init_missions(self):
        mission1_texts = [
            "РАЙОННЫЙ ОТДЕЛ. СЕРЁГА ПОДХОДИТ К МЕНТАМ...",
            "МЕНТ: Э, шкет, куда прешь? Это наша территория!",
            "СЕРЁГА: Ваша? С какого хрена? Я тут 10 лет отсидел,\nа вы тут за неделю всё захватили?",
            "МЕНТ: А тебе чё, пацан? Хочешь проблем? Мы тебя щас\nпо статье отправим!",
            "СЕРЁГА: Попробуйте, мусора... Только троньте -\nваши семьи завтра хоронить будут!",
            "МЕНТ: Ах ты гангстер малолетний! Ребята, взять его!\nПокажем кто в районе хозяин!",
            "ЗАВЯЗЫВАЕТСЯ ЖЕСТОКАЯ ДРАКА...",
            "СЕРЁГА: Вот так, мусора! Теперь вы знаете\nкто тут настоящий хозяин!"
        ]

        mission2_texts = [
            "СЕРЁГА: Ментов поставили на место...\nТеперь бизнесмены зажрались!",
            "ОНИ ДУМАЮТ ЧТО МОГУТ НЕ ПЛАТИТЬ ЗА ПРИКРЫТИЕ?",
            "СЕРЁГА: Я им покажу что значит уважение!\nНикто не смеет не платить мне!",
            "ПОРА СОБРАТЬ ДАНИ И НАПОМНИТЬ КТО ТУТ БОСС!",
            "5000 РУБЛЕЙ ИЛИ КРОВЬ... ВЫБОР ЗА НИМИ!",
            "СЕРЁГА: Каждый должен знать своё место\nв этой игре!"
        ]

        mission3_texts = [
            "СЛУХИ О СЕРЁГЕ РАЗНОСЯТСЯ ПО ГОРОДУ...",
            "НОВАЯ БАНДА РЕШИЛА ЗАХВАТИТЬ ЕГО РАЙОН!",
            "СЕРЁГА: Пусть только попробуют!\nЯ им устрою кровавую баню!",
            "ЭТО БУДЕТ САМАЯ ЖЕСТОКАЯ БИТВА...\nВЫЖИВИ 2 МИНУТЫ И СТАНЕШЬ ЛЕГЕНДОЙ!",
            "СЕРЁГА: Они не знают с кем связались!\nЯ покажу им настоящую мощь!"
        ]

        mission4_texts = [
            "СЕРЁГА: Теперь я контролирую район...",
            "НО ЕСТЬ ОДИН ПРОБЛЕМНЫЙ ТИП - БОСС СТАРОЙ БАНДЫ",
            "ОН НЕ ХОЧЕТ УХОДИТЬ И ПЫТАЕТСЯ ВЕРНУТЬ ВЛАСТЬ",
            "СЕРЁГА: Время показать ему кто теперь главный!",
            "УБЕЙ 3 БОССОВ И ДОКАЖИ СВОЮ СИЛУ!",
            "ЭТО БУДЕТ НЕ ЛЕГКО, НО ТЫ СПРАВИШЬСЯ!"
        ]

        mission5_texts = [
            "ФИНАЛЬНАЯ БИТВА! ВСЯ ГОРОДСКАЯ МАФИЯ",
            "ОБЪЕДИНИЛАСЬ ПРОТИВ ТЕБЯ!",
            "СЕРЁГА: Пусть все придут! Я готов!",
            "ВЫЖИВИ 3 МИНУТЫ ПРОТИВ ВСЕХ!",
            "ЕСЛИ ПРОЙДЁШЬ ЭТО - СТАНЕШЬ ЛЕГЕНДОЙ!",
            "НИКТО БОЛЬШЕ НЕ ПОСМЕЕТ БРОСИТЬ ТЕБЕ ВЫЗОВ!"
        ]

        self.missions = [
            Mission("РАЗБОРКА С МЕНТАМИ",
                    "Убери 15 ментов чтобы показать кто в районе хозяин",
                    15, 1500, "kill", mission1_texts),

            Mission("СБОР ДАНИ",
                    "Собери 5000 рублей с врагов",
                    5000, 2000, "collect", mission2_texts),

            Mission("УЛИЧНАЯ ВОЙНА",
                    "Продержись 2 минуты против волн врагов",
                    120, 3000, "survive", mission3_texts),

            Mission("УБИТЬ БОССОВ",
                    "Уничтожь 3 боссов чтобы закрепить власть",
                    3, 4000, "kill", mission4_texts),

            Mission("ФИНАЛЬНАЯ БИТВА",
                    "Выживи 3 минуты против всех врагов",
                    180, 5000, "survive", mission5_texts)
        ]

    def start_mission_cutscene(self, mission_index):
        mission = self.missions[mission_index]
        self.cutscene = Cutscene(mission.cutscene_texts)
        self.state = GameState.CUTSCENE
        # Музыка продолжает играть если она уже играет
        if not pygame.mixer.music.get_busy():
            try:
                pygame.mixer.music.load("music/musicingame.ogg")
                pygame.mixer.music.play(-1)
            except:
                pass

    def complete_mission(self):
        mission = self.missions[self.current_mission_index]
        self.player.money += mission.reward
        self.player.completed_missions += 1
        self.score += mission.reward // 10

        complete_texts = [
            f"ЗАДАЧА ВЫПОЛНЕНА: {mission.title}",
            f"Получено: {mission.reward} рублей",
            "Так держать, братан!\nТвой авторитет растет!"
        ]

        if self.player.completed_missions >= len(self.missions):
            complete_texts.append("ТЫ СТАЛ КОРОЛЁМ РАЙОНА!\nНажми ПРОБЕЛ для победы!")
        else:
            complete_texts.append("Готовься к следующей задаче...")

        self.cutscene = Cutscene(complete_texts, (40, 80, 40), mission_complete=True)
        self.state = GameState.CUTSCENE

    def spawn_enemies(self, count):
        for _ in range(count):
            # Спавн врагов вокруг игрока в открытом мире
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(400, 600)
            x = self.player.x + math.cos(angle) * distance
            y = self.player.y + math.sin(angle) * distance
            
            # Ограничиваем границами мира
            x = max(50, min(self.city.world_size - 50, x))
            y = max(50, min(self.city.world_size - 50, y))

            # Вероятность появления специальных врагов увеличивается с волной
            boss_chance = min(0.1 + self.wave * 0.05, 0.4)
            sniper_chance = min(0.05 + self.wave * 0.03, 0.25) if self.wave >= 2 else 0
            tank_chance = min(0.03 + self.wave * 0.02, 0.2) if self.wave >= 4 else 0
            
            rand = random.random()
            if rand < boss_chance and self.wave >= 3:
                enemy_type = "босс"
            elif rand < boss_chance + sniper_chance and self.wave >= 2:
                enemy_type = "снайпер"
            elif rand < boss_chance + sniper_chance + tank_chance and self.wave >= 4:
                enemy_type = "танк"
            else:
                enemy_type = random.choices(["мент", "быдло", "крыса"],
                                            weights=[0.4, 0.35, 0.25])[0]
            self.enemies.append(Enemy(x, y, enemy_type, self.wave))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSE
                    elif self.state == GameState.PAUSE:
                        self.state = GameState.PLAYING
                    elif self.state == GameState.CONTROLS:
                        self.state = GameState.MAIN_MENU
                    elif self.state == GameState.SHOP:
                        self.state = GameState.PLAYING
                    elif self.state == GameState.SKILLS:
                        self.state = GameState.PLAYING
                    elif self.state in [GameState.GAME_OVER, GameState.WIN]:
                        self.state = GameState.MAIN_MENU
                
                elif self.state == GameState.SHOP:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.shop.selected_item = max(0, self.shop.selected_item - 1)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.shop.selected_item = min(len(self.shop.items) - 1, self.shop.selected_item + 1)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        item = self.shop.items[self.shop.selected_item]
                        success, message = self.shop.buy_item(item, self.player)
                        self.shop_message = message
                        self.shop_message_timer = 120
                
                elif self.state == GameState.SKILLS:
                    if event.key == pygame.K_1:
                        if self.player.skill_points > 0:
                            self.player.skills["damage"] += 1
                            self.player.skill_points -= 1
                            for weapon in self.player.weapons:
                                weapon.damage = int(weapon.damage * 1.1)
                    elif event.key == pygame.K_2:
                        if self.player.skill_points > 0:
                            self.player.skills["health"] += 1
                            self.player.skill_points -= 1
                            self.player.max_health += 15
                            self.player.health += 15
                    elif event.key == pygame.K_3:
                        if self.player.skill_points > 0:
                            self.player.skills["speed"] += 1
                            self.player.skill_points -= 1
                            self.player.speed = min(8, self.player.speed + 0.3)
                    elif event.key == pygame.K_4:
                        if self.player.skill_points > 0:
                            self.player.skills["ammo"] += 1
                            self.player.skill_points -= 1
                            for weapon in self.player.weapons:
                                weapon.max_ammo = int(weapon.max_ammo * 1.15)
                                weapon.ammo = weapon.max_ammo
                    elif event.key == pygame.K_5:
                        if self.player.skill_points > 0:
                            self.player.skills["regen"] += 1
                            self.player.skill_points -= 1

                elif event.key == pygame.K_SPACE:
                    if self.state == GameState.CUTSCENE:
                        # Проверяем какая катсцена активна
                        if self.hotline_cutscene:
                            if self.hotline_cutscene.update(skip=True):
                                # Катсцена Hotline Miami завершена, переходим к миссии
                                self.hotline_cutscene = None
                                self.start_mission_cutscene(0)
                        elif self.cutscene:
                            if self.cutscene.update(9999):
                                if self.cutscene.mission_complete:
                                    self.current_mission_index += 1
                                    if self.current_mission_index < len(self.missions):
                                        self.start_mission_cutscene(self.current_mission_index)
                                    else:
                                        self.state = GameState.WIN
                                else:
                                    self.state = GameState.PLAYING
                                    self.mission_start_time = pygame.time.get_ticks()
                                    # Убеждаемся что музыка играет
                                    if not pygame.mixer.music.get_busy():
                                        try:
                                            pygame.mixer.music.load("music/musicingame.ogg")
                                            pygame.mixer.music.play(-1)
                                        except:
                                            pass

                elif event.key == pygame.K_r and self.state == GameState.PLAYING:
                    # Перезарядка текущего оружия
                    self.player.weapons[self.player.current_weapon].ammo = \
                        self.player.weapons[self.player.current_weapon].max_ammo
                
                elif event.key == pygame.K_u and self.state == GameState.PLAYING:
                    # Меню навыков (открывается всегда, даже без очков)
                    self.state = GameState.SKILLS
                
                elif event.key == pygame.K_e and self.state == GameState.PLAYING:
                    # Вход в магазин (E) в открытом мире
                    location = self.city.get_current_location()
                    shop_world_x = location.world_x
                    shop_world_y = location.world_y
                    dist = math.sqrt((self.player.x - shop_world_x) ** 2 + (self.player.y - shop_world_y) ** 2)
                    if dist < 200:
                        self.state = GameState.SHOP
                
                elif event.key == pygame.K_t and self.state == GameState.PLAYING:
                    # Смена локации (T)
                    self.city.current_location_index = (self.city.current_location_index + 1) % len(self.city.locations)
                    # Эффект перехода
                    for _ in range(50):
                        angle = random.uniform(0, 2 * math.pi)
                        speed = random.uniform(2, 6)
                        self.particles.append(Particle(
                            self.player.x, self.player.y,
                            BLUE,
                            math.cos(angle) * speed,
                            math.sin(angle) * speed,
                            60
                        ))

                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8] and self.state == GameState.PLAYING:
                    weapon_index = event.key - pygame.K_1
                    if weapon_index < len(self.player.weapons):
                        self.player.current_weapon = weapon_index

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # ЛКМ
                    if self.state == GameState.PLAYING:
                        bullet = self.player.shoot()
                        if bullet:
                            self.bullets.append(bullet)
                        self.player.auto_fire = True
                    elif self.state == GameState.MAIN_MENU:
                        # Обработка кликов по кнопкам главного меню
                        mouse_pos = pygame.mouse.get_pos()
                        button_y = 350
                        button_width = 200
                        button_height = 50
                        center_x = SCREEN_WIDTH // 2
                        
                        for i in range(3):
                            btn_x = center_x - button_width // 2
                            btn_y = button_y + i * 80
                            if (btn_x <= mouse_pos[0] <= btn_x + button_width and
                                btn_y <= mouse_pos[1] <= btn_y + button_height):
                                if i == 0:  # НАЧАТЬ ИГРУ
                                    self.start_game()
                                elif i == 1:  # УПРАВЛЕНИЕ
                                    self.state = GameState.CONTROLS
                                elif i == 2:  # ВЫХОД
                                    return False

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.state == GameState.PLAYING:
                    self.player.auto_fire = False

        return True

    def update(self):
        if self.state == GameState.PLAYING:
            dt = self.clock.get_time() / 1000.0

            # Обновление направления игрока по курсору (с учетом камеры)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # Преобразуем координаты экрана в координаты мира
            world_mouse_x = mouse_x + self.city.camera_x
            world_mouse_y = mouse_y + self.city.camera_y
            self.player.update_direction(world_mouse_x, world_mouse_y)

            # Управление движением
            keys = pygame.key.get_pressed()
            dx, dy = 0, 0

            if keys[pygame.K_w] or keys[pygame.K_UP]:
                dy -= 1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                dy += 1
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                dx -= 1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                dx += 1

            if dx != 0 and dy != 0:
                dx *= 0.7071
                dy *= 0.7071

            self.player.move(dx, dy, self.city.world_size)
            
            # Обновление камеры
            self.city.update_camera(self.player.x, self.player.y)
            
            # Проверка перехода между локациями
            self.city.check_location_transition(self.player.x, self.player.y)

            # Автоматическая стрельба
            if self.player.auto_fire:
                bullet = self.player.shoot()
                if bullet:
                    self.bullets.append(bullet)

            # Спавн врагов
            self.enemy_spawn_timer += 1
            current_mission = self.missions[self.current_mission_index]
            max_enemies = 8 + self.wave

            # Увеличиваем частоту спавна с волной
            spawn_rate = max(60, 90 - self.wave * 5)
            if self.enemy_spawn_timer >= spawn_rate and len(self.enemies) < max_enemies:
                spawn_count = 1 if self.wave < 3 else min(2, max_enemies - len(self.enemies))
                self.spawn_enemies(spawn_count)
                self.enemy_spawn_timer = 0

            # Обновление миссии
            if current_mission.type == "survive":
                elapsed = (pygame.time.get_ticks() - self.mission_start_time) / 1000.0
                if current_mission.update_timer(elapsed):
                    self.complete_mission()

            # Обновление пуль
            for bullet in self.bullets[:]:
                if not bullet.update(self.city.world_size):
                    self.bullets.remove(bullet)
                else:
                    # Проверка попадания (используем мировые координаты)
                    hit_enemies = []
                    for enemy in self.enemies[:]:
                        # Используем увеличенный хитбокс для лучшего попадания
                        hitbox_size = max(enemy.size, 30)  # Минимальный размер хитбокса 30
                        dist = math.sqrt((bullet.x - enemy.x) ** 2 + (bullet.y - enemy.y) ** 2)
                        if dist < hitbox_size:
                            hit_enemies.append((enemy, dist))
                    
                    # Обработка взрывных пуль
                    if bullet.type == "explosive" and bullet.lifetime <= 1:
                        # Взрыв
                        explosion_radius = bullet.explosion_radius
                        for enemy in self.enemies[:]:
                            dist = math.sqrt((bullet.x - enemy.x) ** 2 + (bullet.y - enemy.y) ** 2)
                            if dist < explosion_radius:
                                hit_enemies.append((enemy, dist))
                        
                        # Эффект взрыва
                        for _ in range(40):
                            angle = random.uniform(0, 2 * math.pi)
                            speed = random.uniform(3, 10)
                            self.particles.append(Particle(
                                bullet.x, bullet.y,
                                (255, 150, 0),
                                math.cos(angle) * speed,
                                math.sin(angle) * speed,
                                50
                            ))
                    
                    # Обработка попаданий
                    for enemy, dist in hit_enemies:
                        # Урон уменьшается с расстоянием для взрывных пуль
                        damage = bullet.damage
                        is_critical = random.random() < 0.1  # 10% шанс крита
                        if is_critical:
                            damage = int(damage * 1.5)
                        
                        if bullet.type == "explosive":
                            damage = int(damage * (1 - dist / bullet.explosion_radius * 0.5))
                        
                        # Отображение урона (в координатах мира)
                        self.damage_numbers.append(DamageNumber(enemy.x, enemy.y - enemy.size, damage, is_critical))
                        
                        # Тряска экрана при большом уроне
                        if damage > 50:
                            self.screen_shake = 10
                            self.screen_shake_intensity = 5
                        
                        if enemy.take_damage(damage):
                                # Эффект частиц при убийстве
                                for _ in range(15):
                                    angle = random.uniform(0, 2 * math.pi)
                                    speed = random.uniform(2, 6)
                                    self.particles.append(Particle(
                                        enemy.x, enemy.y,
                                        enemy.color,
                                        math.cos(angle) * speed,
                                        math.sin(angle) * speed,
                                        40
                                    ))
                                
                                # Убийство врага
                                self.enemies.remove(enemy)
                                self.player.kills += 1
                                
                                # Добавление в ленту убийств
                                self.kill_feed.append(KillFeedEntry(enemy.type))
                                if len(self.kill_feed) > 5:
                                    self.kill_feed.pop(0)
                                
                                # Комбо система
                                self.player.combo += 1
                                self.player.combo_timer = 180
                                combo_bonus = 1 + (self.player.combo // 5) * 0.1
                                
                                bounty = int(enemy.bounty * combo_bonus)
                                self.player.money += bounty
                                self.score += int(bounty // 2 * combo_bonus)
                                self.player.total_damage_dealt += damage
                                
                                # Опыт за убийство
                                exp_gain = 10 + enemy.level * 5
                                if enemy.type == "босс":
                                    exp_gain *= 3
                                self.player.experience += exp_gain
                                
                                # Проверка повышения уровня
                                while self.player.experience >= self.player.experience_to_next:
                                    self.player.experience -= self.player.experience_to_next
                                    self.player.level += 1
                                    self.player.skill_points += 1
                                    self.player.experience_to_next = int(self.player.experience_to_next * 1.5)
                                    # Восстановление здоровья при повышении уровня
                                    self.player.health = self.player.max_health
                                    # Эффект повышения уровня
                                    for _ in range(50):
                                        angle = random.uniform(0, 2 * math.pi)
                                        speed = random.uniform(2, 8)
                                        self.particles.append(Particle(
                                            self.player.x, self.player.y,
                                            (0, 255, 255),
                                            math.cos(angle) * speed,
                                            math.sin(angle) * speed,
                                            60
                                        ))
                                
                                # Подсчет боссов
                                if enemy.type == "босс":
                                    self.player.bosses_killed += 1
                                elif enemy.type == "снайпер":
                                    self.player.headshots += 1
                                
                                # Кровавые частицы
                                for _ in range(20):
                                    angle = random.uniform(0, 2 * math.pi)
                                    speed = random.uniform(1, 4)
                                    self.particles.append(BloodParticle(
                                        enemy.x, enemy.y,
                                        math.cos(angle) * speed,
                                        math.sin(angle) * speed
                                    ))

                                # Обновление миссий
                                current_mission = self.missions[self.current_mission_index]
                                if current_mission.type == "kill":
                                    if current_mission.title == "РАЗБОРКА С МЕНТАМИ" and enemy.type == "мент":
                                        self.player.mission_kills += 1
                                        if current_mission.update():
                                            self.complete_mission()
                                    elif current_mission.title == "УБИТЬ БОССОВ" and enemy.type == "босс":
                                        self.player.mission_kills += 1
                                        if current_mission.update():
                                            self.complete_mission()
                                elif current_mission.type == "collect":
                                    if current_mission.update(enemy.bounty):
                                        self.complete_mission()

                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
                        if bullet.type != "explosive":
                            break

            # Регенерация здоровья (медленная)
            self.player.regen_timer += 1
            current_time = pygame.time.get_ticks()
            if current_time - self.player.last_damage_time > 5000 and self.player.health < self.player.max_health:
                if self.player.regen_timer >= 180:  # Каждые 3 секунды
                    self.player.health = min(self.player.max_health, self.player.health + 1)
                    self.player.regen_timer = 0
            
            # Обновление комбо
            if self.player.combo_timer > 0:
                self.player.combo_timer -= 1
            else:
                self.player.combo = 0

            # Обновление врагов
            for enemy in self.enemies:
                damage = enemy.update(self.player.x, self.player.y)
                if damage > 0:
                    # Броня снижает урон
                    actual_damage = max(1, damage - self.player.armor // 2)
                    self.player.health -= actual_damage
                    self.player.last_damage_time = current_time
                    self.player.regen_timer = 0

                if self.player.health <= 0:
                    self.state = GameState.GAME_OVER

            # Обновление частиц (в координатах мира)
            for particle in self.particles[:]:
                if not particle.update():
                    self.particles.remove(particle)
                # Ограничиваем частицы границами мира
                particle.x = max(0, min(self.city.world_size, particle.x))
                particle.y = max(0, min(self.city.world_size, particle.y))
            
            # Обновление чисел урона
            for dmg_num in self.damage_numbers[:]:
                if not dmg_num.update():
                    self.damage_numbers.remove(dmg_num)
            
            # Обновление ленты убийств
            for kill_entry in self.kill_feed[:]:
                if not kill_entry.update():
                    self.kill_feed.remove(kill_entry)
            
            # Обновление тряски экрана
            if self.screen_shake > 0:
                self.screen_shake -= 1
                self.screen_shake_intensity *= 0.9

            # Проверка близости к магазину в открытом мире
            location = self.city.get_current_location()
            shop_world_x = location.world_x
            shop_world_y = location.world_y
            dist_to_shop = math.sqrt((self.player.x - shop_world_x) ** 2 + (self.player.y - shop_world_y) ** 2)
            if dist_to_shop < 200:  # Радиус входа в магазин
                # Показываем подсказку о входе в магазин
                pass

            # Смена волны
            if self.player.kills >= self.wave * 10:
                self.wave += 1
                # Восстановление здоровья при смене волны
                self.player.health = min(self.player.max_health, self.player.health + 20)
                # Эффект при смене волны
                for _ in range(30):
                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(3, 8)
                    self.particles.append(Particle(
                        self.player.x, self.player.y,
                        GOLD,
                        math.cos(angle) * speed,
                        math.sin(angle) * speed,
                        50
                    ))
        
        # Обновление сообщения магазина
        if self.shop_message_timer > 0:
            self.shop_message_timer -= 1
        
        # Проверка достижений (только в игре)
        if self.state == GameState.PLAYING:
            for achievement in self.achievements:
                if achievement.check(self.player, self):
                    self.current_achievement_notification = achievement
                    self.achievement_notification_timer = 180
        
        # Обновление таймера достижения
        if self.achievement_notification_timer > 0:
            self.achievement_notification_timer -= 1
            if self.achievement_notification_timer == 0:
                self.current_achievement_notification = None
        
        # Обновление времени игры
        if self.state == GameState.PLAYING:
            self.player.time_played += dt

    def draw_minimap(self):
        # Мини-карта открытого мира
        minimap_size = 200
        minimap_x = SCREEN_WIDTH - minimap_size - 10
        minimap_y = SCREEN_HEIGHT - minimap_size - 10
        
        # Фон мини-карты
        minimap_surface = pygame.Surface((minimap_size, minimap_size), pygame.SRCALPHA)
        minimap_surface.fill((0, 0, 0, 180))
        self.screen.blit(minimap_surface, (minimap_x, minimap_y))
        pygame.draw.rect(self.screen, WHITE, (minimap_x, minimap_y, minimap_size, minimap_size), 2)
        
        # Масштаб для открытого мира
        scale = minimap_size / self.city.world_size
        
        # Все локации на карте
        for i, loc in enumerate(self.city.locations):
            loc_map_x = minimap_x + int(loc.world_x * scale)
            loc_map_y = minimap_y + int(loc.world_y * scale)
            if minimap_x <= loc_map_x <= minimap_x + minimap_size and minimap_y <= loc_map_y <= minimap_y + minimap_size:
                color = GOLD if i == self.city.current_location_index else LIGHT_GREY
                size = 6 if i == self.city.current_location_index else 4
                pygame.draw.circle(self.screen, color, (loc_map_x, loc_map_y), size)
        
        # Игрок на карте
        player_map_x = minimap_x + int(self.player.x * scale)
        player_map_y = minimap_y + int(self.player.y * scale)
        if minimap_x <= player_map_x <= minimap_x + minimap_size and minimap_y <= player_map_y <= minimap_y + minimap_size:
            pygame.draw.circle(self.screen, GREEN, (player_map_x, player_map_y), 5)
            # Направление взгляда
            dir_x = player_map_x + int(math.cos(self.player.direction) * 8)
            dir_y = player_map_y + int(math.sin(self.player.direction) * 8)
            pygame.draw.line(self.screen, GREEN, (player_map_x, player_map_y), (dir_x, dir_y), 2)
        
        # Враги на карте
        for enemy in self.enemies:
            enemy_map_x = minimap_x + int(enemy.x * scale)
            enemy_map_y = minimap_y + int(enemy.y * scale)
            if minimap_x <= enemy_map_x <= minimap_x + minimap_size and minimap_y <= enemy_map_y <= minimap_y + minimap_size:
                color = RED if enemy.type == "босс" else (200, 100, 100)
                pygame.draw.circle(self.screen, color, (enemy_map_x, enemy_map_y), 2)
        
        # Магазин на карте
        location = self.city.get_current_location()
        shop_map_x = minimap_x + int(location.world_x * scale)
        shop_map_y = minimap_y + int(location.world_y * scale)
        if minimap_x <= shop_map_x <= minimap_x + minimap_size and minimap_y <= shop_map_y <= minimap_y + minimap_size:
            pygame.draw.rect(self.screen, GOLD, (shop_map_x - 3, shop_map_y - 3, 6, 6))
        
        # Название текущей локации
        loc_name = small_font.render(location.name, True, GOLD)
        self.screen.blit(loc_name, (minimap_x, minimap_y - 20))

    def draw_crosshair(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Улучшенный прицел с эффектами
        size = 15
        
        # Свечение прицела
        crosshair_glow = pygame.Surface((size * 2 + 20, size * 2 + 20), pygame.SRCALPHA)
        for radius in range(size + 10, 0, -2):
            alpha = int(50 * (1 - radius / (size + 10)))
            pygame.draw.circle(crosshair_glow, (*RED[:3], alpha), (size + 10, size + 10), radius)
        self.screen.blit(crosshair_glow, (mouse_x - size - 10, mouse_y - size - 10))
        
        # Внешние линии с градиентом
        line_length = 8
        for i in range(line_length):
            alpha = 255 - i * 20
            color = (255, int(200 - i * 10), int(200 - i * 10))
            # Верх
            pygame.draw.line(self.screen, color, 
                           (mouse_x, mouse_y - size + i), 
                           (mouse_x, mouse_y - size + i + 1), 2)
            # Низ
            pygame.draw.line(self.screen, color, 
                           (mouse_x, mouse_y + size - i), 
                           (mouse_x, mouse_y + size - i - 1), 2)
            # Лево
            pygame.draw.line(self.screen, color, 
                           (mouse_x - size + i, mouse_y), 
                           (mouse_x - size + i + 1, mouse_y), 2)
            # Право
            pygame.draw.line(self.screen, color, 
                           (mouse_x + size - i, mouse_y), 
                           (mouse_x + size - i - 1, mouse_y), 2)
        
        # Центральный круг с эффектом
        pygame.draw.circle(self.screen, RED, (mouse_x, mouse_y), 6, 2)
        pygame.draw.circle(self.screen, (255, 150, 150), (mouse_x, mouse_y), 4, 1)
        pygame.draw.circle(self.screen, (255, 255, 255), (mouse_x, mouse_y), 2)
        pygame.draw.circle(self.screen, RED, (mouse_x, mouse_y), 1)

    def draw_ui(self):
        # Полоса здоровья
        health_width = (self.player.health / self.player.max_health) * 200
        pygame.draw.rect(self.screen, DARK_GREY, (10, 10, 204, 24))
        pygame.draw.rect(self.screen, RED, (12, 12, health_width, 20))
        pygame.draw.rect(self.screen, WHITE, (10, 10, 204, 24), 2)

        health_text = small_font.render(f"ЗДОРОВЬЕ: {self.player.health}", True, WHITE)
        self.screen.blit(health_text, (220, 12))

        # Оружие
        weapon = self.player.weapons[self.player.current_weapon]
        ammo_text = small_font.render(f"{weapon.name}: {weapon.ammo}/{weapon.max_ammo}", True, weapon.color)
        self.screen.blit(ammo_text, (10, 40))
        
        # Индикатор выбранного оружия
        for i, w in enumerate(self.player.weapons):
            color = GOLD if i == self.player.current_weapon else LIGHT_GREY
            weapon_indicator = small_font.render(f"{i+1}: {w.name[:3]}", True, color)
            self.screen.blit(weapon_indicator, (10 + i * 80, 115))

        # Ресурсы
        money_text = small_font.render(f"БАБЛО: {self.player.money} РУБ.", True, GOLD)
        self.screen.blit(money_text, (10, 65))

        wave_text = small_font.render(f"ВОЛНА: {self.wave}", True, BLUE)
        self.screen.blit(wave_text, (10, 90))

        # Миссия
        if self.current_mission_index < len(self.missions):
            mission = self.missions[self.current_mission_index]
            if mission.type == "survive":
                elapsed = (pygame.time.get_ticks() - self.mission_start_time) / 1000.0
                progress = f"{int(elapsed)}/{mission.target} сек"
            elif mission.type == "kill":
                progress = f"{self.player.mission_kills}/{mission.target}"
            else:
                progress = f"{mission.current}/{mission.target}"

            mission_text = small_font.render(f"ЗАДАЧА: {mission.title} - {progress}", True, GREEN)
            self.screen.blit(mission_text, (SCREEN_WIDTH - 300, 10))

        # Прогресс
        progress_text = small_font.render(f"ВЫПОЛНЕНО: {self.player.completed_missions}/{len(self.missions)}", True,
                                          WHITE)
        self.screen.blit(progress_text, (SCREEN_WIDTH - 300, 35))

        # Счет
        score_text = small_font.render(f"СЧЕТ: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH - 150, 10))

        # Управление
        controls = [
            "WASD - ДВИЖЕНИЕ",
            "ЛКМ - ОГОНЬ (ЗАЖАТЬ)",
            "1-8 - ОРУЖИЕ",
            "R - ПЕРЕЗАРЯДКА",
            "E - МАГАЗИН",
            "T - СМЕНА ЛОКАЦИИ",
            "U - НАВЫКИ",
            "ESC - ПАУЗА"
        ]

        for i, control in enumerate(controls):
            text = small_font.render(control, True, LIGHT_GREY)
            self.screen.blit(text, (SCREEN_WIDTH - 150, 60 + i * 20))
        
        # Подсказка о входе в магазин в открытом мире
        location = self.city.get_current_location()
        shop_world_x = location.world_x
        shop_world_y = location.world_y
        dist = math.sqrt((self.player.x - shop_world_x) ** 2 + (self.player.y - shop_world_y) ** 2)
        if dist < 200:
            hint_text = small_font.render("НАЖМИ E ДЛЯ ВХОДА В МАГАЗИН", True, GOLD)
            self.screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, SCREEN_HEIGHT - 150))
        
        # Сообщение магазина
        if self.shop_message_timer > 0:
            msg_text = small_font.render(self.shop_message, True, GREEN if "Куплено" in self.shop_message or "увелич" in self.shop_message else RED)
            self.screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, SCREEN_HEIGHT - 120))
        
        # Название локации
        location_text = small_font.render(f"ЛОКАЦИЯ: {location.name}", True, BLUE)
        self.screen.blit(location_text, (SCREEN_WIDTH - 300, 60))
        
        # Статистика
        stats_text = small_font.render(f"УБИТО: {self.player.kills} | БОССОВ: {self.player.bosses_killed}", True, WHITE)
        self.screen.blit(stats_text, (SCREEN_WIDTH - 300, 85))
        
        # Комбо
        if self.player.combo > 0:
            combo_text = small_font.render(f"КОМБО x{self.player.combo}!", True, GOLD)
            combo_alpha = min(255, int(255 * (self.player.combo_timer / 60)))
            self.screen.blit(combo_text, (SCREEN_WIDTH // 2 - combo_text.get_width() // 2, 200))
        
        # Броня
        if self.player.armor > 0:
            armor_text = small_font.render(f"БРОНЯ: {self.player.armor}", True, BLUE)
            self.screen.blit(armor_text, (10, 140))
        
        # Уровень и опыт
        level_text = small_font.render(f"УРОВЕНЬ: {self.player.level}", True, (0, 255, 255))
        self.screen.blit(level_text, (10, 165))
        
        exp_progress = self.player.experience / self.player.experience_to_next
        exp_bar_width = 150
        pygame.draw.rect(self.screen, DARK_GREY, (10, 185, exp_bar_width + 4, 12))
        pygame.draw.rect(self.screen, (0, 255, 255), (12, 187, int(exp_bar_width * exp_progress), 8))
        pygame.draw.rect(self.screen, WHITE, (10, 185, exp_bar_width + 4, 12), 1)
        
        exp_text = small_font.render(f"{self.player.experience}/{self.player.experience_to_next} ОПЫТ", True, WHITE)
        self.screen.blit(exp_text, (170, 183))
        
        # Очки навыков
        if self.player.skill_points > 0:
            skill_text = small_font.render(f"ОЧКИ НАВЫКОВ: {self.player.skill_points} (нажми U)", True, GOLD)
            self.screen.blit(skill_text, (10, 205))
        
        # Достижения
        unlocked_count = sum(1 for a in self.achievements if a.unlocked)
        achievements_text = small_font.render(f"ДОСТИЖЕНИЯ: {unlocked_count}/{len(self.achievements)}", True, GOLD)
        self.screen.blit(achievements_text, (SCREEN_WIDTH - 300, 110))

    def draw_main_menu(self):
        self.screen.fill(DARK_GREY)

        # Анимированный заголовок
        pulse = math.sin(pygame.time.get_ticks() * 0.003) * 5
        title = title_font.render("БРАТВА: УЛИЦЫ СТОЛИЦЫ", True, GOLD)
        shadow = title_font.render("БРАТВА: УЛИЦЫ СТОЛИЦЫ", True, (100, 80, 0))

        self.screen.blit(shadow, (SCREEN_WIDTH // 2 - title.get_width() // 2 + 3, 153 + pulse))
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150 + pulse))

        # Подзаголовок
        subtitle = menu_font.render("ЭПИЧЕСКИЙ РЕМАСТЕР В СТИЛЕ RDR2!", True, WHITE)
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 230))

        # Кнопки
        button_y = 350
        buttons = [
            ("НАЧАТЬ ИГРУ", self.start_game),
            ("УПРАВЛЕНИЕ", self.show_controls),
            ("ВЫХОД", sys.exit)
        ]

        mouse_pos = pygame.mouse.get_pos()
        for i, (text, action) in enumerate(buttons):
            color = GOLD if (mouse_pos[0] > SCREEN_WIDTH // 2 - 100 and mouse_pos[0] < SCREEN_WIDTH // 2 + 100 and
                             mouse_pos[1] > button_y + i * 80 and mouse_pos[1] < button_y + i * 80 + 50) else LIGHT_GREY

            pygame.draw.rect(self.screen, color, (SCREEN_WIDTH // 2 - 100, button_y + i * 80, 200, 50))
            pygame.draw.rect(self.screen, WHITE, (SCREEN_WIDTH // 2 - 100, button_y + i * 80, 200, 50), 2)

            btn_text = menu_font.render(text, True, BLACK)
            self.screen.blit(btn_text, (SCREEN_WIDTH // 2 - btn_text.get_width() // 2, button_y + i * 80 + 10))

    def show_controls(self):
        self.screen.fill(DARK_GREY)

        title = title_font.render("УПРАВЛЕНИЕ", True, GOLD)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        controls = [
            "W, A, S, D / СТРЕЛКИ - ПЕРЕДВИЖЕНИЕ",
            "ЛЕВАЯ КНОПКА МЫШИ - ОГОНЬ (ЗАЖАТЬ ДЛЯ АВТО)",
            "1-8 - ВЫБОР ОРУЖИЯ",
            "U - МЕНЮ НАВЫКОВ",
            "R - ПЕРЕЗАРЯДКА",
            "ESC - ПАУЗА / МЕНЮ",
            "ПРОБЕЛ - ПРОПУСК ДИАЛОГОВ"
        ]

        for i, control in enumerate(controls):
            text = dialog_font.render(control, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 200 + i * 40))

        back_text = small_font.render("Нажми ESC для возврата", True, LIGHT_GREY)
        self.screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, SCREEN_HEIGHT - 100))

    def draw_game(self):
        # Применение тряски экрана
        shake_x = 0
        shake_y = 0
        if self.screen_shake > 0:
            shake_x = random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity)
            shake_y = random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity)
        
        # Создание поверхности для отрисовки с тряской
        if abs(shake_x) > 0.1 or abs(shake_y) > 0.1:
            game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            game_surface.fill(BLACK)
        else:
            game_surface = self.screen
        
        # Отрисовка открытого мира
        self.city.draw(game_surface, self.player.x, self.player.y)

        # Отрисовка врагов (с учётом камеры)
        for enemy in self.enemies:
            enemy_screen_x = enemy.x - self.city.camera_x
            enemy_screen_y = enemy.y - self.city.camera_y
            old_ex, old_ey = enemy.x, enemy.y
            enemy.x, enemy.y = enemy_screen_x, enemy_screen_y
            enemy.draw(game_surface)
            enemy.x, enemy.y = old_ex, old_ey

        # Отрисовка пуль (с учётом камеры)
        for bullet in self.bullets:
            bullet_screen_x = bullet.x - self.city.camera_x
            bullet_screen_y = bullet.y - self.city.camera_y
            old_bx, old_by = bullet.x, bullet.y
            bullet.x, bullet.y = bullet_screen_x, bullet_screen_y
            bullet.draw(game_surface)
            bullet.x, bullet.y = old_bx, old_by

        # Отрисовка частиц (с учётом камеры)
        for particle in self.particles:
            particle_screen_x = particle.x - self.city.camera_x
            particle_screen_y = particle.y - self.city.camera_y
            old_px, old_py = particle.x, particle.y
            particle.x, particle.y = particle_screen_x, particle_screen_y
            particle.draw(game_surface)
            particle.x, particle.y = old_px, old_py
        
        # Отрисовка чисел урона (с учётом камеры)
        for dmg_num in self.damage_numbers:
            dmg_screen_x = dmg_num.x - self.city.camera_x
            dmg_screen_y = dmg_num.y - self.city.camera_y
            old_dx, old_dy = dmg_num.x, dmg_num.y
            dmg_num.x, dmg_num.y = dmg_screen_x, dmg_screen_y
            dmg_num.draw(game_surface)
            dmg_num.x, dmg_num.y = old_dx, old_dy
        
        # Отрисовка игрока (с учётом камеры)
        player_screen_x = self.player.x - self.city.camera_x
        player_screen_y = self.player.y - self.city.camera_y
        
        # Сохраняем оригинальные координаты
        old_x, old_y = self.player.x, self.player.y
        self.player.x, self.player.y = player_screen_x, player_screen_y
        self.player.draw(game_surface)
        self.player.x, self.player.y = old_x, old_y
        
        # Применение тряски к экрану
        if abs(shake_x) > 0.1 or abs(shake_y) > 0.1:
            self.screen.blit(game_surface, (int(shake_x), int(shake_y)))
        
        # Отрисовка ленты убийств (поверх всего)
        for i, kill_entry in enumerate(self.kill_feed):
            kill_entry.draw(self.screen, SCREEN_HEIGHT - 200 - i * 25)

        # Прицел
        self.draw_crosshair()
        
        # Мини-карта
        self.draw_minimap()

        # Интерфейс
        self.draw_ui()
        
        # Уведомление о достижении
        if self.current_achievement_notification and self.achievement_notification_timer > 0:
            alpha = min(255, int(255 * (self.achievement_notification_timer / 60)))
            achievement = self.current_achievement_notification
            
            # Фон уведомления
            notification_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, 50, 500, 100)
            s = pygame.Surface((500, 100), pygame.SRCALPHA)
            s.fill((0, 0, 0, alpha))
            self.screen.blit(s, (SCREEN_WIDTH // 2 - 250, 50))
            pygame.draw.rect(self.screen, GOLD, notification_rect, 3)
            
            # Текст достижения
            title_text = menu_font.render("ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО!", True, GOLD)
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 60))
            
            name_text = dialog_font.render(achievement.name, True, WHITE)
            self.screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, 100))

    def draw_pause(self):
        self.draw_game()

        # Затемнение
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        self.screen.blit(s, (0, 0))

        # Меню паузы
        pause_text = title_font.render("ПАУЗА", True, GOLD)
        self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 200))

        options = [
            "ПРОДОЛЖИТЬ (ESC)",
            "В ГЛАВНОЕ МЕНЮ"
        ]

        mouse_pos = pygame.mouse.get_pos()
        for i, option in enumerate(options):
            color = GOLD if (mouse_pos[0] > SCREEN_WIDTH // 2 - 150 and mouse_pos[0] < SCREEN_WIDTH // 2 + 150 and
                             mouse_pos[1] > 300 + i * 70 and mouse_pos[1] < 300 + i * 70 + 50) else WHITE

            text = menu_font.render(option, True, color)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 300 + i * 70))

    def draw_game_over(self):
        self.screen.fill(BLACK)

        game_over = title_font.render("ТЕБЯ ЗАКОНСИЛИЛИ!", True, RED)
        self.screen.blit(game_over, (SCREEN_WIDTH // 2 - game_over.get_width() // 2, 200))

        stats = [
            f"Волна: {self.wave}",
            f"Убито врагов: {self.player.kills}",
            f"Выполнено задач: {self.player.completed_missions}",
            f"Заработано: {self.player.money} рублей",
            f"Финальный счет: {self.score}"
        ]

        for i, stat in enumerate(stats):
            text = menu_font.render(stat, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 300 + i * 50))

        restart = menu_font.render("Нажми R для рестарта или ESC в меню", True, LIGHT_GREY)
        self.screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, 600))

    def draw_win(self):
        self.screen.fill(DARK_GREY)

        win = title_font.render("ПОБЕДА! ТЫ КОРОЛЬ РАЙОНА!", True, GOLD)
        self.screen.blit(win, (SCREEN_WIDTH // 2 - win.get_width() // 2, 150))

        stats = [
            "Ты прошел все испытания и стал",
            "настоящим хозяином улиц!",
            "",
            f"ФИНАЛЬНАЯ СТАТИСТИКА:",
            f"Волна: {self.wave}",
            f"Убито врагов: {self.player.kills}",
            f"Заработано: {self.player.money} рублей",
            f"Финальный счет: {self.score}",
            "",
            "Уважение тебе обеспечено!"
        ]

        for i, stat in enumerate(stats):
            color = GOLD if i == 3 else WHITE
            text = dialog_font.render(stat, True, color)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 250 + i * 35))

        restart = menu_font.render("Нажми R для новой игры или ESC в меню", True, LIGHT_GREY)
        self.screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, 600))
    
    def draw_skills_menu(self):
        # Фон меню навыков
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Заголовок
        title = title_font.render("НАВЫКИ", True, GOLD)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        # Очки навыков
        points_text = menu_font.render(f"ОЧКИ НАВЫКОВ: {self.player.skill_points}", True, GOLD)
        self.screen.blit(points_text, (SCREEN_WIDTH // 2 - points_text.get_width() // 2, 120))
        
        # Список навыков
        skills_list = [
            ("1 - УРОН", f"Уровень: {self.player.skills['damage']}", "Увеличивает урон всех оружий на 10%"),
            ("2 - ЗДОРОВЬЕ", f"Уровень: {self.player.skills['health']}", "Увеличивает максимальное здоровье на 15"),
            ("3 - СКОРОСТЬ", f"Уровень: {self.player.skills['speed']}", "Увеличивает скорость передвижения"),
            ("4 - ПАТРОНЫ", f"Уровень: {self.player.skills['ammo']}", "Увеличивает размер магазина на 15%"),
            ("5 - РЕГЕНЕРАЦИЯ", f"Уровень: {self.player.skills['regen']}", "Ускоряет восстановление здоровья"),
        ]
        
        start_y = 200
        for i, (key, level, desc) in enumerate(skills_list):
            y_pos = start_y + i * 80
            
            # Фон навыка (меняем цвет если нет очков)
            bg_color = DARK_GREY if self.player.skill_points > 0 else (30, 30, 30)
            border_color = GOLD if self.player.skill_points > 0 else LIGHT_GREY
            pygame.draw.rect(self.screen, bg_color, (SCREEN_WIDTH // 2 - 300, y_pos, 600, 70))
            pygame.draw.rect(self.screen, border_color, (SCREEN_WIDTH // 2 - 300, y_pos, 600, 70), 2)
            
            # Текст
            key_text = dialog_font.render(key, True, WHITE)
            self.screen.blit(key_text, (SCREEN_WIDTH // 2 - 280, y_pos + 10))
            
            level_text = small_font.render(level, True, GOLD)
            self.screen.blit(level_text, (SCREEN_WIDTH // 2 - 280, y_pos + 35))
            
            desc_text = small_font.render(desc, True, LIGHT_GREY)
            self.screen.blit(desc_text, (SCREEN_WIDTH // 2 - 280, y_pos + 50))
            
            # Показываем статус доступности
            if self.player.skill_points == 0:
                no_points_text = small_font.render("Нет очков навыков", True, RED)
                self.screen.blit(no_points_text, (SCREEN_WIDTH // 2 + 200, y_pos + 35))
        
        # Подсказка
        if self.player.skill_points > 0:
            hint = small_font.render("Нажми 1-5 для улучшения навыка | ESC - выход", True, LIGHT_GREY)
        else:
            hint = small_font.render("Нет очков навыков! Получайте опыт за убийства | ESC - выход", True, RED)
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 80))

    def start_game(self):
        # Начинаем с катсцены в стиле Hotline Miami
        self.hotline_cutscene = HotlineCutscene()
        self.state = GameState.CUTSCENE
        self.player = Player()
        # Размещаем игрока в центре текущей локации
        current_loc = self.city.get_current_location()
        self.player.x = current_loc.world_x
        self.player.y = current_loc.world_y
        self.enemies = []
        self.bullets = []
        self.particles = []
        self.damage_numbers = []
        self.kill_feed = []
        self.score = 0
        self.wave = 1
        self.current_mission_index = 0
        self.enemy_spawn_timer = 0
        self.player.completed_missions = 0
        self.player.mission_kills = 0
        # Инициализируем камеру
        self.city.update_camera(self.player.x, self.player.y)

    def run(self):
        running = True

        while running:
            running = self.handle_events()

            # Обновление игры только если не в паузе или меню
            if self.state == GameState.PLAYING:
                self.update()
            elif self.state == GameState.CUTSCENE and self.hotline_cutscene:
                # Обновление катсцены Hotline Miami (только анимация, без пропуска)
                if self.hotline_cutscene.update(skip=False):
                    # Катсцена завершена автоматически
                    self.hotline_cutscene = None
                    self.start_mission_cutscene(0)

            # Отрисовка
            if self.state == GameState.MAIN_MENU:
                self.draw_main_menu()
            elif self.state == GameState.PLAYING:
                self.draw_game()
            elif self.state == GameState.CUTSCENE:
                if self.hotline_cutscene:
                    self.hotline_cutscene.draw(self.screen)
                elif self.cutscene:
                    self.cutscene.draw(self.screen)
            elif self.state == GameState.PAUSE:
                self.draw_pause()
            elif self.state == GameState.GAME_OVER:
                self.draw_game_over()
            elif self.state == GameState.WIN:
                self.draw_win()
            elif self.state == GameState.CONTROLS:
                self.show_controls()
            elif self.state == GameState.SHOP:
                self.draw_game()
                self.shop.draw(self.screen, self.player)
            elif self.state == GameState.SKILLS:
                self.draw_game()
                self.draw_skills_menu()

            # Обработка кликов в меню паузы
            if self.state == GameState.PAUSE:
                mouse_pos = pygame.mouse.get_pos()
                if pygame.mouse.get_pressed()[0]:
                    # Продолжить
                    if (mouse_pos[0] > SCREEN_WIDTH // 2 - 150 and mouse_pos[0] < SCREEN_WIDTH // 2 + 150 and
                        mouse_pos[1] > 300 and mouse_pos[1] < 350):
                        self.state = GameState.PLAYING
                    # В главное меню
                    elif (mouse_pos[0] > SCREEN_WIDTH // 2 - 150 and mouse_pos[0] < SCREEN_WIDTH // 2 + 150 and
                          mouse_pos[1] > 370 and mouse_pos[1] < 420):
                        self.state = GameState.MAIN_MENU

            # Обработка рестарта
            keys = pygame.key.get_pressed()
            if self.state in [GameState.GAME_OVER, GameState.WIN] and keys[pygame.K_r]:
                self.start_game()

            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()


# Запуск игры
if __name__ == "__main__":
    game = Game()
    game.run()