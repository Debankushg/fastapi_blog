from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.role_model import Role
from app.models.user_model import User
from app.repositories import role_repository, user_repository
from app.services import user_service
from app.utils.constants import ADMIN_ROLE
from app.utils.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.validators.role_validator import RoleCreate, SetPermissionsRequest


def list_roles(db: Session) -> list[Role]:
    return role_repository.find_all(db)


def get_role(db: Session, role_id: int) -> Role:
    role = role_repository.find_by_id(db, role_id)
    if not role:
        raise NotFoundError(f"Role with id {role_id} not found")
    return role


def create_role(db: Session, data: RoleCreate) -> Role:
    if role_repository.find_by_name(db, data.name):
        raise ConflictError("Role name already exists")
    return role_repository.create(db, data.name, data.description)


def update_role(db: Session, role_id: int, data: RoleCreate) -> Role:
    role = get_role(db, role_id)
    if role.is_system:
        raise ForbiddenError("System roles cannot be modified")
    existing = role_repository.find_by_name(db, data.name)
    if existing and existing.id != role.id:
        raise ConflictError("Role name already exists")
    return role_repository.update(db, role, data.name, data.description)


def delete_role(db: Session, role_id: int) -> None:
    role = get_role(db, role_id)
    if role.is_system:
        raise ForbiddenError("System roles cannot be deleted")
    role_repository.delete(db, role)


def set_permissions(db: Session, role_id: int, data: SetPermissionsRequest) -> Role:
    role = get_role(db, role_id)
    if role.name == ADMIN_ROLE:
        raise ForbiddenError("The Admin role always has full access")
    items = [item.model_dump() for item in data.permissions]
    return role_repository.set_permissions(db, role, items)


def assign_roles(db: Session, user_id: int, role_ids: list[int]) -> User:
    user = user_service.get_user(db, user_id)
    roles = role_repository.find_by_ids(db, role_ids)

    missing = set(role_ids) - {role.id for role in roles}
    if missing:
        raise NotFoundError(f"Role id(s) not found: {sorted(missing)}")

    # Never lock the default admin account out of the Admin role
    if user.username == settings.ADMIN_USERNAME and not any(
        role.name == ADMIN_ROLE for role in roles
    ):
        raise ForbiddenError("The default admin must keep the Admin role")

    return user_repository.set_roles(db, user, roles)
