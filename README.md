# Python Blog API

A simple Blog API built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**, featuring JWT-based authentication for admin-only operations.

## Features

- User registration (with bcrypt password hashing)
- JWT login/authentication
- Blog CRUD (create, read, update, delete) — write operations require a valid token
- Pagination and title search on blog listing
- Layered architecture (routers → crud → models)

## Tech Stack

- FastAPI
- SQLAlchemy (ORM)
- PostgreSQL
- python-jose (JWT)
- bcrypt (password hashing)
- Pydantic (request/response validation)

## Project Structure

```
app/
├── main.py              # App entrypoint, mounts routers
├── core/
│   ├── config.py        # App settings (DB URL, JWT secret, etc.)
│   └── security.py       # JWT create/verify, password hashing
├── db/
│   └── session.py        # Engine, session, Base, get_db dependency
├── models/                # SQLAlchemy table definitions
│   ├── blog.py
│   └── user.py
├── schemas/                # Pydantic request/response models
│   ├── blog.py
│   ├── user.py
│   └── auth.py
├── crud/                   # DB query logic
│   ├── blog.py
│   └── user.py
└── routers/                # Route handlers (HTTP layer)
    ├── auth.py
    ├── blog.py
    └── user.py
```

## Setup

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-jose bcrypt email-validator
```

Update the database URL in `core/config.py` (or set the `DATABASE_URL` env var) to point to your PostgreSQL instance.

## Run

```bash
uvicorn app.main:app --reload
```

API docs available at `http://localhost:8000/docs`.

## API Endpoints

| Method | Path          | Description                    | Auth required |
|--------|---------------|---------------------------------|----------------|
| POST   | `/auth/login` | Get JWT access token             | No             |
| POST   | `/user`       | Register a new user              | No             |
| GET    | `/users`      | List users (paginated, search)   | No             |
| GET    | `/user/{id}`  | Get a single user                | No             |
| PUT    | `/user/{id}`  | Update a user                    | Yes            |
| DELETE | `/user/{id}`  | Delete a user                    | Yes            |
| POST   | `/blog`       | Create a blog                    | Yes            |
| GET    | `/blogs`      | List blogs (paginated, search)   | No             |
| GET    | `/blog/{id}`  | Get a single blog                | No             |
| PUT    | `/blog/{id}`  | Update a blog                    | Yes            |
| DELETE | `/blog/{id}`  | Delete a blog                    | Yes            |
| DELETE | `/blogs`      | Delete all blogs                 | Yes            |
