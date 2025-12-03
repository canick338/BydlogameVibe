"""
Класс части тела врага для эффекта разрезания
"""
import pygame
import random
import math


class BodyPart:
    def __init__(self, x, y, part_type, color):
        self.x = x
        self.y = y
        self.part_type = part_type  # "head", "torso", "limb"
        self.color = color
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -1)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-5, 5)
        self.lifetime = 180
        self.size = random.randint(8, 20) if part_type == "torso" else random.randint(5, 12)
        
    def update(self):
        """Обновление части тела"""
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2  # Гравитация
        self.rotation += self.rotation_speed
        self.lifetime -= 1
        return self.lifetime > 0
    
    def draw(self, screen):
        """Отрисовка части тела"""
        if self.lifetime <= 0:
            return
            
        # Создаем поверхность для части тела
        part_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        
        # Форма зависит от типа части
        if self.part_type == "head":
            pygame.draw.circle(part_surf, self.color, (self.size, self.size), self.size)
        elif self.part_type == "torso":
            pygame.draw.ellipse(part_surf, self.color, (0, 0, self.size * 2, self.size * 1.5))
        else:  # limb
            pygame.draw.ellipse(part_surf, self.color, (0, 0, self.size, self.size * 1.5))
        
        # Поворот и отрисовка
        rotated = pygame.transform.rotate(part_surf, self.rotation)
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(rotated, rect)
        
        # Кровавый след
        if random.random() < 0.3:
            pygame.draw.circle(screen, (100, 0, 0), (int(self.x), int(self.y)), 3)

