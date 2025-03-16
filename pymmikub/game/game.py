from typing import List
from .color import Color
from dataclasses import dataclass
from itertools import cycle
from flask_socketio import emit
import random
import uuid


@dataclass
class Tile:
    id: str
    number: int
    color: Color
    is_new: bool


    def __init__(self, number: int, color: Color, is_new: bool, id: str = None) -> None:
        if id is None:
            self.id = str(uuid.uuid4())
        else:
            self.id = id
        self.number = number
        self.color = color
        self.is_new = is_new


    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "number" : self.number,
            "color" : self.color.value,
            "is_new" : self.is_new,
        }


    def __eq__(self, other) -> bool:
        return self.id == other.id


class Combination:
    tiles: List[Tile] = []


    def __init__(self) -> None:
        self.tiles = []


    def insert_tile(self, tile: Tile, position: int) -> None:
        self.tiles.insert(position, tile)


    def check_validity(self) -> bool:
        if len(self.tiles) == 0:
            print("Combination empty")
            return True
        
        if len(self.tiles) < 3:
            print("Combination too short")
            return False

        numbers: List[int] = [tile.number for tile in self.tiles]
        numbers = sorted(numbers)
        colors: List[Color] = [tile.color for tile in self.tiles]
        unique_numbers: int = len(set(numbers))
        unique_colors: int = len(set(colors))

        print(f'numbers: {numbers}')
        print(f'colors: {colors}')
        print(f'unique_numbers: {unique_numbers}')
        print(f'unique_colors: {unique_colors}')

        # series of unique numbers of one color
        if unique_numbers == len(numbers) and \
            numbers == list(range(numbers[0], numbers[-1]+1)) and \
            unique_colors == 1:
            return True
        # one number in several unique colors
        elif unique_numbers == 1 and unique_colors == len(self.tiles):
            return True
        
        return False
    
    
    def to_dict(self) -> List[dict]:
        data: dict = {}
        data.update({"is_valid" : self.check_validity()})
        data.update({"tiles" : [tile.to_dict() for tile in self.tiles]})
        return data
    

    def __eq__(self, value) -> bool:
        if isinstance(value, Combination):
            return self.tiles == value.tiles


class Player:
    hand: Combination = Combination()
    name: str
    sid: str

    has_entered: bool = False


    def __init__(self, sid: str, name: str) -> None:
        self.sid = sid
        self.name = name


    def to_dict(self) -> dict:
        return {
            "name" : self.name,
            "hand" : self.hand.to_dict(),
        }


class Board:
    combos: List[Combination] = []

    def __init__(self) -> None:
        self.refresh_board()


    def check_valid_board(self) -> bool:
        for combo in self.combos:
            if combo.check_validity() == False:
                print(combo.tiles)
                return False
        return True
    

    def refresh_board(self) -> None:
        self.combos = [combo for combo in self.combos if len(combo.tiles) > 0]
        self.combos.append(Combination())


class Game:
    room: str = ""
    
    tiles: List[Tile] = []
    board: Board = Board()
    players: dict[str, Player] = {}
    current_player: str = ""
    tile_count: int = 0


    def __init__(self, room: str) -> None:
        self.initialize_tiles()
        self.room = room


    def initialize_tiles(self) -> None:
        # i in range (2, 28) and floor division by 2 gives us two tiles of each number
        for color in Color:
            for i in range(2, 28):
                self.tiles.extend([Tile(i // 2, color, True)])
        
        # TODO: add jokers
        random.shuffle(self.tiles)


    def draw_tile(self, n: int = 1) -> List[Tile]:
        # figure out what to do if there are not enough tiles in heap
        drawn_tiles, self.tiles = self.tiles[:n], self.tiles[n:]

        return drawn_tiles
    

    def has_current_player_moved(self) -> bool:
        return len(self.players.get(self.current_player).hand.tiles) != self.tile_count



    def place_tile(self, player: Player, tile: Tile, origin: Combination, target: Combination, position: int) -> None:
        # shuffle tiles in hand, should be able to do even if it's not your turn
        if tile in player.hand.tiles and target == player.hand:
            player.hand.tiles.remove(tile)
            target.insert_tile(tile, position)
            return

        # check for player turn
        if player != self.players.get(self.current_player):
            return

        # if tile is in hand, place it on board
        if tile in player.hand.tiles and target != player.hand:
            target.insert_tile(tile, position)
            player.hand.tiles.remove(tile)
        # else if target is hand
        elif not (tile in player.hand.tiles) and target == player.hand and tile.is_new:
            player.hand.insert_tile(tile, position)
            origin.tiles.remove(tile)
        # else if target is board
        elif tile not in player.hand.tiles and target != player.hand:
            target.insert_tile(tile, position)
            origin.tiles.remove(tile)

        self.board.refresh_board()


    def connect_player(self, sid, name: str) -> None:
        player: Player = Player(sid, name)
        self.players.update({sid: player})
        
        player.hand = Combination()
        player.hand.tiles = self.draw_tile(14)
        
        if self.current_player == "":
            self.current_player = sid
            self.tile_count = 14
        
        emit('lobby_update', {"players" : [*self.players]})
        emit('turn_update', {"current_player" : self.current_player, "remaining_tiles" : len(self.tiles)})
    

    def end_turn(self) -> None:
        p : Player = self.players.get(self.current_player)
        
        if not self.board.check_valid_board():
            return
        if len(p.hand.tiles) == self.tile_count:
            p.hand.tiles.append(self.draw_tile(1)[0])
        
        self.current_player = next(iter(cycle(self.players)))
        self.tile_count = len(p.hand.tiles)

        for combo in self.board.combos:
            for tile in combo.tiles:
                tile.is_new = False
        
        emit('turn_update', {"current_player" : self.current_player, "remaining_tiles" : len(self.tiles)})
        

class GameEncoder():
    def encode(o, sid) -> dict:
        if isinstance(o, Game):
            roominfo = {
                #"tiles": [(tile[0], str(tile[1])) for tile in o.tiles],
                "tiles": len(o.tiles),
                "board": [combo.to_dict() for combo in o.board.combos],
                "hand" : o.players.get(sid).hand.to_dict(),
                "players": [player for player in o.players],
                "has_player_moved": o.has_current_player_moved(),
                }
            gameinfo = {o.room : roominfo}
            return gameinfo
        else:
            return ""