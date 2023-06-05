import os
import uuid
from hashlib import sha256


class User:
    id = None
    username = None
    password = None
    authenticated = False

    def __init__(self, username, password):
        self.id = "1123123213123"
        #self.id = uuid.uuid4()
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


# TODO: use Werkzeug to hash the password
admin = User(
    os.getenv('ADMIN_USER'),
    sha256(os.getenv('ADMIN_PASSWORD').encode('utf-8')).hexdigest(),
)
