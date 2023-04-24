import pytest


@pytest.fixture()
def app():
    from app import app
    from flask_login import FlaskLoginClient
    app.test_client_class = FlaskLoginClient
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def admin_client(app):
    from app import admin
    return app.test_client(user=admin)


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
