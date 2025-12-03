"""
Управление тряской экрана
"""
import random


class ScreenShake:
    """Эффект тряски экрана"""
    
    def __init__(self):
        self.intensity = 0
        self.timer = 0
    
    def shake(self, intensity=5, duration=10):
        """Запуск тряски"""
        self.intensity = intensity
        self.timer = duration
    
    def update(self):
        """Обновление тряски"""
        if self.timer > 0:
            self.timer -= 1
            self.intensity *= 0.9
            return True
        return False
    
    def get_offset(self):
        """Получение смещения для тряски"""
        if self.timer > 0:
            return (
                random.uniform(-self.intensity, self.intensity),
                random.uniform(-self.intensity, self.intensity)
            )
        return (0, 0)

