"""
Система кейсов с карточками фембоев - открытие как в CS2
"""
import random
import pygame
import math
from game.config import SCREEN_WIDTH, SCREEN_HEIGHT, BASE_WIDTH, BASE_HEIGHT, title_font, menu_font, dialog_font, small_font, GOLD, WHITE, LIGHT_GREY, RED, BLUE, GREEN, BLACK, DARK_GREY


class Case:
    """Кейс с карточками"""
    def __init__(self, name, price, color, rarity):
        self.name = name
        self.price = price
        self.color = color
        self.rarity = rarity  # "common", "rare", "epic", "legendary"
    
    def get_reward_card(self, all_cards):
        """Возвращает случайную карточку в зависимости от редкости кейса"""
        # Фильтруем карточки по редкости
        cards_by_rarity = {
            "common": [c for c in all_cards if getattr(c, 'rarity', 'common') == 'common'],
            "rare": [c for c in all_cards if getattr(c, 'rarity', 'common') == 'rare'],
            "epic": [c for c in all_cards if getattr(c, 'rarity', 'common') == 'epic'],
            "legendary": [c for c in all_cards if getattr(c, 'rarity', 'common') == 'legendary']
        }
        
        # Выбираем карточку в зависимости от редкости кейса
        if self.rarity == "common":
            # 70% common, 25% rare, 5% epic
            rand = random.random()
            if rand < 0.70:
                pool = cards_by_rarity["common"] if cards_by_rarity["common"] else all_cards
            elif rand < 0.95:
                pool = cards_by_rarity["rare"] if cards_by_rarity["rare"] else all_cards
            else:
                pool = cards_by_rarity["epic"] if cards_by_rarity["epic"] else all_cards
        elif self.rarity == "rare":
            # 50% rare, 40% epic, 10% legendary
            rand = random.random()
            if rand < 0.50:
                pool = cards_by_rarity["rare"] if cards_by_rarity["rare"] else all_cards
            elif rand < 0.90:
                pool = cards_by_rarity["epic"] if cards_by_rarity["epic"] else all_cards
            else:
                pool = cards_by_rarity["legendary"] if cards_by_rarity["legendary"] else all_cards
        elif self.rarity == "epic":
            # 30% epic, 60% legendary, 10% rare
            rand = random.random()
            if rand < 0.30:
                pool = cards_by_rarity["epic"] if cards_by_rarity["epic"] else all_cards
            elif rand < 0.90:
                pool = cards_by_rarity["legendary"] if cards_by_rarity["legendary"] else all_cards
            else:
                pool = cards_by_rarity["rare"] if cards_by_rarity["rare"] else all_cards
        else:  # legendary
            # 20% epic, 80% legendary
            rand = random.random()
            if rand < 0.20:
                pool = cards_by_rarity["epic"] if cards_by_rarity["epic"] else all_cards
            else:
                pool = cards_by_rarity["legendary"] if cards_by_rarity["legendary"] else all_cards
        
        if not pool:
            pool = all_cards
        
        return random.choice(pool)


class CaseSystem:
    """Система управления кейсами с анимацией CS2"""
    def __init__(self, all_cards):
        self.all_cards = all_cards
        self.cases = [
            Case("ОБЫЧНЫЙ КЕЙС", 500, LIGHT_GREY, "common"),
            Case("РЕДКИЙ КЕЙС", 1500, BLUE, "rare"),
            Case("ЭПИЧЕСКИЙ КЕЙС", 4000, (150, 50, 200), "epic"),
            Case("ЛЕГЕНДАРНЫЙ КЕЙС", 10000, GOLD, "legendary"),
        ]
        self.selected_case_index = 0
        
        # Анимация открытия (как в CS2)
        self.is_opening = False
        self.is_spinning = False  # Флаг прокрутки
        self.opening_timer = 0
        self.current_reward_card = None
        self.showing_reward = False
        self.reward_timer = 0
        self.reward_duration = 300  # 5 секунд показа награды
        
        # Для анимации вращения карточек
        self.card_slots = []  # Список карточек для показа в анимации
        self.scroll_position = 0.0  # Позиция прокрутки (float для плавности)
        self.scroll_speed = 0.0
        self.target_card_index = 0
        self.is_slowing_down = False  # Флаг замедления
        self.stop_requested = False  # Запрос на остановку
    
    def buy_case(self, player, case_index):
        """Покупка кейса"""
        if case_index < 0 or case_index >= len(self.cases):
            return False, "Неверный индекс кейса"
        
        case = self.cases[case_index]
        if player.money < case.price:
            return False, f"Недостаточно монет! Нужно {case.price}, у вас {player.money}"
        
        player.money -= case.price
        return True, f"Кейс '{case.name}' куплен за {case.price} монет!"
    
    def start_opening(self, case_index):
        """Начинает анимацию открытия кейса"""
        if case_index < 0 or case_index >= len(self.cases):
            return None
        
        case = self.cases[case_index]
        
        # Получаем награду
        reward_card = case.get_reward_card(self.all_cards)
        self.current_reward_card = reward_card
        
        # Создаем список карточек для анимации (дублируем для бесконечной прокрутки)
        self.card_slots = []
        for _ in range(3):  # Повторяем 3 раза для плавной прокрутки
            shuffled = self.all_cards.copy()
            random.shuffle(shuffled)
            self.card_slots.extend(shuffled)
        
        # Находим индекс награды в списке (берем из середины)
        try:
            # Ищем карточку в середине списка
            mid_start = len(self.card_slots) // 3
            mid_end = len(self.card_slots) * 2 // 3
            for i in range(mid_start, mid_end):
                if self.card_slots[i].card_id == reward_card.card_id:
                    self.target_card_index = i
                    break
            else:
                self.target_card_index = len(self.card_slots) // 2
        except:
            self.target_card_index = len(self.card_slots) // 2
        
        # Начинаем анимацию
        self.is_opening = True
        self.is_spinning = True
        self.opening_timer = 0
        self.showing_reward = False
        self.reward_timer = 0
        self.scroll_position = 0.0
        self.scroll_speed = 25.0  # Начальная скорость прокрутки
        self.is_slowing_down = False
        self.stop_requested = False
        
        return reward_card
    
    def request_stop(self):
        """Запрашивает остановку прокрутки (нажатие кнопки)"""
        if self.is_spinning and not self.is_slowing_down:
            self.stop_requested = True
    
    def update(self):
        """Обновление анимации"""
        if self.is_opening and self.is_spinning:
            self.opening_timer += 1
            
            # Фаза 1: Быстрая прокрутка (первые 60 кадров или пока не нажата кнопка)
            if not self.stop_requested and self.opening_timer < 60:
                self.scroll_position += self.scroll_speed
                # Небольшое случайное замедление для реалистичности
                if random.random() < 0.1:
                    self.scroll_speed = max(15.0, self.scroll_speed - 0.2)
            
            # Фаза 2: Замедление после нажатия кнопки или через 60 кадров
            elif self.stop_requested or self.opening_timer >= 60:
                if not self.is_slowing_down:
                    self.is_slowing_down = True
                
                # Замедляем прокрутку
                self.scroll_speed = max(0.1, self.scroll_speed * 0.92)
                self.scroll_position += self.scroll_speed
                
                # Проверяем, достигли ли мы нужной карточки
                card_width = 280
                total_width = len(self.card_slots) * card_width
                target_pos = self.target_card_index * card_width
                current_pos = self.scroll_position % total_width
                
                # Нормализуем позицию для правильного сравнения
                if current_pos > total_width / 2:
                    current_pos -= total_width
                
                # Вычисляем разницу
                diff = target_pos - current_pos
                
                # Если разница слишком большая, корректируем
                if diff > total_width / 2:
                    diff -= total_width
                elif diff < -total_width / 2:
                    diff += total_width
                
                # Если скорость очень маленькая и мы близко к цели - останавливаемся
                if self.scroll_speed < 0.3 and abs(diff) < card_width * 0.5:
                    # Точная остановка на награде
                    self.scroll_position = self.target_card_index * card_width
                    self.is_spinning = False
                    self.is_opening = False
                    self.showing_reward = True
                    self.reward_timer = 0
        
        if self.showing_reward:
            self.reward_timer += 1
            if self.reward_timer >= self.reward_duration:
                self.showing_reward = False
                self.current_reward_card = None
    
    def _get_rarity_glow(self, rarity):
        """Возвращает цвет свечения в зависимости от редкости"""
        glow_colors = {
            'common': (150, 150, 150, 100),  # Серое свечение
            'rare': (50, 150, 255, 150),     # Синее свечение
            'epic': (200, 50, 255, 200),     # Фиолетовое свечение
            'legendary': (255, 215, 0, 255)  # Золотое свечение
        }
        return glow_colors.get(rarity, (150, 150, 150, 100))
    
    def _get_rarity_particles(self, rarity):
        """Возвращает цвет частиц в зависимости от редкости"""
        particle_colors = {
            'common': (200, 200, 200),
            'rare': (100, 200, 255),
            'epic': (255, 100, 255),
            'legendary': (255, 255, 100)
        }
        return particle_colors.get(rarity, (200, 200, 200))
    
    def draw(self, screen, player):
        """Отрисовка меню кейсов"""
        # Фон
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))
        
        # Если идет анимация открытия
        if self.is_opening or self.is_spinning:
            self._draw_opening_animation(screen)
            return
        
        # Если показываем награду
        if self.showing_reward and self.current_reward_card:
            self._draw_reward(screen)
            return
        
        # Обычное меню выбора кейсов
        # Заголовок
        title = title_font.render("КЕЙСЫ", True, GOLD)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        # Монеты игрока
        coins_text = menu_font.render(f"ВАШИ МОНЕТЫ: {player.money}", True, GOLD)
        screen.blit(coins_text, (SCREEN_WIDTH // 2 - coins_text.get_width() // 2, 120))
        
        # Список кейсов
        case_start_y = 200
        case_width = 600
        case_height = 120
        case_spacing = 20
        
        for i, case in enumerate(self.cases):
            y_pos = case_start_y + i * (case_height + case_spacing)
            x_pos = SCREEN_WIDTH // 2 - case_width // 2
            
            # Подсветка выбранного кейса
            is_selected = i == self.selected_case_index
            border_color = GOLD if is_selected else case.color
            border_width = 4 if is_selected else 2
            
            # Фон кейса
            pygame.draw.rect(screen, (30, 30, 40), (x_pos, y_pos, case_width, case_height))
            pygame.draw.rect(screen, border_color, (x_pos, y_pos, case_width, case_height), border_width)
            
            # Название кейса
            name_text = menu_font.render(case.name, True, case.color)
            screen.blit(name_text, (x_pos + 20, y_pos + 15))
            
            # Цена
            price_text = dialog_font.render(f"Цена: {case.price} монет", True, GOLD)
            screen.blit(price_text, (x_pos + 20, y_pos + 50))
            
            # Редкость
            rarity_text = small_font.render(f"Редкость: {case.rarity.upper()}", True, case.color)
            screen.blit(rarity_text, (x_pos + 20, y_pos + 80))
            
            # Кнопка покупки/открытия
            button_x = x_pos + case_width - 200
            button_y = y_pos + 30
            button_width = 180
            button_height = 60
            
            can_afford = player.money >= case.price
            button_color = GOLD if can_afford and is_selected else (LIGHT_GREY if can_afford else (50, 50, 50))
            
            pygame.draw.rect(screen, button_color, (button_x, button_y, button_width, button_height))
            pygame.draw.rect(screen, WHITE, (button_x, button_y, button_width, button_height), 2)
            
            button_text = dialog_font.render("ОТКРЫТЬ" if can_afford else "НЕДОСТАТОЧНО", True, BLACK if can_afford else RED)
            screen.blit(button_text, (button_x + button_width // 2 - button_text.get_width() // 2, 
                                     button_y + button_height // 2 - button_text.get_height() // 2))
        
        # Подсказки
        hint_y = SCREEN_HEIGHT - 150
        hints = [
            "СТРЕЛКИ ВВЕРХ/ВНИЗ - выбор кейса",
            "ENTER/ПРОБЕЛ - открыть кейс",
            "ESC - вернуться в меню"
        ]
        
        for i, hint in enumerate(hints):
            hint_text = small_font.render(hint, True, LIGHT_GREY)
            screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, hint_y + i * 25))
    
    def _draw_opening_animation(self, screen):
        """Анимация открытия кейса в стиле CS2"""
        # Фон с градиентом
        for y in range(SCREEN_HEIGHT):
            progress = y / SCREEN_HEIGHT
            r = int(10 + (5 * progress))
            g = int(10 + (5 * progress))
            b = int(20 + (10 * progress))
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Заголовок
        title = title_font.render("ОТКРЫВАЕМ КЕЙС...", True, GOLD)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))
        
        # Область для прокрутки карточек
        card_area_y = 150
        card_area_height = 550
        card_width = 280
        card_height = 420
        
        # Центральная позиция (где будет остановка)
        center_x = SCREEN_WIDTH // 2
        
        # Рисуем карточки с эффектом прокрутки
        visible_range = 7  # Сколько карточек показываем
        
        for i in range(-visible_range, visible_range + 1):
            # Вычисляем индекс карточки
            base_index = int(self.scroll_position / card_width)
            card_index = (base_index + i) % len(self.card_slots)
            
            card = self.card_slots[card_index]
            
            # Позиция карточки
            offset = (self.scroll_position % card_width)
            card_x = center_x - card_width // 2 - offset + i * card_width
            
            # Вычисляем расстояние от центра
            distance_from_center = abs(card_x - center_x + card_width // 2)
            max_distance = card_width * visible_range
            
            # Масштаб и прозрачность в зависимости от расстояния
            scale = max(0.4, 1.0 - (distance_from_center / max_distance) * 0.6)
            alpha = max(80, int(255 * (1.0 - distance_from_center / max_distance * 0.7)))
            
            # Если это награда - увеличиваем масштаб
            if card == self.current_reward_card and self.is_slowing_down:
                scale = min(1.15, scale + 0.15)
                alpha = 255
            
            # Создаем поверхность для карточки
            scaled_width = int(card_width * scale)
            scaled_height = int(card_height * scale)
            card_surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
            
            # Рисуем карточку
            card.draw_card(card_surface, 0, 0, scaled_width, scaled_height)
            
            # Применяем прозрачность
            card_surface.set_alpha(alpha)
            
            # Позиция для отрисовки
            card_y = card_area_y + (card_area_height - scaled_height) // 2
            screen.blit(card_surface, (card_x, card_y))
            
            # Свечение в зависимости от редкости (только для центральных карточек)
            if distance_from_center < card_width * 2:
                rarity = getattr(card, 'rarity', 'common')
                glow_color = self._get_rarity_glow(rarity)
                
                # Рисуем свечение вокруг карточки
                glow_size = int(scaled_width * 1.15)
                glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
                
                # Градиентное свечение
                for radius in range(glow_size // 2, 0, -2):
                    alpha = int(glow_color[3] * (1 - radius / (glow_size // 2)))
                    if alpha > 0:
                        glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                        pygame.draw.circle(glow_surf, (*glow_color[:3], alpha), (radius, radius), radius)
                        screen.blit(glow_surf, (card_x + scaled_width // 2 - radius, card_y + scaled_height // 2 - radius))
        
        # Подсветка центральной области с эффектом пульсации
        pulse = math.sin(pygame.time.get_ticks() * 0.01) * 0.1 + 1.0
        highlight_width = int((card_width + 30) * pulse)
        highlight_height = int((card_height + 30) * pulse)
        
        highlight = pygame.Surface((highlight_width, highlight_height), pygame.SRCALPHA)
        
        # Градиентная рамка
        for i in range(5):
            alpha = int(100 * (1 - i / 5))
            color = (*GOLD[:3], alpha)
            pygame.draw.rect(highlight, color, (i, i, highlight_width - i*2, highlight_height - i*2), 2)
        
        screen.blit(highlight, (center_x - highlight_width // 2, card_area_y + (card_area_height - highlight_height) // 2))
        
        # Кнопка остановки (если еще крутится)
        if self.is_spinning and not self.is_slowing_down:
            button_y = SCREEN_HEIGHT - 120
            button_width = 300
            button_height = 60
            
            # Пульсирующая кнопка
            pulse_alpha = int(180 + math.sin(pygame.time.get_ticks() * 0.02) * 75)
            
            button_surface = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
            button_surface.fill((255, 100, 100, pulse_alpha))
            pygame.draw.rect(button_surface, RED, (0, 0, button_width, button_height), 3)
            
            screen.blit(button_surface, (SCREEN_WIDTH // 2 - button_width // 2, button_y))
            
            button_text = menu_font.render("НАЖМИ ДЛЯ ОСТАНОВКИ", True, WHITE)
            screen.blit(button_text, (SCREEN_WIDTH // 2 - button_text.get_width() // 2, button_y + 15))
        
        # Индикатор скорости прокрутки
        if self.is_spinning:
            speed_text = small_font.render(f"Скорость: {int(self.scroll_speed * 10)}", True, LIGHT_GREY)
            screen.blit(speed_text, (SCREEN_WIDTH // 2 - speed_text.get_width() // 2, SCREEN_HEIGHT - 50))
    
    def _draw_reward(self, screen):
        """Отрисовка полученной награды"""
        if not self.current_reward_card:
            return
        
        card = self.current_reward_card
        rarity = getattr(card, 'rarity', 'common')
        
        # Фон с эффектом свечения редкости
        glow_color = self._get_rarity_glow(rarity)
        particle_color = self._get_rarity_particles(rarity)
        
        # Градиентный фон
        for y in range(SCREEN_HEIGHT):
            progress = y / SCREEN_HEIGHT
            r = int(glow_color[0] * progress * 0.3)
            g = int(glow_color[1] * progress * 0.3)
            b = int(glow_color[2] * progress * 0.3)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Частицы в фоне
        import random
        random.seed(42)
        for _ in range(30):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            size = random.randint(2, 5)
            alpha = random.randint(50, 150)
            particle_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, (*particle_color, alpha), (size, size), size)
            screen.blit(particle_surf, (x - size, y - size))
        
        # Заголовок с эффектом
        title_pulse = math.sin(pygame.time.get_ticks() * 0.01) * 5 + 1
        title = title_font.render("ВЫ ПОЛУЧИЛИ!", True, GOLD)
        title_shadow = title_font.render("ВЫ ПОЛУЧИЛИ!", True, (0, 0, 0))
        screen.blit(title_shadow, (SCREEN_WIDTH // 2 - title.get_width() // 2 + 3, 53))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
        
        # Редкость карточки с свечением
        rarity_colors = {
            'common': (LIGHT_GREY, "ОБЫЧНАЯ"),
            'rare': (BLUE, "РЕДКАЯ"),
            'epic': ((150, 50, 200), "ЭПИЧЕСКАЯ"),
            'legendary': (GOLD, "ЛЕГЕНДАРНАЯ")
        }
        rarity_color, rarity_name = rarity_colors.get(rarity, (LIGHT_GREY, "ОБЫЧНАЯ"))
        
        # Свечение вокруг текста редкости
        rarity_text = menu_font.render(f"РЕДКОСТЬ: {rarity_name}", True, rarity_color)
        glow_surf = pygame.Surface((rarity_text.get_width() + 20, rarity_text.get_height() + 20), pygame.SRCALPHA)
        for radius in range(15, 0, -2):
            alpha = int(glow_color[3] * (1 - radius / 15))
            if alpha > 0:
                pygame.draw.circle(glow_surf, (*glow_color[:3], alpha), 
                                 (rarity_text.get_width() // 2 + 10, rarity_text.get_height() // 2 + 10), radius)
        screen.blit(glow_surf, (SCREEN_WIDTH // 2 - rarity_text.get_width() // 2 - 10, 110))
        screen.blit(rarity_text, (SCREEN_WIDTH // 2 - rarity_text.get_width() // 2, 120))
        
        # Карточка по центру с эффектом свечения
        card_x = SCREEN_WIDTH // 2 - 220
        card_y = 200
        
        # Свечение вокруг карточки
        glow_size = 500
        glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        for radius in range(glow_size // 2, 0, -5):
            alpha = int(glow_color[3] * (1 - radius / (glow_size // 2)) * 0.5)
            if alpha > 0:
                pygame.draw.circle(glow_surf, (*glow_color[:3], alpha), (glow_size // 2, glow_size // 2), radius)
        screen.blit(glow_surf, (card_x + 220 - glow_size // 2, card_y + 300 - glow_size // 2))
        
        # Сама карточка
        card.draw_card(screen, card_x, card_y, 440, 600, selected=True)
        
        # Подсказка
        hint_text = small_font.render("Нажми ESC для продолжения", True, LIGHT_GREY)
        screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, SCREEN_HEIGHT - 80))
