
from src.tmp.auth.schemas import UserRead

def require_superuser(user: UserRead):
    # TODO: implement later
    pass

def require_manager(user):
    pass
    # if user.role != UserRole.MANAGER:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Only managers can perform this action."
    #     )
    

def require_delivery_person(user):
    pass
    # if user.role != UserRole.DELIVERY:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Only delivery personnel can perform this action."
    #     )
