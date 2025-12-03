"""
Система частиц
"""
import pygame


class Particle:
    def __init__(self, x, y, color, velocity_x, velocity_y, lifetime=30):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.lifetime = lifetime
        self.max_lifetime = lifetime

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_x *= 0.95
        self.velocity_y *= 0.95
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self, screen):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        size = max(1, int(3 * (self.lifetime / self.max_lifetime)))
        if size > 0:
            # Свечение частицы
            if size > 2:
                glow_surface = pygame.Surface((size * 2 + 4, size * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(glow_surface, (*self.color[:3], alpha // 2), (size + 2, size + 2), size + 2)
                screen.blit(glow_surface, (int(self.x) - size - 2, int(self.y) - size - 2))
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)
            pygame.draw.circle(screen, tuple(min(255, c + 50) for c in self.color), (int(self.x), int(self.y)), size - 1)


class BloodParticle(Particle):
    def __init__(self, x, y, velocity_x, velocity_y):
        super().__init__(x, y, (150, 0, 0), velocity_x, velocity_y, 60)
    
    def draw(self, screen):
        size = max(1, int(4 * (self.lifetime / self.max_lifetime)))
        if size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)

