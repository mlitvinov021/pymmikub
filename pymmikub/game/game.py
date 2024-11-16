from .color import Color
from collections import Counter
import random


class Game:
    tiles = [(int, Color)]
    players: [Player] = []
    current_player: Player
    current_turn: int


    def __init__(self) -> None:
        initialize_tiles()
        current_turn = 0


    def initialize_tiles() -> None:
        for i in range(4):
            for y in range(13):
                tiles.append((y, Color(i + 1)))
        # TODO: add jokers
        random.shuffle(tiles)


    def draw_tile(n: int = 1) -> [(int, Color)]:
        drawn_tiles = [(int, Color)]
        drawn_tiles = tiles[:n]
        tiles = [n:]

        return drawn_tiles


    def change_turn() -> None:
        current_turn += 1
        current_player = players[current_turn % players.length]


    def place_tile(player: Player, tile: (int, Color), combo: Combination) -> None:
        if player != current_player:
            return
        if player.hand.pop(tile) == None:
            return
        combo.append(tile)


class Player:
    hand: [(int, Color)] = []
    name: str
    uuid: str

    has_entered: bool
    has_placed: bool


    def __init__(self, name) -> None:
        self.name = name


class Board:
    combos: [Combination] = []


    def check_valid_board() -> bool:
        for combo in combos:
            if combo.check_validity() == False:
                return False
        return True


class Combination:
    tiles: [(int, Color)] = []


    def check_validity() -> bool:
        if tiles.length > 0 and tiles.length < 3:
            return False

        numbers: [int] = [i[0] for i in tiles]
        numbers = sorted(numbers)
        colors: [Color] = [i[1] for i in tiles]
        unique_numbers: int = Counter(numbers).values()
        unique_colors: int = Counter(colors).values()

        # series of unique numbers of one color
        if unique_numbers == numbers.length and \
            numbers == list(range(numbers[0], numbers[-1]+1)) and \
            unique_colors == 1:
            return True
        # one number in several unique colors
        elif unique_numbers == 1 and unique_colors == tiles.length:
            return True
        
        return False