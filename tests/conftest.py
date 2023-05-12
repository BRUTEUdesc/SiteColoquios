import os
import pytest
from dotenv import load_dotenv
from flask_login import FlaskLoginClient
from app.app import create_app


def pytest_configure(config):
    load_dotenv()


@pytest.fixture(scope='session', autouse=True)
def db_setup(app):
    from app.utils.database import create_db, init_db
    with app.app_context():
        create_db()
        init_db()


@pytest.fixture(scope='session')
def app():
    app = create_app()
    app.test_client_class = FlaskLoginClient
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        DB_URL=os.environ.get('DB_TEST_URL'),
        DB_NAME=os.environ.get('DB_TEST_NAME'),
    )
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def admin_client(app):
    from app.app import admin
    return app.test_client(user=admin)


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
