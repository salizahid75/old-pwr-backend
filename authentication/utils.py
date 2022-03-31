from django.core.mail import send_mail
import random
from django.utils import timezone
from .models import VerificationToken


class EmailVerification:
    TIMEOUT_ERROR = "TIMEOUT"
    ERROR = "ERROR"

    @classmethod
    def get_verification_code(cls, user_obj):

        try:
            token = VerificationToken.objects.get(
                user=user_obj.id, token_type=VERIFICATION_TYPES.EMAIL)
        except:
            token = False

        if token:
            token.delete()

        new_token = VerificationToken(
            user=user_obj, code=cls.generate_token(), token_type=VERIFICATION_TYPES.EMAIL)
        new_token.save()

        return new_token.code

    @classmethod
    def check_verification_token(cls, user, code):
        try:
            token = VerificationToken.objects.get(
                user=user.id, code=str(code), token_type=VERIFICATION_TYPES.EMAIL)
            if timezone.now() >= token.expires:
                token = False
        except Exception as e:
            token = None

        return token

    @classmethod
    def generate_token(cls, length=5):
        """
        creates a verification code(token)
        """

        token = random.randint(10000, 99999)
        return token

        return token

    @classmethod
    def send_email(cls, to_address, verification_code):

        subject = "Email Verification"
        _from = "CRM"
        message = f"Verification Code: {verification_code}"

        is_sent = False

        try:
            mail_status = send_mail(subject, message, _from, [to_address])
            if mail_status:
                is_sent = True
        except Exception as e:
            print(e)
            pass

        return is_sent


class VERIFICATION_TYPES:
    EMAIL = "em"
    OTP = "op"
