from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.controllers import role_controller
from app.middleware.auth_middleware import require_admin
from app.validators.role_validator import (
    AssignRolesRequest,
    ResourcesResponse,
    RoleCreate,
    RoleDetailResponse,
    RoleListResponse,
    SetPermissionsRequest,
)
from app.validators.user_validator import UserCreateResponse

# Every role-management endpoint is admin only
router = APIRouter(tags=["Roles"], dependencies=[Depends(require_admin)])


# List resources and actions available for the permission matrix
@router.get("/roles/resources", response_model=ResourcesResponse)
async def get_resources():
    return await role_controller.get_resources()


# List all roles with their permissions
@router.get("/roles", response_model=RoleListResponse)
async def get_roles(db: Session = Depends(get_db)):
    return await role_controller.get_roles(db)


# Create a role
@router.post("/roles", status_code=201, response_model=RoleDetailResponse)
async def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    return await role_controller.create_role(db, role)


# Read a single role
@router.get("/roles/{role_id}", response_model=RoleDetailResponse)
async def get_role(role_id: int, db: Session = Depends(get_db)):
    return await role_controller.get_role(db, role_id)


# Rename a role / change description
@router.put("/roles/{role_id}", response_model=RoleDetailResponse)
async def update_role(role_id: int, role: RoleCreate, db: Session = Depends(get_db)):
    return await role_controller.update_role(db, role_id, role)


# Delete a role
@router.delete("/roles/{role_id}", status_code=200)
async def delete_role(role_id: int, db: Session = Depends(get_db)):
    return await role_controller.delete_role(db, role_id)


# Replace a role's permission matrix
@router.put("/roles/{role_id}/permissions", response_model=RoleDetailResponse)
async def set_permissions(
    role_id: int,
    body: SetPermissionsRequest,
    db: Session = Depends(get_db),
):
    return await role_controller.set_permissions(db, role_id, body)


# Assign roles to a user (replaces the user's current roles)
@router.put("/user/{id}/roles", response_model=UserCreateResponse)
async def assign_roles(
    id: int, body: AssignRolesRequest, db: Session = Depends(get_db)
):
    return await role_controller.assign_roles(db, id, body.role_ids)
