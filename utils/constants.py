# Role names
ADMIN_ROLE = "Admin"
EDITOR_ROLE = "Editor"
VIEWER_ROLE = "Viewer"
DEFAULT_ROLE = VIEWER_ROLE  # assigned to every newly registered user

# Resources that permissions can be granted on (like "Document Type")
RESOURCES = ("blog", "user")

# Actions a role can be allowed to perform on a resource
ACTIONS = ("read", "write", "create", "delete")

# Roles created on first startup: name -> (description, is_system, permissions)
# Permissions: resource -> actions allowed. Admin has full access, so it needs none.
DEFAULT_ROLES = {
    ADMIN_ROLE: ("Full access, can manage roles and users", True, {}),
    EDITOR_ROLE: (
        "Can read, write and create blogs",
        False,
        {"blog": ("read", "write", "create"), "user": ("read",)},
    ),
    VIEWER_ROLE: ("Read-only access", True, {"blog": ("read",)}),
}
