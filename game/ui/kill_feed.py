"""
Класс ленты убийств
"""
import pygame
from game.config import small_font


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

