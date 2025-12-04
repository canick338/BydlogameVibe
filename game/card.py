"""
Класс карточки фембоя
"""
import pygame
from game.config import BASE_WIDTH, BASE_HEIGHT, GOLD, WHITE, LIGHT_GREY, DARK_GREY, RED, GREEN, menu_font, dialog_font, small_font


class Card:
    def __init__(self, card_id, name, age, appearance, style, personality, bio, 
                 damage_bonus=0, speed_bonus=0, health_bonus=0, 
                 special_ability=None, price=0, image_path=None, rarity='common'):
        self.card_id = card_id
        self.name = name
        self.age = age
        self.appearance = appearance
        self.style = style
        self.personality = personality
        self.bio = bio
        
        # Бафы
        self.damage_bonus = damage_bonus  # Множитель урона (например 1.15 = +15%)
        self.speed_bonus = speed_bonus  # Бонус скорости
        self.health_bonus = health_bonus  # Бонус здоровья
        
        # Уникальная способность (строка описания)
        self.special_ability = special_ability
        
        # Цена в магазине
        self.price = price
        
        # Редкость карточки
        self.rarity = rarity  # "common", "rare", "epic", "legendary"
        
        # Изображение карточки
        self.image_path = image_path
        self.image = None
        if image_path:
            try:
                self.image = pygame.image.load(image_path)
                # Конвертируем для прозрачности если нужно
                if self.image.get_flags() & pygame.SRCALPHA == 0:
                    self.image = self.image.convert_alpha()
            except Exception as e:
                print(f"Не удалось загрузить изображение {image_path}: {e}")
                self.image = None
    
    def apply_buffs(self, player):
        """Применяет бафы карточки к игроку"""
        if self.damage_bonus > 1.0:  # Если это множитель больше 1
            player.damage_multiplier *= self.damage_bonus
        if self.speed_bonus > 0:
            player.speed += self.speed_bonus
        if self.health_bonus > 0:
            player.max_health += self.health_bonus
            # Восстанавливаем здоровье пропорционально
            health_ratio = player.health / (player.max_health - self.health_bonus) if (player.max_health - self.health_bonus) > 0 else 1.0
            player.health = int(player.max_health * health_ratio)
    
    def draw_card(self, screen, x, y, width=300, height=450, selected=False, owned=False, active=False):
        """Отрисовывает карточку с изображением"""
        # Создаем поверхность для карточки
        card_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Красивый градиентный фон (от тёмно-фиолетового к розовому)
        for i in range(height):
            progress = i / height
            r = int(40 + (255 - 40) * progress)
            g = int(20 + (150 - 20) * progress)
            b = int(60 + (200 - 60) * progress)
            pygame.draw.line(card_surface, (r, g, b), (0, i), (width, i))
        
        # Рамка карточки (толще если выбрана или активна)
        border_color = GOLD if selected else (255, 100, 255) if active else (150, 100, 200)
        border_width = 5 if selected or active else 3
        pygame.draw.rect(card_surface, border_color, (0, 0, width, height), border_width)
        
        # Внутренняя рамка для красоты
        pygame.draw.rect(card_surface, (255, 255, 255, 50), (border_width, border_width, 
                                                              width - border_width * 2, height - border_width * 2), 1)
        
        # Изображение фембоя (если есть)
        image_y = 50
        image_height = 200
        if self.image:
            try:
                # Масштабируем изображение
                img_width = width - 40
                scaled_image = pygame.transform.scale(self.image, (img_width, image_height))
                # Центрируем изображение
                img_x = (width - img_width) // 2
                card_surface.blit(scaled_image, (img_x, image_y))
                
                # Полупрозрачная рамка вокруг изображения
                pygame.draw.rect(card_surface, (255, 255, 255, 100), 
                               (img_x - 2, image_y - 2, img_width + 4, image_height + 4), 2)
            except Exception as e:
                print(f"Ошибка отрисовки изображения: {e}")
        
        # Имя (заголовок) - сверху
        name_text = menu_font.render(self.name, True, GOLD)
        name_shadow = menu_font.render(self.name, True, (0, 0, 0))
        name_rect = name_text.get_rect(center=(width // 2, 25))
        # Тень для текста
        card_surface.blit(name_shadow, (name_rect.x + 2, name_rect.y + 2))
        card_surface.blit(name_text, name_rect)
        
        # Информация под изображением
        info_y = image_y + image_height + 15
        
        # Возраст
        age_text = small_font.render(f"Возраст: {self.age}", True, WHITE)
        card_surface.blit(age_text, (15, info_y))
        
        # Бафы (компактно)
        buffs_y = info_y + 25
        buff_texts = []
        if self.damage_bonus > 1.0:
            buff_texts.append(f"⚔ +{int((self.damage_bonus - 1) * 100)}% урон")
        if self.speed_bonus > 0:
            buff_texts.append(f"🏃 +{self.speed_bonus} скорость")
        if self.health_bonus > 0:
            buff_texts.append(f"❤ +{self.health_bonus} HP")
        
        for i, buff_text in enumerate(buff_texts):
            buff_render = small_font.render(buff_text, True, GOLD)
            card_surface.blit(buff_render, (15, buffs_y + i * 18))
        
        # Уникальная способность
        if self.special_ability:
            ability_y = buffs_y + len(buff_texts) * 18 + 10
            ability_text = small_font.render(f"✨ {self.special_ability}", True, (255, 200, 255))
            ability_lines = self._wrap_text(f"✨ {self.special_ability}", width - 30, small_font)
            for i, line in enumerate(ability_lines[:2]):
                line_render = small_font.render(line, True, (255, 200, 255))
                card_surface.blit(line_render, (15, ability_y + i * 16))
        
        # Статусы внизу
        status_y = height - 50
        if owned:
            owned_text = small_font.render("✓ В КОЛЛЕКЦИИ", True, GREEN)
            card_surface.blit(owned_text, (width - owned_text.get_width() - 10, status_y))
        if active:
            active_text = small_font.render("★ АКТИВНА", True, GOLD)
            card_surface.blit(active_text, (width - active_text.get_width() - 10, status_y + 20))
        
        # Цена (если не куплена) - внизу по центру
        if not owned:
            price_bg = pygame.Surface((width - 20, 35), pygame.SRCALPHA)
            price_bg.fill((0, 0, 0, 180))
            card_surface.blit(price_bg, (10, height - 40))
            price_text = dialog_font.render(f"{self.price} РУБ.", True, GOLD)
            price_rect = price_text.get_rect(center=(width // 2, height - 22))
            card_surface.blit(price_text, price_rect)
        
        # Блестки для красоты (если выбрана)
        if selected or active:
            import random
            random.seed(self.card_id)
            for _ in range(5):
                sparkle_x = random.randint(10, width - 10)
                sparkle_y = random.randint(10, height - 10)
                sparkle_size = random.randint(3, 5)
                sparkle_alpha = random.randint(150, 255)
                sparkle_surf = pygame.Surface((sparkle_size * 2, sparkle_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(sparkle_surf, (255, 255, 255, sparkle_alpha), 
                                 (sparkle_size, sparkle_size), sparkle_size)
                card_surface.blit(sparkle_surf, (sparkle_x - sparkle_size, sparkle_y - sparkle_size))
        
        screen.blit(card_surface, (x, y))
    
    def _wrap_text(self, text, max_width, font):
        """Переносит текст на несколько строк"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def to_dict(self):
        """Преобразует карточку в словарь для сохранения"""
        return {
            "card_id": self.card_id,
            "name": self.name,
            "age": self.age,
            "appearance": self.appearance,
            "style": self.style,
            "personality": self.personality,
            "bio": self.bio,
            "damage_bonus": self.damage_bonus,
            "speed_bonus": self.speed_bonus,
            "health_bonus": self.health_bonus,
            "special_ability": self.special_ability,
            "price": self.price,
            "image_path": self.image_path
        }
    
    @staticmethod
    def from_dict(data):
        """Создает карточку из словаря"""
        return Card(
            card_id=data["card_id"],
            name=data["name"],
            age=data["age"],
            appearance=data["appearance"],
            style=data["style"],
            personality=data["personality"],
            bio=data["bio"],
            damage_bonus=data.get("damage_bonus", 0),
            speed_bonus=data.get("speed_bonus", 0),
            health_bonus=data.get("health_bonus", 0),
            special_ability=data.get("special_ability"),
            price=data.get("price", 0),
            image_path=data.get("image_path")
        )

