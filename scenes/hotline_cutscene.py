"""
Катсцена в стиле Hotline Miami
"""
import pygame
import math
import random
from game.config import SCREEN_WIDTH, SCREEN_HEIGHT, BASE_WIDTH, BASE_HEIGHT, GOLD, WHITE, LIGHT_GREY, RED, menu_font, dialog_font, small_font
from game.sprites.enemy_sprite_manager import EnemySpriteManager


class HotlineCutscene:
    def __init__(self):
        self.car_image = None
        self.music = None
        self.load_assets()
        self.phase = 0  # 0 - машина подъезжает, 1 - выход персонажа, 2 - менты подходят, 3 - диалог
        # Используем базовое разрешение для позиций (независимо от реального разрешения)
        self.car_x = -300
        self.car_y = BASE_HEIGHT // 2 - 50
        self.car_speed = 3  # Скорость в пикселях за кадр (независимо от разрешения)
        self.player_exit_x = BASE_WIDTH // 2
        self.player_exit_y = BASE_HEIGHT // 2 + 50
        self.player_exit_progress = 0
        self.ment_x = BASE_WIDTH + 100
        self.ment_y = BASE_HEIGHT // 2
        self.ment_speed = 2  # Скорость в пикселях за кадр (независимо от разрешения)
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
            if self.car_x >= BASE_WIDTH // 2 - 100:
                self.car_x = BASE_WIDTH // 2 - 100
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
            if self.ment_x <= BASE_WIDTH // 2 + 150:
                self.ment_x = BASE_WIDTH // 2 + 150
                if self.timer > 120:  # Пауза перед диалогом
                    self.phase = 3
                    self.dialog_active = True
                    self.dialog_text = self.dialogs[0]
                    self.dialog_index = 0
                    self.waiting_for_input = True
                    self.timer = 0
        
        elif self.phase == 3:  # Диалог с выбором
            if skip:
                # Переход к следующему диалогу (ПРОБЕЛ всегда работает в фазе диалога)
                self.dialog_index += 1
                if self.dialog_index >= len(self.dialogs):
                    return True  # Катсцена завершена
                self.dialog_text = self.dialogs[self.dialog_index]
                self.timer = 0
                self.waiting_for_input = True
        
        return False
    
    def draw(self, screen):
        # Рисуем в базовом разрешении для правильного масштабирования
        # Фон улицы ночью
        screen.fill((20, 20, 30))
        
        # Здания на фоне
        for i in range(5):
            x = i * 200
            height = 200 + (i % 3) * 50
            pygame.draw.rect(screen, (40, 40, 50), (x, BASE_HEIGHT - height, 150, height))
            # Окна
            for wy in range(BASE_HEIGHT - height + 20, BASE_HEIGHT - 40, 30):
                for wx in range(x + 20, x + 130, 40):
                    lit = random.random() > 0.5
                    color = (255, 255, 150) if lit else (60, 60, 80)
                    pygame.draw.rect(screen, color, (wx, wy, 25, 20))
        
        # Дорога
        pygame.draw.rect(screen, (30, 30, 40), (0, BASE_HEIGHT - 100, BASE_WIDTH, 100))
        # Разметка (анимированная)
        offset = (self.timer * 2) % 80
        for i in range(-80, BASE_WIDTH + 80, 80):
            pygame.draw.rect(screen, (200, 200, 100), (i + offset, BASE_HEIGHT - 50, 40, 4))
        
        # Фонари на столбах
        for i in range(0, BASE_WIDTH, 250):
            # Столб
            pygame.draw.rect(screen, (60, 60, 60), (i, BASE_HEIGHT - 200, 8, 100))
            # Фонарь
            light_intensity = 0.7 + 0.3 * math.sin(self.timer * 0.1)
            light_color = tuple(int(255 * light_intensity) for _ in range(3))
            pygame.draw.circle(screen, light_color, (i + 4, BASE_HEIGHT - 200), 15)
            # Свет от фонаря
            light_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
            for radius in range(50, 0, -5):
                alpha = int(30 * (1 - radius / 50))
                pygame.draw.circle(light_surface, (*light_color[:3], alpha), (50, 50), radius)
            screen.blit(light_surface, (i - 50, BASE_HEIGHT - 250))
        
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
            dialog_x = BASE_WIDTH // 2 - dialog_width // 2
            dialog_y = BASE_HEIGHT - 200
            
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
        
        # Подсказка для продолжения (только в фазе диалога)
        if self.phase == 3:
            if pygame.time.get_ticks() % 1000 < 500:
                hint = small_font.render("Нажми ПРОБЕЛ чтобы продолжить диалог", True, GOLD)
                screen.blit(hint, (BASE_WIDTH // 2 - hint.get_width() // 2, BASE_HEIGHT - 50))
        
        # Индикатор музыки
        if not self.music_loaded:
            music_hint = small_font.render("Музыка не найдена (music/musicingame.ogg)", True, LIGHT_GREY)
            screen.blit(music_hint, (10, BASE_HEIGHT - 30))

