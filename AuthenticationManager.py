import json


class AuthenticationManager:

    check_token = True

    def __init__(self, user_manager):
        self.user_manager = user_manager

    def verify_token(self, headers):
        if self.check_token is False:
            return [True, "", ""]

        [success, token_result] = AuthenticationManager.extract_bearer_token(headers)

        if success is True:
            user = self.user_manager.find_user_by_token(token_result)
            if user is None:
                return [False, '{"status": "fail", "message": "No user with that token"}', None]

            res = json.loads('{"status": "OK"}')
            return [True, res, user]
        else:
            return [False, token_result, None]

    @staticmethod
    def extract_bearer_token(headers):
        if 'AUTHORIZATION' in headers:
            return [True, headers['AUTHORIZATION'].split("Bearer")[1].replace(" ", "")]
        else:
            return [False, '{"status": "fail", "message": "No authentication token supplied"}']

