import psycopg2
from urllib.parse import urlparse


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
