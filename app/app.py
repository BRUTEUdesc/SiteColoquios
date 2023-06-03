import os

from dotenv import load_dotenv
from flask import Blueprint, Flask, redirect, url_for, current_app

load_dotenv()

index_bp = Blueprint('index', __name__, template_folder='templates')
blueprint = Blueprint('coloquios', __name__, url_prefix='/coloquios')


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        HOME_ROUTE='coloquios.coloquios.index',
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
    app.register_blueprint(index_bp)
    blueprint.register_blueprint(auth.blueprint)
    blueprint.register_blueprint(coloquios.blueprint)
    blueprint.register_blueprint(pessoas.blueprint)
    app.register_blueprint(blueprint)

    return app


@index_bp.route('/', methods=['GET', 'POST'])
def index():
    return redirect(url_for(current_app.config.get('HOME_ROUTE')))


@blueprint.route('/', methods=['GET', 'POST'])
def index():
    return redirect(url_for(current_app.config.get('HOME_ROUTE')))
