class User:
    user = None
    password = None
    authenticated = False

    def get_id(self):
        return self.user

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

