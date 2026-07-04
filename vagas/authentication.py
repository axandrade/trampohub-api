import datetime

from django.conf import settings
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)

        minutos = getattr(settings, 'TOKEN_EXPIRATION_MINUTES', 15)
        expirou = token.created < timezone.now() - datetime.timedelta(minutes=minutos)
        if expirou:
            token.delete()
            raise AuthenticationFailed('Token expirado. Faça login novamente.')

        return user, token
