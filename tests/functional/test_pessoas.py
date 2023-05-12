class TestPessoas:
    path = '/pessoas'

    def test_render(self, admin_client):
        response = admin_client.get(self.path, follow_redirects=True)
        assert response.status_code == 200
        assert b'Pessoas' in response.data
        assert b'Uma lista de todos os pessoas' in response.data

    def test_create(self, admin_client):
        response = admin_client.post(self.path, follow_redirects=True, data={
            'nome': 'Korhal',
            'cpf': '371.297.789-11',
            'curso': 'Ciência da Computação',
            'dateNasc': '2000-12-12',
        })
        assert response.status_code == 200
        assert b'Korhal' in response.data
        assert b'12/12/2000' in response.data
        assert b'371.297.789-11' in response.data
