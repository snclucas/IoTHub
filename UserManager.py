import json
import jwt

import config


class UserManager:
    """User manager."""

    def __init__(self, database):
        self.database = database
        self.salt = config.salt

    def save_user(self, user):
        if self.__check_user__(user):
            result = self.find_user_by_username(user['username'])
            if result is None:
                user['token'] = self.create_token_for_user(user, self.salt)
                return self.database.save('users', user)
            else:
                return json.loads({"status": "fail", "message": "Username already exists"})
        else:
            return json.loads({"status": "fail", "message": "Bad user data"})

    def find_user_by_token(self, token):
        result = self.database.get_one_where('users', 'token', token)
        print(result)
        if result is not None:
            return json.loads(self.database.get_one_where('users', 'token', token))
        else:
            return None

    def find_user_by_id(self, _id):
        return json.loads(self.database.get_one_where('users', 'id', _id))

    def find_user_by_username(self, username):
        return self.database.get_one_where('users', 'username', username)

    def __check_user__(self, user):
        if 'username' in user and \
                'email' in user:
            return True
        else:
            return False

    def create_token_for_user(self, username, salt):
        return jwt.encode({'username': username['username'], 'is_admin': 'false'}, salt, algorithm='HS256')
