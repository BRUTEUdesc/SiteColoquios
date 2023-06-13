import pytest

from app.extensions.database import get_db


class TestApresentadores:
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
                cursor.execute(
                    "INSERT INTO coloquios.pessoa(nome, datanasc, curso, cpf) VALUES "
                    "('Weliton', '2000-12-21', 'Ciência da Computação', '02064398902')"
                    "RETURNING cpf;"
                )
                pessoa_cpf = cursor.fetchone()[0]
                cursor.execute(
                    "INSERT INTO coloquios.palestrante (idpal, idcol) VALUES ('1', '1') "
                    "RETURNING idpal;"
                )
                palestrante_id = cursor.fetchone()[0]
                db.commit()
        return coloquio_id

    def test_render(self, admin_client, create_coloquio):
        response = admin_client.get(f"coloquios/coloquios/apresentadores/{create_coloquio}", follow_redirects=True)
        assert response.status_code == 200
        assert b'Coloquio 1' in response.data
        assert b'Weliton' in response.data

