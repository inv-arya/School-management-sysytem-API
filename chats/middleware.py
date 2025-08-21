from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from jwt import decode as jwt_decode
from jwt.exceptions import InvalidTokenError
from django.conf import settings
from django.contrib.auth import get_user_model

@database_sync_to_async
def get_user(user_id):
    User = get_user_model()
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = parse_qs(scope["query_string"].decode())
        token = query_string.get("token")
        if token:
            try:
                
                AccessToken(token[0])
                decoded_data = jwt_decode(token[0], settings.SECRET_KEY, algorithms=["HS256"])
                user = await get_user(decoded_data["user_id"])
                if not user.is_active:
                    scope["user"] = AnonymousUser()
                else:
                    scope["user"] = user
            except InvalidTokenError:
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
