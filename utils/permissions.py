from app.utils.constants import ACTIONS, ADMIN_ROLE, RESOURCES


def is_admin(user) -> bool:
    return any(role.name == ADMIN_ROLE for role in user.roles)


def has_permission(user, resource: str, action: str) -> bool:
    """Admin role is allowed everything; otherwise any role granting it is enough."""
    if is_admin(user):
        return True
    for role in user.roles:
        for permission in role.permissions:
            if permission.resource == resource and getattr(
                permission, f"can_{action}"
            ):
                return True
    return False


def effective_permissions(user) -> dict[str, dict[str, bool]]:
    return {
        resource: {action: has_permission(user, resource, action) for action in ACTIONS}
        for resource in RESOURCES
    }
