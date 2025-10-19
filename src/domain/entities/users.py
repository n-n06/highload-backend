from dataclasses import dataclass
from typing import Optional
from ..value_objects.user_role import UserRole
from ..exceptions.auth_exceptions import InvalidPasswordError, PermissionDeniedError


@dataclass
class User:
    id: Optional[int]
    email: str
    hashed_password: str
    role: UserRole
    is_active: bool = True
    is_verified: bool = False

    def can_perform_action(self, required_roles: list[UserRole]) -> bool:
        if not self.is_active:
            return False
        return self.role in required_roles

    def require_permission(self, required_roles: list[UserRole]) -> None:
        if not self.can_perform_action(required_roles):
            raise PermissionDeniedError(
                f"User role {self.role} doesn't have required permissions"
            )

    def is_superuser(self) -> bool:
        return self.role == UserRole.ADMIN

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False

    def verify(self) -> None:
        self.is_verified = True