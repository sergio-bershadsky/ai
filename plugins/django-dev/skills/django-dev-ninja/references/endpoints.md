# Endpoint Patterns

Detailed patterns for Django Ninja endpoints.

## Authentication

### JWT Authentication

```python
# api/auth.py
from ninja.security import HttpBearer
from jose import jwt, JWTError
from django.conf import settings


class JWTAuth(HttpBearer):
    def authenticate(self, request, token: str):
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )
            user_id = payload.get("sub")
            if user_id is None:
                return None

            from ..models import User
            return User.objects.filter(id=user_id, is_active=True).first()

        except JWTError:
            return None
```

### API Key Authentication

```python
# api/auth.py
from ninja.security import APIKeyHeader


class ApiKeyAuth(APIKeyHeader):
    param_name = "X-API-Key"

    def authenticate(self, request, key: str):
        from ..models import APIKey
        api_key = APIKey.objects.filter(key=key, is_active=True).first()
        if api_key:
            return api_key.user
        return None
```

### Combined Authentication

```python
# api/__init__.py
from ninja import NinjaAPI
from .auth import JWTAuth, ApiKeyAuth

api = NinjaAPI(
    auth=[JWTAuth(), ApiKeyAuth()],  # Either works
)
```

### Public Endpoints

```python
# api/auth/login.py
from ninja import Router

router = Router()


@router.post("/login", auth=None)  # Disable auth for this endpoint
def login(request, payload: LoginIn):
    """Public login endpoint."""
    pass
```

## Permissions

### Permission Decorator

```python
# api/permissions.py
from functools import wraps
from ninja.errors import HttpError


def require_permission(*permissions):
    """Check user has required permissions."""
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.auth:
                raise HttpError(401, "Authentication required")

            user = request.auth
            if not user.has_perms(permissions):
                raise HttpError(403, "Permission denied")

            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_staff(func):
    """Require staff user."""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.auth or not request.auth.is_staff:
            raise HttpError(403, "Staff access required")
        return func(request, *args, **kwargs)
    return wrapper
```

Usage:

```python
# api/admin/users.py
from ninja import Router
from ..permissions import require_staff, require_permission

router = Router()


@router.delete("/{user_id}")
@require_permission("users.delete_user")
def delete_user(request, user_id: UUID):
    """Delete user (requires permission)."""
    pass


@router.get("/audit-log")
@require_staff
def audit_log(request):
    """View audit log (staff only)."""
    pass
```

## Request Handling

### Path Parameters

```python
@router.get("/{user_id}/orders/{order_id}")
def get_order(request, user_id: UUID, order_id: UUID):
    """Get specific order for user."""
    pass
```

### Query Parameters

```python
from ninja import Query
from datetime import date
from enum import Enum


class OrderStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"


@router.get("/")
def list_orders(
    request,
    status: OrderStatus = Query(None),
    start_date: date = Query(None),
    end_date: date = Query(None),
    search: str = Query(None, min_length=3),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    """List orders with filters."""
    pass
```

### Request Body

```python
from ninja import Body


@router.post("/")
def create_order(
    request,
    payload: OrderIn = Body(...),
    notify: bool = Query(True),
):
    """Create order with optional notification."""
    pass
```

### Headers

```python
from ninja import Header


@router.post("/webhook")
def webhook(
    request,
    payload: WebhookPayload,
    x_signature: str = Header(..., alias="X-Signature"),
):
    """Handle webhook with signature verification."""
    pass
```

## Response Handling

### Multiple Response Types

```python
from typing import Union


@router.post("/", response={201: UserOut, 400: ErrorResponse, 409: ErrorResponse})
def create_user(request, payload: UserIn):
    """Create user with detailed error responses."""
    if not is_valid_email(payload.email):
        return 400, {"detail": "Invalid email format"}

    if User.objects.filter(email=payload.email).exists():
        return 409, {"detail": "Email already registered"}

    user = UserService.create(payload)
    return 201, user
```

### No Content Response

```python
@router.delete("/{user_id}", response={204: None})
def delete_user(request, user_id: UUID):
    """Delete user."""
    UserService.delete(user_id)
    return 204, None
```

### Streaming Response

```python
from django.http import StreamingHttpResponse


@router.get("/export")
def export_data(request):
    """Stream large data export."""
    def generate():
        for chunk in DataService.export_chunks():
            yield chunk

    return StreamingHttpResponse(
        generate(),
        content_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="export.csv"'},
    )
```

## Error Handling

### Global Exception Handler

```python
# api/__init__.py
from ninja import NinjaAPI
from django.core.exceptions import ValidationError
from pydantic import ValidationError as PydanticValidationError


api = NinjaAPI()


@api.exception_handler(ValidationError)
def django_validation_error(request, exc):
    return api.create_response(
        request,
        {"detail": str(exc)},
        status=400,
    )


@api.exception_handler(PydanticValidationError)
def pydantic_validation_error(request, exc):
    return api.create_response(
        request,
        {"detail": exc.errors()},
        status=422,
    )


@api.exception_handler(Exception)
def generic_error(request, exc):
    import logging
    logging.exception("Unhandled exception")
    return api.create_response(
        request,
        {"detail": "Internal server error"},
        status=500,
    )
```

### Custom Exceptions

```python
# exceptions.py
from ninja.errors import HttpError


class NotFoundError(HttpError):
    def __init__(self, resource: str, id: str):
        super().__init__(404, f"{resource} with id {id} not found")


class ConflictError(HttpError):
    def __init__(self, message: str):
        super().__init__(409, message)
```

Usage:

```python
from ..exceptions import NotFoundError


@router.get("/{user_id}")
def get_user(request, user_id: UUID):
    user = UserService.get_by_id(user_id)
    if not user:
        raise NotFoundError("User", str(user_id))
    return user
```

## Async Endpoints

```python
@router.get("/async-data")
async def get_async_data(request):
    """Async endpoint for I/O-bound operations."""
    from ..services.external import ExternalService

    # Async service calls
    data = await ExternalService.fetch_data()
    return data
```

## File Operations

### File Download

```python
from django.http import FileResponse


@router.get("/{file_id}/download")
def download_file(request, file_id: UUID):
    """Download file."""
    file = FileService.get(file_id)
    return FileResponse(
        file.content,
        as_attachment=True,
        filename=file.name,
    )
```

### Multiple File Upload

```python
from ninja import File, UploadedFile
from typing import List


@router.post("/upload-multiple")
def upload_files(request, files: List[UploadedFile] = File(...)):
    """Upload multiple files."""
    results = []
    for file in files:
        result = FileService.save(file)
        results.append(result)
    return {"uploaded": results}
```

## Testing Endpoints

```python
# tests/test_api_users.py
import pytest
from ninja.testing import TestClient
from apps.myapp.api import api


@pytest.fixture
def client():
    return TestClient(api)


@pytest.fixture
def auth_client(client, user):
    client.headers["Authorization"] = f"Bearer {user.get_token()}"
    return client


def test_create_user(client):
    response = client.post("/users/", json={
        "email": "test@example.com",
        "name": "Test User",
        "password": "securepass123",
    })
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"


def test_get_user_unauthorized(client):
    response = client.get("/users/some-id")
    assert response.status_code == 401
```
