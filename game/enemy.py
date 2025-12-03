"""
Класс врага
"""
import math
import random
import pygame
from game.sprites.enemy_sprite_manager import EnemySpriteManager
from game.config import RED, GREEN, GOLD


class Enemy:
    def __init__(self, x, y, enemy_type, level=1):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.level = level
        self.max_health = 80 + level * 20
        self.health = self.max_health
        self.direction = random.uniform(0, 2 * math.pi)
        self.attack_cooldown = 0
        self.speed_modifier = 0.8 + level * 0.1
        self.stun_timer = 0
        self.flash_timer = 0
        self.last_damage_time = 0
        self.pathfinding_timer = 0
        self.aggro_range = 400
        
        # Анимация
        self.sprite_manager = EnemySpriteManager()
        self.animation_state = "Idle"
        self.animation_frame = 0
        self.animation_timer = 0
        self.is_moving = False
        self.is_dead = False
        self.is_hurt = False
        self.shot_animation_timer = 0
        
        # Размер спрайта
        self.sprite_size = 64
        self.last_x = x
        self.last_y = y
        self.animation_state_prev = "Idle"
        self.sprite_available = False
        self.check_sprite_availability()

        if enemy_type == "мент":
            self.color = (70, 70, 200)
            self.size = max(38, 30)
            self.speed = 2.2 * self.speed_modifier
            self.damage = 3
            self.attack_range = 85
            self.bounty = 200
        elif enemy_type == "быдло":
            self.color = (160, 100, 60)
            self.size = max(42, 30)
            self.speed = 1.8 * self.speed_modifier
            self.damage = 2
            self.attack_range = 70
            self.bounty = 100
        elif enemy_type == "босс":
            self.color = (200, 0, 0)
            self.size = max(55, 30)
            self.speed = 1.5 * self.speed_modifier
            self.damage = 5
            self.attack_range = 100
            self.bounty = 500
            self.aggro_range = 600
        elif enemy_type == "снайпер":
            self.color = (100, 150, 100)
            self.size = max(30, 30)
            self.speed = 1.2 * self.speed_modifier
            self.damage = 8
            self.attack_range = 300
            self.bounty = 300
            self.aggro_range = 500
        elif enemy_type == "танк":
            self.color = (80, 80, 80)
            self.size = max(50, 30)
            self.speed = 0.8 * self.speed_modifier
            self.damage = 4
            self.attack_range = 90
            self.bounty = 400
            self.max_health = 150 + level * 30
            self.health = self.max_health
        else:  # крыса
            self.color = (120, 120, 120)
            self.size = max(25, 30)
            self.speed = 2.8 * self.speed_modifier
            self.damage = 1
            self.attack_range = 50
            self.bounty = 50
        
        self.check_sprite_availability()
    
    def check_sprite_availability(self):
        sprite_type = self.type if self.type in ["мент", "босс"] else "другой"
        test_sprite = self.sprite_manager.get_sprite(sprite_type, "Idle", 0)
        if test_sprite:
            try:
                w, h = test_sprite.get_size()
                self.sprite_available = w > 0 and h > 0
            except:
                self.sprite_available = False
        else:
            self.sprite_available = False

    def update(self, player_x, player_y):
        if self.is_dead:
            self.animation_state = "Dead"
            return 0
            
        if self.stun_timer > 0:
            self.stun_timer -= 1
            return 0
        
        dx = player_x - self.x
        dy = player_y - self.y
        distance = max(0.1, math.sqrt(dx * dx + dy * dy))
        
        if self.flash_timer > 0:
            self.flash_timer -= 1
            self.is_hurt = True
        else:
            self.is_hurt = False
        
        moved = abs(self.x - self.last_x) > 0.1 or abs(self.y - self.last_y) > 0.1
        self.last_x = self.x
        self.last_y = self.y
        
        self.animation_timer += 1
        self.is_moving = moved
        
        if self.shot_animation_timer > 0:
            self.shot_animation_timer -= 1
            if self.shot_animation_timer == 0:
                if self.is_moving:
                    self.animation_state = "Run" if self.speed > 2 else "Walk"
                else:
                    self.animation_state = "Idle"
        
        if self.type == "снайпер" and distance < self.aggro_range:
            self.direction = math.atan2(dy, dx)
            self.attack_cooldown -= 1
            if self.attack_cooldown <= 0 and distance > 150:
                self.attack_cooldown = 60
                self.animation_state = "Shot"
                self.shot_animation_timer = 15
                return self.damage
            if self.shot_animation_timer == 0:
                self.animation_state = "Idle"
            return 0

        if distance < self.attack_range:
            self.direction = math.atan2(dy, dx)
            self.attack_cooldown -= 1
            if self.attack_cooldown <= 0:
                self.attack_cooldown = 25 if self.type != "танк" else 35
                self.animation_state = "Shot"
                self.shot_animation_timer = 15
                return self.damage
            if self.shot_animation_timer == 0:
                self.animation_state = "Idle"
        elif distance < self.aggro_range:
            self.pathfinding_timer += 1
            if self.pathfinding_timer > 30:
                self.direction = math.atan2(dy, dx) + random.uniform(-0.15, 0.15)
                self.pathfinding_timer = 0
            else:
                self.direction = math.atan2(dy, dx) + random.uniform(-0.1, 0.1)
            
            if self.stun_timer == 0:
                self.x += math.cos(self.direction) * self.speed
                self.y += math.sin(self.direction) * self.speed
                self.is_moving = True
                self.animation_state = "Run" if self.speed > 2 else "Walk"
        else:
            self.animation_state = "Idle"
        
        if self.animation_state != self.animation_state_prev:
            self.animation_frame = 0
            self.animation_state_prev = self.animation_state
        
        if self.animation_state == "Shot":
            anim_speed = 4
        elif self.animation_state == "Hurt":
            anim_speed = 3
        elif self.animation_state == "Dead":
            anim_speed = 8
        elif self.is_moving:
            anim_speed = 6
        else:
            anim_speed = 12
        
        if self.animation_timer >= anim_speed:
            self.animation_timer = 0
            sprite_type = self.type if self.type in ["мент", "босс"] else "другой"
            key = f"{sprite_type}_{self.animation_state}"
            frames = self.sprite_manager.sprites.get(key, [])
            max_frames = len(frames) if frames else 1
            if max_frames > 0:
                if self.animation_state in ["Shot", "Dead"]:
                    if self.animation_frame < max_frames - 1:
                        self.animation_frame += 1
                    if self.animation_state == "Shot" and self.shot_animation_timer == 0:
                        self.animation_frame = 0
                else:
                    self.animation_frame = (self.animation_frame + 1) % max_frames

        return 0

    def take_damage(self, damage):
        self.health -= damage
        self.flash_timer = 10
        self.is_hurt = True
        self.animation_state = "Hurt"
        self.last_damage_time = pygame.time.get_ticks()
        if damage > 50 and random.random() < 0.3:
            self.stun_timer = 30
        if self.health <= 0:
            self.is_dead = True
            self.animation_state = "Dead"
        return self.health <= 0

    def draw(self, screen):
        shadow_surface = pygame.Surface((self.sprite_size + 10, 15), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 120), (0, 0, self.sprite_size + 10, 15))
        screen.blit(shadow_surface, (int(self.x) - self.sprite_size // 2 - 5, int(self.y) + self.sprite_size // 2))
        
        if self.sprite_available:
            sprite_type = self.type if self.type in ["мент", "босс"] else "другой"
            sprite = self.sprite_manager.get_sprite(sprite_type, self.animation_state, self.animation_frame)
            
            if not sprite:
                sprite = self.sprite_manager.get_sprite(sprite_type, "Idle", 0)
            
            sprite_loaded = sprite is not None
            if sprite_loaded:
                try:
                    orig_width, orig_height = sprite.get_size()
                    sprite_loaded = orig_width > 0 and orig_height > 0
                except:
                    sprite_loaded = False
        else:
            sprite_loaded = False
            sprite = None
        
        if sprite_loaded and sprite is not None:
            if self.type == "босс":
                scale = 1.8
            elif self.type == "танк":
                scale = 1.5
            elif self.type == "снайпер":
                scale = 1.0
            else:
                scale = 1.6
            
            orig_width, orig_height = sprite.get_size()
            
            if orig_width > 0 and orig_height > 0:
                scaled_width = max(30, int(orig_width * scale))
                scaled_height = max(40, int(orig_height * scale))
                
                scaled_sprite = pygame.transform.scale(sprite, (scaled_width, scaled_height))
                
                if math.cos(self.direction) < 0:
                    scaled_sprite = pygame.transform.flip(scaled_sprite, True, False)
                
                if self.flash_timer > 0:
                    flash_sprite = scaled_sprite.copy()
                    white_overlay = pygame.Surface(scaled_sprite.get_size(), pygame.SRCALPHA)
                    white_overlay.fill((255, 255, 255, 150))
                    flash_sprite.blit(white_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                    scaled_sprite = flash_sprite
                
                if self.animation_state == "Shot" and self.shot_animation_timer > 0:
                    glow_surface = pygame.Surface((scaled_width + 10, scaled_height + 10), pygame.SRCALPHA)
                    for radius in range(15, 0, -2):
                        alpha = int(100 * (1 - radius / 15))
                        pygame.draw.circle(glow_surface, (255, 200, 0, alpha), 
                                         (scaled_width // 2 + 5, scaled_height // 2 + 5), radius)
                    screen.blit(glow_surface, (int(self.x) - scaled_width // 2 - 5, int(self.y) - scaled_height // 2 - 15))
                
                sprite_rect = scaled_sprite.get_rect(center=(int(self.x), int(self.y) - 15))
                screen.blit(scaled_sprite, sprite_rect)
        else:
            draw_color = self.color
            if self.flash_timer > 0:
                draw_color = tuple(min(255, c + 100) for c in self.color)
            
            for radius in range(self.size, 0, -2):
                grad_factor = radius / self.size
                grad_color = tuple(int(c * (0.7 + grad_factor * 0.3)) for c in draw_color)
                pygame.draw.circle(screen, grad_color, (int(self.x), int(self.y)), radius)
            pygame.draw.circle(screen, tuple(min(255, c + 30) for c in draw_color), (int(self.x), int(self.y)), self.size, 2)
        
        if self.stun_timer > 0:
            stun_glow = pygame.Surface((self.size * 2 + 20, self.size * 2 + 20), pygame.SRCALPHA)
            for radius in range(self.size + 10, 0, -3):
                alpha = int(150 * (1 - radius / (self.size + 10)))
                pygame.draw.circle(stun_glow, (255, 255, 0, alpha), (self.size + 10, self.size + 10), radius)
            screen.blit(stun_glow, (int(self.x) - self.size - 10, int(self.y) - self.size - 10))
            pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), self.size + 5, 3)

        health_width = (self.health / self.max_health) * (self.size * 2)
        pygame.draw.rect(screen, RED, (self.x - self.size, self.y - self.size - 20, self.size * 2, 6))
        pygame.draw.rect(screen, GREEN, (self.x - self.size, self.y - self.size - 20, health_width, 6))
        
        if self.type == "босс":
            crown_y = self.y - self.size - 25
            pygame.draw.polygon(screen, GOLD, [
                (self.x - self.size // 2, crown_y),
                (self.x - self.size // 4, crown_y - 8),
                (self.x, crown_y),
                (self.x + self.size // 4, crown_y - 8),
                (self.x + self.size // 2, crown_y)
            ])

