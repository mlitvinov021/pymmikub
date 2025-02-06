import os

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
from pymmikub.game.color import Color
from pymmikub.game.game import Combination, Game, GameEncoder, Player, Tile
from . import db
import json

# blueprint imports
from .auth import auth as auth_blueprint
from .main import main as main_blueprint


def create_app(test_config=None):
    app: Flask = Flask(__name__, instance_relative_config=True)
    socketio: SocketIO = SocketIO(app)

    games = {}
    playernames = {}

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
        room: str = data['room']

        # TODO: of course set the actual player name
        playernames[request.sid] = request.sid

        join_room(room)

        if room not in games:
            game: Game = Game(room)
            games.update({room: game})

        
        games.get(room).connect_player(request.sid, playernames.get(request.sid))
        data = GameEncoder.encode(games.get(room), request.sid)
        emit('game_update', data)


    # TODO: this should update the game state in game object (MODEL), update the games[room] and emit the signal for the VIEW
    @socketio.on('place_tile')
    def handle_place_tile(data):
        room: Game = games[data['room']]
        player: Player = room.players[request.sid]
        tile: Tile = Tile(data['tile']['number'], Color(data['tile']['color']), True, data['tile']['id'])
        origin: Combination = room.board.combos[int(data['origin']) - 1]

        if int(data['target']) == 0:
            target: Combination = player.hand
        else:
            target: Combination = room.board.combos[int(data['target']) - 1]
        
        position: int = int(data['position'])
        
        room.place_tile(player, tile, origin, target, position)

        data = GameEncoder.encode(room, request.sid)
        emit('game_update', data)


    return app