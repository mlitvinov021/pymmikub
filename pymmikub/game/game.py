from typing import List
from .color import Color
from flask_socketio import emit
import random
import uuid


class Tile:
    id: str
    number: int
    color: Color
    is_new: bool


    def __init__(self, number: int, color: Color, is_new: bool = True, id: str = "") -> None:
        if len(id) == 0:
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


    def check_valid_group(self) -> bool:
            values: set[int] = set(tile.number for tile in self.tiles if not tile.color == Color.JOKER)
            colors: set[Color] = set(tile.color for tile in self.tiles if not tile.color == Color.JOKER)
            joker_count: int = sum(1 for tile in self.tiles if tile.color == Color.JOKER)

            if len(values) > 1:
                return False
            
            if len(colors) != len(self.tiles) - joker_count:
                return False
            
            return True


    def check_valid_run(self):
            colors: set[Color] = set(tile.color for tile in self.tiles if not tile.color == Color.JOKER)
            sorted_values: list[int] = sorted([tile.number for tile in self.tiles if not tile.color == Color.JOKER])

            if len(colors) > 1:
                return False
            
            missing_values = set(range(sorted_values[0], sorted_values[-1] + 1)) - set(sorted_values)
            joker_count: int = sum(1 for tile in self.tiles if tile.color == Color.JOKER)

            return len(missing_values) <= joker_count


    def check_validity(self) -> bool:
        if len(self.tiles) == 0:
            return True
        
        if len(self.tiles) < 3:
            return False
        
        return self.check_valid_group() or self.check_valid_run()
    
    
    def to_dict(self) -> dict:
        data: dict = {}
        data.update({"is_valid" : self.check_validity()})
        data.update({"tiles" : [tile.to_dict() for tile in self.tiles]})
        return data
    

    def __eq__(self, value) -> bool:
        if isinstance(value, Combination):
            return self.tiles == value.tiles
        else:
            return False


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
            if not combo.check_validity():
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
    current_player_index: int = 0
    tile_count: int = 0


    def __init__(self, room: str) -> None:
        self.initialize_tiles()
        self.room = room


    def get_current_player(self) -> Player:
        return list(self.players.values())[self.current_player_index]
    

    def initialize_tiles(self) -> None:
        # For first 4 colors, add 26 tiles, 2 of each number.
        for color in list(Color)[:4]:
            for i in range(1, 14):
                self.tiles.extend([Tile(i, color), Tile(i, color)])
        
        # After that, add 2 jokers and shuffle the deck.
        self.tiles.extend([Tile(0, Color.JOKER), Tile(0, Color.JOKER)])
        random.shuffle(self.tiles)


    def draw_tile(self, n: int = 1) -> List[Tile]:
        # TODO: figure out what to do if there are not enough tiles in heap
        drawn_tiles, self.tiles = self.tiles[:n], self.tiles[n:]

        return drawn_tiles
    

    def has_current_player_moved(self) -> bool:
        return len(self.get_current_player().hand.tiles) != self.tile_count


    def place_tile(self, player: Player, tile: Tile, origin: Combination, target: Combination, position: int) -> None:
        # shuffle tiles in hand, should be able to do even if it's not your turn
        if tile in player.hand.tiles and target == player.hand:
            player.hand.tiles.remove(tile)
            target.insert_tile(tile, position)
            return

        # check for player turn
        if player != self.get_current_player():
            return

        # if tile is in hand, place it on board
        if tile in player.hand.tiles and target != player.hand:
            target.insert_tile(tile, position)
            player.hand.tiles.remove(tile)
        # else if target is hand
        elif tile not in player.hand.tiles and target == player.hand and tile.is_new:
            player.hand.insert_tile(tile, position)
            origin.tiles.remove(tile)
        # else if target is board
        elif tile not in player.hand.tiles and target != player.hand:
            target.insert_tile(tile, position)
            origin.tiles.remove(tile)

        self.board.refresh_board()


    def connect_player(self, sid: str, name: str) -> None:
        player: Player = Player(sid, name)
        self.players.update({sid: player})
        
        player.hand = Combination()
        player.hand.tiles = self.draw_tile(14)
        
        if len(self.players) == 1:  # If first player joins, start game
            self.current_player_index = 0
            self.tile_count = 14

        emit('turn_update', {"players" : [*self.players], "current_player" : self.get_current_player().name}, to=self.room)
    
    
    def disconnect_player(self, sid: str) -> None:
        if sid in self.players:
            idx = list(self.players).index(sid)
            self.players.pop(sid)

            # Adjust turn index to ensure it remains valid
            if idx < self.current_player_index:
                self.current_player_index -= 1
            elif self.current_player_index >= len(self.players):
                self.current_player_index = 0  # Reset to first player
        
        #TODO: actual disconnect


    def end_turn(self, player: Player) -> None:
        current_player : Player = self.get_current_player()
        
        # Check if the function was called by a current player
        if player != current_player:
            # TODO: error message (cannot end other player turn)
            return
        
        # Check whether we need to end current player turn or skip it
        if not self.board.check_valid_board():
            # TODO: error message (invalid board)
            return
        if len(current_player.hand.tiles) == self.tile_count:
            current_player.hand.tiles.append(self.draw_tile(1)[0])
        
        # Advance current player index
        if self.players:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            self.tile_count = len(self.get_current_player().hand.tiles)

        # Set all tiles on board as old
        for combo in self.board.combos:
            for tile in combo.tiles:
                tile.is_new = False
        
        #emit('turn_update', {"players" : [*self.players], "current_player" : self.get_current_player().name}, to=self.room)
    
    
    def end_game(self):
        # Make all of the tiles old so they cant be placed or moved.
        for combo in self.board.combos:
            for tile in combo.tiles:
                tile.is_new = False
        
        for player in self.players.values():
            for tile in player.hand.tiles:
                tile.is_new = False
        
        # Count player scores by adding up numbers on tiles.
        scores: dict[str, int] = {}
        for player in self.players.values():
            score: int = 0
            for tile in player.hand.tiles:
                score += 30 if tile.color == Color.JOKER else tile.number
            scores[player.name] = score

        # Sort scores: lowest wins
        sorted_scores = sorted(scores.items(), key=lambda x: x[1])
        winner_name = sorted_scores[0][0]

        # Emit win screen info to all players in room
        emit("game_won", {
            "winner": winner_name,
            "scores": sorted_scores
        }, to=self.room)
        

class GameEncoder():
    @staticmethod
    def encode(game, sid) -> dict: # type: ignore
        if isinstance(game, Game):
            player = game.players.get(sid)
            roominfo = {
                #"tiles": [(tile[0], str(tile[1])) for tile in o.tiles],
                "tiles": len(game.tiles),
                "board": [combo.to_dict() for combo in game.board.combos],
                "hand": player.hand.to_dict() if player else None,
                "players": [player for player in game.players],
                "current_player": game.get_current_player().name,
                "has_player_moved": game.has_current_player_moved(),
                }
            gameinfo = {game.room : roominfo}
            return gameinfo
        else:
            return dict()
