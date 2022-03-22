import jwt
from django.conf import settings
from rest_framework import authentication, exceptions
from .models import User
from referal_app.settings import SECRET_KEY
class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'Token'

    def authenticate(self, request):
        """
        Метод отвечает за аутентификацию. Возвращает два состояния: None если 
        аутентификация не пройдена и пару (user, token) в случае успеха
        """
        request.user = None
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()
        if not auth_header:
            return None

        if len(auth_header) == 1:
            return None
        elif len(auth_header) > 2:
            return None
        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix:
            return None
        return self._authenticate_credentials(request, token)

    def _authenticate_credentials(self, request, token):
        """
        Попытка аутентификации с предоставленными данными. Если успешно -
        вернуть пользователя и токен, иначе - сгенерировать исключение.
        """
        try:
            payload = jwt.decode(token, SECRET_KEY ,algorithms=['HS256'])
        except Exception:
            msg = 'Ошибка аутентификации. Невозможно декодировать токеню'
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get(phone=payload['id'])
        except User.DoesNotExist:
            msg = 'Пользователь соответствующий данному токену не найден.'
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = 'Данный пользователь деактивирован.'
            raise exceptions.AuthenticationFailed(msg)

        return (user, token)