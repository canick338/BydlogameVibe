"""
Класс Game для управления игрой
ВНИМАНИЕ: Этот файл не должен запускаться напрямую!
Используйте main.py из корневой директории проекта.
"""
import pygame
import sys
import os
import random
import math

# Исправление пути для импортов при прямом запуске
if __name__ == "__main__":
    print("ОШИБКА: Этот файл нельзя запускать напрямую!")
    print("Используйте: python main.py")
    sys.exit(1)

from game.config import *
from game.game_state import GameState
from game.player import Player
from game.enemy import Enemy
from game.weapon import Weapon
from game.bullet import Bullet
from game.particle import Particle, BloodParticle
from game.achievement import Achievement
from game.mission import Mission
from game.shop import Shop
from game.city import City, Location
from scenes.hotline_cutscene import HotlineCutscene
from scenes.cutscene import Cutscene
from game.ui.damage_number import DamageNumber
from game.ui.kill_feed import KillFeedEntry
from game.managers.wave_manager import WaveManager
from game.managers.screen_shake import ScreenShake
from game.managers.gameplay_manager import GameplayManager
from game.knife import Knife
from game.body_part import BodyPart


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("БРАТВА: УЛИЦЫ СТОЛИЦЫ - ЭПИЧЕСКИЙ РЕМАСТЕР!")
        self.clock = pygame.time.Clock()
        self.state = GameState.MAIN_MENU
        self.player = Player()
        self.city = City()
        self.enemies = []
        self.bullets = []
        self.particles = []
        self.damage_numbers = []
        self.body_parts = []  # Части тел врагов для эффекта разрезания
        self.missions = []
        self.current_mission_index = 0
        self.cutscene = None
        self.hotline_cutscene = None
        self.score = 0
        self.mission_start_time = 0
        self.shop = Shop()
        self.shop_message = ""
        self.shop_message_timer = 0
        self.achievements = []
        self.current_achievement_notification = None
        self.achievement_notification_timer = 0
        self.kill_feed = []  # Инициализация перед созданием менеджеров
        
        # Флаг пропуска катсцены
        self.skip_cutscene_prompt = False
        self.skip_cutscene_timer = 0

        # Инициализация миссий и достижений перед созданием менеджеров
        self.init_missions()
        self.init_achievements()

        # Менеджеры (создаются после инициализации всех атрибутов)
        self.wave_manager = WaveManager()
        self.screen_shake = ScreenShake()
        self.gameplay_manager = GameplayManager(
            self.player, self.city, self.enemies, self.bullets,
            self.particles, self.damage_numbers, self.kill_feed, self.screen_shake,
            mission_callback=self._handle_enemy_kill_for_mission
        )

    def init_achievements(self):
        self.achievements = [
            Achievement("ПЕРВАЯ КРОВЬ", "Убей первого врага",
                       lambda p, g: p.kills >= 1),
            Achievement("МАССОВЫЙ УБИЙЦА", "Убей 50 врагов",
                       lambda p, g: p.kills >= 50),
            Achievement("БОСС УБИЙЦА", "Убей 10 боссов",
                       lambda p, g: p.bosses_killed >= 10),
            Achievement("МИЛЛИОНЕР", "Заработай 10000 рублей",
                       lambda p, g: p.money >= 10000),
            Achievement("НЕУЯЗВИМЫЙ", "Пройди миссию без потери здоровья",
                       lambda p, g: False),  # Специальная проверка
            Achievement("МАСТЕР СТРЕЛЬБЫ", "Сделай 100 убийств",
                       lambda p, g: p.kills >= 100),
            Achievement("ЛЕГЕНДА", "Пройди все миссии",
                       lambda p, g: p.completed_missions >= len(self.missions)),
            Achievement("ВОЛНА УЖАСА", "Достигни 10 волны",
                       lambda p, g: g.wave_manager.wave >= 10),
        ]

    def init_missions(self):
        mission1_texts = [
            "РАЙОННЫЙ ОТДЕЛ. СЕРЁГА ПОДХОДИТ К МЕНТАМ...",
            "МЕНТ: Э, шкет, куда прешь? Это наша территория!",
            "СЕРЁГА: Ваша? С какого хрена? Я тут 10 лет отсидел,\nа вы тут за неделю всё захватили?",
            "МЕНТ: А тебе чё, пацан? Хочешь проблем? Мы тебя щас\nпо статье отправим!",
            "СЕРЁГА: Попробуйте, мусора... Только троньте -\nваши семьи завтра хоронить будут!",
            "МЕНТ: Ах ты гангстер малолетний! Ребята, взять его!\nПокажем кто в районе хозяин!",
            "ЗАВЯЗЫВАЕТСЯ ЖЕСТОКАЯ ДРАКА...",
            "СЕРЁГА: Вот так, мусора! Теперь вы знаете\nкто тут настоящий хозяин!"
        ]

        mission2_texts = [
            "СЕРЁГА: Ментов поставили на место...\nТеперь бизнесмены зажрались!",
            "ОНИ ДУМАЮТ ЧТО МОГУТ НЕ ПЛАТИТЬ ЗА ПРИКРЫТИЕ?",
            "СЕРЁГА: Я им покажу что значит уважение!\nНикто не смеет не платить мне!",
            "ПОРА СОБРАТЬ ДАНИ И НАПОМНИТЬ КТО ТУТ БОСС!",
            "5000 РУБЛЕЙ ИЛИ КРОВЬ... ВЫБОР ЗА НИМИ!",
            "СЕРЁГА: Каждый должен знать своё место\nв этой игре!"
        ]

        mission3_texts = [
            "СЛУХИ О СЕРЁГЕ РАЗНОСЯТСЯ ПО ГОРОДУ...",
            "НОВАЯ БАНДА РЕШИЛА ЗАХВАТИТЬ ЕГО РАЙОН!",
            "СЕРЁГА: Пусть только попробуют!\nЯ им устрою кровавую баню!",
            "ЭТО БУДЕТ САМАЯ ЖЕСТОКАЯ БИТВА...\nВЫЖИВИ 2 МИНУТЫ И СТАНЕШЬ ЛЕГЕНДОЙ!",
            "СЕРЁГА: Они не знают с кем связались!\nЯ покажу им настоящую мощь!"
        ]

        mission4_texts = [
            "СЕРЁГА: Теперь я контролирую район...",
            "НО ЕСТЬ ОДИН ПРОБЛЕМНЫЙ ТИП - БОСС СТАРОЙ БАНДЫ",
            "ОН НЕ ХОЧЕТ УХОДИТЬ И ПЫТАЕТСЯ ВЕРНУТЬ ВЛАСТЬ",
            "СЕРЁГА: Время показать ему кто теперь главный!",
            "УБЕЙ 3 БОССОВ И ДОКАЖИ СВОЮ СИЛУ!",
            "ЭТО БУДЕТ НЕ ЛЕГКО, НО ТЫ СПРАВИШЬСЯ!"
        ]

        mission5_texts = [
            "ФИНАЛЬНАЯ БИТВА! ВСЯ ГОРОДСКАЯ МАФИЯ",
            "ОБЪЕДИНИЛАСЬ ПРОТИВ ТЕБЯ!",
            "СЕРЁГА: Пусть все придут! Я готов!",
            "ВЫЖИВИ 3 МИНУТЫ ПРОТИВ ВСЕХ!",
            "ЕСЛИ ПРОЙДЁШЬ ЭТО - СТАНЕШЬ ЛЕГЕНДОЙ!",
            "НИКТО БОЛЬШЕ НЕ ПОСМЕЕТ БРОСИТЬ ТЕБЕ ВЫЗОВ!"
        ]

        self.missions = [
            Mission("РАЗБОРКА С МЕНТАМИ",
                    "Убери 15 ментов чтобы показать кто в районе хозяин",
                    15, 1500, "kill", mission1_texts),

            Mission("СБОР ДАНИ",
                    "Собери 5000 рублей с врагов",
                    5000, 2000, "collect", mission2_texts),

            Mission("УЛИЧНАЯ ВОЙНА",
                    "Продержись 2 минуты против волн врагов",
                    120, 3000, "survive", mission3_texts),

            Mission("УБИТЬ БОССОВ",
                    "Уничтожь 3 боссов чтобы закрепить власть",
                    3, 4000, "kill", mission4_texts),

            Mission("ФИНАЛЬНАЯ БИТВА",
                    "Выживи 3 минуты против всех врагов",
                    180, 5000, "survive", mission5_texts)
        ]

    def start_mission_cutscene(self, mission_index):
        mission = self.missions[mission_index]
        self.cutscene = Cutscene(mission.cutscene_texts)
        self.state = GameState.CUTSCENE
        # Музыка продолжает играть если она уже играет
        if not pygame.mixer.music.get_busy():
            try:
                pygame.mixer.music.load("music/musicingame.ogg")
                pygame.mixer.music.play(-1)
            except:
                pass

    def complete_mission(self):
        mission = self.missions[self.current_mission_index]
        self.player.money += mission.reward
        self.player.completed_missions += 1
        self.score += mission.reward // 10

        complete_texts = [
            f"ЗАДАЧА ВЫПОЛНЕНА: {mission.title}",
            f"Получено: {mission.reward} рублей",
            "Так держать, братан!\nТвой авторитет растет!"
        ]

        if self.player.completed_missions >= len(self.missions):
            complete_texts.append("ТЫ СТАЛ КОРОЛЁМ РАЙОНА!\nНажми ПРОБЕЛ для победы!")
        else:
            complete_texts.append("Готовься к следующей задаче...")

        self.cutscene = Cutscene(complete_texts, (40, 80, 40), mission_complete=True)
        self.state = GameState.CUTSCENE

    def spawn_enemies(self, count):
        """Спавн врагов (используется WaveManager)"""
        self.wave_manager.spawn_enemies(count, self.enemies, self.player, self.city)

    def _create_body_parts(self, enemy):
        """Создание частей тела врага при убийстве ножом"""
        # Создаем разные части тела
        parts = [
            ("head", 1),
            ("torso", 3),
            ("limb", 4)
        ]

        for part_type, count in parts:
            for _ in range(count):
                offset_x = random.uniform(-20, 20)
                offset_y = random.uniform(-20, 20)
                self.body_parts.append(BodyPart(
                    enemy.x + offset_x,
                    enemy.y + offset_y,
                    part_type,
                    enemy.color
                ))

    def _handle_knife_kill(self, enemy, damage):
        """Обработка убийства врага ножом"""
        self.player.kills += 1

        # Лента убийств
        self.kill_feed.append(KillFeedEntry(enemy.type + " (НОЖ)"))
        if len(self.kill_feed) > 5:
            self.kill_feed.pop(0)

        # Комбо система
        self.player.combo += 1
        self.player.combo_timer = 180
        combo_bonus = 1 + (self.player.combo // 5) * 0.1

        bounty = int(enemy.bounty * combo_bonus * 1.5)  # Бонус за нож
        self.player.money += bounty
        score_change = int(bounty // 2 * combo_bonus)
        self.score += score_change
        self.player.total_damage_dealt += damage

        # Опыт (бонус за ближний бой)
        exp_gain = int((10 + enemy.level * 5) * 1.5)
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

        # Обновление миссий
        self._handle_enemy_kill_for_mission(enemy, bounty)

    def _handle_enemy_kill_for_mission(self, enemy, bounty):
        """Callback для обработки убийства врага для миссий"""
        if self.current_mission_index < len(self.missions):
            current_mission = self.missions[self.current_mission_index]
            if current_mission.type == "kill":
                if current_mission.title == "РАЗБОРКА С МЕНТАМИ" and enemy.type == "мент":
                    self.player.mission_kills += 1
                    if current_mission.update():
                        self.complete_mission()
                elif current_mission.title == "УБИТЬ БОССОВ" and enemy.type == "босс":
                    self.player.mission_kills += 1
                    if current_mission.update():
                        self.complete_mission()
            elif current_mission.type == "collect":
                if current_mission.update(bounty):
                    self.complete_mission()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == GameState.PLAYING:
                        self.state = GameState.PAUSE
                    elif self.state == GameState.PAUSE:
                        self.state = GameState.PLAYING
                    elif self.state == GameState.CONTROLS:
                        self.state = GameState.MAIN_MENU
                    elif self.state == GameState.SHOP:
                        self.state = GameState.PLAYING
                    elif self.state == GameState.SKILLS:
                        self.state = GameState.PLAYING
                    elif self.state in [GameState.GAME_OVER, GameState.WIN]:
                        self.state = GameState.MAIN_MENU

                elif self.state == GameState.SHOP:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.shop.selected_item = max(0, self.shop.selected_item - 1)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.shop.selected_item = min(len(self.shop.items) - 1, self.shop.selected_item + 1)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        item = self.shop.items[self.shop.selected_item]
                        success, message = self.shop.buy_item(item, self.player)
                        self.shop_message = message
                        self.shop_message_timer = 120

                elif self.state == GameState.SKILLS:
                    if event.key == pygame.K_1:
                        if self.player.skill_points > 0:
                            self.player.skills["damage"] += 1
                            self.player.skill_points -= 1
                            for weapon in self.player.weapons:
                                weapon.damage = int(weapon.damage * 1.1)
                    elif event.key == pygame.K_2:
                        if self.player.skill_points > 0:
                            self.player.skills["health"] += 1
                            self.player.skill_points -= 1
                            self.player.max_health += 15
                            self.player.health += 15
                    elif event.key == pygame.K_3:
                        if self.player.skill_points > 0:
                            self.player.skills["speed"] += 1
                            self.player.skill_points -= 1
                            self.player.speed = min(8, self.player.speed + 0.3)
                    elif event.key == pygame.K_4:
                        if self.player.skill_points > 0:
                            self.player.skills["ammo"] += 1
                            self.player.skill_points -= 1
                            for weapon in self.player.weapons:
                                weapon.max_ammo = int(weapon.max_ammo * 1.15)
                                weapon.ammo = weapon.max_ammo
                    elif event.key == pygame.K_5:
                        if self.player.skill_points > 0:
                            self.player.skills["regen"] += 1
                            self.player.skill_points -= 1

                elif event.key == pygame.K_SPACE:
                    if self.state == GameState.CUTSCENE:
                        # Пропуск катсцены Hotline Miami
                        if self.hotline_cutscene:
                            # Если это первое нажатие, показываем подсказку
                            if not self.skip_cutscene_prompt:
                                self.skip_cutscene_prompt = True
                                self.skip_cutscene_timer = 120  # 2 секунды для подтверждения
                            else:
                                # Подтвержденный пропуск
                                self.hotline_cutscene = None
                                self.skip_cutscene_prompt = False
                                self.start_mission_cutscene(0)
                        # Пропуск обычной катсцены
                        elif self.cutscene:
                            if self.cutscene.update(9999):
                                if self.cutscene.mission_complete:
                                    self.current_mission_index += 1
                                    if self.current_mission_index < len(self.missions):
                                        self.start_mission_cutscene(self.current_mission_index)
                                    else:
                                        self.state = GameState.WIN
                                else:
                                    self.state = GameState.PLAYING
                                    self.mission_start_time = pygame.time.get_ticks()
                                    # Убеждаемся что музыка играет
                                    if not pygame.mixer.music.get_busy():
                                        try:
                                            pygame.mixer.music.load("music/musicingame.ogg")
                                            pygame.mixer.music.play(-1)
                                        except:
                                            pass

                elif event.key == pygame.K_r and self.state == GameState.PLAYING:
                    # Перезарядка текущего оружия
                    self.player.weapons[self.player.current_weapon].ammo = \
                        self.player.weapons[self.player.current_weapon].max_ammo

                elif event.key == pygame.K_u and self.state == GameState.PLAYING:
                    # Меню навыков (открывается всегда, даже без очков)
                    self.state = GameState.SKILLS

                elif event.key == pygame.K_e and self.state == GameState.PLAYING:
                    # Вход в магазин (E) в открытом мире
                    location = self.city.get_current_location()
                    shop_world_x = location.world_x
                    shop_world_y = location.world_y
                    dist = math.sqrt((self.player.x - shop_world_x) ** 2 + (self.player.y - shop_world_y) ** 2)
                    if dist < 200:
                        self.state = GameState.SHOP

                elif event.key == pygame.K_t and self.state == GameState.PLAYING:
                    # Смена локации (T)
                    self.city.current_location_index = (self.city.current_location_index + 1) % len(self.city.locations)
                    # Эффект перехода
                    for _ in range(50):
                        angle = random.uniform(0, 2 * math.pi)
                        speed = random.uniform(2, 6)
                        self.particles.append(Particle(
                            self.player.x, self.player.y,
                            BLUE,
                            math.cos(angle) * speed,
                            math.sin(angle) * speed,
                            60
                        ))

                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9] and self.state == GameState.PLAYING:
                    weapon_index = event.key - pygame.K_1
                    if weapon_index < len(self.player.weapons) and self.player.weapons[weapon_index] is not None:
                        self.player.current_weapon = weapon_index
                        if isinstance(self.player.weapons[weapon_index], Knife):
                            self.player.auto_fire = False  # Нож не стреляет автоматически

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # ЛКМ
                    if self.state == GameState.PLAYING:
                        # Проверяем, нож ли это
                        if isinstance(self.player.weapons[self.player.current_weapon], Knife):
                            # Атака ножом обрабатывается в update()
                            pass
                        else:
                            bullet = self.player.shoot()
                            if bullet:
                                self.bullets.append(bullet)
                            self.player.auto_fire = True
                    elif self.state == GameState.MAIN_MENU:
                        # Обработка кликов по кнопкам главного меню
                        mouse_pos = pygame.mouse.get_pos()
                        button_y = 350
                        button_width = 200
                        button_height = 50
                        center_x = SCREEN_WIDTH // 2

                        for i in range(3):
                            btn_x = center_x - button_width // 2
                            btn_y = button_y + i * 80
                            if (btn_x <= mouse_pos[0] <= btn_x + button_width and
                                btn_y <= mouse_pos[1] <= btn_y + button_height):
                                if i == 0:  # НАЧАТЬ ИГРУ
                                    self.start_game()
                                elif i == 1:  # УПРАВЛЕНИЕ
                                    self.state = GameState.CONTROLS
                                elif i == 2:  # ВЫХОД
                                    return False

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.state == GameState.PLAYING:
                    self.player.auto_fire = False

        return True

    def update(self):
        if self.state == GameState.PLAYING:
            dt = self.clock.get_time() / 1000.0

            # Обновление направления игрока по курсору (с учетом камеры)
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # Преобразуем координаты экрана в координаты мира
            world_mouse_x = mouse_x + self.city.camera_x
            world_mouse_y = mouse_y + self.city.camera_y
            self.player.update_direction(world_mouse_x, world_mouse_y)

            # Управление движением (ПРЯМО В UPDATE - как в старом коде)
            keys = pygame.key.get_pressed()
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

            # Обновление камеры
            self.city.update_camera(self.player.x, self.player.y)

            # Проверка перехода между локациями
            self.city.check_location_transition(self.player.x, self.player.y)

            # Автоматическая стрельба (только для огнестрельного оружия)
            if self.player.auto_fire and not isinstance(self.player.weapons[self.player.current_weapon], Knife):
                bullet = self.player.shoot()
                if bullet:
                    self.bullets.append(bullet)

            # Атака ножом
            if isinstance(self.player.weapons[self.player.current_weapon], Knife):
                keys = pygame.key.get_pressed()
                mouse_buttons = pygame.mouse.get_pressed()
                if mouse_buttons[0]:  # ЛКМ зажата
                    attack_info = self.player.attack_with_knife()
                    if attack_info:
                        # Проверяем попадание по врагам
                        for enemy in self.enemies[:]:
                            dist = math.sqrt((enemy.x - attack_info["x"]) ** 2 + (enemy.y - attack_info["y"]) ** 2)
                            if dist < attack_info["range"]:
                                # Проверяем угол атаки (враг должен быть перед игроком)
                                angle_to_enemy = math.atan2(enemy.y - attack_info["y"], enemy.x - attack_info["x"])
                                angle_diff = abs(angle_to_enemy - attack_info["direction"])
                                if angle_diff > math.pi:
                                    angle_diff = 2 * math.pi - angle_diff

                                if angle_diff < math.pi / 2:  # Враг в зоне атаки
                                    damage = attack_info["damage"]

                                    # Критический удар при атаке сзади
                                    is_critical = angle_diff > math.pi / 3
                                    if is_critical:
                                        damage = int(damage * 1.5)

                                    self.damage_numbers.append(DamageNumber(enemy.x, enemy.y - enemy.size, damage, is_critical))
                                    self.screen_shake.shake(8, 15)

                                    # Эффект резания
                                    for _ in range(30):
                                        angle = random.uniform(0, 2 * math.pi)
                                        speed = random.uniform(2, 8)
                                        self.particles.append(BloodParticle(
                                            enemy.x, enemy.y,
                                            math.cos(angle) * speed,
                                            math.sin(angle) * speed
                                        ))

                                    if enemy.take_damage(damage):
                                        # УБИЙСТВО НОЖОМ - РЕЗАЕМ НА ЧАСТИ!
                                        self._create_body_parts(enemy)
                                        self._handle_knife_kill(enemy, damage)
                                        self.enemies.remove(enemy)
                                    break  # Нож бьет только одного врага за раз

            # Спавн врагов (используется WaveManager)
            self.wave_manager.update(self.enemies, self.player, self.city)

            # Обновление миссии (survive)
            current_mission = self.missions[self.current_mission_index]
            if current_mission.type == "survive":
                elapsed = (pygame.time.get_ticks() - self.mission_start_time) / 1000.0
                if current_mission.update_timer(elapsed):
                    self.complete_mission()

            # Текущее время (нужно для обновления)
            current_time = pygame.time.get_ticks()

            # Обновление пуль (ПРЯМО В UPDATE - как в старом коде)
            for bullet in self.bullets[:]:
                if not bullet.update(self.city.world_size):
                    self.bullets.remove(bullet)
                else:
                    # Проверка попадания (используем мировые координаты)
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
                            # Обработка смерти врага (ПРЯМО В UPDATE - как в старом коде)
                            # Эффект частиц при убийстве
                            for _ in range(15):
                                angle = random.uniform(0, 2 * math.pi)
                                speed = random.uniform(2, 6)
                                self.particles.append(Particle(
                                    enemy.x, enemy.y, enemy.color,
                                    math.cos(angle) * speed,
                                    math.sin(angle) * speed, 40
                                ))

                            # Убийство врага
                            self.enemies.remove(enemy)
                            self.player.kills += 1

                            # Лента убийств
                            self.kill_feed.append(KillFeedEntry(enemy.type))
                            if len(self.kill_feed) > 5:
                                self.kill_feed.pop(0)

                            # Комбо система
                            self.player.combo += 1
                            self.player.combo_timer = 180
                            combo_bonus = 1 + (self.player.combo // 5) * 0.1

                            bounty = int(enemy.bounty * combo_bonus)
                            self.player.money += bounty
                            score_change = int(bounty // 2 * combo_bonus)
                            self.score += score_change
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

                            # Обновление миссий
                            self._handle_enemy_kill_for_mission(enemy, bounty)

                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
                        if bullet.type != "explosive":
                            break

            # Обновление врагов (ПРЯМО В UPDATE - как в старом коде)
            for enemy in self.enemies:
                damage = enemy.update(self.player.x, self.player.y)
                if damage > 0:
                    actual_damage = max(1, damage - self.player.armor // 2)
                    self.player.health -= actual_damage
                    self.player.last_damage_time = current_time
                    self.player.regen_timer = 0
                    if self.player.health <= 0:
                        self.state = GameState.GAME_OVER

            # Обновление частиц (ПРЯМО В UPDATE - как в старом коде)
            for particle in self.particles[:]:
                if not particle.update():
                    self.particles.remove(particle)
                particle.x = max(0, min(self.city.world_size, particle.x))
                particle.y = max(0, min(self.city.world_size, particle.y))

            # Обновление чисел урона
            for dmg_num in self.damage_numbers[:]:
                if not dmg_num.update():
                    self.damage_numbers.remove(dmg_num)

            # Обновление ленты убийств
            for kill_entry in self.kill_feed[:]:
                if not kill_entry.update():
                    self.kill_feed.remove(kill_entry)

            # Обновление частей тел
            for body_part in self.body_parts[:]:
                if not body_part.update():
                    self.body_parts.remove(body_part)

            # Регенерация здоровья
            self.player.regen_timer += 1
            if current_time - self.player.last_damage_time > 5000 and self.player.health < self.player.max_health:
                if self.player.regen_timer >= 180:
                    self.player.health = min(self.player.max_health, self.player.health + 1)
                    self.player.regen_timer = 0

            # Обновление комбо
            if self.player.combo_timer > 0:
                self.player.combo_timer -= 1
            else:
                self.player.combo = 0

            # Обновление тряски экрана
            self.screen_shake.update()

            # Проверка близости к магазину в открытом мире
            location = self.city.get_current_location()
            shop_world_x = location.world_x
            shop_world_y = location.world_y
            dist_to_shop = math.sqrt((self.player.x - shop_world_x) ** 2 + (self.player.y - shop_world_y) ** 2)
            if dist_to_shop < 200:  # Радиус входа в магазин
                # Показываем подсказку о входе в магазин
                pass

            # Смена волны (используется WaveManager)
            self.wave_manager.check_wave_change(self.player.kills, self.particles, self.player)

        # Обновление сообщения магазина
        if self.shop_message_timer > 0:
            self.shop_message_timer -= 1

        # Обновление таймера пропуска катсцены
        if self.skip_cutscene_timer > 0:
            self.skip_cutscene_timer -= 1
            if self.skip_cutscene_timer == 0:
                self.skip_cutscene_prompt = False

        # Проверка достижений (только в игре)
        if self.state == GameState.PLAYING:
            for achievement in self.achievements:
                if achievement.check(self.player, self):
                    self.current_achievement_notification = achievement
                    self.achievement_notification_timer = 180

        # Обновление таймера достижения
        if self.achievement_notification_timer > 0:
            self.achievement_notification_timer -= 1
            if self.achievement_notification_timer == 0:
                self.current_achievement_notification = None

        # Обновление времени игры
        if self.state == GameState.PLAYING:
            self.player.time_played += dt

    def draw_minimap(self):
        # Мини-карта открытого мира
        minimap_size = 200
        minimap_x = SCREEN_WIDTH - minimap_size - 10
        minimap_y = SCREEN_HEIGHT - minimap_size - 10

        # Фон мини-карты
        minimap_surface = pygame.Surface((minimap_size, minimap_size), pygame.SRCALPHA)
        minimap_surface.fill((0, 0, 0, 180))
        self.screen.blit(minimap_surface, (minimap_x, minimap_y))
        pygame.draw.rect(self.screen, WHITE, (minimap_x, minimap_y, minimap_size, minimap_size), 2)

        # Масштаб для открытого мира
        scale = minimap_size / self.city.world_size

        # Все локации на карте
        for i, loc in enumerate(self.city.locations):
            loc_map_x = minimap_x + int(loc.world_x * scale)
            loc_map_y = minimap_y + int(loc.world_y * scale)
            if minimap_x <= loc_map_x <= minimap_x + minimap_size and minimap_y <= loc_map_y <= minimap_y + minimap_size:
                color = GOLD if i == self.city.current_location_index else LIGHT_GREY
                size = 6 if i == self.city.current_location_index else 4
                pygame.draw.circle(self.screen, color, (loc_map_x, loc_map_y), size)

        # Игрок на карте
        player_map_x = minimap_x + int(self.player.x * scale)
        player_map_y = minimap_y + int(self.player.y * scale)
        if minimap_x <= player_map_x <= minimap_x + minimap_size and minimap_y <= player_map_y <= minimap_y + minimap_size:
            pygame.draw.circle(self.screen, GREEN, (player_map_x, player_map_y), 5)
            # Направление взгляда
            dir_x = player_map_x + int(math.cos(self.player.direction) * 8)
            dir_y = player_map_y + int(math.sin(self.player.direction) * 8)
            pygame.draw.line(self.screen, GREEN, (player_map_x, player_map_y), (dir_x, dir_y), 2)

        # Враги на карте
        for enemy in self.enemies:
            enemy_map_x = minimap_x + int(enemy.x * scale)
            enemy_map_y = minimap_y + int(enemy.y * scale)
            if minimap_x <= enemy_map_x <= minimap_x + minimap_size and minimap_y <= enemy_map_y <= minimap_y + minimap_size:
                color = RED if enemy.type == "босс" else (200, 100, 100)
                pygame.draw.circle(self.screen, color, (enemy_map_x, enemy_map_y), 2)

        # Магазин на карте
        location = self.city.get_current_location()
        shop_map_x = minimap_x + int(location.world_x * scale)
        shop_map_y = minimap_y + int(location.world_y * scale)
        if minimap_x <= shop_map_x <= minimap_x + minimap_size and minimap_y <= shop_map_y <= minimap_y + minimap_size:
            pygame.draw.rect(self.screen, GOLD, (shop_map_x - 3, shop_map_y - 3, 6, 6))

        # Название текущей локации
        loc_name = small_font.render(location.name, True, GOLD)
        self.screen.blit(loc_name, (minimap_x, minimap_y - 20))

    def draw_crosshair(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Улучшенный прицел с эффектами
        size = 15

        # Свечение прицела
        crosshair_glow = pygame.Surface((size * 2 + 20, size * 2 + 20), pygame.SRCALPHA)
        for radius in range(size + 10, 0, -2):
            alpha = int(50 * (1 - radius / (size + 10)))
            pygame.draw.circle(crosshair_glow, (*RED[:3], alpha), (size + 10, size + 10), radius)
        self.screen.blit(crosshair_glow, (mouse_x - size - 10, mouse_y - size - 10))

        # Внешние линии с градиентом
        line_length = 8
        for i in range(line_length):
            alpha = 255 - i * 20
            color = (255, int(200 - i * 10), int(200 - i * 10))
            # Верх
            pygame.draw.line(self.screen, color,
                           (mouse_x, mouse_y - size + i),
                           (mouse_x, mouse_y - size + i + 1), 2)
            # Низ
            pygame.draw.line(self.screen, color,
                           (mouse_x, mouse_y + size - i),
                           (mouse_x, mouse_y + size - i - 1), 2)
            # Лево
            pygame.draw.line(self.screen, color,
                           (mouse_x - size + i, mouse_y),
                           (mouse_x - size + i + 1, mouse_y), 2)
            # Право
            pygame.draw.line(self.screen, color,
                           (mouse_x + size - i, mouse_y),
                           (mouse_x + size - i - 1, mouse_y), 2)

        # Центральный круг с эффектом
        pygame.draw.circle(self.screen, RED, (mouse_x, mouse_y), 6, 2)
        pygame.draw.circle(self.screen, (255, 150, 150), (mouse_x, mouse_y), 4, 1)
        pygame.draw.circle(self.screen, (255, 255, 255), (mouse_x, mouse_y), 2)
        pygame.draw.circle(self.screen, RED, (mouse_x, mouse_y), 1)

    def draw_ui(self):
        # Полоса здоровья
        health_width = (self.player.health / self.player.max_health) * 200
        pygame.draw.rect(self.screen, DARK_GREY, (10, 10, 204, 24))
        pygame.draw.rect(self.screen, RED, (12, 12, health_width, 20))
        pygame.draw.rect(self.screen, WHITE, (10, 10, 204, 24), 2)

        health_text = small_font.render(f"ЗДОРОВЬЕ: {self.player.health}", True, WHITE)
        self.screen.blit(health_text, (220, 12))

        # Оружие
        weapon = self.player.weapons[self.player.current_weapon]
        if isinstance(weapon, Knife):
            ammo_text = small_font.render(f"{weapon.name}: БЛИЖНИЙ БОЙ", True, (255, 100, 100))
        else:
            ammo_text = small_font.render(f"{weapon.name}: {weapon.ammo}/{weapon.max_ammo}", True, weapon.color)
        self.screen.blit(ammo_text, (10, 40))

        # Индикатор выбранного оружия
        for i, w in enumerate(self.player.weapons):
            if w is None:
                continue
            color = GOLD if i == self.player.current_weapon else LIGHT_GREY
            weapon_name = w.name[:3] if hasattr(w, 'name') else "НОЖ"
            weapon_indicator = small_font.render(f"{i+1}: {weapon_name}", True, color)
            self.screen.blit(weapon_indicator, (10 + i * 80, 115))

        # Ресурсы
        money_text = small_font.render(f"БАБЛО: {self.player.money} РУБ.", True, GOLD)
        self.screen.blit(money_text, (10, 65))

        wave_text = small_font.render(f"ВОЛНА: {self.wave_manager.wave}", True, BLUE)
        self.screen.blit(wave_text, (10, 90))

        # Миссия
        if self.current_mission_index < len(self.missions):
            mission = self.missions[self.current_mission_index]
            if mission.type == "survive":
                elapsed = (pygame.time.get_ticks() - self.mission_start_time) / 1000.0
                progress = f"{int(elapsed)}/{mission.target} сек"
            elif mission.type == "kill":
                progress = f"{self.player.mission_kills}/{mission.target}"
            else:
                progress = f"{mission.current}/{mission.target}"

            mission_text = small_font.render(f"ЗАДАЧА: {mission.title} - {progress}", True, GREEN)
            self.screen.blit(mission_text, (SCREEN_WIDTH - 300, 10))

        # Прогресс
        progress_text = small_font.render(f"ВЫПОЛНЕНО: {self.player.completed_missions}/{len(self.missions)}", True,
                                          WHITE)
        self.screen.blit(progress_text, (SCREEN_WIDTH - 300, 35))

        # Счет
        score_text = small_font.render(f"СЧЕТ: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH - 150, 10))

        # Управление
        controls = [
            "WASD - ДВИЖЕНИЕ",
            "ЛКМ - ОГОНЬ (ЗАЖАТЬ)",
            "1-8 - ОРУЖИЕ",
            "R - ПЕРЕЗАРЯДКА",
            "E - МАГАЗИН",
            "T - СМЕНА ЛОКАЦИИ",
            "U - НАВЫКИ",
            "ESC - ПАУЗА"
        ]

        for i, control in enumerate(controls):
            text = small_font.render(control, True, LIGHT_GREY)
            self.screen.blit(text, (SCREEN_WIDTH - 150, 60 + i * 20))

        # Подсказка о входе в магазин в открытом мире
        location = self.city.get_current_location()
        shop_world_x = location.world_x
        shop_world_y = location.world_y
        dist = math.sqrt((self.player.x - shop_world_x) ** 2 + (self.player.y - shop_world_y) ** 2)
        if dist < 200:
            hint_text = small_font.render("НАЖМИ E ДЛЯ ВХОДА В МАГАЗИН", True, GOLD)
            self.screen.blit(hint_text, (SCREEN_WIDTH // 2 - hint_text.get_width() // 2, SCREEN_HEIGHT - 150))

        # Сообщение магазина
        if self.shop_message_timer > 0:
            msg_text = small_font.render(self.shop_message, True, GREEN if "Куплено" in self.shop_message or "увелич" in self.shop_message else RED)
            self.screen.blit(msg_text, (SCREEN_WIDTH // 2 - msg_text.get_width() // 2, SCREEN_HEIGHT - 120))

        # Название локации
        location_text = small_font.render(f"ЛОКАЦИЯ: {location.name}", True, BLUE)
        self.screen.blit(location_text, (SCREEN_WIDTH - 300, 60))

        # Статистика
        stats_text = small_font.render(f"УБИТО: {self.player.kills} | БОССОВ: {self.player.bosses_killed}", True, WHITE)
        self.screen.blit(stats_text, (SCREEN_WIDTH - 300, 85))

        # Комбо
        if self.player.combo > 0:
            combo_text = small_font.render(f"КОМБО x{self.player.combo}!", True, GOLD)
            combo_alpha = min(255, int(255 * (self.player.combo_timer / 60)))
            self.screen.blit(combo_text, (SCREEN_WIDTH // 2 - combo_text.get_width() // 2, 200))

        # Броня
        if self.player.armor > 0:
            armor_text = small_font.render(f"БРОНЯ: {self.player.armor}", True, BLUE)
            self.screen.blit(armor_text, (10, 140))

        # Уровень и опыт
        level_text = small_font.render(f"УРОВЕНЬ: {self.player.level}", True, (0, 255, 255))
        self.screen.blit(level_text, (10, 165))

        exp_progress = self.player.experience / self.player.experience_to_next
        exp_bar_width = 150
        pygame.draw.rect(self.screen, DARK_GREY, (10, 185, exp_bar_width + 4, 12))
        pygame.draw.rect(self.screen, (0, 255, 255), (12, 187, int(exp_bar_width * exp_progress), 8))
        pygame.draw.rect(self.screen, WHITE, (10, 185, exp_bar_width + 4, 12), 1)

        exp_text = small_font.render(f"{self.player.experience}/{self.player.experience_to_next} ОПЫТ", True, WHITE)
        self.screen.blit(exp_text, (170, 183))

        # Очки навыков
        if self.player.skill_points > 0:
            skill_text = small_font.render(f"ОЧКИ НАВЫКОВ: {self.player.skill_points} (нажми U)", True, GOLD)
            self.screen.blit(skill_text, (10, 205))

        # Достижения
        unlocked_count = sum(1 for a in self.achievements if a.unlocked)
        achievements_text = small_font.render(f"ДОСТИЖЕНИЯ: {unlocked_count}/{len(self.achievements)}", True, GOLD)
        self.screen.blit(achievements_text, (SCREEN_WIDTH - 300, 110))

    def draw_main_menu(self):
        self.screen.fill(DARK_GREY)

        # Анимированный заголовок
        pulse = math.sin(pygame.time.get_ticks() * 0.003) * 5
        title = title_font.render("БРАТВА: УЛИЦЫ СТОЛИЦЫ", True, GOLD)
        shadow = title_font.render("БРАТВА: УЛИЦЫ СТОЛИЦЫ", True, (100, 80, 0))

        self.screen.blit(shadow, (SCREEN_WIDTH // 2 - title.get_width() // 2 + 3, 153 + pulse))
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150 + pulse))

        # Подзаголовок
        subtitle = menu_font.render("ЭПИЧЕСКИЙ РЕМАСТЕР В СТИЛЕ RDR2!", True, WHITE)
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 230))

        # Кнопки
        button_y = 350
        buttons = [
            ("НАЧАТЬ ИГРУ", self.start_game),
            ("УПРАВЛЕНИЕ", self.show_controls),
            ("ВЫХОД", sys.exit)
        ]

        mouse_pos = pygame.mouse.get_pos()
        for i, (text, action) in enumerate(buttons):
            color = GOLD if (mouse_pos[0] > SCREEN_WIDTH // 2 - 100 and mouse_pos[0] < SCREEN_WIDTH // 2 + 100 and
                             mouse_pos[1] > button_y + i * 80 and mouse_pos[1] < button_y + i * 80 + 50) else LIGHT_GREY

            pygame.draw.rect(self.screen, color, (SCREEN_WIDTH // 2 - 100, button_y + i * 80, 200, 50))
            pygame.draw.rect(self.screen, WHITE, (SCREEN_WIDTH // 2 - 100, button_y + i * 80, 200, 50), 2)

            btn_text = menu_font.render(text, True, BLACK)
            self.screen.blit(btn_text, (SCREEN_WIDTH // 2 - btn_text.get_width() // 2, button_y + i * 80 + 10))

    def show_controls(self):
        self.screen.fill(DARK_GREY)

        title = title_font.render("УПРАВЛЕНИЕ", True, GOLD)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        controls = [
            "W, A, S, D / СТРЕЛКИ - ПЕРЕДВИЖЕНИЕ",
            "ЛЕВАЯ КНОПКА МЫШИ - ОГОНЬ / АТАКА НОЖОМ",
            "1-9 - ВЫБОР ОРУЖИЯ (9 - НОЖ)",
            "U - МЕНЮ НАВЫКОВ",
            "R - ПЕРЕЗАРЯДКА",
            "ESC - ПАУЗА / МЕНЮ",
            "ПРОБЕЛ - ПРОПУСК ДИАЛОГОВ"
        ]

        for i, control in enumerate(controls):
            text = dialog_font.render(control, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 200 + i * 40))

        back_text = small_font.render("Нажми ESC для возврата", True, LIGHT_GREY)
        self.screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, SCREEN_HEIGHT - 100))

    def draw_game(self):
        # Применение тряски экрана (используется ScreenShake)
        shake_x, shake_y = self.screen_shake.get_offset()

        # Создание поверхности для отрисовки с тряской
        if abs(shake_x) > 0.1 or abs(shake_y) > 0.1:
            game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            game_surface.fill(BLACK)
        else:
            game_surface = self.screen
        # Отрисовка открытого мира
        self.city.draw(game_surface, self.player.x, self.player.y)

        # Отрисовка врагов (с учётом камеры)
        for enemy in self.enemies:
            enemy_screen_x = enemy.x - self.city.camera_x
            enemy_screen_y = enemy.y - self.city.camera_y
            old_ex, old_ey = enemy.x, enemy.y
            enemy.x, enemy.y = enemy_screen_x, enemy_screen_y
            enemy.draw(game_surface)
            enemy.x, enemy.y = old_ex, old_ey

        # Отрисовка пуль (с учётом камеры)
        for bullet in self.bullets:
            bullet_screen_x = bullet.x - self.city.camera_x
            bullet_screen_y = bullet.y - self.city.camera_y
            old_bx, old_by = bullet.x, bullet.y
            bullet.x, bullet.y = bullet_screen_x, bullet_screen_y
            bullet.draw(game_surface)
            bullet.x, bullet.y = old_bx, old_by

        # Отрисовка частиц (с учётом камеры)
        for particle in self.particles:
            particle_screen_x = particle.x - self.city.camera_x
            particle_screen_y = particle.y - self.city.camera_y
            old_px, old_py = particle.x, particle.y
            particle.x, particle.y = particle_screen_x, particle_screen_y
            particle.draw(game_surface)
            particle.x, particle.y = old_px, old_py

        # Отрисовка чисел урона (с учётом камеры)
        for dmg_num in self.damage_numbers:
            dmg_screen_x = dmg_num.x - self.city.camera_x
            dmg_screen_y = dmg_num.y - self.city.camera_y
            old_dx, old_dy = dmg_num.x, dmg_num.y
            dmg_num.x, dmg_num.y = dmg_screen_x, dmg_screen_y
            dmg_num.draw(game_surface)
            dmg_num.x, dmg_num.y = old_dx, old_dy

        # Отрисовка частей тел (с учётом камеры)
        for body_part in self.body_parts:
            body_screen_x = body_part.x - self.city.camera_x
            body_screen_y = body_part.y - self.city.camera_y
            old_bpx, old_bpy = body_part.x, body_part.y
            body_part.x, body_part.y = body_screen_x, body_screen_y
            body_part.draw(game_surface)
            body_part.x, body_part.y = old_bpx, old_bpy

        # Отрисовка игрока (с учётом камеры - как в старом коде)
        player_screen_x = self.player.x - self.city.camera_x
        player_screen_y = self.player.y - self.city.camera_y

        # Сохраняем оригинальные координаты
        old_x, old_y = self.player.x, self.player.y
        self.player.x, self.player.y = player_screen_x, player_screen_y
        self.player.draw(game_surface)
        self.player.x, self.player.y = old_x, old_y


        # Применение тряски к экрану
        if abs(shake_x) > 0.1 or abs(shake_y) > 0.1:
            self.screen.blit(game_surface, (int(shake_x), int(shake_y)))

        # Отрисовка ленты убийств (поверх всего)
        for i, kill_entry in enumerate(self.kill_feed):
            kill_entry.draw(self.screen, SCREEN_HEIGHT - 200 - i * 25)

        # Прицел
        self.draw_crosshair()

        # Мини-карта
        self.draw_minimap()

        # Интерфейс
        self.draw_ui()

        # Уведомление о достижении
        if self.current_achievement_notification and self.achievement_notification_timer > 0:
            alpha = min(255, int(255 * (self.achievement_notification_timer / 60)))
            achievement = self.current_achievement_notification

            # Фон уведомления
            notification_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, 50, 500, 100)
            s = pygame.Surface((500, 100), pygame.SRCALPHA)
            s.fill((0, 0, 0, alpha))
            self.screen.blit(s, (SCREEN_WIDTH // 2 - 250, 50))
            pygame.draw.rect(self.screen, GOLD, notification_rect, 3)

            # Текст достижения
            title_text = menu_font.render("ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО!", True, GOLD)
            self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 60))

            name_text = dialog_font.render(achievement.name, True, WHITE)
            self.screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, 100))

    def draw_pause(self):
        self.draw_game()

        # Затемнение
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        s.fill((0, 0, 0, 150))
        self.screen.blit(s, (0, 0))

        # Меню паузы
        pause_text = title_font.render("ПАУЗА", True, GOLD)
        self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 200))

        options = [
            "ПРОДОЛЖИТЬ (ESC)",
            "В ГЛАВНОЕ МЕНЮ"
        ]

        mouse_pos = pygame.mouse.get_pos()
        for i, option in enumerate(options):
            color = GOLD if (mouse_pos[0] > SCREEN_WIDTH // 2 - 150 and mouse_pos[0] < SCREEN_WIDTH // 2 + 150 and
                             mouse_pos[1] > 300 + i * 70 and mouse_pos[1] < 300 + i * 70 + 50) else WHITE

            text = menu_font.render(option, True, color)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 300 + i * 70))

    def draw_game_over(self):
        self.screen.fill(BLACK)

        game_over = title_font.render("ТЕБЯ ЗАКОНСИЛИЛИ!", True, RED)
        self.screen.blit(game_over, (SCREEN_WIDTH // 2 - game_over.get_width() // 2, 200))

        stats = [
            f"Волна: {self.wave_manager.wave}",
            f"Убито врагов: {self.player.kills}",
            f"Выполнено задач: {self.player.completed_missions}",
            f"Заработано: {self.player.money} рублей",
            f"Финальный счет: {self.score}"
        ]

        for i, stat in enumerate(stats):
            text = menu_font.render(stat, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 300 + i * 50))

        restart = menu_font.render("Нажми R для рестарта или ESC в меню", True, LIGHT_GREY)
        self.screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, 600))

    def draw_win(self):
        self.screen.fill(DARK_GREY)

        win = title_font.render("ПОБЕДА! ТЫ КОРОЛЬ РАЙОНА!", True, GOLD)
        self.screen.blit(win, (SCREEN_WIDTH // 2 - win.get_width() // 2, 150))

        stats = [
            "Ты прошел все испытания и стал",
            "настоящим хозяином улиц!",
            "",
            f"ФИНАЛЬНАЯ СТАТИСТИКА:",
            f"Волна: {self.wave_manager.wave}",
            f"Убито врагов: {self.player.kills}",
            f"Заработано: {self.player.money} рублей",
            f"Финальный счет: {self.score}",
            "",
            "Уважение тебе обеспечено!"
        ]

        for i, stat in enumerate(stats):
            color = GOLD if i == 3 else WHITE
            text = dialog_font.render(stat, True, color)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 250 + i * 35))

        restart = menu_font.render("Нажми R для новой игры или ESC в меню", True, LIGHT_GREY)
        self.screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, 600))

    def draw_skills_menu(self):
        # Фон меню навыков
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        # Заголовок
        title = title_font.render("НАВЫКИ", True, GOLD)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))

        # Очки навыков
        points_text = menu_font.render(f"ОЧКИ НАВЫКОВ: {self.player.skill_points}", True, GOLD)
        self.screen.blit(points_text, (SCREEN_WIDTH // 2 - points_text.get_width() // 2, 120))

        # Список навыков
        skills_list = [
            ("1 - УРОН", f"Уровень: {self.player.skills['damage']}", "Увеличивает урон всех оружий на 10%"),
            ("2 - ЗДОРОВЬЕ", f"Уровень: {self.player.skills['health']}", "Увеличивает максимальное здоровье на 15"),
            ("3 - СКОРОСТЬ", f"Уровень: {self.player.skills['speed']}", "Увеличивает скорость передвижения"),
            ("4 - ПАТРОНЫ", f"Уровень: {self.player.skills['ammo']}", "Увеличивает размер магазина на 15%"),
            ("5 - РЕГЕНЕРАЦИЯ", f"Уровень: {self.player.skills['regen']}", "Ускоряет восстановление здоровья"),
        ]

        start_y = 200
        for i, (key, level, desc) in enumerate(skills_list):
            y_pos = start_y + i * 80

            # Фон навыка (меняем цвет если нет очков)
            bg_color = DARK_GREY if self.player.skill_points > 0 else (30, 30, 30)
            border_color = GOLD if self.player.skill_points > 0 else LIGHT_GREY
            pygame.draw.rect(self.screen, bg_color, (SCREEN_WIDTH // 2 - 300, y_pos, 600, 70))
            pygame.draw.rect(self.screen, border_color, (SCREEN_WIDTH // 2 - 300, y_pos, 600, 70), 2)

            # Текст
            key_text = dialog_font.render(key, True, WHITE)
            self.screen.blit(key_text, (SCREEN_WIDTH // 2 - 280, y_pos + 10))

            level_text = small_font.render(level, True, GOLD)
            self.screen.blit(level_text, (SCREEN_WIDTH // 2 - 280, y_pos + 35))

            desc_text = small_font.render(desc, True, LIGHT_GREY)
            self.screen.blit(desc_text, (SCREEN_WIDTH // 2 - 280, y_pos + 50))

            # Показываем статус доступности
            if self.player.skill_points == 0:
                no_points_text = small_font.render("Нет очков навыков", True, RED)
                self.screen.blit(no_points_text, (SCREEN_WIDTH // 2 + 200, y_pos + 35))

        # Подсказка
        if self.player.skill_points > 0:
            hint = small_font.render("Нажми 1-5 для улучшения навыка | ESC - выход", True, LIGHT_GREY)
        else:
            hint = small_font.render("Нет очков навыков! Получайте опыт за убийства | ESC - выход", True, RED)
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 80))

    def start_game(self):
        # Начинаем с катсцены в стиле Hotline Miami
        self.hotline_cutscene = HotlineCutscene()
        self.state = GameState.CUTSCENE
        self.player = Player()
        # Размещаем игрока в центре текущей локации
        current_loc = self.city.get_current_location()
        self.player.x = current_loc.world_x
        self.player.y = current_loc.world_y
        self.enemies = []
        self.bullets = []
        self.particles = []
        self.damage_numbers = []
        self.body_parts = []  # Очищаем части тел при старте новой игры
        self.kill_feed = []
        self.score = 0
        self.wave_manager.wave = 1
        self.current_mission_index = 0
        self.enemy_spawn_timer = 0
        self.player.completed_missions = 0
        self.player.mission_kills = 0
        # Инициализируем камеру
        self.city.update_camera(self.player.x, self.player.y)
        # Сбрасываем флаг пропуска катсцены
        self.skip_cutscene_prompt = False
        self.skip_cutscene_timer = 0

    def run(self):
        running = True

        while running:
            running = self.handle_events()

            # Обновление игры только если не в паузе или меню
            if self.state == GameState.PLAYING:
                self.update()
            elif self.state == GameState.CUTSCENE and self.hotline_cutscene:
                # Обновление катсцены Hotline Miami (только анимация, без пропуска)
                if self.hotline_cutscene.update(skip=False):
                    # Катсцена завершена автоматически
                    self.hotline_cutscene = None
                    self.start_mission_cutscene(0)

            # Отрисовка
            if self.state == GameState.MAIN_MENU:
                self.draw_main_menu()
            elif self.state == GameState.PLAYING:
                self.draw_game()
            elif self.state == GameState.CUTSCENE:
                if self.hotline_cutscene:
                    # Отображение подсказки о пропуске катсцены
                    self.hotline_cutscene.draw(self.screen)

                    # Отображение подсказки о пропуске катсцены
                    if self.skip_cutscene_prompt:
                        # Фон подсказки
                        prompt_surface = pygame.Surface((400, 80), pygame.SRCALPHA)
                        prompt_surface.fill((0, 0, 0, 180))
                        prompt_rect = prompt_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
                        self.screen.blit(prompt_surface, prompt_rect)

                        # Текст подсказки
                        prompt_text1 = dialog_font.render("Нажми ПРОБЕЛ еще раз чтобы пропустить", True, GOLD)
                        prompt_text2 = small_font.render(f"Истекает через: {self.skip_cutscene_timer // 60 + 1} сек", True, WHITE)

                        self.screen.blit(prompt_text1, (SCREEN_WIDTH // 2 - prompt_text1.get_width() // 2, SCREEN_HEIGHT - 120))
                        self.screen.blit(prompt_text2, (SCREEN_WIDTH // 2 - prompt_text2.get_width() // 2, SCREEN_HEIGHT - 80))
                    else:
                        # Стандартная подсказка о пропуске
                        skip_text = small_font.render("Нажми ПРОБЕЛ для пропуска вступления", True, LIGHT_GREY)
                        self.screen.blit(skip_text, (SCREEN_WIDTH // 2 - skip_text.get_width() // 2, SCREEN_HEIGHT - 50))
                elif self.cutscene:
                    self.cutscene.draw(self.screen)
            elif self.state == GameState.PAUSE:
                self.draw_pause()
            elif self.state == GameState.GAME_OVER:
                self.draw_game_over()
            elif self.state == GameState.WIN:
                self.draw_win()
            elif self.state == GameState.CONTROLS:
                self.show_controls()
            elif self.state == GameState.SHOP:
                self.draw_game()
                self.shop.draw(self.screen, self.player)
            elif self.state == GameState.SKILLS:
                self.draw_game()
                self.draw_skills_menu()

            # Обработка кликов в меню паузы
            if self.state == GameState.PAUSE:
                mouse_pos = pygame.mouse.get_pos()
                if pygame.mouse.get_pressed()[0]:
                    # Продолжить
                    if (mouse_pos[0] > SCREEN_WIDTH // 2 - 150 and mouse_pos[0] < SCREEN_WIDTH // 2 + 150 and
                        mouse_pos[1] > 300 and mouse_pos[1] < 350):
                        self.state = GameState.PLAYING
                    # В главное меню
                    elif (mouse_pos[0] > SCREEN_WIDTH // 2 - 150 and mouse_pos[0] < SCREEN_WIDTH // 2 + 150 and
                          mouse_pos[1] > 370 and mouse_pos[1] < 420):
                        self.state = GameState.MAIN_MENU

            # Обработка рестарта
            keys = pygame.key.get_pressed()
            if self.state in [GameState.GAME_OVER, GameState.WIN] and keys[pygame.K_r]:
                self.start_game()

            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()