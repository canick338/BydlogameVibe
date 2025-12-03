"""
Класс пули
"""
import math
import pygame
from game.config import GOLD


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
