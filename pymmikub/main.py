from flask import Blueprint, render_template, make_response, request
from . import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Ensure a persistent player cookie exists so reconnects reuse player state
    resp = make_response(render_template('index.html'))
    player_id = request.cookies.get('player_id')
    if not player_id:
        import uuid
        player_id = str(uuid.uuid4())
        # Not HttpOnly so client JS can read it for UI/logic
        resp.set_cookie('player_id', player_id, samesite='Lax')
    return resp

@main.route('/profile')
def profile():
    return render_template('profile.html')
