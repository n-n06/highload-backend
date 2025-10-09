from fastapi import Depends, status
from fastapi_users.authentication import JWTStrategy
from fastapi.exceptions import HTTPException
import jwt

from src.auth.strategy import fastapi_users
from src.auth.models import UserRole
from src.auth.config import SECRET

# checks for logger in active user
current_active_user = fastapi_users.current_user(active=True)

# checks user permissions
def has_permissions(required_roles: list[UserRole]):
    
    async def validate_permissions(
        token: str = Depends(JWTStrategy().transport.get_login_token)
    ):
        try:
            payload = jwt.decode(token, SECRET, algorithms=["HS256"])
            user_role : str = payload.get("role", None)

            required_role_list = [role.value for role in required_roles]

            if user_role is None or user_role not in required_role_list:
                raise HTTPException(
                    status.HTTP_403_FORBIDDEN,
                    detail="Permission denied."
                ) 
            
            return payload
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalide authentication credentials."
            )
        
    return validate_permissions
    
    