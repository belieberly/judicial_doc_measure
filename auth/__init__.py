from config import oauth_config
from flask import g
from flask_httpauth import HTTPTokenAuth
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadHeader

expires_time = oauth_config.expires_time
secret_key = oauth_config.secret_key
token_type = oauth_config.token_type

token_serializer = Serializer(secret_key=secret_key, expires_in=expires_time)

auth = HTTPTokenAuth(token_type)


@auth.verify_token
def verify_token(token):
    g.user = None
    try:
        data = token_serializer.loads(token)
    except (BadHeader, SignatureExpired, Exception):  # noqa: E722
        return False
    if 'username' in data and 'open_id' in data:
        g.user = data
        return True
    return False

