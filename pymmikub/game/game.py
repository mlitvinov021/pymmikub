from typing import List
from .color import Color
from collections import Counter
import random


class Player:
    hand: List[tuple[int, Color]] = []
    name: str
    uuid: str

    has_entered: bool
    has_placed: bool


    def __init__(self, name) -> None:
        self.name = name


class Combination:
    tiles: List[tuple[int, Color]] = []


    def check_validity(self) -> bool:
        if self.tiles.length > 0 and self.tiles.length < 3:
            return False

        numbers: List[int] = [i[0] for i in self.tiles]
        numbers = sorted(numbers)
        colors: List[Color] = [i[1] for i in self.tiles]
        unique_numbers: int = Counter(numbers).values()
        unique_colors: int = Counter(colors).values()

        # series of unique numbers of one color
        if unique_numbers == numbers.length and \
            numbers == list(range(numbers[0], numbers[-1]+1)) and \
            unique_colors == 1:
            return True
        # one number in several unique colors
        elif unique_numbers == 1 and unique_colors == self.tiles.length:
            return True
        
        return False


class Board:
    combos: List[Combination] = []


    def check_valid_board(self) -> bool:
        for combo in self.combos:
            if combo.check_validity() == False:
                return False
        return True


class Game:
    tiles: List[tuple[int, Color]] = []
    players: List[Player] = []
    current_player: Player
    current_turn: int


    def __init__(self) -> None:
        self.initialize_tiles()
        current_turn = 0


    def initialize_tiles(self) -> None:
        for i in range(4):
            for j in range(1, 13):
                self.tiles.append((j, Color(i + 1)))
        # TODO: add jokers
        random.shuffle(self.tiles)


    def draw_tile(self, n: int = 1) -> List[tuple[int, Color]]:
        # drawn_tiles: List[tuple[int, Color]] = []
        drawn_tiles = self.tiles[:n]

        return drawn_tiles


    def change_turn(self) -> None:
        current_turn += 1
        current_player = self.players[current_turn % self.players.length]


    def place_tile(self, player: Player, tile: tuple[int, Color], combo: Combination) -> None:
        if player != self.current_player:
            return
        if player.hand.pop(tile) == None:
            return
        combo.append(tile)