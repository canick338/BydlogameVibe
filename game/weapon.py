"""
Класс оружия
"""
import pygame
import random
import math
from game.bullet import Bullet


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

