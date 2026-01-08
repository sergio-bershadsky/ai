---
name: django-dev-test
description: |
  This skill should be used when the user asks to "write tests", "django tests", "pytest",
  "test factories", "create test", "add tests", "test coverage", or mentions testing Django
  applications, fixtures, or factory_boy. Provides pytest-django patterns with factory_boy
  for test data generation.
---

# Django Testing Patterns

pytest-django testing with factory_boy for fixture management.

## Core Principles

1. **pytest only** - Never use Django's TestCase
2. **factory_boy** - Use factories for all test data
3. **Mirror structure** - Tests mirror app structure
4. **Isolation** - Each test fully isolated
5. **Fast fixtures** - Prefer `@pytest.fixture` over setUp

## Installation

```bash
pip install pytest pytest-django factory-boy pytest-cov
```

## Configuration

`pytest.ini` or `pyproject.toml`:

```toml
# pyproject.toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings"
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "-ra",
    "--tb=short",
]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
]
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── factories/
│   ├── __init__.py
│   ├── user.py              # UserFactory
│   ├── product.py           # ProductFactory
│   └── order.py             # OrderFactory
├── unit/
│   ├── models/
│   │   ├── test_user.py
│   │   └── test_product.py
│   └── services/
│       └── test_user_service.py
├── integration/
│   └── api/
│       ├── test_users.py
│       └── test_products.py
└── e2e/
    └── test_checkout.py
```

## Conftest Setup

`tests/conftest.py`:

```python
import pytest
from django.test import Client
from ninja.testing import TestClient

from apps.myapp.api import api


@pytest.fixture
def client():
    """Django test client."""
    return Client()


@pytest.fixture
def api_client():
    """Django Ninja test client."""
    return TestClient(api)


@pytest.fixture
def authenticated_client(api_client, user):
    """API client with authentication."""
    api_client.headers["Authorization"] = f"Bearer {user.get_token()}"
    return api_client


@pytest.fixture
def user(user_factory):
    """Default test user."""
    return user_factory()


@pytest.fixture
def admin_user(user_factory):
    """Admin test user."""
    return user_factory(is_staff=True, is_superuser=True)
```

## Factory Pattern

Base factory in `factories/__init__.py`:

```python
import factory
from factory.django import DjangoModelFactory


class BaseFactory(DjangoModelFactory):
    """Base factory with common patterns."""

    class Meta:
        abstract = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override to handle soft-deleted models."""
        obj = super()._create(model_class, *args, **kwargs)
        return obj
```

User factory in `factories/user.py`:

```python
import factory
from factory import fuzzy
from apps.users.models import User
from . import BaseFactory


class UserFactory(BaseFactory):
    """Factory for User model."""

    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.LazyAttribute(
        lambda obj: f"{obj.name.lower().replace(' ', '.')}@example.com"
    )
    name = factory.Faker("name")
    is_active = True

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        password = extracted or "testpass123"
        obj.set_password(password)
        if create:
            obj.save(update_fields=["password"])

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Create with explicit password handling."""
        password = kwargs.pop("password", None)
        user = super()._create(model_class, *args, **kwargs)
        if password:
            user.set_password(password)
            user.save(update_fields=["password"])
        return user
```

Order factory with relationships (`factories/order.py`):

```python
import factory
from decimal import Decimal
from apps.orders.models import Order, OrderItem
from . import BaseFactory
from .user import UserFactory
from .product import ProductFactory


class OrderFactory(BaseFactory):
    """Factory for Order model."""

    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    status = "pending"
    total = factory.LazyAttribute(lambda obj: Decimal("0.00"))

    @factory.post_generation
    def items(obj, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for item in extracted:
                OrderItemFactory(order=obj, **item)
        else:
            # Create 1-3 random items
            import random
            for _ in range(random.randint(1, 3)):
                OrderItemFactory(order=obj)

        # Update total
        obj.total = sum(item.subtotal for item in obj.items.all())
        obj.save(update_fields=["total"])


class OrderItemFactory(BaseFactory):
    """Factory for OrderItem model."""

    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = factory.fuzzy.FuzzyInteger(1, 5)
    unit_price = factory.LazyAttribute(lambda obj: obj.product.price)
```

## Register Fixtures

In `conftest.py`:

```python
from tests.factories.user import UserFactory
from tests.factories.product import ProductFactory
from tests.factories.order import OrderFactory


@pytest.fixture
def user_factory():
    return UserFactory


@pytest.fixture
def product_factory():
    return ProductFactory


@pytest.fixture
def order_factory():
    return OrderFactory
```

## Test Patterns

### Model Tests

```python
# tests/unit/models/test_user.py
import pytest
from apps.users.models import User


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self, user_factory):
        user = user_factory(email="test@example.com", name="Test User")

        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.is_active is True
        assert user.id is not None

    def test_soft_delete(self, user_factory):
        user = user_factory()
        user.delete()

        assert user.is_deleted is True
        assert User.objects.filter(id=user.id).exists()

    def test_display_name(self, user_factory):
        user = user_factory(name="John Doe")
        assert user.display_name == "John Doe"

        user_no_name = user_factory(name="", email="jane@example.com")
        assert user_no_name.display_name == "jane"
```

### Service Tests

```python
# tests/unit/services/test_user_service.py
import pytest
from unittest.mock import patch, MagicMock
from apps.users.services import UserService


@pytest.mark.django_db
class TestUserService:
    def test_create_user(self, user_factory):
        user = UserService.create(
            email="new@example.com",
            name="New User",
            password="securepass123",
        )

        assert user.email == "new@example.com"
        assert user.check_password("securepass123")

    def test_create_user_duplicate_email(self, user_factory):
        user_factory(email="existing@example.com")

        with pytest.raises(ValueError, match="already registered"):
            UserService.create(
                email="existing@example.com",
                name="Another User",
                password="password123",
            )

    @patch("apps.users.services.email.send_welcome_email")
    def test_create_user_sends_email(self, mock_send, user_factory):
        user = UserService.create(
            email="new@example.com",
            name="New User",
            password="password123",
        )

        mock_send.assert_called_once_with(user)
```

### API Tests

```python
# tests/integration/api/test_users.py
import pytest


@pytest.mark.django_db
class TestUsersAPI:
    def test_list_users_requires_auth(self, api_client):
        response = api_client.get("/users/")
        assert response.status_code == 401

    def test_list_users(self, authenticated_client, user_factory):
        user_factory.create_batch(5)

        response = authenticated_client.get("/users/")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 5

    def test_create_user(self, authenticated_client):
        response = authenticated_client.post("/users/", json={
            "email": "new@example.com",
            "name": "New User",
            "password": "securepass123",
        })

        assert response.status_code == 201
        assert response.json()["email"] == "new@example.com"

    def test_get_user(self, authenticated_client, user_factory):
        user = user_factory()

        response = authenticated_client.get(f"/users/{user.id}")

        assert response.status_code == 200
        assert response.json()["id"] == str(user.id)

    def test_get_user_not_found(self, authenticated_client):
        import uuid
        fake_id = uuid.uuid4()

        response = authenticated_client.get(f"/users/{fake_id}")

        assert response.status_code == 404
```

## Fixtures

See `references/fixtures.md` for advanced fixture patterns including:
- Database transactions
- File uploads
- External service mocking
- Time freezing

## Additional Resources

### Reference Files

- **`references/fixtures.md`** - Advanced fixture patterns, mocking, parametrization

### Related Skills

- **django-dev** - Core Django patterns
- **django-dev-ninja** - API patterns being tested
