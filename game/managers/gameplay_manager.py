"""
Менеджер игровой логики - обновление всех игровых объектов
"""
import random
import math
import pygame
from game.config import BLUE
from game.particle import Particle, BloodParticle
from game.ui.damage_number import DamageNumber
from game.ui.kill_feed import KillFeedEntry


class GameplayManager:
    """Управление игровой логикой"""
    
    def __init__(self, player, city, enemies, bullets, particles, damage_numbers, kill_feed, screen_shake, mission_callback=None):
        self.player = player
        self.city = city
        self.enemies = enemies
        self.bullets = bullets
        self.particles = particles
        self.damage_numbers = damage_numbers
        self.kill_feed = kill_feed
        self.screen_shake = screen_shake
        self.mission_callback = mission_callback  # Callback для обновления миссий (enemy, bounty)
    
    def update_player_movement(self, keys, dt):
        """Обновление движения игрока"""
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1
        
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
        
        self.player.move(dx, dy, self.city.world_size)
        self.city.update_camera(self.player.x, self.player.y)
        self.city.check_location_transition(self.player.x, self.player.y)
    
    def update_bullets(self, world_size):
        """Обновление пуль и проверка попаданий. Возвращает изменение счета"""
        score_change = 0
        bullets_to_remove = []
        for bullet in self.bullets[:]:
            if not bullet.update(world_size):
                self.bullets.remove(bullet)
            else:
                hit_enemies = []
                for enemy in self.enemies[:]:
                    hitbox_size = max(enemy.size, 30)
                    dist = math.sqrt((bullet.x - enemy.x) ** 2 + (bullet.y - enemy.y) ** 2)
                    if dist < hitbox_size:
                        hit_enemies.append((enemy, dist))
                
                # Взрывные пули
                if bullet.type == "explosive" and bullet.lifetime <= 1:
                    explosion_radius = bullet.explosion_radius
                    for enemy in self.enemies[:]:
                        dist = math.sqrt((bullet.x - enemy.x) ** 2 + (bullet.y - enemy.y) ** 2)
                        if dist < explosion_radius:
                            hit_enemies.append((enemy, dist))
                    
                    for _ in range(40):
                        angle = random.uniform(0, 2 * math.pi)
                        speed = random.uniform(3, 10)
                        self.particles.append(Particle(
                            bullet.x, bullet.y, (255, 150, 0),
                            math.cos(angle) * speed,
                            math.sin(angle) * speed, 50
                        ))
                
                # Обработка попаданий
                for enemy, dist in hit_enemies:
                    damage = bullet.damage
                    is_critical = random.random() < 0.1
                    if is_critical:
                        damage = int(damage * 1.5)
                    if bullet.type == "explosive":
                        damage = int(damage * (1 - dist / bullet.explosion_radius * 0.5))
                    
                    self.damage_numbers.append(DamageNumber(enemy.x, enemy.y - enemy.size, damage, is_critical))
                    
                    if damage > 50:
                        self.screen_shake.shake(5, 10)
                    
                    if enemy.take_damage(damage):
                        change = self._handle_enemy_death(enemy, damage)
                        score_change += change
                    
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if bullet.type != "explosive":
                        break
        return score_change
    
    def _handle_enemy_death(self, enemy, damage):
        """Обработка смерти врага. Возвращает изменение счета"""
        # Эффект частиц
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            self.particles.append(Particle(
                enemy.x, enemy.y, enemy.color,
                math.cos(angle) * speed,
                math.sin(angle) * speed, 40
            ))
        
        self.enemies.remove(enemy)
        self.player.kills += 1
        
        # Лента убийств
        self.kill_feed.append(KillFeedEntry(enemy.type))
        if len(self.kill_feed) > 5:
            self.kill_feed.pop(0)
        
        # Комбо
        self.player.combo += 1
        self.player.combo_timer = 180
        combo_bonus = 1 + (self.player.combo // 5) * 0.1
        
        bounty = int(enemy.bounty * combo_bonus)
        self.player.money += bounty
        score_change = int(bounty // 2 * combo_bonus)
        self.player.total_damage_dealt += damage
        
        # Опыт
        exp_gain = 10 + enemy.level * 5
        if enemy.type == "босс":
            exp_gain *= 3
        self.player.experience += exp_gain
        
        # Повышение уровня
        while self.player.experience >= self.player.experience_to_next:
            self.player.experience -= self.player.experience_to_next
            self.player.level += 1
            self.player.skill_points += 1
            self.player.experience_to_next = int(self.player.experience_to_next * 1.5)
            self.player.health = self.player.max_health
            
            for _ in range(50):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(2, 8)
                self.particles.append(Particle(
                    self.player.x, self.player.y, (0, 255, 255),
                    math.cos(angle) * speed,
                    math.sin(angle) * speed, 60
                ))
        
        if enemy.type == "босс":
            self.player.bosses_killed += 1
        elif enemy.type == "снайпер":
            self.player.headshots += 1
        
        # Кровь
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 4)
            self.particles.append(BloodParticle(
                enemy.x, enemy.y,
                math.cos(angle) * speed,
                math.sin(angle) * speed
            ))
        
        # Обработка миссий через callback
        if self.mission_callback:
            self.mission_callback(enemy, bounty)
        
        return score_change
    
    def update_enemies(self):
        """Обновление врагов"""
        current_time = pygame.time.get_ticks()
        for enemy in self.enemies:
            damage = enemy.update(self.player.x, self.player.y)
            if damage > 0:
                actual_damage = max(1, damage - self.player.armor // 2)
                self.player.health -= actual_damage
                self.player.last_damage_time = current_time
                self.player.regen_timer = 0
                return True if self.player.health <= 0 else False
        return False
    
    def update_particles(self, world_size):
        """Обновление частиц"""
        for particle in self.particles[:]:
            if not particle.update():
                self.particles.remove(particle)
            particle.x = max(0, min(world_size, particle.x))
            particle.y = max(0, min(world_size, particle.y))
    
    def update_damage_numbers(self):
        """Обновление чисел урона"""
        for dmg_num in self.damage_numbers[:]:
            if not dmg_num.update():
                self.damage_numbers.remove(dmg_num)
    
    def update_kill_feed(self):
        """Обновление ленты убийств"""
        for kill_entry in self.kill_feed[:]:
            if not kill_entry.update():
                self.kill_feed.remove(kill_entry)
    
    def update_player_regen(self):
        """Обновление регенерации здоровья"""
        self.player.regen_timer += 1
        current_time = pygame.time.get_ticks()
        if current_time - self.player.last_damage_time > 5000 and self.player.health < self.player.max_health:
            if self.player.regen_timer >= 180:
                self.player.health = min(self.player.max_health, self.player.health + 1)
                self.player.regen_timer = 0
    
    def update_combo(self):
        """Обновление комбо"""
        if self.player.combo_timer > 0:
            self.player.combo_timer -= 1
        else:
            self.player.combo = 0

