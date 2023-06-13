from app.extensions.database import get_db


class TestXLS:
    def test_xls(self, admin_client, app):
        coloquio_id = None
        with app.app_context():
            db = get_db()
            with db.cursor() as cur:
                cur.execute(
                    "INSERT INTO coloquios.apresentacao (titulo, datacol) VALUES ('Coloquio 1', '2019-12-12') "
                    "RETURNING id;"
                )
                coloquio_id = cur.fetchone()[0]

                cur.execute("INSERT INTO coloquios.pessoa(nome, datanasc, curso, cpf) VALUES ('Elitu', '2001-07-07', "
                            "'TADS', '65183755078') RETURNING id;")
                idpar = cur.fetchone()
                cur.execute('insert into coloquios.participante(idcol, idpar) values (%s, %s)', (coloquio_id, idpar))

                db.commit()
            response = admin_client.get(f"coloquios/coloquios/download/{coloquio_id}", follow_redirects=True)

            assert response.status_code == 200
            assert response.headers["Content-Type"] == "application/vnd.ms-excel"

        return coloquio_id
