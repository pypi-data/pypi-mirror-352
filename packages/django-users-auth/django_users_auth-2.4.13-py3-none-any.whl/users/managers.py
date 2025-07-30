from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken as BaseRefreshToken
from rest_framework.exceptions import AuthenticationFailed
from django.utils.crypto import get_random_string
import logging
from django.core.cache import cache
from rest_framework.authentication import get_authorization_header
from users.settings import users_auth_settings
import requests
import json
import jwt
from rest_framework import exceptions

logger = logging.getLogger(__name__)


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email=None, username=None, password=None, **extra_fields):
        """Crear usuario normal"""
        if not email:
            raise ValueError("El usuario debe tener un email")

        if not username:
            # Si no se proporciona username, usar parte del email
            username = email.split('@')[0]

        email = self.normalize_email(email)

        # Si no se proporciona password, generar uno aleatorio
        if not password:
            password = get_random_string(12)

        user = self.model(
            email=email,
            username=username,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username=None, password=None, **extra_fields):
        """Crear superusuario"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser debe tener is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser debe tener is_superuser=True")

        if not username:
            username = email.split('@')[0]

        return self.create_user(
            email=email,
            username=username,
            password=password,
            **extra_fields
        )


class CustomJWTAuthentication(JWTAuthentication):

    def __init__(self):
        self.keycloak_cert_url = f"{users_auth_settings.OIDC_OP_BASE_URL}/protocol/openid-connect/certs"

    def get_keycloak_public_key(self, kid, email=None):
        cache_key = "keycloak_public_keys"
        if email:
            cache_key = f"oidc_token_{email}"

        cached_keys = cache.get(cache_key)
        if not cached_keys:
            try:
                response = requests.get(self.keycloak_cert_url)
                response.raise_for_status()
                keys_data = response.json()
                cache.set(cache_key, json.dumps(keys_data), 3600)
            except Exception as e:
                raise exceptions.AuthenticationFailed('Error obtaining public keys')
        else:
            keys_data = json.loads(cached_keys)

        for key in keys_data['keys']:
            if key['kid'] == kid:
                return jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))

        raise exceptions.AuthenticationFailed('No matching public key found')

    def authenticate(self, request):
        header = get_authorization_header(request).decode('utf-8')
        if not header:
            return None

        parts = header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None

        token = parts[1]
        try:
            try:
                # Intentar decodificar como token JWT local
                logger.debug("Intentando decodificar como token JWT local")
                decoded_token = jwt.decode(
                    token,
                    users_auth_settings.SECRET_KEY,
                    algorithms=['HS256']
                )

                try:
                    user = User.objects.get(id=decoded_token.get('user_id'))
                    return (user, token)
                except User.DoesNotExist:
                    raise exceptions.AuthenticationFailed('User not found')

            except jwt.InvalidTokenError:
                # Si falla como local, intentar como token Keycloak
                logger.debug("Token JWT local inválido, intentando como token de Keycloak")

                unverified_header = jwt.get_unverified_header(token)
                kid = unverified_header.get('kid')
                if not kid:
                    raise exceptions.AuthenticationFailed('Invalid token format')

                # Obtener email sin verificar firma
                decoded_partial = jwt.decode(token, options={"verify_signature": False})
                email = decoded_partial.get('email')
                if not email:
                    raise exceptions.AuthenticationFailed('No email found in token')

                # Obtener clave pública usando el email para cache
                public_key = self.get_keycloak_public_key(kid, email=email)

                # Verificar completamente el token ahora con la clave pública
                decoded_token = jwt.decode(
                    token,
                    public_key,
                    algorithms=['RS256'],
                    audience='account',
                    options={
                        'verify_exp': True,
                        'verify_aud': False,
                    }
                )
                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'username': decoded_token.get('preferred_username', email),
                        'first_name': decoded_token.get('given_name', ''),
                        'last_name': decoded_token.get('family_name', ''),
                        'is_active': True
                    }
                )

                return (user, token)

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except Exception as e:
            raise exceptions.AuthenticationFailed(str(e))



class CustomRefreshToken(BaseRefreshToken):
    def verify(self):
        try:
            super().verify()
        except TokenError as e:
            if 'refresh' in str(e):
                raise TokenError('Refresh token is invalid or expired. Please log in again.')
            else:
                raise TokenError(f'Token error: {str(e)}')

    def get_new_access_token(self):
        try:
            access_token = self.access_token
            return str(access_token)
        except TokenError as e:
            raise TokenError(f'Error generating new access token: {str(e)}')