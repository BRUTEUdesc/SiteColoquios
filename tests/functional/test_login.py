class TestLogin:
    path = '/auth/login'

    def test_render(self, client):
        response = client.get(self.path, follow_redirects=True)
        assert response.status_code == 200
        assert b'User' in response.data
        assert b'Senha' in response.data
        assert b'Logar' in response.data

    def test_auth(self, client):
        response = client.post(self.path, follow_redirects=True, data={
            'user': 'bruteudesc',
            'password': 'brutebrute'
        })
        assert response.status_code == 200
        assert len(response.history) == 1
        assert response.request.path == "/"

    def test_auth_fail(self, client):
        response = client.post(self.path, follow_redirects=True, data={
            'user': 'bruteudesc',
            'password': 'brutebrute2'
        })
        assert response.status_code == 200
        assert len(response.history) == 0
        assert response.request.path == self.path
