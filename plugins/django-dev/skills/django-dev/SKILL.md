---
name: django-dev
description: |
  This skill should be used when the user asks to "create a django project", "new django app",
  "django models", "django forms", "set up django", "configure django settings", or mentions
  Django project structure, model organization, or Dynaconf configuration. Provides opinionated
  Django development patterns with 1-file-per-model organization and consistent naming conventions.
---

# Django Development Patterns

Opinionated Django development toolkit enforcing consistent, production-ready patterns.

## Core Principles

1. **One file = one model/form** - Each model and form lives in its own file
2. **Consistent prefixes** - Abstract (`Base*`), virtual (`Virtual*`), proxy (`Proxy*`)
3. **UUID primary keys** - All models use UUID instead of auto-increment
4. **Timestamps everywhere** - All models inherit created_at/updated_at
5. **Soft delete by default** - Use deleted_at instead of hard deletes
6. **Dynaconf for config** - Never use plain settings.py
7. **uv + pyproject.toml** - Use uv for package management with split deps
8. **Class member ordering** - Strict ordering for readability
9. **Docker in /docker** - All Docker artifacts in `/docker` folder

## Project Setup (uv + pyproject.toml)

Always use uv for package management with split dependencies:

```bash
# Initialize project
uv init myproject
cd myproject

# Add dependencies by group
uv add django dynaconf django-unfold django-ninja
uv add --group dev ruff mypy django-stubs
uv add --group test pytest pytest-django factory-boy pytest-cov
```

`pyproject.toml`:

```toml
[project]
name = "myproject"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "django>=5.0",
    "dynaconf[toml]>=3.2",
    "django-unfold>=0.30",
    "django-ninja>=1.0",
    "psycopg[binary]>=3.1",
    "whitenoise>=6.6",
]

[dependency-groups]
dev = [
    "ruff>=0.3",
    "mypy>=1.8",
    "django-stubs>=4.2",
    "ipython>=8.0",
]
test = [
    "pytest>=8.0",
    "pytest-django>=4.8",
    "factory-boy>=3.3",
    "pytest-cov>=4.1",
    "freezegun>=1.4",
]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.mypy]
plugins = ["mypy_django_plugin.main"]
strict = true
```

## Project Structure

Standard Django project layout:

```
project/
├── pyproject.toml           # Dependencies (uv)
├── uv.lock                  # Lock file
├── docker/
│   ├── Dockerfile           # Main Dockerfile
│   ├── Dockerfile.dev       # Development Dockerfile
│   ├── docker-compose.yml   # Main compose
│   ├── docker-compose.dev.yml
│   ├── nginx/
│   │   └── nginx.conf
│   └── scripts/
│       ├── entrypoint.sh
│       └── wait-for-it.sh
├── config/
│   ├── __init__.py
│   ├── settings.py          # Dynaconf integration
│   ├── .secrets.toml        # Gitignored secrets
│   └── settings.toml        # Environment config
├── apps/
│   └── myapp/
│       ├── models/          # Package, not single file
│       │   ├── __init__.py
│       │   ├── base.py      # Base classes
│       │   └── user.py      # One model per file
│       ├── forms/
│       │   ├── __init__.py
│       │   └── user.py
│       ├── managers/
│       │   ├── __init__.py
│       │   └── user.py
│       ├── api/             # Django Ninja (see django-dev-ninja)
│       └── admin/           # Unfold admin (see django-dev-unfold)
├── tests/                   # See django-dev-test
└── manage.py
```

## Docker Configuration

All Docker artifacts in `/docker` folder:

```dockerfile
# docker/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application
COPY . .

# Collect static files
RUN uv run python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["uv", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

```yaml
# docker/docker-compose.yml
services:
  web:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DJANGO_ENV=production
    env_file:
      - ../.env
    depends_on:
      - db

  db:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=myproject
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${DB_PASSWORD}

volumes:
  postgres_data:
```

## Model Organization

### Base Classes

Create base classes in `models/base.py`:

```python
import uuid
from django.db import models
from django.utils import timezone


class BaseTimeStamped(models.Model):
    """Adds created_at and updated_at timestamps."""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        get_latest_by = "created_at"


class BaseSoftDelete(models.Model):
    """Adds soft delete capability with deleted_at field."""
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def hard_delete(self):
        super().delete()

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None


class BaseUUID(models.Model):
    """Uses UUID as primary key instead of auto-increment."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class BaseModel(BaseUUID, BaseTimeStamped, BaseSoftDelete):
    """Standard base model with UUID, timestamps, and soft delete."""

    class Meta:
        abstract = True
```

### Naming Conventions

| Prefix | Type | Example |
|--------|------|---------|
| `Base*` | Abstract base class | `BaseTimeStamped`, `BaseModel` |
| `Virtual*` | In-memory only (not persisted) | `VirtualCart`, `VirtualSession` |
| `Proxy*` | Proxy model | `ProxyActiveUser`, `ProxyAdmin` |
| (none) | Regular model | `User`, `Product`, `Order` |

### Class Member Ordering

All classes follow strict member ordering:

1. **`class Meta`** - ALWAYS FIRST in the class
2. **Fields** - Class attributes (model fields)
3. **Managers** - `objects = Manager()`
4. **Properties** (`@property`) - Alphabetical order
5. **Private/dunder methods** (`_method`, `__str__`) - Alphabetical order
6. **Public methods** - Alphabetical order

```python
class User(BaseModel):
    """User account model."""

    # 1. class Meta - ALWAYS FIRST
    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    # 2. Fields
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    # 3. Manager
    objects = UserManager()

    # 4. Properties (alphabetical)
    @property
    def display_name(self) -> str:
        return self.name or self.email.split("@")[0]

    @property
    def is_verified(self) -> bool:
        return self.email_verified_at is not None

    # 5. Private/dunder methods (alphabetical)
    def __repr__(self) -> str:
        return f"<User {self.email}>"

    def __str__(self) -> str:
        return self.email

    def _calculate_score(self) -> int:
        return len(self.orders.all())

    def _validate_status(self) -> bool:
        return self.is_active

    # 6. Public methods (alphabetical)
    def activate(self) -> None:
        self.is_active = True
        self.save(update_fields=["is_active"])

    def can_place_order(self) -> bool:
        return self.is_active and not self.is_deleted

    def deactivate(self) -> None:
        self.is_active = False
        self.save(update_fields=["is_active"])
```

### Model File Template

Each model in its own file (`models/user.py`):

```python
from django.db import models
from .base import BaseModel
from ..managers.user import UserManager


class User(BaseModel):
    """User account model."""

    # 1. class Meta - ALWAYS FIRST
    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]

    # 2. Fields
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    # 3. Manager
    objects = UserManager()

    # 4. Properties
    @property
    def display_name(self) -> str:
        return self.name or self.email.split("@")[0]

    # 5. Private/dunder methods
    def __str__(self) -> str:
        return self.email
```

### Model Package Init

Re-export all models in `models/__init__.py`:

```python
from .base import BaseModel, BaseTimeStamped, BaseSoftDelete, BaseUUID
from .user import User
from .product import Product

__all__ = [
    "BaseModel",
    "BaseTimeStamped",
    "BaseSoftDelete",
    "BaseUUID",
    "User",
    "Product",
]
```

## Custom Managers

Place managers in `managers/` package:

```python
# managers/user.py
from django.db import models


class UserQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True, deleted_at__isnull=True)

    def by_email(self, email: str):
        return self.filter(email__iexact=email)


class UserManager(models.Manager):
    def get_queryset(self) -> UserQuerySet:
        return UserQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def by_email(self, email: str):
        return self.get_queryset().by_email(email)
```

## Dynaconf Configuration

Always use Dynaconf for Django settings. See `references/dynaconf.md` for complete setup.

Quick setup:

```bash
pip install dynaconf
dynaconf init -f toml
```

Update `config/settings.py`:

```python
from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DJANGO",
    settings_files=["settings.toml", ".secrets.toml"],
    environments=True,
    env_switcher="DJANGO_ENV",
)
```

## Form Organization

Forms follow the same 1-file-per-form pattern. See `references/forms.md` for details.

```python
# forms/user.py
from django import forms
from ..models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email", "name"]
```

## Creating a New App

To create a new Django app with proper structure:

1. Create app directory with packages:
```bash
mkdir -p apps/myapp/{models,forms,managers,api,admin}
touch apps/myapp/__init__.py
touch apps/myapp/{models,forms,managers,api,admin}/__init__.py
```

2. Create base classes in `models/base.py`
3. Add app to `INSTALLED_APPS` using Dynaconf
4. Create initial models following conventions

## Additional Resources

### Reference Files

For detailed patterns and setup guides:

- **`references/models.md`** - Advanced model patterns, relationships, constraints
- **`references/forms.md`** - Form organization, validation, widgets
- **`references/dynaconf.md`** - Complete Dynaconf setup and environment configuration

### Related Skills

- **django-dev-ninja** - API development with Django Ninja
- **django-dev-unfold** - Admin customization with Unfold
- **django-dev-test** - Testing with pytest and factories
