from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.exceptions import HTTPException
import fastapi_users
import jwt
from jwt.exceptions import DecodeError


from src.domain.value_objects.user_roles import UserRole
from src.bootstrap.config import settings
from src.infrastructure.user.jwt_strategies import fastapi_users

SECRET = settings.SECRET
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# checks for logger in active user
get_current_active_user = fastapi_users.current_user(active=True)


# checks user permissions
def has_permissions(required_roles: list[UserRole]):
    
    async def validate_permission(token: str = Depends(oauth2_scheme)):

        try:
            payload = jwt.decode(
                jwt=token, key=SECRET, 
                algorithms=["HS256"], audience=['fastapi-users:auth']
            )
            user_role: str = payload.get("role")

            if not user_role:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="Missing role in token"
                )

            if user_role not in [role.value for role in required_roles]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Permissions denied",
                )
            
            return payload
        except jwt.DecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {e}",
            )
    
    return validate_permission
    

