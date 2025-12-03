"""
Менеджер волн и спавна врагов
"""
import random
import math
from game.enemy import Enemy
from game.particle import Particle
from game.config import GOLD


class WaveManager:
    """Управление волнами врагов"""
    
    def __init__(self):
        self.wave = 1
        self.enemy_spawn_timer = 0
        
    def update(self, enemies, player, city):
        """Обновление спавна врагов"""
        self.enemy_spawn_timer += 1
        max_enemies = 8 + self.wave
        
        spawn_rate = max(60, 90 - self.wave * 5)
        if self.enemy_spawn_timer >= spawn_rate and len(enemies) < max_enemies:
            spawn_count = 1 if self.wave < 3 else min(2, max_enemies - len(enemies))
            self.spawn_enemies(spawn_count, enemies, player, city)
            self.enemy_spawn_timer = 0
    
    def spawn_enemies(self, count, enemies, player, city):
        """Спавн врагов вокруг игрока"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(400, 600)
            x = player.x + math.cos(angle) * distance
            y = player.y + math.sin(angle) * distance
            
            x = max(50, min(city.world_size - 50, x))
            y = max(50, min(city.world_size - 50, y))
            
            enemy_type = self._choose_enemy_type()
            enemies.append(Enemy(x, y, enemy_type, self.wave))
    
    def _choose_enemy_type(self):
        """Выбор типа врага на основе волны"""
        boss_chance = min(0.1 + self.wave * 0.05, 0.4)
        sniper_chance = min(0.05 + self.wave * 0.03, 0.25) if self.wave >= 2 else 0
        tank_chance = min(0.03 + self.wave * 0.02, 0.2) if self.wave >= 4 else 0
        
        rand = random.random()
        if rand < boss_chance and self.wave >= 3:
            return "босс"
        elif rand < boss_chance + sniper_chance and self.wave >= 2:
            return "снайпер"
        elif rand < boss_chance + sniper_chance + tank_chance and self.wave >= 4:
            return "танк"
        else:
            return random.choices(["мент", "быдло", "крыса"], weights=[0.4, 0.35, 0.25])[0]
    
    def check_wave_change(self, player_kills, particles, player):
        """Проверка смены волны"""
        if player_kills >= self.wave * 10:
            self.wave += 1
            player.health = min(player.max_health, player.health + 20)
            
            # Эффект при смене волны
            for _ in range(30):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(3, 8)
                particles.append(Particle(
                    player.x, player.y,
                    GOLD,
                    math.cos(angle) * speed,
                    math.sin(angle) * speed,
                    50
                ))
            return True
        return False

