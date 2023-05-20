import os

from dotenv import load_dotenv
from flask import Blueprint, Flask, redirect, url_for
import flask_login

load_dotenv()

blueprint = Blueprint('index', __name__, template_folder='templates')


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY'),
        DB_NAME=os.environ.get('DB_NAME'),
        DB_HOST=os.environ.get('DB_HOST'),
        DB_PORT=os.environ.get('DB_PORT'),
        DB_USER=os.environ.get('DB_USER'),
        DB_PASSWORD=os.environ.get('DB_PASSWORD'),
    )

    from app.extensions.login_manager import login_manager
    from app.extensions.bootstrap import bootstrap
    from app.extensions.database import database
    login_manager.init_app(app)
    bootstrap.init_app(app)
    database.init_app(app)

    from app.routes import auth
    from app.routes import coloquios
    from app.routes import pessoas
    app.register_blueprint(blueprint)
    app.register_blueprint(auth.blueprint)
    app.register_blueprint(coloquios.blueprint)
    app.register_blueprint(pessoas.blueprint)

    return app


@blueprint.route('/', methods=['GET', 'POST'])
@flask_login.login_required
def index():
    return redirect(url_for('coloquios.index'))
