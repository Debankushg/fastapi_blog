from sqlalchemy.orm import Session

from app.config.database import SessionLocal
from app.config.settings import settings
from app.repositories import role_repository, user_repository
from app.utils.constants import ACTIONS, ADMIN_ROLE, DEFAULT_ROLES
from app.utils.security import hash_password


def _seed_roles(db: Session) -> None:
    """Create the default roles. Existing roles are left untouched so edits persist."""
    for name, (description, is_system, grants) in DEFAULT_ROLES.items():
        if role_repository.find_by_name(db, name):
            continue
        role = role_repository.create(db, name, description, is_system)
        items = [
            {"resource": resource, **{a: a in actions for a in ACTIONS}}
            for resource, actions in grants.items()
        ]
        if items:
            role_repository.set_permissions(db, role, items)


def _seed_admin(db: Session) -> None:
    """Create the default admin user and make sure it holds the Admin role."""
    admin_role = role_repository.find_by_name(db, ADMIN_ROLE)
    admin = user_repository.find_by_username(db, settings.ADMIN_USERNAME)
    if not admin:
        user_repository.create(
            db,
            settings.ADMIN_USERNAME,
            settings.ADMIN_EMAIL,
            hash_password(settings.ADMIN_PASSWORD),
            roles=[admin_role],
        )
    elif admin_role not in admin.roles:
        user_repository.set_roles(db, admin, [*admin.roles, admin_role])


def seed_defaults() -> None:
    db = SessionLocal()
    try:
        _seed_roles(db)
        _seed_admin(db)
    finally:
        db.close()
