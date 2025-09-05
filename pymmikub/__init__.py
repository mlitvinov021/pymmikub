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
    # Optional mapping for display names by player_id (can be extended later)
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

        # Identify the player via cookie; fallback to request SID if missing
        player_id = request.cookies.get('player_id') or request.sid  # type: ignore

        # Optional nickname provided by client
        nickname = data.get('nickname')
        if nickname:
            playernames[player_id] = nickname
        else:
            # preserve existing or default to id
            playernames.setdefault(player_id, player_id)

        join_room(room_name)

        if room_name not in games:
            new_game: Game = Game(room_name)
            games.update({room_name: new_game})

        game: Game | None = games.get(room_name)
        if game:
            game.connect_player(player_id, request.sid, playernames.get(player_id, player_id))  # type: ignore
        else:
            print(f"Game room '{room_name}' not found.")

        update_room(room_name)


    @socketio.on('place_tile')
    def handle_place_tile(data):
        room_name: str = data['room']
        game: Game = games[room_name]
        # Lookup player by cookie player_id
        player_id = request.cookies.get('player_id')  # type: ignore
        if not player_id or player_id not in game.players:
            return
        player: Player = game.players[player_id]  # type: ignore
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
        player_id = request.cookies.get('player_id')  # type: ignore
        if not player_id or player_id not in game.players:
            return
        player: Player = game.players[player_id]  # type: ignore
        game.end_turn(player)

        update_room(room_name)


    def update_room(room_name: str) -> None: 
        game: Game | None = games.get(room_name)
        if game is None:
            return

        # Send personalized update to each active SID of each player
        for pid, player in game.players.items():
            data = GameEncoder.encode(game, pid)
            # Player can have multiple SIDs (multiple tabs)
            for sid in list(game._connections.get(pid, set())):
                emit('game_update', data, to=sid)

    @socketio.on('disconnect')
    def handle_disconnect():
        # Find the game this SID belongs to and remove it
        sid = request.sid  # type: ignore
        for room_name, game in games.items():
            if sid in game._sid_to_pid:
                game.disconnect_sid(sid)
                update_room(room_name)
                break


    return app
