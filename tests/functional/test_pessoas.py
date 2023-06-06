class TestPessoas:
    path = '/coloquios/pessoas'

    def test_render(self, admin_client):
        response = admin_client.get(self.path, follow_redirects=True)
        assert response.status_code == 200
        assert b'Pessoas' in response.data
        assert b'Uma lista de todas as pessoas' in response.data

    def test_create(self, admin_client):
        response = admin_client.post(self.path, follow_redirects=True, data={
            'nome': 'Korhal',
            'cpf': '37129778911',
            'curso': 'Ciência da Computação',
            'dateNasc': '2000-12-12',
        })
        assert response.status_code == 200
        assert b'Korhal' in response.data
        assert b'12/12/2000' in response.data
        assert b'37129778911' in response.data
