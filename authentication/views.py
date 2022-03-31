from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth import authenticate
from django.core.validators import validate_email
import datetime

from .models import MainUser as User, VerificationToken

from power.utils import ERRS, ok_0, ok_1

from .serializers import RegisterSerializer, LoginSerializer, VerificationTokenSerializer, ResendVerificationTokenSerializer
from .auth import encode_jwt
from .decorators import is_authorized
from .utils import EmailVerification, VERIFICATION_TYPES


@api_view(["POST", ])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():

        try:
            is_already_exists = User.objects.get(
                email=serializer.validated_data['email'])
        except:
            is_already_exists = None

        if is_already_exists:
            return ok_0(code=ERRS.DUP_ERROR, status=status.HTTP_400_BAD_REQUEST)

        user = User(
            email=serializer.validated_data['email'], name=serializer.validated_data['name'])
        user.set_password(serializer.validated_data['password'])
        user.save()

        verification_code = EmailVerification.get_verification_code(user)

        is_verification_email_sent = EmailVerification.send_email(
            user.email, verification_code)

        if not is_verification_email_sent:
            return ok_0(code=ERRS.SERVER_ERROR, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return ok_1()

    return ok_0(code=ERRS.INVALID_BODY, status=status.HTTP_400_BAD_REQUEST, body=serializer.errors)


@api_view(["POST", ])
def login_view(request):
    try:
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():

            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')

            user = authenticate(email=email, password=password)

            if not user:
                return ok_0(code=ERRS.INVALID_LOGIN, status=status.HTTP_400_BAD_REQUEST)

            elif not user.is_active:
                return ok_0(code=ERRS.NOT_VERIFIED, status=status.HTTP_401_UNAUTHORIZED)

            expires = timezone.now() + timedelta(seconds=settings.JWT_MAX_AGE)

            user_id = user.id
            token = encode_jwt(user_id)

            should_send_cookies = False if request.headers.get(
                'no-cookies') in [1, '1'] else True

            if should_send_cookies:
                response = ok_1()
                response.set_cookie(
                    key=settings.JWT_ACCESS_TOKEN,
                    value=token,
                    httponly=True,
                    expires=expires.strftime("%a, %d-%b-%Y %H:%M:%S UTC"),
                    max_age=settings.JWT_MAX_AGE,
                    samesite="none",
                    secure=True
                )

                return response
            else:
                response = ok_1(token=token)
                return response

        return ok_0(code=ERRS.INVALID_BODY, status=status.HTTP_400_BAD_REQUEST, body=serializer.errors)
    except:
         return ok_0(code=ERRS.SERVER_ERROR, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@is_authorized
@api_view(["GET", "PUT"])
def user_view(request, user_id):
    if request.method == "PUT":
        serializer = RegisterSerializer(
            user_id, data=request.data, partial=True)

        if not serializer.is_valid():
            return ok_0(code=ERRS.INVALID_BODY, status=status.HTTP_400_BAD_REQUEST, body=serializer.errors)

        serializer.save()
        return ok_1()

    elif request.method == "GET":
        serializer = RegisterSerializer(user_id)
        return ok_1(data=serializer.data)


@api_view(["POST", ])
def verify_verification_code(request):
    serializer = VerificationTokenSerializer(data=request.data)

    if not serializer.is_valid():
        return ok_0(code=ERRS.INVALID_BODY, status=status.HTTP_400_BAD_REQUEST, body=serializer.errors)

    code = serializer.validated_data.get('code')
    user_email = serializer.validated_data.get('user_email')

    try:
        user_obj = User.objects.get(email=user_email)
    except:
        user_obj = False

    if user_obj == False:
        return ok_0(code=ERRS.NOT_FOUND, status=status.HTTP_400_BAD_REQUEST)

    if user_obj.is_active:
        return ok_0(code=ERRS.ALREADY_VERIFIED, status=status.HTTP_400_BAD_REQUEST)

    token_obj = EmailVerification.check_verification_token(user_obj, code)

    print(token_obj)

    if not token_obj:
        return ok_0(code=ERRS.INVALID_TOKEN, status=status.HTTP_400_BAD_REQUEST)

    user_obj.is_active = True
    user_obj.save()

    token_obj.delete()

    # return the jwt token. same as what login does.

    expires = timezone.now() + timedelta(seconds=settings.JWT_MAX_AGE)
    jwt_token = encode_jwt(user_obj.id)
    should_send_cookies = False if request.headers.get(
        'no-cookies') in [1, '1'] else True

    if should_send_cookies:
        response = ok_1()
        response.set_cookie(
            key=settings.JWT_ACCESS_TOKEN,
            value=jwt_token,
            httponly=True,
            expires=expires.strftime("%a, %d-%b-%Y %H:%M:%S UTC"),
            max_age=settings.JWT_MAX_AGE,
            samesite="none",
            secure=True
        )

        return response
    else:
        response = ok_1(token=jwt_token)
        return response


@api_view(["POST", ])
def resend_verification_code(request):

    serializer = ResendVerificationTokenSerializer(data=request.data)

    if not serializer.is_valid():
        return ok_0(code=ERRS.INVALID_BODY, status=status.HTTP_400_BAD_REQUEST, body=serializer.errors)

    try:
        user = User.objects.get(email=serializer.validated_data['email'])
    except:
        user = None

    if not user:
        return ok_0(code=ERRS.NOT_FOUND, status=status.HTTP_400_BAD_REQUEST)

    if user.is_active:
        return ok_0(code=ERRS.ALREADY_VERIFIED, status=status.HTTP_400_BAD_REQUEST)

    verification_code = EmailVerification.get_verification_code(user)

    is_verification_email_sent = EmailVerification.send_email(
        user.email, verification_code)

    if not is_verification_email_sent:
        return ok_0(code=ERRS.SERVER_ERROR, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return ok_1()

@is_authorized
@api_view(["GET"])
def logout_view(request, user_id):
    response = ok_1()
    response.set_cookie(
            key=settings.JWT_ACCESS_TOKEN,
            value=None,
            httponly=True,
            expires=datetime.datetime(1970, 1, 1).strftime("%a, %d-%b-%Y %H:%M:%S UTC"),
            max_age=settings.JWT_MAX_AGE,
            samesite="none",
            secure=True
        )

    return response