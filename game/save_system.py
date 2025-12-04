"""
Система сохранения игры
"""
import json
import os


class SaveSystem:
    SAVE_FILE = "savegame.json"
    
    @staticmethod
    def save_game(player_money, owned_cards, active_cards):
        """Сохраняет прогресс игры"""
        data = {
            "money": player_money,
            "owned_cards": owned_cards,  # Список ID карточек
            "active_cards": active_cards  # Список активных ID карточек
        }
        try:
            with open(SaveSystem.SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False
    
    @staticmethod
    def load_game():
        """Загружает прогресс игры"""
        if not os.path.exists(SaveSystem.SAVE_FILE):
            return {
                "money": 1000,  # Стартовые деньги
                "owned_cards": [],
                "active_cards": []
            }
        
        try:
            with open(SaveSystem.SAVE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Проверяем что все поля есть
                if "money" not in data:
                    data["money"] = 1000
                if "owned_cards" not in data:
                    data["owned_cards"] = []
                if "active_cards" not in data:
                    data["active_cards"] = []
                return data
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            return {
                "money": 1000,
                "owned_cards": [],
                "active_cards": []
            }

