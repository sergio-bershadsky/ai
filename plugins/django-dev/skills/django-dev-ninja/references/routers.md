# Router Organization

Advanced router patterns for Django Ninja.

## Nested Routers

For deeply nested resources:

```python
# api/users/__init__.py
from ninja import Router

from .list import router as list_router
from .detail import router as detail_router
from .orders import router as orders_router

router = Router()

router.add_router("", list_router)
router.add_router("", detail_router)
router.add_router("/{user_id}/orders", orders_router)  # Nested
```

```python
# api/users/orders/__init__.py
from ninja import Router

router = Router()


@router.get("/")
def list_user_orders(request, user_id: UUID):
    """List orders for specific user."""
    return OrderService.list_by_user(user_id)


@router.post("/")
def create_user_order(request, user_id: UUID, payload: OrderIn):
    """Create order for user."""
    return OrderService.create_for_user(user_id, payload)
```

## API Versioning

### URL-based Versioning

```python
# api/v1/__init__.py
from ninja import NinjaAPI
from .users import router as users_router

api_v1 = NinjaAPI(version="1.0.0", urls_namespace="api_v1")
api_v1.add_router("/users", users_router)

# api/v2/__init__.py
from ninja import NinjaAPI
from .users import router as users_router

api_v2 = NinjaAPI(version="2.0.0", urls_namespace="api_v2")
api_v2.add_router("/users", users_router)
```

```python
# urls.py
from django.urls import path
from api.v1 import api_v1
from api.v2 import api_v2

urlpatterns = [
    path("api/v1/", api_v1.urls),
    path("api/v2/", api_v2.urls),
]
```

### Header-based Versioning

```python
# api/__init__.py
from ninja import NinjaAPI


def get_api_version(request):
    return request.headers.get("X-API-Version", "1")


api = NinjaAPI()


@api.get("/data")
def get_data(request):
    version = get_api_version(request)
    if version == "2":
        return DataService.get_v2()
    return DataService.get_v1()
```

## OpenAPI Customization

### Custom Schema

```python
from ninja import NinjaAPI

api = NinjaAPI(
    title="My API",
    version="1.0.0",
    description="""
    # My API Documentation

    This API provides access to user and product data.

    ## Authentication

    Use Bearer token in Authorization header.
    """,
    docs_url="/docs",
    openapi_url="/openapi.json",
)
```

### Tag Descriptions

```python
api = NinjaAPI()

api.add_router("/users", users_router, tags=["Users"])
api.add_router("/products", products_router, tags=["Products"])


# In endpoint decorators, add descriptions
@router.get("/", summary="List all users", description="Returns paginated list of users.")
def list_users(request):
    pass
```

### Custom OpenAPI Extensions

```python
from ninja import Schema


class UserOut(Schema):
    id: UUID
    email: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
            }
        }
```

## Router Middleware

### Per-Router Middleware

```python
# api/admin/__init__.py
from ninja import Router
from functools import wraps


def admin_only(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.auth or not request.auth.is_staff:
            raise HttpError(403, "Admin access required")
        return func(request, *args, **kwargs)
    return wrapper


router = Router()


# Apply to all endpoints in router
@router.api_operation(["GET", "POST", "PUT", "DELETE"], "/{path:path}")
@admin_only
def admin_operations(request, path: str):
    pass
```

### Request/Response Hooks

```python
# api/__init__.py
from ninja import NinjaAPI
import time


api = NinjaAPI()


@api.on_request
def log_request(request):
    request.start_time = time.time()


@api.on_response
def log_response(request, response):
    duration = time.time() - request.start_time
    print(f"{request.method} {request.path} - {response.status_code} ({duration:.3f}s)")
    return response
```

## Rate Limiting

```python
# api/throttle.py
from functools import wraps
from django.core.cache import cache
from ninja.errors import HttpError


def rate_limit(key: str, limit: int, period: int):
    """Rate limit decorator.

    Args:
        key: Cache key prefix
        limit: Max requests
        period: Time period in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            user_key = f"{key}:{request.auth.id if request.auth else request.META['REMOTE_ADDR']}"
            count = cache.get(user_key, 0)

            if count >= limit:
                raise HttpError(429, "Rate limit exceeded")

            cache.set(user_key, count + 1, period)
            return func(request, *args, **kwargs)
        return wrapper
    return decorator
```

Usage:

```python
@router.post("/send-email")
@rate_limit("email", limit=10, period=3600)  # 10 per hour
def send_email(request, payload: EmailIn):
    pass
```

## CORS Configuration

```python
# api/__init__.py
from ninja import NinjaAPI
from django.conf import settings

api = NinjaAPI()


if settings.DEBUG:
    from ninja.cors import CORSMiddleware

    api.add_middleware(CORSMiddleware, allow_origins=["*"])
```

For production, use django-cors-headers:

```python
# settings.py
INSTALLED_APPS = [
    "corsheaders",
    ...
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    ...
]

CORS_ALLOWED_ORIGINS = [
    "https://app.example.com",
]
```

## Testing Routers

```python
# tests/conftest.py
import pytest
from ninja.testing import TestClient
from apps.myapp.api import api


@pytest.fixture
def api_client():
    return TestClient(api)


@pytest.fixture
def authenticated_client(api_client, user_factory):
    user = user_factory()
    api_client.headers["Authorization"] = f"Bearer {user.get_token()}"
    api_client.user = user
    return api_client
```

```python
# tests/test_users_router.py
def test_users_router_requires_auth(api_client):
    response = api_client.get("/users/")
    assert response.status_code == 401


def test_users_router_lists_users(authenticated_client, user_factory):
    user_factory.create_batch(5)
    response = authenticated_client.get("/users/")
    assert response.status_code == 200
    assert len(response.json()["items"]) >= 5
```

## Modular Router Files

For very large APIs, split by HTTP method:

```
api/users/
├── __init__.py
├── get.py          # All GET endpoints
├── post.py         # All POST endpoints
├── put.py          # All PUT endpoints
├── patch.py        # All PATCH endpoints
└── delete.py       # All DELETE endpoints
```

Or by action:

```
api/users/
├── __init__.py
├── crud.py         # Basic CRUD
├── search.py       # Search/filter endpoints
├── bulk.py         # Bulk operations
└── export.py       # Export endpoints
```
