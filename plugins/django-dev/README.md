# Django Dev Plugin

Opinionated Django development toolkit with Ninja API, Unfold admin, pytest, and Dynaconf patterns.

## Installation

```bash
claude mcp add-from-marketplace bershadsky-claude-tools/django-dev
```

## Overview

This plugin enforces consistent, production-ready Django patterns:

- **One file = one model/form/endpoint** — Clear organization
- **UUID primary keys** — All models use UUID
- **Timestamps everywhere** — created_at/updated_at on all models
- **Soft delete by default** — deleted_at instead of hard deletes
- **Dynaconf for config** — Environment-aware settings
- **uv + pyproject.toml** — Modern dependency management
- **Docker in /docker** — All Docker artifacts organized

## Skills

### django-dev

Core Django development patterns for models, forms, and project structure.

**Triggers:**
- "Create a django project"
- "Django models"
- "Django forms"
- "Configure django settings"

**Features:**
- Project scaffolding with uv
- Model organization (1 file = 1 model)
- Base classes (UUID, timestamps, soft delete)
- Dynaconf configuration
- Docker setup

### django-dev-ninja

API development with Django Ninja (1 endpoint = 1 file).

**Triggers:**
- "Create api endpoint"
- "Django ninja"
- "REST api django"

**API Structure:**
```
myapp/api/
├── __init__.py           # NinjaAPI instance
├── users/
│   ├── __init__.py       # Router
│   ├── list.py           # GET /users/
│   ├── detail.py         # GET /users/{id}
│   └── create.py         # POST /users/
└── schemas/
    └── user.py           # Pydantic schemas
```

### django-dev-unfold

Modern admin with Unfold theme and HTMX.

**Triggers:**
- "Set up unfold admin"
- "Django admin"
- "Admin dashboard"

**Features:**
- One admin = one file
- HTMX for dynamics
- Tailwind styling
- Custom dashboards

### django-dev-test

Testing with pytest and factory_boy.

**Triggers:**
- "Write tests"
- "Django tests"
- "Test factories"

**Test Structure:**
```
tests/
├── conftest.py
├── factories/
│   ├── user.py           # UserFactory
│   └── product.py
├── unit/
│   └── models/
└── integration/
    └── api/
```

## Agents

### django-review

Code reviewer for convention compliance. Checks:
- Model organization (1 file = 1 model)
- Naming conventions (Base*, Virtual*, Proxy* prefixes)
- Class member ordering
- API structure
- Security issues

## Project Structure

```
project/
├── pyproject.toml           # Dependencies (uv)
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx/
├── config/
│   ├── settings.py          # Dynaconf integration
│   └── settings.toml
├── apps/
│   └── myapp/
│       ├── models/          # 1 file per model
│       ├── forms/           # 1 file per form
│       ├── managers/
│       ├── api/             # Django Ninja
│       └── admin/           # Unfold
└── tests/
```

## Core Patterns

### Base Model

```python
class BaseModel(BaseUUID, BaseTimeStamped, BaseSoftDelete):
    """Standard base model with UUID, timestamps, and soft delete."""

    class Meta:
        abstract = True
```

### Naming Conventions

| Prefix | Type | Example |
|--------|------|---------|
| `Base*` | Abstract base class | `BaseTimeStamped` |
| `Virtual*` | In-memory only | `VirtualCart` |
| `Proxy*` | Proxy model | `ProxyActiveUser` |
| (none) | Regular model | `User`, `Product` |

### Class Member Ordering

**All classes follow strict ordering:**

1. `class Meta` — ALWAYS FIRST
2. Fields — Class attributes
3. Managers — `objects = Manager()`
4. Properties — `@property` (alphabetical)
5. Private/dunder methods — `_method`, `__str__` (alphabetical)
6. Public methods — (alphabetical)

```python
class User(BaseModel):
    # 1. class Meta - ALWAYS FIRST
    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    # 2. Fields
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)

    # 3. Manager
    objects = UserManager()

    # 4. Properties
    @property
    def display_name(self) -> str:
        return self.name or self.email.split("@")[0]

    # 5. Private/dunder
    def __str__(self) -> str:
        return self.email

    # 6. Public methods
    def activate(self) -> None:
        self.is_active = True
        self.save(update_fields=["is_active"])
```

## Quick Start

### Initialize Project

```bash
uv init myproject
cd myproject
uv add django dynaconf django-unfold django-ninja
uv add --group dev ruff mypy django-stubs
uv add --group test pytest pytest-django factory-boy
```

### Create App with Packages

```bash
mkdir -p apps/myapp/{models,forms,managers,api,admin}
touch apps/myapp/__init__.py
touch apps/myapp/{models,forms,managers,api,admin}/__init__.py
```

## References

- [Django Ninja Docs](https://django-ninja.dev/)
- [Django Unfold Docs](https://unfoldadmin.com/)
- [Dynaconf Docs](https://www.dynaconf.com/)
- [pytest-django Docs](https://pytest-django.readthedocs.io/)

## License

[Unlicense](LICENSE) - Public Domain
