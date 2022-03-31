from rest_framework import serializers, status
from .models import MainUser as User
from power.utils import ERRS, get_ok0_obj
from power.utils import get_error_messages


class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=150, error_messages=get_error_messages())
    email = serializers.EmailField(error_messages=get_error_messages())
    password = serializers.CharField(
        max_length=100, min_length=10, write_only=True, error_messages=get_error_messages())
    created = serializers.DateTimeField(
        read_only=True, error_messages=get_error_messages())

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)

        if 'password' in validated_data:
            instance.set_password(validated_data['password'])

        instance.save()

        return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(error_messages=get_error_messages())
    password = serializers.CharField(
        max_length=100, write_only=True, error_messages=get_error_messages())


class VerificationTokenSerializer(serializers.Serializer):
    user_email = serializers.EmailField(error_messages=get_error_messages())
    code = serializers.IntegerField(
        error_messages=get_error_messages(), max_value=99999, min_value=10000)


class ResendVerificationTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(error_messages=get_error_messages())
