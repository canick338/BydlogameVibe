"""
Классы Location и City для открытого мира
"""
import pygame
import math
import random
from game.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BUILDING_COLORS, GOLD, LIGHT_GREY, BLUE,
    ASPHALT, small_font
)


class Location:
    def __init__(self, name, description, color_modifier=(1.0, 1.0, 1.0), world_pos=(0, 0)):
        self.name = name
        self.description = description
        self.color_modifier = color_modifier
        self.world_x, self.world_y = world_pos
        self.buildings = []
        self.shop_pos = None
        self.generate_buildings()

    def generate_buildings(self):
        # Улучшенная генерация зданий с правильным расположением
        building_positions = [
            # Левая сторона
            (80, 150, 120, 200), (80, 400, 120, 180), (80, 620, 120, 140),
            # Центр-лево
            (250, 100, 140, 250), (250, 400, 140, 200), (250, 650, 140, 100),
            # Центр-право
            (650, 120, 150, 280), (650, 450, 150, 220), (650, 700, 150, 60),
            # Правая сторона
            (820, 180, 130, 200), (820, 430, 130, 180), (820, 650, 130, 110),
        ]
        
        for x, y, width, height in building_positions:
            color = random.choice(BUILDING_COLORS)
            # Применяем модификатор цвета локации
            color = tuple(int(c * self.color_modifier[i]) for i, c in enumerate(color))
            windows = []

            # Генерация окон
            for wx in range(x + 15, x + width - 15, 25):
                for wy in range(y + 15, y + height - 15, 30):
                    if random.random() > 0.4:
                        lit = random.random() > 0.3
                        windows.append((wx, wy, lit))

            self.buildings.append((x, y, width, height, color, windows))
        
        # Магазин всегда в центре
        self.shop_pos = (SCREEN_WIDTH // 2 - 40, SCREEN_HEIGHT // 2 - 40, 80, 80)

    def draw(self, screen):
        # Здания
        for x, y, width, height, color, windows in self.buildings:
            # Основное здание
            pygame.draw.rect(screen, color, (x, y, width, height))

            # Тень
            pygame.draw.polygon(screen, (20, 20, 30), [
                (x + width, y),
                (x + width + 10, y - 10),
                (x + width + 10, y + height - 10),
                (x + width, y + height)
            ])

            # Окна
            for wx, wy, lit in windows:
                window_color = (255, 255, 150) if lit else (80, 80, 120)
                pygame.draw.rect(screen, window_color, (wx, wy, 18, 22))

            # Дверь
            door_x = x + width // 2 - 15
            door_y = y + height - 50
            pygame.draw.rect(screen, (40, 30, 20), (door_x, door_y, 30, 50))
        
        # Магазин
        if self.shop_pos:
            sx, sy, sw, sh = self.shop_pos
            # Здание магазина
            pygame.draw.rect(screen, (150, 100, 50), (sx, sy, sw, sh))
            pygame.draw.rect(screen, GOLD, (sx, sy, sw, sh), 3)
            # Вывеска
            sign_text = small_font.render("МАГАЗИН", True, GOLD)
            screen.blit(sign_text, (sx + sw // 2 - sign_text.get_width() // 2, sy - 20))


class City:
    def __init__(self):
        self.locations = []
        self.current_location_index = 0
        self.world_size = 5000  # Размер открытого мира
        self.camera_x = 0
        self.camera_y = 0
        self.init_locations()
        self.transition_points = []  # Точки перехода между локациями
        self.init_transition_points()

    def init_locations(self):
        self.locations = [
            Location("ЦЕНТРАЛЬНЫЙ РАЙОН", "Богатый район с высокими зданиями", (1.2, 1.1, 1.0), (2500, 2500)),
            Location("ПРОМЗОНА", "Заброшенные заводы и склады", (0.7, 0.7, 0.8), (1000, 1000)),
            Location("СТАРЫЙ ГОРОД", "Узкие улочки и старые дома", (0.9, 0.85, 0.9), (1500, 3500)),
            Location("ПОРТОВАЯ ЗОНА", "Доки и причалы", (0.8, 0.9, 1.1), (4000, 2000)),
            Location("ЭЛИТНЫЙ КВАРТАЛ", "Роскошные особняки", (1.3, 1.2, 1.1), (3500, 1000)),
            Location("ГЕТТО", "Опасные улицы, полные бандитов", (0.6, 0.5, 0.6), (500, 3000)),
            Location("ПРОМЫШЛЕННЫЙ РАЙОН", "Заводы и фабрики", (0.8, 0.8, 0.9), (4500, 4000)),
            Location("ТОРГОВЫЙ ЦЕНТР", "Магазины и рынки", (1.1, 1.0, 0.9), (2000, 1500))
        ]

    def init_transition_points(self):
        # Создаём точки перехода между локациями
        for i, loc in enumerate(self.locations):
            for j, other_loc in enumerate(self.locations):
                if i != j:
                    # Создаём переходы между соседними локациями
                    dist = math.sqrt((loc.world_x - other_loc.world_x)**2 + (loc.world_y - other_loc.world_y)**2)
                    if dist < 2000:  # Только близкие локации
                        mid_x = (loc.world_x + other_loc.world_x) // 2
                        mid_y = (loc.world_y + other_loc.world_y) // 2
                        self.transition_points.append({
                            'x': mid_x, 'y': mid_y,
                            'from': i, 'to': j,
                            'radius': 100
                        })

    def get_current_location(self):
        return self.locations[self.current_location_index]
    
    def update_camera(self, player_x, player_y):
        # Камера следует за игроком в открытом мире
        self.camera_x = player_x - SCREEN_WIDTH // 2
        self.camera_y = player_y - SCREEN_HEIGHT // 2
        
        # Ограничиваем камеру границами мира
        self.camera_x = max(0, min(self.world_size - SCREEN_WIDTH, self.camera_x))
        self.camera_y = max(0, min(self.world_size - SCREEN_HEIGHT, self.camera_y))
    
    def check_location_transition(self, player_x, player_y):
        # Проверяем переходы между локациями
        for tp in self.transition_points:
            dist = math.sqrt((player_x - tp['x'])**2 + (player_y - tp['y'])**2)
            if dist < tp['radius']:
                self.current_location_index = tp['to']
                return True
        return False

    def draw(self, screen, player_x=0, player_y=0):
        # Фон открытого мира с улучшенным градиентом
        for y in range(0, SCREEN_HEIGHT, 10):
            color_factor = y / SCREEN_HEIGHT
            # Более насыщенный градиент
            color = (
                int(10 + color_factor * 15),
                int(12 + color_factor * 18),
                int(20 + color_factor * 25)
            )
            pygame.draw.rect(screen, color, (0, y, SCREEN_WIDTH, 10))
        
        # Рисуем улучшенную сетку с эффектом глубины
        grid_color = (30, 30, 40)
        grid_bright = (40, 40, 50)
        for x in range(int(self.camera_x % 200), SCREEN_WIDTH + 200, 200):
            screen_x = x - int(self.camera_x % 200)
            pygame.draw.line(screen, grid_bright, (screen_x, 0), (screen_x, SCREEN_HEIGHT), 2)
        for y in range(int(self.camera_y % 200), SCREEN_HEIGHT + 200, 200):
            screen_y = y - int(self.camera_y % 200)
            pygame.draw.line(screen, grid_bright, (0, screen_y), (SCREEN_WIDTH, screen_y), 2)
        
        # Мелкая сетка
        for x in range(int(self.camera_x % 50), SCREEN_WIDTH + 50, 50):
            screen_x = x - int(self.camera_x % 50)
            pygame.draw.line(screen, grid_color, (screen_x, 0), (screen_x, SCREEN_HEIGHT), 1)
        for y in range(int(self.camera_y % 50), SCREEN_HEIGHT + 50, 50):
            screen_y = y - int(self.camera_y % 50)
            pygame.draw.line(screen, grid_color, (0, screen_y), (SCREEN_WIDTH, screen_y), 1)
        
        # Добавляем случайные объекты на карте (деревья, столбы, мусор)
        for i in range(20):
            obj_x = (self.camera_x + i * 300) % (self.world_size - 200) + 100
            obj_y = (self.camera_y + i * 250) % (self.world_size - 200) + 100
            screen_x = obj_x - self.camera_x
            screen_y = obj_y - self.camera_y
            
            if -50 < screen_x < SCREEN_WIDTH + 50 and -50 < screen_y < SCREEN_HEIGHT + 50:
                obj_type = i % 4
                if obj_type == 0:  # Дерево
                    # Ствол
                    pygame.draw.rect(screen, (60, 40, 20), (screen_x - 5, screen_y, 10, 30))
                    # Крона
                    pygame.draw.circle(screen, (20, 80, 20), (int(screen_x), int(screen_y - 10)), 20)
                    pygame.draw.circle(screen, (30, 100, 30), (int(screen_x), int(screen_y - 10)), 15)
                elif obj_type == 1:  # Столб
                    pygame.draw.rect(screen, (50, 50, 50), (screen_x - 3, screen_y, 6, 40))
                    # Фонарь
                    pygame.draw.circle(screen, (200, 200, 150), (int(screen_x), int(screen_y - 5)), 8)
                elif obj_type == 2:  # Мусорный бак
                    pygame.draw.rect(screen, (40, 40, 50), (screen_x - 8, screen_y, 16, 20))
                    pygame.draw.rect(screen, (60, 60, 70), (screen_x - 8, screen_y, 16, 5))
                elif obj_type == 3:  # Камень/препятствие
                    pygame.draw.circle(screen, (70, 70, 80), (int(screen_x), int(screen_y)), 12)
                    pygame.draw.circle(screen, (50, 50, 60), (int(screen_x), int(screen_y)), 8)
        
        # Рисуем все локации в открытом мире
        for i, loc in enumerate(self.locations):
            # Позиция локации относительно камеры
            loc_screen_x = loc.world_x - self.camera_x
            loc_screen_y = loc.world_y - self.camera_y
            
            # Рисуем только видимые локации
            if -500 < loc_screen_x < SCREEN_WIDTH + 500 and -500 < loc_screen_y < SCREEN_HEIGHT + 500:
                # Мини-индикатор локации с эффектом свечения
                if i == self.current_location_index:
                    # Свечение
                    glow_surface = pygame.Surface((120, 120), pygame.SRCALPHA)
                    for radius in range(60, 0, -5):
                        alpha = int(100 * (1 - radius / 60))
                        pygame.draw.circle(glow_surface, (*GOLD[:3], alpha), (60, 60), radius)
                    screen.blit(glow_surface, (int(loc_screen_x) - 60, int(loc_screen_y) - 60))
                    
                    pygame.draw.circle(screen, GOLD, (int(loc_screen_x), int(loc_screen_y)), 50, 4)
                    pygame.draw.circle(screen, (255, 255, 150), (int(loc_screen_x), int(loc_screen_y)), 45, 2)
                    name_text = small_font.render(loc.name, True, GOLD)
                    screen.blit(name_text, (int(loc_screen_x) - name_text.get_width() // 2, int(loc_screen_y) - 70))
                else:
                    pygame.draw.circle(screen, LIGHT_GREY, (int(loc_screen_x), int(loc_screen_y)), 30, 2)
                    pygame.draw.circle(screen, (60, 60, 70), (int(loc_screen_x), int(loc_screen_y)), 25, 1)
        
        # Рисуем точки перехода с эффектом
        for tp in self.transition_points:
            tp_screen_x = tp['x'] - self.camera_x
            tp_screen_y = tp['y'] - self.camera_y
            if -100 < tp_screen_x < SCREEN_WIDTH + 100 and -100 < tp_screen_y < SCREEN_HEIGHT + 100:
                # Пульсирующее свечение
                pulse = math.sin(pygame.time.get_ticks() * 0.005) * 0.3 + 0.7
                glow_radius = int(tp['radius'] * pulse)
                glow_surface = pygame.Surface((glow_radius * 2 + 10, glow_radius * 2 + 10), pygame.SRCALPHA)
                for radius in range(glow_radius, 0, -5):
                    alpha = int(80 * (1 - radius / glow_radius))
                    pygame.draw.circle(glow_surface, (*BLUE[:3], alpha), (glow_radius + 5, glow_radius + 5), radius)
                screen.blit(glow_surface, (int(tp_screen_x) - glow_radius - 5, int(tp_screen_y) - glow_radius - 5))
                pygame.draw.circle(screen, BLUE, (int(tp_screen_x), int(tp_screen_y)), tp['radius'], 3)
                pygame.draw.circle(screen, (100, 150, 255), (int(tp_screen_x), int(tp_screen_y)), tp['radius'] - 5, 1)
        
        # Дороги между локациями с улучшенной графикой
        for i in range(len(self.locations)):
            for j in range(i + 1, len(self.locations)):
                loc1 = self.locations[i]
                loc2 = self.locations[j]
                dist = math.sqrt((loc1.world_x - loc2.world_x)**2 + (loc1.world_y - loc2.world_y)**2)
                if dist < 2000:
                    x1 = loc1.world_x - self.camera_x
                    y1 = loc1.world_y - self.camera_y
                    x2 = loc2.world_x - self.camera_x
                    y2 = loc2.world_y - self.camera_y
                    if (x1 > -200 and x1 < SCREEN_WIDTH + 200 and y1 > -200 and y1 < SCREEN_HEIGHT + 200) or \
                       (x2 > -200 and x2 < SCREEN_WIDTH + 200 and y2 > -200 and y2 < SCREEN_HEIGHT + 200):
                        # Тень дороги
                        pygame.draw.line(screen, (20, 20, 25), (int(x1), int(y1) + 1), (int(x2), int(y2) + 1), 5)
                        # Основная дорога
                        pygame.draw.line(screen, (50, 50, 60), (int(x1), int(y1)), (int(x2), int(y2)), 4)
                        # Разметка
                        steps = int(dist / 50)
                        for step in range(0, steps, 2):
                            t = step / steps
                            mark_x = int(x1 + (x2 - x1) * t)
                            mark_y = int(y1 + (y2 - y1) * t)
                            pygame.draw.circle(screen, (180, 180, 100), (mark_x, mark_y), 3)
        
        # Отрисовка текущей локации (детали)
        current_loc = self.get_current_location()
        loc_screen_x = current_loc.world_x - self.camera_x
        loc_screen_y = current_loc.world_y - self.camera_y
        
        # Если игрок в текущей локации, рисуем детали (увеличиваем радиус)
        dist_to_loc = math.sqrt((player_x - current_loc.world_x)**2 + (player_y - current_loc.world_y)**2)
        if dist_to_loc < 1200:  # Увеличили радиус отрисовки
            # Смещаем отрисовку зданий
            offset_x = loc_screen_x - SCREEN_WIDTH // 2
            offset_y = loc_screen_y - SCREEN_HEIGHT // 2
            
            # Асфальт с текстурой
            for i in range(0, SCREEN_WIDTH, 40):
                for j in range(SCREEN_HEIGHT - 100, SCREEN_HEIGHT, 40):
                    if (i + j) % 80 < 40:
                        pygame.draw.rect(screen, (25, 25, 35), (offset_x + i, offset_y + j, 40, 40))
            pygame.draw.rect(screen, ASPHALT, (offset_x, offset_y + SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))
            
            # Дороги с разметкой и эффектом
            road_color = (35, 35, 45)
            for i in range(0, SCREEN_WIDTH, 120):
                # Тень дороги
                pygame.draw.rect(screen, (20, 20, 30), (offset_x + i - 1, offset_y + SCREEN_HEIGHT // 2 - 3, 62, 6))
                pygame.draw.rect(screen, road_color, (offset_x + i, offset_y + SCREEN_HEIGHT // 2 - 2, 60, 4))
                # Разметка с эффектом
                mark_offset = int((self.camera_x + self.camera_y) % 80)
                if i + mark_offset < SCREEN_WIDTH:
                    pygame.draw.rect(screen, (200, 200, 100), (offset_x + i + mark_offset, offset_y + SCREEN_HEIGHT // 2 - 1, 40, 2))
            
            for i in range(0, SCREEN_HEIGHT, 120):
                pygame.draw.rect(screen, (20, 20, 30), (offset_x + SCREEN_WIDTH // 2 - 3, offset_y + i - 1, 6, 62))
                pygame.draw.rect(screen, road_color, (offset_x + SCREEN_WIDTH // 2 - 2, offset_y + i, 4, 60))
                mark_offset = int((self.camera_x + self.camera_y) % 80)
                if i + mark_offset < SCREEN_HEIGHT:
                    pygame.draw.rect(screen, (200, 200, 100), (offset_x + SCREEN_WIDTH // 2 - 1, offset_y + i + mark_offset, 2, 40))
            
            # Дополнительные объекты на локации (машины, фонари, мусор)
            for i in range(8):
                obj_x = offset_x + random.randint(50, SCREEN_WIDTH - 50)
                obj_y = offset_y + SCREEN_HEIGHT - 120 + random.randint(-20, 20)
                
                if -100 < obj_x < SCREEN_WIDTH + 100 and -100 < obj_y < SCREEN_HEIGHT + 100:
                    obj_type = i % 3
                    if obj_type == 0:  # Машина
                        car_color = random.choice([(100, 150, 200), (200, 100, 100), (150, 150, 150), (200, 200, 100)])
                        pygame.draw.rect(screen, car_color, (obj_x - 25, obj_y - 15, 50, 30))
                        pygame.draw.rect(screen, (200, 200, 200), (obj_x - 20, obj_y - 12, 18, 20))
                        pygame.draw.rect(screen, (200, 200, 200), (obj_x + 2, obj_y - 12, 18, 20))
                        pygame.draw.circle(screen, (30, 30, 30), (int(obj_x - 15), int(obj_y + 12)), 6)
                        pygame.draw.circle(screen, (30, 30, 30), (int(obj_x + 15), int(obj_y + 12)), 6)
                    elif obj_type == 1:  # Фонарь
                        pygame.draw.rect(screen, (60, 60, 60), (obj_x - 2, obj_y - 30, 4, 30))
                        light_intensity = 0.7 + 0.3 * math.sin(pygame.time.get_ticks() * 0.01 + i)
                        light_color = tuple(int(255 * light_intensity) for _ in range(3))
                        pygame.draw.circle(screen, light_color, (int(obj_x), int(obj_y - 30)), 8)
                        # Свет от фонаря
                        light_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
                        for radius in range(30, 0, -5):
                            alpha = int(40 * (1 - radius / 30))
                            pygame.draw.circle(light_surf, (*light_color[:3], alpha), (30, 30), radius)
                        screen.blit(light_surf, (obj_x - 30, obj_y - 60))
                    elif obj_type == 2:  # Мусорный бак
                        pygame.draw.rect(screen, (40, 40, 50), (obj_x - 8, obj_y - 20, 16, 20))
                        pygame.draw.rect(screen, (60, 60, 70), (obj_x - 8, obj_y - 20, 16, 4))
            
            # Здания текущей локации с улучшенной графикой
            for x, y, width, height, color, windows in current_loc.buildings:
                screen_x = offset_x + x
                screen_y = offset_y + y
                
                # Проверяем видимость здания
                if screen_x + width < 0 or screen_x > SCREEN_WIDTH or screen_y + height < 0 or screen_y > SCREEN_HEIGHT:
                    continue
                
                # Основа здания с градиентом
                for i in range(height):
                    gradient_factor = i / height
                    grad_color = tuple(int(c * (0.8 + gradient_factor * 0.2)) for c in color)
                    pygame.draw.line(screen, grad_color, (screen_x, screen_y + i), (screen_x + width, screen_y + i))
                
                # Тень с эффектом
                shadow_points = [
                    (screen_x + width, screen_y),
                    (screen_x + width + 15, screen_y - 15),
                    (screen_x + width + 15, screen_y + height - 15),
                    (screen_x + width, screen_y + height)
                ]
                pygame.draw.polygon(screen, (10, 10, 15), shadow_points)
                
                # Обводка здания
                pygame.draw.rect(screen, tuple(min(255, c + 30) for c in color), (screen_x, screen_y, width, height), 2)
                
                # Окна с эффектом свечения
                for wx, wy, lit in windows:
                    win_screen_x = offset_x + wx
                    win_screen_y = offset_y + wy
                    
                    if lit:
                        # Свечение окна
                        glow_surface = pygame.Surface((25, 25), pygame.SRCALPHA)
                        for radius in range(12, 0, -2):
                            alpha = int(80 * (1 - radius / 12))
                            pygame.draw.circle(glow_surface, (255, 255, 150, alpha), (12, 12), radius)
                        screen.blit(glow_surface, (win_screen_x - 3, win_screen_y - 3))
                    
                    window_color = (255, 255, 180) if lit else (60, 60, 80)
                    pygame.draw.rect(screen, window_color, (win_screen_x, win_screen_y, 18, 22))
                    pygame.draw.rect(screen, (40, 40, 50), (win_screen_x, win_screen_y, 18, 22), 1)
                    
                    # Отражение в окнах
                    if lit and random.random() > 0.7:
                        pygame.draw.line(screen, (255, 255, 255), 
                                       (win_screen_x + 2, win_screen_y + 2), 
                                       (win_screen_x + 16, win_screen_y + 20), 1)
                
                # Крыша здания
                roof_color = tuple(int(c * 0.7) for c in color)
                pygame.draw.polygon(screen, roof_color, [
                    (screen_x, screen_y),
                    (screen_x + width // 2, screen_y - 20),
                    (screen_x + width, screen_y)
                ])
                
                # Дверь с деталями
                door_x = screen_x + width // 2 - 15
                door_y = screen_y + height - 50
                pygame.draw.rect(screen, (30, 20, 15), (door_x, door_y, 30, 50))
                pygame.draw.rect(screen, (50, 40, 30), (door_x, door_y, 30, 50), 2)
                # Ручка двери
                pygame.draw.circle(screen, (150, 150, 150), (door_x + 25, door_y + 25), 3)
            
            # Магазин с улучшенной графикой
            if current_loc.shop_pos:
                sx, sy, sw, sh = current_loc.shop_pos
                shop_world_x = current_loc.world_x - SCREEN_WIDTH // 2 + sx + sw // 2
                shop_world_y = current_loc.world_y - SCREEN_HEIGHT // 2 + sy + sh // 2
                shop_screen_x = shop_world_x - self.camera_x
                shop_screen_y = shop_world_y - self.camera_y
                
                # Свечение магазина
                shop_glow = pygame.Surface((sw + 40, sh + 40), pygame.SRCALPHA)
                for radius in range(40, 0, -5):
                    alpha = int(60 * (1 - radius / 40))
                    pygame.draw.circle(shop_glow, (*GOLD[:3], alpha), (sw // 2 + 20, sh // 2 + 20), radius)
                screen.blit(shop_glow, (shop_screen_x - sw // 2 - 20, shop_screen_y - sh // 2 - 20))
                
                # Здание магазина с градиентом
                shop_color = (150, 100, 50)
                for i in range(sh):
                    grad_factor = i / sh
                    grad_color = tuple(int(c * (0.9 + grad_factor * 0.1)) for c in shop_color)
                    pygame.draw.line(screen, grad_color, 
                                   (shop_screen_x - sw // 2, shop_screen_y - sh // 2 + i),
                                   (shop_screen_x + sw // 2, shop_screen_y - sh // 2 + i))
                
                pygame.draw.rect(screen, GOLD, (shop_screen_x - sw // 2, shop_screen_y - sh // 2, sw, sh), 4)
                pygame.draw.rect(screen, (255, 255, 200), (shop_screen_x - sw // 2, shop_screen_y - sh // 2, sw, sh), 2)
                
                # Вывеска с эффектом
                sign_y = shop_screen_y - sh // 2 - 25
                sign_bg = pygame.Surface((sw + 20, 30), pygame.SRCALPHA)
                sign_bg.fill((0, 0, 0, 200))
                screen.blit(sign_bg, (shop_screen_x - sw // 2 - 10, sign_y))
                sign_text = small_font.render("МАГАЗИН", True, GOLD)
                screen.blit(sign_text, (shop_screen_x - sign_text.get_width() // 2, sign_y + 5))
                
                # Окна магазина
                for i in range(2):
                    win_x = shop_screen_x - sw // 2 + 15 + i * 35
                    win_y = shop_screen_y - sh // 2 + 15
                    pygame.draw.rect(screen, (255, 255, 200), (win_x, win_y, 20, 25))
                    pygame.draw.rect(screen, GOLD, (win_x, win_y, 20, 25), 2)

