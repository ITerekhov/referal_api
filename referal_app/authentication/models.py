from django.db import models
import jwt
from datetime import datetime, timedelta
from django.conf import settings 
from django.contrib.auth.models import (
	AbstractBaseUser, BaseUserManager, PermissionsMixin
)
class UserManager(BaseUserManager):
    """
    Определяем порядок сохранения новых юзеров для custom модели user
    """
    def create_user(self, phone, referal=None, referal_link=None, **kwargs):
        if phone is None:
            raise TypeError('Users must have a phone number.')
        user = self.model(phone = phone, referal_link = referal_link, referal = referal)
        user.save()
        return user


    def create_superuser(self, phone, **kwargs):
        """ Создает и возвращет пользователя с привилегиями суперадмина. """
        if phone is None:
            raise TypeError('Users must have a phone number.')
        user = self.create_user(phone)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user

class User(AbstractBaseUser, PermissionsMixin):
    """Переопределяем модель юзера"""

    phone = models.CharField(db_index=True, max_length=30, unique=True)
    referal_link = models.CharField(blank=True, max_length=6)
    referal = models.CharField(blank=True, max_length=6)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'phone'
    objects = UserManager()

    def __str__(self):
        return self.phone

    @property
    def token(self):
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        dt = datetime.now() + timedelta(days=1)
        token = jwt.encode({
            'id': self.phone,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token

class ConfirmCode(models.Model):
    """Модель для хранения кодов проверки телефонных номеров """
    phone = models.CharField(max_length=30)
    code = models.IntegerField()