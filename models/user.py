import uuid


class User:
    id = None
    username = None
    password = None
    authenticated = False

    def __init__(self, username, password):
        self.id = uuid.uuid4()
        self.username = username
        self.password = password

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return True

    def is_anonymous(self):
        return False
