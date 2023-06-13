import datetime
import re

import pytest

from app.extensions.database import get_db


class TestColoquio:
    @pytest.fixture
    def create_coloquio(self, app):
        coloquio_id = None
        with app.app_context():
            db = get_db()
            with db.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO coloquios.apresentacao (titulo, datacol) VALUES ('Coloquio 1', '2019-12-12') "
                    "RETURNING id;"
                )
                coloquio_id = cursor.fetchone()[0]
                db.commit()
        return coloquio_id

    def test_render(self, admin_client, create_coloquio):
        response = admin_client.get(f"coloquios/coloquios/{create_coloquio}", follow_redirects=True)
        assert response.status_code == 200
        assert b'Coloquio 1' in response.data
        date_pattern = r'value="(\d{4}-\d{2}-\d{2})"'
        match = re.search(date_pattern, response.data.decode('utf-8'))
        assert match is not None, 'Date field not found in the response'

        date_str = match.group(1)
        expected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()

    def test_edit(self, admin_client, create_coloquio, app):
        with app.app_context():
            db = get_db()
            with db.cursor() as cursor:
                cursor.execute(
                    "UPDATE coloquios.apresentacao SET titulo = 'Korhal', datacol = '2000-12-12' "
                    f"WHERE id = '{create_coloquio}';"
                )
                db.commit()

        response = admin_client.get(f"coloquios/coloquios/{create_coloquio}", follow_redirects=True)

        assert response.status_code == 200
        assert b'Korhal' in response.data
        assert b'2000-12-12' in response.data
