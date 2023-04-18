import os

import psycopg2
from urllib.parse import urlparse


conStr = os.getenv("DB_URL")
p = urlparse(conStr)

pg_connection_dict = {
    'dbname': p.hostname,
    'user': p.username,
    'password': p.password,
    'port': p.port,
    'host': p.scheme
}
Cursos = ['Ciência da Computação', 'Eng.Civil', 'Lic.Quí', 'Lic.Fis', 'Lic.Mat', 'Eng.Elétrica', 'Eng.Mecânica',
          'Eng.Produção', 'TADS']

con = psycopg2.connect(**pg_connection_dict)
