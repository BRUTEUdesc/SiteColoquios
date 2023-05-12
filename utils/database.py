import os

import click
import psycopg2
from urllib.parse import urlparse
from flask import current_app, g


def get_connection(db_url):
    p = urlparse(db_url)

    pg_connection_dict = {
        'dbname': p.hostname,
        'user': p.username,
        'password': p.password,
        'port': p.port,
        'host': p.scheme
    }

    return psycopg2.connect(**pg_connection_dict)


def get_db():
    if 'db' not in g:
        g.db = get_connection(current_app.config['DB_URL'])

    return g.db


def get_db_schemaless():
    db_url = "localhost://postgres:postgres@postgres:5432"
    return get_connection(db_url)


def init_db():
    con = get_db()
    with current_app.open_resource(os.getenv("DB_SCHEMA_PATH")) as f:
        with con.cursor() as cur:
            cur.execute(f.read())
            con.commit()


def create_db():
    con = get_db_schemaless()
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


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(db_init_command)
    app.cli.add_command(db_create_command)
