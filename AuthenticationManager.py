import json
import jwt

import config


class AuthenticationManager:

    check_token = True

    def __init__(self, user_manager):
        self.user_manager = user_manager

    def verify_jwt(self, headers):
        if self.check_token is False:
            return [True, "", ""]

        [success, token_result] = AuthenticationManager.extract_bearer_token(headers)

        if success is True:
            try:
                jwt_result = jwt.decode(token_result, config.token_secret, algorithm=['HS256'])
                user = self.user_manager.find_user_by_token(token_result)
                if user is None:
                    return [False, '{"status": "fail", "message": "No user with that token"}', None]

                res = json.loads('{"status": "OK"}')
                res['jwt'] = json.dumps(jwt_result)
                return [True, res, user]
            except jwt.InvalidTokenError as ex:
                print(ex)
                return [False, '{"status": "Fail", "message": "Invalid token"}', None]
        else:
            return [False, token_result, None]

    @staticmethod
    def extract_bearer_token(headers):
        if 'AUTHORIZATION' in headers:
            return [True, headers['AUTHORIZATION'].split("Bearer")[1].replace(" ", "")]
        else:
            return [False, '{"status": "Fail", "message": "No authentication token supplied"}']

    def user_is_admin(self, jwt_result):
        if 'admin' in jwt_result and jwt_result['admin'] is True:
            return True
        else:
            return False
