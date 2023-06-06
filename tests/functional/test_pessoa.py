import datetime
import re

import pytest

from app.extensions.database import get_db


class TestPessoa:
    @pytest.fixture
    def create_pessoa(self, app):
        pessoa_cpf = None
        with app.app_context():
            db = get_db()
            with db.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO coloquios.pessoa(nome, datanasc, curso, cpf) VALUES "
                    "('Weliton', '2000-12-21', 'Ciência da Computação', '02064398902')"
                    "RETURNING cpf;"
                )
                pessoa_cpf = cursor.fetchone()[0]
                db.commit()
        return pessoa_cpf

    def test_render(self, admin_client, create_pessoa):
        response = admin_client.get(f"coloquios/pessoas/{create_pessoa}", follow_redirects=True)
        assert response.status_code == 200
        assert b'Weliton' in response.data

        cpf_pattern = r'value="(\d{11})"'
        match = re.search(cpf_pattern, response.data.decode('utf-8'))
        assert match is not None, 'CPF field not found in the response'

        date_pattern = r'value="(\d{4}-\d{2}-\d{2})"'
        match = re.search(date_pattern, response.data.decode('utf-8'))
        assert match is not None, 'Date field not found in the response'

        date_str = match.group(1)
        expected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()