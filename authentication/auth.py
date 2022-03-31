import jwt
from datetime import timedelta, datetime
from django.conf import settings


def encode_jwt(user_id):

    token = jwt.encode({'uid': user_id, 'exp': datetime.now(
    ) + timedelta(minutes=settings.JWT_MAX_AGE)}, settings.SECRET_KEY, algorithm='HS256')
    return token


def decode_jwt(token):
    try:
        decode = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
        user_id = decode['uid']
        return user_id
    except:
        return None
