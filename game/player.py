"""
Класс игрока
"""
import math
import pygame
from game.weapon import Weapon


class Player:
    def __init__(self):
        self.x = 2500  # Центр мира по умолчанию
        self.y = 2500
        self.width = 40
        self.height = 60
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.money = 1000
        self.reputation = 5
        self.direction = 0

        # Оружие
        self.weapons = [
            Weapon("ПИСТОЛЕТ", 25, 3, 30, (180, 180, 180), 0.05),
            Weapon("АВТОМАТ", 15, 10, 60, (100, 150, 200), 0.15),
            Weapon("ДРОБОВИК", 40, 1.5, 12, (200, 100, 50), 0.3),
            Weapon("СНАЙПЕРКА", 60, 1, 10, (150, 200, 150), 0.02),
            Weapon("ПУЛЕМЁТ", 20, 15, 100, (200, 150, 100), 0.2),
            Weapon("ГРАНАТОМЁТ", 80, 0.5, 5, (255, 100, 0), 0.1),
            Weapon("РЕВОЛЬВЕР", 35, 2, 18, (200, 200, 200), 0.03),
            Weapon("АВТОМАТ-2", 18, 12, 80, (120, 180, 220), 0.12)
        ]

        self.current_weapon = 0
        self.kills = 0
        self.completed_missions = 0
        self.total_missions = 5
        self.mission_kills = 0
        self.auto_fire = False
        self.total_damage_dealt = 0
        self.headshots = 0
        self.bosses_killed = 0
        self.time_played = 0
        self.armor = 0
        self.damage_multiplier = 1.0
        self.speed_multiplier = 1.0
        self.regen_timer = 0
        self.last_damage_time = 0
        self.combo = 0
        self.combo_timer = 0
        self.level = 1
        self.experience = 0
        self.experience_to_next = 100
        self.skill_points = 0
        self.skills = {
            "damage": 0,
            "health": 0,
            "speed": 0,
            "ammo": 0,
            "regen": 0
        }

    def move(self, dx, dy, world_size=5000):
        self.x += dx * self.speed
        self.y += dy * self.speed
        self.x = max(self.width // 2, min(world_size - self.width // 2, self.x))
        self.y = max(self.height // 2, min(world_size - self.height // 2, self.y))

    def update_direction(self, target_x, target_y):
        self.direction = math.atan2(target_y - self.y, target_x - self.x)

    def shoot(self):
        return self.weapons[self.current_weapon].shoot(self.direction, self.x, self.y)

    def switch_weapon(self, direction):
        self.current_weapon = (self.current_weapon + direction) % len(self.weapons)

    def draw(self, screen):
        # Тень персонажа
        shadow_surface = pygame.Surface((self.width + 10, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 100), (0, 0, self.width + 10, 20))
        screen.blit(shadow_surface, (self.x - (self.width + 10) // 2, self.y + self.height // 2))
        
        # Тело пацана с градиентом
        body_color = (180, 80, 80) if self.health > 50 else (200, 50, 50)
        body_rect = pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)
        
        # Градиент тела
        for i in range(self.height):
            grad_factor = i / self.height
            grad_color = tuple(int(c * (0.85 + grad_factor * 0.15)) for c in body_color)
            pygame.draw.line(screen, grad_color, 
                           (self.x - self.width // 2, self.y - self.height // 2 + i),
                           (self.x + self.width // 2, self.y - self.height // 2 + i))
        
        # Обводка
        pygame.draw.rect(screen, tuple(min(255, c + 40) for c in body_color), body_rect, 2)

        # Голова с эффектом
        head_radius = 16
        head_x = self.x + math.cos(self.direction) * 25
        head_y = self.y + math.sin(self.direction) * 25
        
        # Свечение головы
        head_glow = pygame.Surface((head_radius * 2 + 6, head_radius * 2 + 6), pygame.SRCALPHA)
        pygame.draw.circle(head_glow, (240, 200, 160, 50), (head_radius + 3, head_radius + 3), head_radius + 3)
        screen.blit(head_glow, (int(head_x) - head_radius - 3, int(head_y) - head_radius - 3))
        
        pygame.draw.circle(screen, (240, 200, 160), (int(head_x), int(head_y)), head_radius)
        pygame.draw.circle(screen, (255, 230, 200), (int(head_x), int(head_y)), head_radius, 2)

        # Глаза с эффектом
        eye_offset = 6
        eye1_x = head_x + math.cos(self.direction) * 8 + math.cos(self.direction - math.pi / 2) * eye_offset
        eye1_y = head_y + math.sin(self.direction) * 8 + math.sin(self.direction - math.pi / 2) * eye_offset
        eye2_x = head_x + math.cos(self.direction) * 8 + math.cos(self.direction + math.pi / 2) * eye_offset
        eye2_y = head_y + math.sin(self.direction) * 8 + math.sin(self.direction + math.pi / 2) * eye_offset

        pygame.draw.circle(screen, (30, 30, 100), (int(eye1_x), int(eye1_y)), 5)
        pygame.draw.circle(screen, (30, 30, 100), (int(eye2_x), int(eye2_y)), 5)
        pygame.draw.circle(screen, (100, 150, 255), (int(eye1_x), int(eye1_y)), 3)
        pygame.draw.circle(screen, (100, 150, 255), (int(eye2_x), int(eye2_y)), 3)
        pygame.draw.circle(screen, (0, 0, 0), (int(eye1_x), int(eye1_y)), 2)
        pygame.draw.circle(screen, (0, 0, 0), (int(eye2_x), int(eye2_y)), 2)

        # Оружие с эффектом
        weapon = self.weapons[self.current_weapon]
        weapon_x = self.x + math.cos(self.direction) * 35
        weapon_y = self.y + math.sin(self.direction) * 35
        
        # Металлический эффект оружия
        weapon_rect = pygame.Rect(weapon_x - 8, weapon_y - 4, 25, 8)
        pygame.draw.rect(screen, tuple(int(c * 0.7) for c in weapon.color), weapon_rect)
        pygame.draw.rect(screen, weapon.color, (weapon_x - 7, weapon_y - 3, 23, 6))
        pygame.draw.rect(screen, tuple(min(255, c + 50) for c in weapon.color), (weapon_x - 6, weapon_y - 2, 21, 2))
        pygame.draw.rect(screen, (50, 50, 50), weapon_rect, 1)

