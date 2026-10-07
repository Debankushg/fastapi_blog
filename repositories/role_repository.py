from sqlalchemy.orm import Session

from app.models.role_model import Role, RolePermission


def find_all(db: Session) -> list[Role]:
    return db.query(Role).order_by(Role.id).all()


def find_by_id(db: Session, role_id: int) -> Role | None:
    return db.query(Role).filter(Role.id == role_id).first()


def find_by_name(db: Session, name: str) -> Role | None:
    return db.query(Role).filter(Role.name.ilike(name)).first()


def find_by_ids(db: Session, role_ids: list[int]) -> list[Role]:
    return db.query(Role).filter(Role.id.in_(role_ids)).all()


def create(
    db: Session, name: str, description: str | None, is_system: bool = False
) -> Role:
    role = Role(name=name, description=description, is_system=is_system)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def update(db: Session, role: Role, name: str, description: str | None) -> Role:
    role.name = name
    role.description = description
    db.commit()
    db.refresh(role)
    return role


def delete(db: Session, role: Role) -> None:
    db.delete(role)
    db.commit()


def set_permissions(db: Session, role: Role, items: list[dict]) -> Role:
    """Make the role's permission rows match `items` exactly (upsert + prune)."""
    existing = {p.resource: p for p in role.permissions}
    wanted = {item["resource"] for item in items}

    for item in items:
        permission = existing.get(item["resource"])
        if permission is None:
            permission = RolePermission(role_id=role.id, resource=item["resource"])
            db.add(permission)
        permission.can_read = item["read"]
        permission.can_write = item["write"]
        permission.can_create = item["create"]
        permission.can_delete = item["delete"]

    for resource, permission in existing.items():
        if resource not in wanted:
            db.delete(permission)

    db.commit()
    db.refresh(role)
    return role
