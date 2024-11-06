import os

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
from . import db


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

    @app.route('/')
    def index():
        return render_template('index.html')

    @socketio.on('join_game')
    def handle_join_game(data):
        room = data['room']
        join_room(room)

        if room not in games:
            games[room] = {
                'players': [],
                'tiles': [],  # Main pool of tiles
                'player_tiles': {}  # Tiles held by each player
            }
        
        games[room]['players'].append(request.sid)
        games[room]['player_tiles'][request.sid] = draw_initial_tiles()

        emit('game_update', games[room], room=room)

    def draw_initial_tiles():
        # Returns a list of 14 tiles (just for demonstration purposes)
        return [random.randint(1, 104) for _ in range(14)]

    @socketio.on('place_tile')
    def handle_place_tile(data):
        room = data['room']
        tile = data['tile']
        # Remove the tile from the player's hand and update the game state
        if tile in games[room]['player_tiles'][request.sid]:
            games[room]['player_tiles'][request.sid].remove(tile)
            games[room]['tiles'].append(tile)  # Place it on the board
    
        emit('game_update', games[room], room=room)

    return app