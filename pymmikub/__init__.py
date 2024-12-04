import os

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
from pymmikub.game.game import Game
from . import db

# blueprint imports
from .auth import auth as auth_blueprint
from .main import main as main_blueprint


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    socketio = SocketIO(app)

    games = {}

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
        room = data['room']
        join_room(room)

        if room not in games:
            game: Game = Game()

            games[room] = {
                'players': [],
                'tiles': [],  # Main pool of tiles
                'player_tiles': {}  # Tiles held by each player
            }
        
        games[room]['players'].append(request.sid)
        games[room]['player_tiles'][request.sid] = game.draw_tile(14)

        emit('game_update', games[room], room=room)


    @socketio.on('place_tile')
    def handle_place_tile(data):
        room = data['room']
        tile = tuple(data['tile'])
        # Remove the tile from the player's hand and update the game state
        if tile in games[room]['player_tiles'][request.sid]:
            print("found tile in player hand")
            games[room]['player_tiles'][request.sid].remove(tile)
            games[room]['tiles'].append(tile)  # Place it on the board
    
        emit('game_update', games[room], room=room)

    return app