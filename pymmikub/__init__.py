import os

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room
from pymmikub.game.color import Color
from pymmikub.game.game import Combination, Game, GameEncoder, Player, Tile
from . import db

# blueprint imports
from .auth import auth as auth_blueprint
from .main import main as main_blueprint


def create_app(test_config=None):
    app: Flask = Flask(__name__, instance_relative_config=True)
    socketio: SocketIO = SocketIO(app)

    games: dict[str, Game] = {}
    playernames: dict[str, str] = {}

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'pymmikub.sqlite')
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    db.init_app(app)

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    
    
    @socketio.on('join_game')
    def handle_join_game(data):
        room_name: str = data['room']

        # TODO: of course set the actual player name
        playernames[request.sid] = request.sid # type: ignore

        join_room(room_name)

        if room_name not in games:
            new_game: Game = Game(room_name)
            games.update({room_name: new_game})

        game : Game | None = games.get(room_name)
        if game:
            game.connect_player(request.sid, playernames.get(request.sid)) # type: ignore
        else:
            print(f"Game room '{room_name}' not found.")

        update_room(room_name)


    @socketio.on('place_tile')
    def handle_place_tile(data):
        room_name: str = data['room']
        game: Game = games[room_name]
        player: Player = game.players[request.sid] # type: ignore
        is_new = (lambda x: True if isinstance(x, str) and x.lower() == "true" else False)(data['tile']['is_new'])
        tile: Tile = Tile(data['tile']['number'], Color(data['tile']['color']), is_new, data['tile']['id'])
        origin: Combination = game.board.combos[int(data['origin']) - 1]

        if int(data['target']) == 0:
            target: Combination = player.hand
        else:
            target: Combination = game.board.combos[int(data['target']) - 1]
        
        position: int = int(data['position'])
        
        game.place_tile(player, tile, origin, target, position)

        update_room(room_name)


    @socketio.on('end_turn')
    def handle_end_turn(data):
        room_name: str = data['room']
        game: Game = games[room_name]
        player: Player = game.players[request.sid] # type: ignore
        game.end_turn(player)

        update_room(room_name)


    def update_room(room_name: str) -> None: 
        game: Game | None = games.get(room_name)
        if game is None:
            return

        for player in game.players:
            data = GameEncoder.encode(game, player)
            emit('game_update', data, to=player)


    return app
