from typing import List
from .color import Color
from collections import Counter
import random
from json import JSONEncoder

class Player:
    hand: List[tuple[int, Color]] = []
    name: str
    sid: str

    has_entered: bool
    has_placed: bool


    def __init__(self, sid: str, name: str) -> None:
        self.sid = sid
        self.name = name


    def to_dict(self):
        return {
            "name" : self.name,
            "hand" : [(tile[0], str(tile[1])) for tile in self.hand],
        }


class Combination:
    tiles: List[tuple[int, Color]] = []


    def __init__(self):
        self.tiles = []


    def insert_tile(self, tile: tuple[int, Color], position: int):
        self.tiles.insert(position, tile)


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
    
    
    def to_dict(self):
        return [(tile[0], str(tile[1])) for tile in self.tiles]


class Board:
    combos: List[Combination] = []

    def __init__(self):
        self.refresh_board()


    def check_valid_board(self) -> bool:
        for combo in self.combos:
            if combo.check_validity() == False:
                return False
        return True
    

    def refresh_board(self) -> None:
        self.combos = [combo for combo in self.combos if len(combo.tiles) > 0]
        self.combos.append(Combination())


class Game:
    room: str = ""
    
    tiles: List[tuple[int, Color]] = []
    board: Board = Board()
    players: dict[str, Player] = {}


    def __init__(self, room: str) -> None:
        self.initialize_tiles()
        self.room = room


    def initialize_tiles(self) -> None:
        for color in Color:
            for j in range(1, 13):
                self.tiles.extend([(j, color.value), (j, color.value)])
        # TODO: add jokers
        random.shuffle(self.tiles)


    def draw_tile(self, n: int = 1) -> List[tuple[int, Color]]:
        # figure out what to do if there are not enough tiles in heap
        drawn_tiles = self.tiles[:n]

        return drawn_tiles


    def place_tile(self, player: Player, tile: tuple[int, Color], combo: Combination, position: int) -> None:
        # TODO: check for player turn
        #if player != self.current_player:
        #    return
        
        # TODO: switch tiles on board

        if tile in player.hand:
            combo.insert_tile(tile, position)
            player.hand.remove(tile)
        
        self.board.refresh_board()


    def connect_player(self, sid, name: str) -> None:
        player: Player = Player(sid, name)
        self.players.update({sid: player})
        player.hand = self.draw_tile(14)


class GameEncoder():
    def encode(o, sid) -> dict:
        if isinstance(o, Game):
            roominfo = {
                #"tiles": [(tile[0], str(tile[1])) for tile in o.tiles],
                "tiles": len(o.tiles),
                "board": [combo.tiles for combo in o.board.combos],
                "hand" : o.players.get(sid).hand,
                "players": [player for player in o.players]
                }
            gameinfo = {o.room : roominfo}
            return gameinfo
        else:
            return ""