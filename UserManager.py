import json


class UserManager:

    def __init__(self, database):
        self.database = database

    def save_user(self, user):
        result = self.find_user_by_username(user['username'])
        return self.database.save('users', user)

    def find_user_by_token(self, token):
        return json.loads(self.database.get_one_where('users', 'token', token))

    def find_user_by_id(self, _id):
        return json.loads(self.database.get_one_where('users', 'id', _id))

    def find_user_by_username(self, username):
        return self.database.get_one_where('users', 'username', username)