import os

import click
import psycopg2
from flask import current_app, g


class Database:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    @staticmethod
    def init_app(app):
        app.teardown_appcontext(close_db)
        app.cli.add_command(db_init_command)
        app.cli.add_command(db_create_command)


def get_connection():
    return psycopg2.connect(
        host=current_app.config['DB_HOST'],
        port=current_app.config['DB_PORT'],
        user=current_app.config['DB_USER'],
        password=current_app.config['DB_PASSWORD'],
        dbname=current_app.config['DB_NAME']
    )


def get_schemaless_connection():
    return psycopg2.connect(
        host=current_app.config['DB_HOST'],
        port=current_app.config['DB_PORT'],
        user=current_app.config['DB_USER'],
        password=current_app.config['DB_PASSWORD']
    )


def get_db():
    if 'db' not in g:
        g.db = get_connection()

    return g.db


def init_db():
    con = get_db()
    with current_app.open_resource(os.getenv("DB_SCHEMA_PATH")) as f:
        with con.cursor() as cur:
            cur.execute(f.read())
            con.commit()


def create_db():
    con = get_schemaless_connection()
    with con.cursor() as cur:
        db_name = current_app.config['DB_NAME']
        con.autocommit = True
        cur.execute('DROP DATABASE IF EXISTS ' + db_name + ';')
        cur.execute('CREATE DATABASE ' + db_name + ';')
    con.close()


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


@click.command('db-init')
def db_init_command():
    init_db()
    click.echo('Initialized the database.')


@click.command('db-create')
def db_create_command():
    create_db()
    click.echo('Creating the database.')
