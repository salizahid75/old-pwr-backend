from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.conf import settings
from power.utils import ERRS

from .auth import decode_jwt
from .models import MainUser as User


def is_authorized(view_function):
    def wrapper_function(request, *args, **kwargs):

        user_id = False

        if (settings.JWT_ACCESS_TOKEN in request.COOKIES):
            user_id = decode_jwt(request.COOKIES[settings.JWT_ACCESS_TOKEN])
            try:
                user_id = User.objects.get(id=user_id)
            except:
                user_id = None

        if user_id:
            return view_function(request, *args, **kwargs, user_id=user_id)
        else:
            return JsonResponse({'ok': 0, 'code': ERRS.AUTH_FAILED}, status=401)
    return wrapper_function
