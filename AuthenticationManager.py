import json
import jwt


class AuthenticationManager:

    def __init__(self):
        pass

    @staticmethod
    def verify_jwt(headers):
        [success, token_result] = AuthenticationManager.extract_bearer_token(headers)
        if success is True:
            try:
                jwt_result = jwt.decode(token_result, 'secret', algorithm=['HS256'])
                res = json.loads('{"status": "OK"}')
                res['jwt'] = json.dumps(jwt_result)
                return [True, res]
            except jwt.InvalidTokenError:
                return [False, '{"status": "Fail", "message": "Invalid token"}']
        else:
            return [False, token_result]

    @staticmethod
    def extract_bearer_token(headers):
        if 'AUTHENTICATION' in headers:
            return [True, headers['AUTHENTICATION'].split("Bearer")[1].replace(" ", "")]
        else:
            return [False, '{"status": "Fail", "message": "No authentication token supplied"}']
