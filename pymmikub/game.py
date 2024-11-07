import random
from enum import Enum

class Color(Enum):
    BLACK = 1
    YELLOW = 2
    BLUE = 3
    RED = 4


tiles = []


def initialize_tiles():
    for i in range(4):
        for y in range(13):
            tiles.append((y, Color(i + 1)))
    # TODO: add jokers


def draw_tile():
    pass


def draw_initial_tiles():
    # Returns a list of 14 tiles (just for demonstration purposes)
    return [random.randint(1, 104) for _ in range(14)]