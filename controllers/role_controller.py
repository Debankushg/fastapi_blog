from sqlalchemy.orm import Session

from app.services import role_service
from app.utils.constants import ACTIONS, RESOURCES
from app.validators.role_validator import RoleCreate, SetPermissionsRequest


async def get_resources():
    return {"resources": list(RESOURCES), "actions": list(ACTIONS)}


async def get_roles(db: Session):
    return {
        "message": "Roles fetched successfully",
        "roles": role_service.list_roles(db),
    }


async def get_role(db: Session, role_id: int):
    return {
        "message": "Role fetched successfully",
        "role": role_service.get_role(db, role_id),
    }


async def create_role(db: Session, data: RoleCreate):
    return {
        "message": "Role created successfully",
        "role": role_service.create_role(db, data),
    }


async def update_role(db: Session, role_id: int, data: RoleCreate):
    return {
        "message": "Role updated successfully",
        "role": role_service.update_role(db, role_id, data),
    }


async def delete_role(db: Session, role_id: int):
    role_service.delete_role(db, role_id)
    return {"message": "Role deleted successfully"}


async def set_permissions(db: Session, role_id: int, data: SetPermissionsRequest):
    return {
        "message": "Role permissions updated successfully",
        "role": role_service.set_permissions(db, role_id, data),
    }


async def assign_roles(db: Session, user_id: int, role_ids: list[int]):
    return {
        "message": "User roles updated successfully",
        "user": role_service.assign_roles(db, user_id, role_ids),
    }
