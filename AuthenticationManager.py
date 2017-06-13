import json
import jwt


class AuthenticationManager:

    def __init__(self, user_manager):
        self.user_manager = user_manager

    def verify_jwt(self, headers):
        [success, token_result] = AuthenticationManager.extract_bearer_token(headers)
        if success is True:
            try:
                jwt_result = jwt.decode(token_result, 'secret', algorithm=['HS256'])
                user_is_admin = self.user_is_admin(jwt_result)
                username = ""
                if user_is_admin is False:
                    user = self.user_manager.find_user_by_token(token_result)
                    if user is None:
                        return [False, '{"status": "fail", "message": "No user with that token"}', None]
                    else:
                        username = user['username']

                res = json.loads('{"status": "OK"}')
                res['jwt'] = json.dumps(jwt_result)
                return [True, res, username]
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
