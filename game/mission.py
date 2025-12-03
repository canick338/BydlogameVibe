"""
Класс миссии
"""
class Mission:
    def __init__(self, title, description, target, reward, mission_type, cutscene_texts):
        self.title = title
        self.description = description
        self.target = target
        self.current = 0
        self.reward = reward
        self.completed = False
        self.type = mission_type  # "kill", "collect", "survive"
        self.timer = 0
        self.cutscene_texts = cutscene_texts

    def update(self, value=1):
        if not self.completed:
            self.current += value
            if self.current >= self.target:
                self.completed = True
                return True
        return False

    def update_timer(self, dt):
        if self.type == "survive":
            self.timer += dt
            self.current = self.timer
            if self.timer >= self.target:
                self.completed = True
                return True
        return False

