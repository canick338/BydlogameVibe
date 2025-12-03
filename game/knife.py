"""
Класс ножа для ближнего боя
"""
import pygame
import math


class Knife:
    def __init__(self):
        self.name = "НОЖ"
        self.damage = 121
        self.range = 60  # Дальность атаки
        self.speed = 2.0  # Скорость атаки (ударов в секунду)
        self.last_attack = 0
        self.attack_angle = 0  # Угол для анимации замаха
        
    def can_attack(self):
        """Проверка возможности атаки"""
        current_time = pygame.time.get_ticks()
        return current_time - self.last_attack > 1000 / self.speed
    
    def attack(self, direction, x, y):
        """Атака ножом - возвращает информацию об атаке"""
        if self.can_attack():
            self.last_attack = pygame.time.get_ticks()
            self.attack_angle = direction
            return {
                "x": x,
                "y": y,
                "direction": direction,
                "range": self.range,
                "damage": self.damage
            }
        return None

