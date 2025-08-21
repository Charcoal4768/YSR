from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_socketio import SocketIO, join_room, leave_room
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['WTF_CSRF_SECRET_KEY'] = os.getenv('WTF_CSRF_SECRET_KEY')
app.config['SESSION_COOKIE_SECURE'] = not app.debug and not app.testing
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_DOMAIN'] = None

db = SQLAlchemy(app)
csrf = CSRFProtect(app)
socket = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
migrate = Migrate(app, db)

from .routes.views import views
from .routes.auth import auth
from .routes.api import api

app.register_blueprint(views)
app.register_blueprint(auth)
app.register_blueprint(api)

login_manager = LoginManager(app)
@login_manager.user_loader
def load_user(user_id):
    from .models import User
    try:
        return User.query.get(user_id)
    except Exception as e:
        return None
    
@app.errorhandler(Exception)
def handle_exception(error):
    print(error, Exception)
    return render_template('errors.html', error=error), 500

@socket.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    socket.emit('message', {'msg': f'User has joined the room: {room}'}, room=room)

with app.app_context():
    db.create_all()