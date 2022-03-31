from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

def get_ok0_obj(code, **kwargs):
    obj = {'ok': 0, 'code': code}

    if kwargs:
        obj['errors'] = {**kwargs}

    return obj


def get_ok1_obj(**kwargs):
    obj = {'ok': 1}

    if kwargs:
        obj['res'] = {**kwargs}

    return obj


def ok_1(**kwargs):
    return Response(get_ok1_obj(**kwargs), status=status.HTTP_200_OK)


def ok_0(code, status, **kwargs):
    return Response(get_ok0_obj(code, **kwargs), status=status)

def get_error_messages():
    return {
        'required': 'REQUIRED',
        'max_length': 'MAX_LENGTH',
        'min_length': 'MIN_LENGTH',
        'invalid': 'INVALID',
        'blank': 'BLANK'
    }


class Result:
    _ERROR = 0
    _OK = 1

    def __init__(self, res_type, **kwargs):
        if res_type == self.__class__._ERROR:
            self.error_code = kwargs["error_code"]
            self.ok = 0
        else:
            self.data = kwargs["data"]
            self.ok = 1

    @classmethod
    def error(cls, error_code):
        return cls(cls._ERROR, error_code=error_code)

    @classmethod
    def ok(cls, data):
        return cls(cls._OK, data=data)


def getVerificationTokenDateTime():
    return timezone.now() + timedelta(minutes=settings.VERIFICATION_TOKEN_MAX_AGE)

# CLIENT_URLS = [
#     "*",
#     "profile",
#     { "auth": ["*", "login", "register"] }
# ]


def transformClientUrls(urls, parent_end_point=""):
    combined_urls = []

    parent_end_point = f"{parent_end_point}/" if parent_end_point else parent_end_point

    for url in urls:
        if url == "*":
            combined_urls.append(parent_end_point.strip('/'))

        elif type(url) == dict:
            new_combos = transformClientUrls(
                list(url.values())[0], parent_end_point+list(url.keys())[0])
            combined_urls += new_combos

        else:
            combined_urls.append(parent_end_point+url)

    return combined_urls



class ERRS:
    AUTH_FAILED = "auth_failed"
    NOT_FOUND = "not_found"
    INVALID_BODY = "invalid_body"
    BAD_REQUEST = "bad_request"
    SERVER_ERROR = "server_error"
    DUP_ERROR = "dup_error"
    NOT_VERIFIED = "not_verified"
    INVALID_LOGIN = "invalid_login"
    INVALID_TOKEN = "invalid_token"
    ALREADY_VERIFIED = "already_verified"