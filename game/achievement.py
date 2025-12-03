"""
Система достижений
"""
class Achievement:
    def __init__(self, name, description, condition_func):
        self.name = name
        self.description = description
        self.condition_func = condition_func
        self.unlocked = False
        self.show_time = 0

    def check(self, player, game):
        if not self.unlocked and self.condition_func(player, game):
            self.unlocked = True
            self.show_time = 180
            return True
        return False

