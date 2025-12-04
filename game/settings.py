"""
Класс настроек игры
"""
import pygame
from game.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BASE_WIDTH, BASE_HEIGHT,
    GOLD, WHITE, LIGHT_GREY, DARK_GREY, BLACK, RED, GREEN, BLUE,
    title_font, menu_font, dialog_font, small_font
)


class Settings:
    def __init__(self):
        self.fullscreen = True
        self.music_volume = 0.7
        self.cutscene_skip_enabled = True
        self.selected_option = 0
        
    def draw(self, screen):
        """Отрисовка меню настроек с улучшенным дизайном"""
        # Градиентный фон
        for y in range(SCREEN_HEIGHT):
            progress = y / SCREEN_HEIGHT
            r = int(20 + (40 - 20) * progress)
            g = int(10 + (30 - 10) * progress)
            b = int(30 + (50 - 30) * progress)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Декоративные элементы на фоне
        import math
        time = pygame.time.get_ticks() / 1000.0
        for i in range(5):
            x = SCREEN_WIDTH // 2 + math.sin(time + i) * 100
            y = 150 + i * 150
            alpha = int(30 + math.sin(time * 2 + i) * 20)
            glow_surf = pygame.Surface((200, 200), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 200, 255, alpha), (100, 100), 100)
            screen.blit(glow_surf, (x - 100, y - 100))
        
        # Заголовок с эффектом свечения
        title = title_font.render("НАСТРОЙКИ", True, GOLD)
        title_shadow = title_font.render("НАСТРОЙКИ", True, (100, 80, 0))
        
        # Эффект пульсации
        pulse = math.sin(time * 2) * 3
        title_x = SCREEN_WIDTH // 2 - title.get_width() // 2
        title_y = 80 + pulse
        
        # Тень
        screen.blit(title_shadow, (title_x + 4, title_y + 4))
        # Основной текст
        screen.blit(title, (title_x, title_y))
        
        # Декоративная линия под заголовком
        line_y = title_y + title.get_height() + 20
        pygame.draw.line(screen, GOLD, (SCREEN_WIDTH // 2 - 200, line_y), 
                        (SCREEN_WIDTH // 2 + 200, line_y), 3)
        
        # Опции настроек
        settings_y = 220
        settings = [
            {
                "name": "ПОЛНОЭКРАННЫЙ РЕЖИМ",
                "value": self.fullscreen,
                "type": "bool",
                "icon": "🖥️"
            },
            {
                "name": "ПРОПУСК КАТСЦЕН",
                "value": self.cutscene_skip_enabled,
                "type": "bool",
                "icon": "⏭️"
            },
            {
                "name": "ГРОМКОСТЬ МУЗЫКИ",
                "value": self.music_volume,
                "type": "slider",
                "icon": "🔊"
            }
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        
        for i, setting in enumerate(settings):
            is_selected = i == self.selected_option
            option_y = settings_y + i * 90
            
            # Определяем позицию и размер опции
            option_width = 600
            option_height = 70
            option_x = SCREEN_WIDTH // 2 - option_width // 2
            
            # Проверка наведения мыши
            is_hovered = (option_x <= mouse_pos[0] <= option_x + option_width and
                         option_y <= mouse_pos[1] <= option_y + option_height)
            
            # Фон опции с градиентом
            option_surface = pygame.Surface((option_width, option_height), pygame.SRCALPHA)
            
            if is_selected or is_hovered:
                # Градиент для выбранной/наведённой опции
                for j in range(option_height):
                    progress = j / option_height
                    r = int(255 - (255 - 200) * progress)
                    g = int(215 - (215 - 150) * progress)
                    b = int(0)
                    pygame.draw.line(option_surface, (r, g, b, 200), (0, j), (option_width, j))
                
                # Рамка с свечением
                pygame.draw.rect(option_surface, GOLD, (0, 0, option_width, option_height), 3)
                # Внутренняя рамка
                pygame.draw.rect(option_surface, (255, 255, 255, 100), (3, 3, option_width - 6, option_height - 6), 1)
            else:
                # Полупрозрачный фон для невыбранной опции
                option_surface.fill((40, 30, 50, 180))
                pygame.draw.rect(option_surface, (100, 80, 120), (0, 0, option_width, option_height), 2)
            
            screen.blit(option_surface, (option_x, option_y))
            
            # Иконка
            icon_text = menu_font.render(setting["icon"], True, WHITE)
            screen.blit(icon_text, (option_x + 20, option_y + option_height // 2 - icon_text.get_height() // 2))
            
            # Название опции
            name_text = menu_font.render(setting["name"], True, WHITE if not (is_selected or is_hovered) else BLACK)
            screen.blit(name_text, (option_x + 70, option_y + 15))
            
            # Значение опции
            value_x = option_x + option_width - 150
            
            if setting["type"] == "bool":
                value = setting["value"]
                value_text = "ВКЛ" if value else "ВЫКЛ"
                value_color = GREEN if value else RED
                
                # Красивая кнопка переключателя
                switch_width = 80
                switch_height = 35
                switch_x = value_x + 20
                switch_y = option_y + option_height // 2 - switch_height // 2
                
                # Фон переключателя
                switch_bg_color = GREEN if value else (80, 80, 80)
                pygame.draw.rect(screen, switch_bg_color, 
                               (switch_x, switch_y, switch_width, switch_height), border_radius=17)
                
                # Кружок переключателя
                circle_x = switch_x + switch_width - 20 if value else switch_x + 20
                pygame.draw.circle(screen, WHITE, (circle_x, switch_y + switch_height // 2), 15)
                
                # Текст
                value_render = small_font.render(value_text, True, value_color)
                screen.blit(value_render, (value_x - value_render.get_width(), option_y + 20))
                
            elif setting["type"] == "slider":
                # Слайдер громкости
                slider_width = 200
                slider_height = 8
                slider_x = value_x - 50
                slider_y = option_y + option_height // 2 - slider_height // 2
                
                # Фон слайдера
                pygame.draw.rect(screen, (60, 60, 60), 
                               (slider_x, slider_y, slider_width, slider_height), border_radius=4)
                
                # Заполненная часть
                fill_width = int(slider_width * setting["value"])
                pygame.draw.rect(screen, GREEN, 
                               (slider_x, slider_y, fill_width, slider_height), border_radius=4)
                
                # Ползунок
                thumb_x = slider_x + fill_width
                pygame.draw.circle(screen, GOLD, (thumb_x, slider_y + slider_height // 2), 10)
                pygame.draw.circle(screen, WHITE, (thumb_x, slider_y + slider_height // 2), 8)
                
                # Процент
                percent_text = dialog_font.render(f"{int(setting['value'] * 100)}%", True, WHITE)
                screen.blit(percent_text, (slider_x + slider_width + 10, option_y + 15))
        
        # Подсказки внизу
        hint_y = SCREEN_HEIGHT - 120
        
        # Фон для подсказок
        hint_bg = pygame.Surface((SCREEN_WIDTH - 100, 80), pygame.SRCALPHA)
        hint_bg.fill((0, 0, 0, 150))
        screen.blit(hint_bg, (50, hint_y))
        
        hints = [
            "СТРЕЛКИ ВВЕРХ/ВНИЗ - выбор опции",
            "ENTER/ПРОБЕЛ - изменить значение",
            "← → - изменение громкости",
            "ESC - возврат в меню"
        ]
        
        for i, hint in enumerate(hints):
            hint_text = small_font.render(hint, True, LIGHT_GREY)
            screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, hint_y + i * 18 + 10))
        
        # Декоративные элементы в углах
        corner_size = 50
        # Левый верхний угол
        pygame.draw.line(screen, GOLD, (20, 20), (20 + corner_size, 20), 3)
        pygame.draw.line(screen, GOLD, (20, 20), (20, 20 + corner_size), 3)
        # Правый верхний угол
        pygame.draw.line(screen, GOLD, (SCREEN_WIDTH - 20, 20), (SCREEN_WIDTH - 20 - corner_size, 20), 3)
        pygame.draw.line(screen, GOLD, (SCREEN_WIDTH - 20, 20), (SCREEN_WIDTH - 20, 20 + corner_size), 3)
        # Левый нижний угол
        pygame.draw.line(screen, GOLD, (20, SCREEN_HEIGHT - 20), (20 + corner_size, SCREEN_HEIGHT - 20), 3)
        pygame.draw.line(screen, GOLD, (20, SCREEN_HEIGHT - 20), (20, SCREEN_HEIGHT - 20 - corner_size), 3)
        # Правый нижний угол
        pygame.draw.line(screen, GOLD, (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20), 
                        (SCREEN_WIDTH - 20 - corner_size, SCREEN_HEIGHT - 20), 3)
        pygame.draw.line(screen, GOLD, (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20), 
                        (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20 - corner_size), 3)

