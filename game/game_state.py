"""
Состояния игры
"""
from enum import Enum


class GameState(Enum):
    MAIN_MENU = 0
    PLAYING = 1
    CUTSCENE = 2
    GAME_OVER = 3
    WIN = 4
    PAUSE = 5
    MISSION_START = 6
    CONTROLS = 7
    SHOP = 8
    LOCATION_SELECT = 9
    SKILLS = 10
    SETTINGS = 11

