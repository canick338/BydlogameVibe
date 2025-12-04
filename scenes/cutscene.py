"""
Класс обычной катсцены
"""
import pygame
from game.config import SCREEN_WIDTH, SCREEN_HEIGHT, DARK_GREY, WHITE, LIGHT_GREY, dialog_font, small_font


class Cutscene:
    def __init__(self, texts, background_color=DARK_GREY, mission_complete=False):
        self.texts = texts
        self.current_text = 0
        self.background_color = background_color
        self.timer = 0
        self.mission_complete = mission_complete

    def update(self, dt):
        self.timer += dt
        if self.timer > 4000:  # 4 секунды на кадр
            self.timer = 0
            self.current_text += 1
            return self.current_text >= len(self.texts)
        return False

    def next(self):
        """
        Принудительно переключить катсцену на следующий текст.
        Возвращает True, если катсцена полностью закончилась.
        """
        self.timer = 0
        self.current_text += 1
        return self.current_text >= len(self.texts)

    def draw(self, screen):
        screen.fill(self.background_color)

        if self.current_text < len(self.texts):
            lines = self.texts[self.current_text].split('\n')
            for i, line in enumerate(lines):
                text = dialog_font.render(line, True, WHITE)
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2,
                                   SCREEN_HEIGHT // 2 - len(lines) * 20 + i * 40))

        # Индикатор продолжения
        if pygame.time.get_ticks() % 1000 < 500:
            hint_text = "Нажми ПРОБЕЛ чтобы продолжить" if not self.mission_complete else "Нажми ПРОБЕЛ для завершения миссии"
            hint = small_font.render(hint_text, True, LIGHT_GREY)
            screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 100))

