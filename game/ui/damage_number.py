"""
Класс отображения урона
"""
import pygame
from game.config import small_font


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

