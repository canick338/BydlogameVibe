"""
Конфигурация игры - все константы и настройки
"""
import pygame

# Инициализация Pygame
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Размеры экрана
SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
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

