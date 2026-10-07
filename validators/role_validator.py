from pydantic import AliasChoices, BaseModel, Field, field_validator

from app.utils.constants import RESOURCES


class RoleBrief(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50, examples=["Moderator"])
    description: str | None = Field(default=None, max_length=255)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Role name must be at least 2 characters")
        return value


class PermissionItem(BaseModel):
    """One row of the permission matrix: a resource and what the role may do on it."""

    resource: str = Field(examples=["blog"])
    # Accepts "read" from requests and "can_read" from the database model
    read: bool = Field(default=False, validation_alias=AliasChoices("read", "can_read"))
    write: bool = Field(default=False, validation_alias=AliasChoices("write", "can_write"))
    create: bool = Field(default=False, validation_alias=AliasChoices("create", "can_create"))
    delete: bool = Field(default=False, validation_alias=AliasChoices("delete", "can_delete"))

    @field_validator("resource")
    @classmethod
    def validate_resource(cls, value: str) -> str:
        if value not in RESOURCES:
            raise ValueError(f"Unknown resource. Allowed: {', '.join(RESOURCES)}")
        return value


class SetPermissionsRequest(BaseModel):
    permissions: list[PermissionItem]

    @field_validator("permissions")
    @classmethod
    def no_duplicate_resources(cls, items: list[PermissionItem]):
        resources = [item.resource for item in items]
        if len(resources) != len(set(resources)):
            raise ValueError("Each resource may appear only once")
        return items


class AssignRolesRequest(BaseModel):
    role_ids: list[int] = Field(examples=[[2]])


class RoleResponse(BaseModel):
    id: int
    name: str
    description: str | None
    is_system: bool
    permissions: list[PermissionItem]

    class Config:
        from_attributes = True


class RoleDetailResponse(BaseModel):
    message: str
    role: RoleResponse


class RoleListResponse(BaseModel):
    message: str
    roles: list[RoleResponse]


class ResourcesResponse(BaseModel):
    resources: list[str]
    actions: list[str]
