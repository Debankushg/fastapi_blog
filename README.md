# Python Blog API

A Blog REST API built with **FastAPI**, **SQLAlchemy** and **PostgreSQL**. It supports user registration, JWT login, a default admin account and **role-based access control**: admins create roles (Editor, Viewer, ...), choose what each role may read, write, create and delete, and assign roles to users.

## Features

- User registration with validated username, email and password (bcrypt hashing)
- JWT login with email (or username) and password
- Default admin user created automatically on startup
- Role management: admins create roles and set a per-resource permission matrix (read / write / create / delete)
- Users can hold several roles; new users get the `Viewer` role automatically
- Every blog and user endpoint is permission-checked; pagination and search on list endpoints
- Layered architecture: Route → Controller → Service → Repository → Model
- Centralised error handling (custom exceptions mapped to HTTP responses)

## Tech Stack

- FastAPI
- SQLAlchemy (ORM)
- PostgreSQL (psycopg 3 driver)
- python-jose (JWT)
- bcrypt (password hashing)
- Pydantic (request/response validation)

## Project Structure

```
app/
├── main.py                  # App entrypoint: DB init, seed roles + admin, error handlers, routes
├── config/
│   ├── settings.py          # App settings (DB URL, JWT secret, admin defaults)
│   └── database.py          # Engine, session, Base, get_db dependency
├── routes/                  # URL definitions and dependencies (HTTP layer)
│   ├── auth_routes.py
│   ├── blog_routes.py
│   ├── role_routes.py
│   └── user_routes.py
├── controllers/             # Build API responses, call services
│   ├── auth_controller.py
│   ├── blog_controller.py
│   ├── role_controller.py
│   └── user_controller.py
├── services/                # Business logic and rules
│   ├── auth_service.py
│   ├── blog_service.py
│   ├── role_service.py
│   └── user_service.py
├── repositories/            # Database queries (only layer touching the DB)
│   ├── blog_repository.py
│   ├── role_repository.py
│   └── user_repository.py
├── models/                  # SQLAlchemy table definitions
│   ├── blog_model.py
│   ├── role_model.py        # Role, RolePermission, user_roles link table
│   └── user_model.py
├── validators/              # Pydantic request/response schemas and validation rules
│   ├── auth_validator.py
│   ├── blog_validator.py
│   ├── role_validator.py
│   └── user_validator.py
├── middleware/
│   ├── auth_middleware.py   # Bearer token, current user, require_permission, require_admin
│   └── error_middleware.py  # Maps AppException to JSON error responses
└── utils/
    ├── constants.py         # Role names, RESOURCES, ACTIONS, default role grants
    ├── permissions.py       # has_permission, is_admin, effective_permissions
    ├── security.py          # Password hashing, JWT create/decode
    ├── exceptions.py        # NotFound / Conflict / Unauthorized / Forbidden errors
    └── seed.py              # Creates default roles and the admin user
```

## Architecture

### 1. Block diagram: which folder talks to which

Arrows mean "imports / calls". Dependencies only point downward, so a lower layer never knows about the layers above it.

```mermaid
flowchart TD
    Client([Client / Swagger UI])

    subgraph Entry["Entry point"]
        MAIN["main.py<br/>creates FastAPI app, registers routes,<br/>error handlers, DB tables, default roles + admin"]
    end

    subgraph HTTP["HTTP layer"]
        ROUTES["routes/<br/>URL paths, HTTP methods,<br/>status codes, Depends()"]
        MW["middleware/<br/>auth_middleware: verify JWT, current user,<br/>require_permission, require_admin<br/>error_middleware: exception to JSON"]
        VAL["validators/<br/>Pydantic request and response schemas,<br/>field validation rules"]
    end

    subgraph App["Application layer"]
        CTRL["controllers/<br/>build response messages,<br/>call services"]
        SVC["services/<br/>business rules: duplicate checks, login,<br/>role rules, 404s, password hashing"]
    end

    subgraph Data["Data layer"]
        REPO["repositories/<br/>the only place that runs DB queries"]
        MODEL["models/<br/>SQLAlchemy tables: Blog, User,<br/>Role, RolePermission, user_roles"]
        DBCFG["config/database.py<br/>engine, SessionLocal, Base, get_db"]
    end

    DB[(PostgreSQL<br/>blogdb)]

    subgraph Shared["Shared"]
        SETTINGS["config/settings.py<br/>env vars, JWT and admin defaults"]
        UTILS["utils/<br/>security.py: hash, JWT<br/>permissions.py: has_permission<br/>constants.py: roles, resources, actions<br/>exceptions.py: AppException<br/>seed.py: default roles + admin"]
    end

    Client -->|HTTP request| MAIN
    MAIN --> ROUTES
    MAIN -.registers.-> MW
    MAIN -.on startup.-> UTILS
    ROUTES -->|validates body with| VAL
    ROUTES -->|guards with| MW
    ROUTES --> CTRL
    CTRL --> SVC
    SVC --> REPO
    SVC -.uses.-> UTILS
    REPO --> MODEL
    MODEL --> DBCFG
    DBCFG --> DB
    MW -.uses.-> UTILS
    MW -.loads user + roles.-> REPO
    UTILS -.reads.-> SETTINGS
    DBCFG -.reads.-> SETTINGS
```

Layer-by-layer version (read top to bottom; this is the path of every request):

```
                               HTTP request
                                       │
                                       ▼
 ┌────────────────────────────────────────────────────────────────────────────┐
 │ main.py   app start-up (runs once, before any request)                     │
 │                                                                            │
 │   1. import models             registers Blog, User, Role, RolePermission  │
 │   2. create_all                creates missing tables in PostgreSQL        │
 │   3. seed_defaults             creates Admin/Editor/Viewer roles and the   │
 │                                admin user (admin / Admin@123) if absent    │
 │   4. register_error_handlers   AppException ► JSON reply                   │
 │   5. include api_router        mounts every route below                    │
 │   GET /  ── home route (defined directly in main.py)                       │
 │   /docs  ── Swagger UI, built in by FastAPI                                │
 └────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
 ┌────────────────────────────────────────────────────────────────────────────┐
 │ ROUTES   routes/                 "which URL goes where"                    │
 │   __init__.py      api_router collects the four routers                    │
 │   auth_routes.py   /auth/register  /auth/login  /auth/me                   │
 │   user_routes.py   /users  /user/{id}                                      │
 │   blog_routes.py   /blog  /blog/{id}  /blogs                               │
 │   role_routes.py   /roles  /roles/{role_id}  /roles/{role_id}/permissions  │
 │                    /roles/resources  /user/{id}/roles   (admin only)       │
 │ Each route declares: path, method, status code, response_model,            │
 │ Depends(get_db) and Depends(require_permission(resource, action)).         │
 └────────────────────────────────────────────────────────────────────────────┘
                                       │ passes through, in order:
                                       ▼
 ┌────────────────────────────────────────────────────────────────────────────┐
 │ VALIDATORS + MIDDLEWARE   validators/   middleware/                        │
 │   validators/   Pydantic checks the JSON body BEFORE the controller        │
 │                 runs. Bad input ► 422 with field-level messages.           │
 │                 user:  username 3-30 [a-zA-Z0-9_], valid email,            │
 │                        password 8-64 with upper + lower + digit            │
 │                 role:  name, permission matrix (resource + 4 flags)        │
 │                 blog / auth: title, content, token and /me shapes          │
 │                 Also shapes every response (password never returned).      │
 │   auth_middleware   verify_access_token  decode Bearer JWT ► 401           │
 │                     get_current_user     token sub ► User + roles ► 401    │
 │                     require_permission   roles grant (resource, action)    │
 │                                          else ► 403                        │
 │                     require_admin        user has Admin role ► 403         │
 └────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
 ┌────────────────────────────────────────────────────────────────────────────┐
 │ CONTROLLERS   controllers/        "request in, response out"               │
 │   auth_ · user_ · blog_ · role_controller.py                               │
 │   Call ONE service, then build { message, data } for the reply.            │
 │   No queries, no business rules, no HTTP errors.                           │
 └────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
 ┌────────────────────────────────────────────────────────────────────────────┐
 │ SERVICES   services/              "business rules"                         │
 │   auth_service   find user by username/email, verify password,             │
 │                  create JWT (sub + username, 30 min)                       │
 │   user_service   duplicate username/email ► 409, hash password,            │
 │                  give new users the Viewer role, missing user ► 404        │
 │   blog_service   missing blog ► 404                                        │
 │   role_service   duplicate role name ► 409, system roles locked ► 403,     │
 │                  Admin permissions fixed ► 403, set permission matrix,     │
 │                  assign roles to a user (unknown role ► 404)               │
 │   Never runs a query itself. Raises AppException subclasses.               │
 │   Uses ──► utils/security.py   hash_password · verify_password ·           │
 │                                create / decode_access_token                │
 │            config/settings.py  token lifetime, secret key, admin name      │
 └────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
 ┌────────────────────────────────────────────────────────────────────────────┐
 │ REPOSITORIES   repositories/      "all database queries"                   │
 │   user_repository   create · find_all · find_by_id · find_by_username ·    │
 │                     find_by_email · find_by_username_or_email ·            │
 │                     update · delete · set_roles                            │
 │   blog_repository   create · find_all · find_by_id · update ·              │
 │                     delete · delete_all                                    │
 │   role_repository   find_all · find_by_id · find_by_name · find_by_ids ·   │
 │                     create · update · delete · set_permissions             │
 │   Only layer that calls db.query / commit / refresh.                       │
 └────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
 ┌────────────────────────────────────────────────────────────────────────────┐
 │ MODELS   models/                  "shape of the data"                      │
 │   user_model.py   User            ► table users                            │
 │   blog_model.py   Blog            ► table blogs                            │
 │   role_model.py   Role            ► table roles                            │
 │                   RolePermission  ► table role_permissions                 │
 │                   user_roles      ► link table (users <-> roles)           │
 │   Built on Base + engine from config/database.py                           │
 └────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
                  ┌─────────────────────────────────────────┐
                  │                PostgreSQL               │
                  │                  blogdb                 │
                  │          users · blogs · roles          │
                  │      role_permissions · user_roles      │
                  └─────────────────────────────────────────┘

 Shared helpers used by many layers:
   config/settings.py    env vars: DATABASE_URL, SECRET_KEY,
                         ADMIN_USERNAME / ADMIN_EMAIL / ADMIN_PASSWORD
   config/database.py    engine, SessionLocal, Base, get_db()
   utils/constants.py    role names, RESOURCES, ACTIONS, default role grants
   utils/permissions.py  has_permission, is_admin, effective_permissions
   utils/exceptions.py   AppException ► NotFoundError (404),
                         ConflictError (409), UnauthorizedError (401),
                         ForbiddenError (403)
   utils/seed.py         default roles + admin creation (called by main.py)

 Errors travel back up:
   AppException (from services)  ► middleware/error_middleware.py
                                    ► JSON { "detail": ... }
   HTTPException (auth guard)    ► FastAPI default JSON reply
   Pydantic validation error     ► FastAPI 422 reply
   Unknown URL                   ► FastAPI default 404
```

### 2. Folder responsibilities and rules

| Folder          | Responsibility                                              | May import from                          | Must NOT do                           |
|-----------------|-------------------------------------------------------------|------------------------------------------|---------------------------------------|
| `main.py`       | Wire everything together                                    | config, routes, middleware, utils        | Contain business logic                |
| `routes/`       | Define URLs, methods, status codes, dependencies            | controllers, validators, middleware, config | Query the DB or hold logic         |
| `validators/`   | Pydantic schemas: input validation and response shape       | nothing from the app                     | Touch the DB                          |
| `middleware/`   | Auth guard (JWT, permissions), error to JSON mapping        | utils, config, repositories (load user)  | Know about controllers or services    |
| `controllers/`  | Turn service results into response payloads                 | services, validators                     | Query the DB, raise HTTP errors       |
| `services/`     | Business rules and decisions, raise `AppException` subclasses | repositories, utils, models, validators | Use `Session.query` directly         |
| `repositories/` | All SQL / ORM queries                                       | models                                   | Contain business rules                |
| `models/`       | Table definitions                                           | config/database                          | Contain logic                         |
| `config/`       | Settings and DB engine/session                              | itself                                   | Import other app layers               |
| `utils/`        | Helpers: hashing, JWT, permissions, exceptions, seed        | config, repositories (seed only)         | Import routes or controllers          |

### 3. Request flow: `POST /auth/register`

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant R as routes/auth_routes.py
    participant V as validators/user_validator.py
    participant CT as controllers/auth_controller.py
    participant S as services/user_service.py
    participant RP as repositories/user_repository.py
    participant U as utils/security.py
    participant DB as PostgreSQL
    participant E as middleware/error_middleware.py

    C->>R: POST /auth/register (JSON)
    R->>V: validate body (UserCreate)
    alt invalid input
        V-->>C: 422 field-level errors
    end
    R->>CT: register(db, data)
    CT->>S: create_user(db, data)
    S->>RP: find_by_username / find_by_email
    RP->>DB: SELECT
    DB-->>RP: row or none
    alt username or email exists
        S-->>E: raise ConflictError
        E-->>C: 409 {detail}
    end
    S->>U: hash_password(password)
    S->>RP: create(username, email, hash)
    RP->>DB: INSERT + COMMIT
    DB-->>RP: new row
    RP-->>S: User model
    S-->>CT: User
    CT-->>R: { message, user }
    R->>V: shape with UserCreateResponse (no password)
    R-->>C: 201 Created
```

### 4. Request flow: `POST /auth/login`

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant R as routes/auth_routes.py
    participant CT as controllers/auth_controller.py
    participant S as services/auth_service.py
    participant RP as repositories/user_repository.py
    participant U as utils/security.py
    participant DB as PostgreSQL

    C->>R: POST /auth/login { email, password }
    R->>CT: login(db, email, password)
    CT->>S: login(db, identifier, password)
    S->>RP: find_by_username_or_email
    RP->>DB: SELECT
    DB-->>S: user or none
    S->>U: verify_password(password, hash)
    alt user missing or wrong password
        S-->>C: 401 Incorrect username/email or password
    end
    S->>U: create_access_token({sub, username})
    U-->>S: JWT
    S-->>C: 200 { access_token, token_type, expires_in }
```

### 5. Request flow: protected route (`POST /blog`, needs `blog:create`)

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant R as routes/blog_routes.py
    participant M as middleware/auth_middleware.py
    participant P as utils/permissions.py
    participant CT as controllers/blog_controller.py
    participant S as services/blog_service.py
    participant RP as repositories/blog_repository.py
    participant DB as PostgreSQL

    C->>R: POST /blog + Authorization: Bearer token
    R->>M: Depends(require_permission("blog", "create"))
    M->>M: verify_access_token (decode JWT)
    alt missing or invalid token
        M-->>C: 401 Could not validate credentials
    end
    M->>DB: load user + roles + permissions (token sub)
    alt user no longer exists
        M-->>C: 401
    end
    M->>P: has_permission(user, "blog", "create")
    alt Admin role: always true. Otherwise a role must grant it
        P-->>M: false
        M-->>C: 403 You do not have 'create' permission on 'blog'
    end
    R->>CT: create_blog(db, data)
    CT->>S: create_blog(db, data)
    S->>RP: create(title, content)
    RP->>DB: INSERT + COMMIT
    DB-->>RP: new row
    RP-->>S: Blog model
    S-->>CT: Blog
    CT-->>C: 201 { message, blog }
```

### 6. Application startup flow (`uvicorn app.main:app`)

```mermaid
flowchart LR
    A["uvicorn imports<br/>app.main"] --> B["import models<br/>registers Blog, User, Role,<br/>RolePermission on Base"]
    B --> C["Base.metadata.create_all<br/>creates missing tables"]
    C --> D["seed_defaults<br/>creates default roles,<br/>then the admin user, if absent"]
    D --> E["FastAPI app created"]
    E --> F["register_error_handlers<br/>AppException to JSON"]
    F --> G["include api_router<br/>auth, blog, user, role routes"]
    G --> H(["Ready: /docs"])
```

### 7. How to add a new feature (for example "comments")

1. `models/comment_model.py`: define the table and export it from `models/__init__.py`.
2. `validators/comment_validator.py`: request and response schemas.
3. `repositories/comment_repository.py`: queries.
4. `services/comment_service.py`: business rules; raise `NotFoundError` / `ConflictError` from `utils/exceptions.py`.
5. `controllers/comment_controller.py`: build the response payloads.
6. `routes/comment_routes.py`: URLs, each guarded with `Depends(require_permission("comment", "<action>"))`.
7. Register the router in `routes/__init__.py`.
8. Add `"comment"` to `RESOURCES` in `utils/constants.py` so it appears in the role permission matrix.

## Setup

1. Install dependencies:

   ```bash
   pip install fastapi uvicorn sqlalchemy "psycopg[binary]" "python-jose[cryptography]" bcrypt "pydantic[email]" python-multipart
   ```

2. Create the PostgreSQL database (the tables are created automatically on startup):

   ```bash
   createdb -h localhost -U <db_user> blogdb
   ```

3. Configure the app through environment variables (all optional, defaults shown):

   | Variable                | Default                                               | Description               |
   |-------------------------|-------------------------------------------------------|---------------------------|
   | `DATABASE_URL`          | `postgresql://debankush:12345@localhost:5432/blogdb`  | PostgreSQL connection URL |
   | `SECRET_KEY`            | `mysecretkey`                                         | JWT signing key           |
   | `ADMIN_USERNAME`        | `admin`                                               | Default admin username    |
   | `ADMIN_EMAIL`           | `admin@example.com`                                   | Default admin email       |
   | `ADMIN_PASSWORD`        | `Admin@123`                                           | Default admin password    |

   > Always set a strong `SECRET_KEY` and `ADMIN_PASSWORD` outside local development.

## Run

Run from the **parent directory** of `app/` (the one that contains the `app` folder):

```bash
uvicorn app.main:app --reload
```

Interactive docs: http://localhost:8000/docs

## Authentication

1. Log in with `POST /auth/login` and copy the `access_token`.
2. In Swagger (`/docs`) click **Authorize** and paste the token, or send it as a header:

   ```
   Authorization: Bearer <access_token>
   ```

Tokens expire after 30 minutes. Every endpoint except `/`, `/auth/register` and `/auth/login` needs a token. A valid token whose user lacks the required permission receives `403`.

Call `GET /auth/me` to see the logged-in user, their roles and their effective permissions.

### Default admin

| Field    | Value               |
|----------|---------------------|
| Username | `admin`             |
| Email    | `admin@example.com` |
| Password | `Admin@123`         |

The `email` field of the login request accepts either the email or the username. The admin account holds the `Admin` role.

## Roles and Permissions

Access is controlled by **roles**. A role holds a **permission matrix**: for each resource, four flags.

| Resource | read              | write              | create          | delete            |
|----------|-------------------|--------------------|-----------------|-------------------|
| `blog`   | `GET /blogs`, `GET /blog/{id}` | `PUT /blog/{id}` | `POST /blog` | `DELETE /blog/{id}`, `DELETE /blogs` |
| `user`   | `GET /users`, `GET /user/{id}` | `PUT /user/{id}` | (registration is public) | `DELETE /user/{id}` |

A user may hold several roles; a permission is granted if **any** of their roles grants it.

### Default roles

Created on first startup. Existing roles are never overwritten, so edits you make persist.

| Role     | System role | blog                      | user | Notes                                    |
|----------|-------------|---------------------------|------|------------------------------------------|
| `Admin`  | yes         | everything                | everything | Full access, manages roles. Permissions cannot be edited. |
| `Editor` | no          | read, write, create       | read | Cannot delete. Editable and deletable.   |
| `Viewer` | yes         | read                      | none | Assigned to every new registration. Permissions editable, role not deletable. |

System roles cannot be renamed or deleted. The default admin user cannot lose the `Admin` role.

### Typical workflow (admin)

1. `GET /roles/resources` to see the resources and actions available.
2. `POST /roles` to create a role, e.g. `{ "name": "Moderator", "description": "Can edit and delete blogs" }`.
3. `PUT /roles/{role_id}/permissions` to set its matrix (replaces the whole matrix; resources left out are removed):

   ```json
   {
     "permissions": [
       { "resource": "blog", "read": true, "write": true, "create": true, "delete": true },
       { "resource": "user", "read": true }
     ]
   }
   ```

4. `PUT /user/{id}/roles` with `{ "role_ids": [4] }` to assign it (replaces the user's roles).

The new permissions apply on the user's next request; the user does not need to log in again.

## API Endpoints

`Permission` means the caller needs that `resource:action`. `Admin` means the Admin role is required.

| Method | Path                          | Description                           | Access                   |
|--------|-------------------------------|---------------------------------------|--------------------------|
| GET    | `/`                           | Health / welcome message              | Public                   |
| POST   | `/auth/register`              | Register a new user (gets `Viewer`)   | Public                   |
| POST   | `/auth/login`                 | Log in and get a JWT access token     | Public                   |
| GET    | `/auth/me`                    | Current user, roles, permissions      | Logged in                |
| GET    | `/users`                      | List users (paginated, search)        | Permission `user:read`   |
| GET    | `/user/{id}`                  | Get a single user                     | Permission `user:read`   |
| PUT    | `/user/{id}`                  | Update a user                         | Permission `user:write`  |
| DELETE | `/user/{id}`                  | Delete a user                         | Permission `user:delete` |
| PUT    | `/user/{id}/roles`            | Assign roles to a user                | Admin                    |
| POST   | `/blog`                       | Create a blog                         | Permission `blog:create` |
| GET    | `/blogs`                      | List blogs (paginated, search)        | Permission `blog:read`   |
| GET    | `/blog/{id}`                  | Get a single blog                     | Permission `blog:read`   |
| PUT    | `/blog/{id}`                  | Update a blog                         | Permission `blog:write`  |
| DELETE | `/blog/{id}`                  | Delete a blog                         | Permission `blog:delete` |
| DELETE | `/blogs`                      | Delete all blogs                      | Permission `blog:delete` |
| GET    | `/roles/resources`            | Resources and actions for the matrix  | Admin                    |
| GET    | `/roles`                      | List roles with permissions           | Admin                    |
| POST   | `/roles`                      | Create a role                         | Admin                    |
| GET    | `/roles/{role_id}`            | Get a role                            | Admin                    |
| PUT    | `/roles/{role_id}`            | Rename a role / change description    | Admin                    |
| DELETE | `/roles/{role_id}`            | Delete a role                         | Admin                    |
| PUT    | `/roles/{role_id}/permissions`| Set the role's permission matrix      | Admin                    |

List endpoints accept `page` (default `1`), `limit` (default `10`) and `search` (matches blog title or username, case-insensitive).

### Examples

**Register**

```http
POST /auth/register
Content-Type: application/json

{ "username": "john_doe", "email": "john@example.com", "password": "Str0ngPass" }
```

Validation rules:

- `username`: 3–30 characters, letters, numbers and underscores only
- `email`: valid email address (stored lowercase)
- `password`: 8–64 characters with at least one uppercase letter, one lowercase letter and one digit

**Login**

```http
POST /auth/login
Content-Type: application/json

{ "email": "admin@example.com", "password": "Admin@123" }
```

Response:

```json
{ "access_token": "<jwt>", "token_type": "bearer", "expires_in": 1800 }
```

**Create a blog (needs `blog:create`)**

```http
POST /blog
Authorization: Bearer <access_token>
Content-Type: application/json

{ "title": "My first post", "content": "Hello world" }
```

## Error Responses

Errors are returned as `{ "detail": "<message>" }`.

| Status | Meaning                                                     |
|--------|-------------------------------------------------------------|
| 401    | Missing/invalid token, or incorrect login credentials       |
| 403    | Valid token, but the user's roles lack the permission, or a system role is protected |
| 404    | Blog, user or role not found                                |
| 409    | Username, email or role name already exists                 |
| 422    | Request body failed validation (field-level messages)       |
