"""
Класс магазина
"""
import pygame
from game.config import SCREEN_WIDTH, SCREEN_HEIGHT, title_font, menu_font, dialog_font, small_font, GOLD, WHITE, LIGHT_GREY


class Shop:
    def __init__(self):
        self.items = [
            {"name": "ПАТРОНЫ ПИСТОЛЕТ", "price": 50, "type": "ammo", "weapon_index": 0, "amount": 30},
            {"name": "ПАТРОНЫ АВТОМАТ", "price": 80, "type": "ammo", "weapon_index": 1, "amount": 60},
            {"name": "ПАТРОНЫ ДРОБОВИК", "price": 120, "type": "ammo", "weapon_index": 2, "amount": 12},
            {"name": "ПАТРОНЫ СНАЙПЕРКА", "price": 200, "type": "ammo", "weapon_index": 3, "amount": 10},
            {"name": "ПАТРОНЫ ПУЛЕМЁТ", "price": 150, "type": "ammo", "weapon_index": 4, "amount": 100},
            {"name": "АПТЕЧКА", "price": 300, "type": "health", "amount": 50},
            {"name": "УЛУЧШЕНИЕ УРОНА", "price": 2000, "type": "upgrade", "stat": "damage"},
            {"name": "УЛУЧШЕНИЕ СКОРОСТИ", "price": 1500, "type": "upgrade", "stat": "speed"},
            {"name": "УЛУЧШЕНИЕ ЗДОРОВЬЯ", "price": 2500, "type": "upgrade", "stat": "health"},
            {"name": "ПАТРОНЫ ГРАНАТОМЁТ", "price": 500, "type": "ammo", "weapon_index": 5, "amount": 5},
            {"name": "ПАТРОНЫ РЕВОЛЬВЕР", "price": 100, "type": "ammo", "weapon_index": 6, "amount": 18},
            {"name": "ПАТРОНЫ АВТОМАТ-2", "price": 120, "type": "ammo", "weapon_index": 7, "amount": 80},
            {"name": "БОЛЬШАЯ АПТЕЧКА", "price": 600, "type": "health", "amount": 100},
            {"name": "УЛУЧШЕНИЕ СКОРОСТИ СТРЕЛЬБЫ", "price": 3000, "type": "upgrade", "stat": "firerate"},
            {"name": "УЛУЧШЕНИЕ ТОЧНОСТИ", "price": 2500, "type": "upgrade", "stat": "accuracy"},
            {"name": "БРОНЯ", "price": 4000, "type": "upgrade", "stat": "armor"},
        ]
        self.selected_item = 0

    def buy_item(self, item, player, save_callback=None):
        if player.money >= item["price"]:
            player.money -= item["price"]
            if save_callback:
                save_callback()  # Сохраняем при покупке
            if item["type"] == "ammo":
                weapon = player.weapons[item["weapon_index"]]
                weapon.ammo = min(weapon.max_ammo, weapon.ammo + item["amount"])
                return True, f"Куплено: {item['name']}"
            elif item["type"] == "health":
                player.health = min(player.max_health, player.health + item["amount"])
                return True, f"Восстановлено {item['amount']} здоровья"
            elif item["type"] == "upgrade":
                if item["stat"] == "damage":
                    for weapon in player.weapons:
                        weapon.damage = int(weapon.damage * 1.2)
                    return True, "Урон всех оружий увеличен на 20%"
                elif item["stat"] == "speed":
                    player.speed = min(8, player.speed + 0.5)
                    return True, "Скорость увеличена"
                elif item["stat"] == "health":
                    player.max_health += 20
                    player.health += 20
                    return True, "Максимальное здоровье +20"
                elif item["stat"] == "firerate":
                    for weapon in player.weapons:
                        weapon.fire_rate = weapon.fire_rate * 1.15
                    return True, "Скорострельность всех оружий +15%"
                elif item["stat"] == "accuracy":
                    for weapon in player.weapons:
                        weapon.spread = max(0.01, weapon.spread * 0.8)
                    return True, "Точность всех оружий +20%"
                elif item["stat"] == "armor":
                    player.armor = getattr(player, 'armor', 0) + 10
                    return True, "Броня +10 (снижение урона)"
        return False, "Недостаточно денег!"

    def draw(self, screen, player):
        # Фон магазина
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        # Заголовок
        title = title_font.render("МАГАЗИН ОРУЖИЯ", True, GOLD)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

        # Деньги игрока
        money_text = menu_font.render(f"БАБЛО: {player.money} РУБ.", True, GOLD)
        screen.blit(money_text, (SCREEN_WIDTH // 2 - money_text.get_width() // 2, 120))

        # Список товаров
        start_y = 180
        item_height = 50
        visible_items = 8
        start_index = max(0, self.selected_item - visible_items // 2)
        end_index = min(len(self.items), start_index + visible_items)

        for i in range(start_index, end_index):
            item = self.items[i]
            y_pos = start_y + (i - start_index) * item_height
            
            # Выделение выбранного товара
            if i == self.selected_item:
                pygame.draw.rect(screen, GOLD, (200, y_pos - 5, SCREEN_WIDTH - 400, item_height), 3)
            
            # Название товара
            item_text = dialog_font.render(item["name"], True, WHITE)
            screen.blit(item_text, (220, y_pos))
            
            # Цена
            price_text = dialog_font.render(f"{item['price']} РУБ.", True, GOLD)
            screen.blit(price_text, (SCREEN_WIDTH - 300, y_pos))

        # Подсказки
        hint1 = small_font.render("СТРЕЛКИ ВВЕРХ/ВНИЗ - ВЫБОР | ENTER - КУПИТЬ | ESC - ВЫХОД", True, LIGHT_GREY)
        screen.blit(hint1, (SCREEN_WIDTH // 2 - hint1.get_width() // 2, SCREEN_HEIGHT - 80))

        # Информация о выбранном товаре
        selected = self.items[self.selected_item]
        info_y = SCREEN_HEIGHT - 150
        if selected["type"] == "ammo":
            weapon = player.weapons[selected["weapon_index"]]
            info_text = small_font.render(f"Текущие патроны: {weapon.ammo}/{weapon.max_ammo}", True, WHITE)
            screen.blit(info_text, (SCREEN_WIDTH // 2 - info_text.get_width() // 2, info_y))
        elif selected["type"] == "health":
            info_text = small_font.render(f"Текущее здоровье: {player.health}/{player.max_health}", True, WHITE)
            screen.blit(info_text, (SCREEN_WIDTH // 2 - info_text.get_width() // 2, info_y))

