class TestColoquios:
    path = "/coloquios/"

    def test_render(self, admin_client):
        response = admin_client.get(self.path, follow_redirects=True)
        assert response.status_code == 200
        assert b'Uma lista de todos os' in response.data

    def test_create(self, admin_client):
        response = admin_client.post(self.path, follow_redirects=True, data={
            'nome': 'Coloquio 1',
            'date': '2019-12-12',
        })
        assert response.status_code == 200
        assert b'Coloquio 1' in response.data
        assert b'12/12/2019' in response.data
