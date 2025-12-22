from fastapi_users import FastAPIUsers, models
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.jwt import generate_jwt

from src.bootstrap.config import settings
from src.infrastructure.db.models.user import User
from src.infrastructure.user.user_manager import get_user_manager

bearer_transport = BearerTransport(tokenUrl="auth/login")


class CustomJWTStrategy(JWTStrategy):
    def __init__(
        self, 
        secret,
        lifetime_seconds, 
        token_audience : list[str] = ["fastapi-users:auth"], 
        algorithm = "HS256", 
        public_key = None
    ):
        super().__init__(secret, lifetime_seconds, token_audience, algorithm, public_key)

    
    async def write_token(self, user: models.UP) -> str:
        role = str(user.role.value)

        data = {
            "sub": str(user.id), "aud": self.token_audience, "role" : user.role.value
        }
        return generate_jwt(
            data, self.encode_key, self.lifetime_seconds, algorithm=self.algorithm
        )


def get_jwt_strategy() -> JWTStrategy:
    return CustomJWTStrategy(
        secret=settings.SECRET_KEY, 
        lifetime_seconds=3600
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


fastapi_users = FastAPIUsers[User, int](
    get_user_manager, [auth_backend]
)

