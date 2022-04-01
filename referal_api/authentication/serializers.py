from rest_framework import serializers
from .models import ConfirmCode, User
import random
import string
letters_and_digits = string.ascii_letters + string.digits

class LoginSerializer(serializers.Serializer):
    """Сериалайзер для обработки авторизации и регистрации юзеров"""
    phone = serializers.CharField(max_length=255)
    referal = serializers.CharField(required=False, max_length=255)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        phone = data.get('phone', None)
        referal = data.get('referal', None)
        code = data.get('code', None)
        if phone is None:
            raise serializers.ValidationError(
                'An phone number is required to log in.'
            )
        if not ConfirmCode.objects.filter(phone=phone).exists():
            raise serializers.ValidationError(
                'Invalid code'
            )
        else:
            code = ConfirmCode.objects.get(phone=phone)
            code.delete()
        try:
            user = User.objects.get(phone=phone)
        except:
            link = ''.join(random.sample(letters_and_digits, 6))
            user = User(phone=phone, referal_link=link)
            if referal is not None:
                if not User.objects.filter(referal_link=referal).exists():
                    raise serializers.ValidationError(
                        "nonexistent referal_link"
                    )
                user.referal = referal
            user.save()

        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        token = user.token
        return {
             'phone': user.phone,
            'token': token,
            'referal': user.referal_link
        }


class UserSerializer(serializers.Serializer):
    """Сериалайзер для получения инфромации о профиле юзера"""
    phone = serializers.CharField(max_length=200)
    user_referals = serializers.DictField(allow_empty=True)
    referal = serializers.CharField(max_length=6)

class UserUpdateSerializer(serializers.Serializer):
    """Сериалайзер для изменения юзером его информации"""
    phone = serializers.CharField(max_length=200)
    referal = serializers.CharField(max_length=6)
    def update(self, instance, validated_data):
        """ Выполняет обновление User. """
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

