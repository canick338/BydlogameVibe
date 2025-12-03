"""
Класс прицела
"""
import pygame
from game.config import RED


class Crosshair:
    @staticmethod
    def draw(screen):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Улучшенный прицел с эффектами
        size = 15
        
        # Свечение прицела
        crosshair_glow = pygame.Surface((size * 2 + 20, size * 2 + 20), pygame.SRCALPHA)
        for radius in range(size + 10, 0, -2):
            alpha = int(50 * (1 - radius / (size + 10)))
            pygame.draw.circle(crosshair_glow, (*RED[:3], alpha), (size + 10, size + 10), radius)
        screen.blit(crosshair_glow, (mouse_x - size - 10, mouse_y - size - 10))
        
        # Внешние линии с градиентом
        line_length = 8
        for i in range(line_length):
            alpha = 255 - i * 20
            color = (255, int(200 - i * 10), int(200 - i * 10))
            # Верх
            pygame.draw.line(screen, color, 
                           (mouse_x, mouse_y - size + i), 
                           (mouse_x, mouse_y - size + i + 1), 2)
            # Низ
            pygame.draw.line(screen, color, 
                           (mouse_x, mouse_y + size - i), 
                           (mouse_x, mouse_y + size - i - 1), 2)
            # Лево
            pygame.draw.line(screen, color, 
                           (mouse_x - size + i, mouse_y), 
                           (mouse_x - size + i + 1, mouse_y), 2)
            # Право
            pygame.draw.line(screen, color, 
                           (mouse_x + size - i, mouse_y), 
                           (mouse_x + size - i - 1, mouse_y), 2)
        
        # Центральный круг с эффектом
        pygame.draw.circle(screen, RED, (mouse_x, mouse_y), 6, 2)
        pygame.draw.circle(screen, (255, 150, 150), (mouse_x, mouse_y), 4, 1)
        pygame.draw.circle(screen, (255, 255, 255), (mouse_x, mouse_y), 2)
        pygame.draw.circle(screen, RED, (mouse_x, mouse_y), 1)

