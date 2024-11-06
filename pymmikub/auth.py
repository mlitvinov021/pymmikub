from flask import Blueprint, render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
#from .models import User
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/signup')
def signup():
    return render_template('signup.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database goes here
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    
    db = get_db()
    error = None

    if not username:
        error = 'Username is required.'
    elif not password:
        error = 'Password is required.'
    elif not email:
        error = 'Email is required.'

    if error is None:
        try:
            db.execute(
                'INSERT INTO user (email, username, password) VALUES (?, ?, ?)',
                (email, username, generate_password_hash(password)),
            )
            db.commit()
        except db.IntegrityError:
            error = f'User {username} is already registered.'

    flash(error)

    return redirect(url_for('auth.login'))


@auth.route('/logout')
def logout():
    return 'Logout'