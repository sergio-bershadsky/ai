# Advanced Fixture Patterns

Detailed pytest fixture patterns for Django testing.

## Database Fixtures

### Transaction Handling

```python
# conftest.py
import pytest


@pytest.fixture
def db_transaction(db):
    """Provide a database transaction that rolls back."""
    from django.db import connection

    # Start transaction
    connection.set_autocommit(False)
    yield
    # Rollback
    connection.rollback()
    connection.set_autocommit(True)


@pytest.fixture(scope="class")
def db_class(django_db_setup, django_db_blocker):
    """Class-scoped database access."""
    with django_db_blocker.unblock():
        yield
```

### Bulk Data

```python
@pytest.fixture
def many_users(user_factory):
    """Create many users for pagination tests."""
    return user_factory.create_batch(100)


@pytest.fixture
def users_with_orders(user_factory, order_factory):
    """Users with associated orders."""
    users = user_factory.create_batch(5)
    for user in users:
        order_factory.create_batch(3, user=user)
    return users
```

## Mocking External Services

### Email

```python
@pytest.fixture
def mock_email(mocker):
    """Mock email sending."""
    return mocker.patch("django.core.mail.send_mail")


@pytest.fixture
def mock_email_backend(settings):
    """Use in-memory email backend."""
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


# Usage
def test_sends_welcome_email(mock_email, user_factory):
    user = UserService.create(email="test@example.com", ...)

    mock_email.assert_called_once()
    assert "Welcome" in mock_email.call_args[0][0]
```

### HTTP Requests

```python
@pytest.fixture
def mock_requests(mocker):
    """Mock requests library."""
    return mocker.patch("requests.get")


@pytest.fixture
def mock_external_api(requests_mock):
    """Mock external API responses using requests-mock."""
    requests_mock.get(
        "https://api.external.com/data",
        json={"status": "ok", "data": []},
    )
    return requests_mock


# Usage
def test_external_api_call(mock_external_api):
    result = ExternalService.fetch_data()
    assert result["status"] == "ok"
```

### AWS Services

```python
@pytest.fixture
def mock_s3(mocker):
    """Mock S3 client."""
    mock_client = mocker.MagicMock()
    mocker.patch("boto3.client", return_value=mock_client)
    return mock_client


@pytest.fixture
def mock_s3_moto():
    """Mock S3 using moto."""
    import moto
    import boto3

    with moto.mock_s3():
        conn = boto3.client("s3", region_name="us-east-1")
        conn.create_bucket(Bucket="test-bucket")
        yield conn
```

## File Handling

### Temporary Files

```python
@pytest.fixture
def temp_file(tmp_path):
    """Create a temporary file."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("test content")
    return file_path


@pytest.fixture
def temp_image(tmp_path):
    """Create a temporary image."""
    from PIL import Image

    image = Image.new("RGB", (100, 100), color="red")
    file_path = tmp_path / "test.png"
    image.save(file_path)
    return file_path
```

### Upload Files

```python
@pytest.fixture
def uploaded_file():
    """Create Django uploaded file."""
    from django.core.files.uploadedfile import SimpleUploadedFile

    return SimpleUploadedFile(
        name="test.txt",
        content=b"file content",
        content_type="text/plain",
    )


@pytest.fixture
def uploaded_image():
    """Create Django uploaded image."""
    from django.core.files.uploadedfile import SimpleUploadedFile
    from io import BytesIO
    from PIL import Image

    image = Image.new("RGB", (100, 100), color="red")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return SimpleUploadedFile(
        name="test.png",
        content=buffer.getvalue(),
        content_type="image/png",
    )
```

## Time Control

### Freeze Time

```python
import pytest
from freezegun import freeze_time
from datetime import datetime


@pytest.fixture
def frozen_time():
    """Freeze time to a specific moment."""
    with freeze_time("2024-01-15 12:00:00"):
        yield datetime(2024, 1, 15, 12, 0, 0)


# Usage
@freeze_time("2024-01-15")
def test_created_at(user_factory):
    user = user_factory()
    assert user.created_at.date() == datetime(2024, 1, 15).date()
```

### Time Travel

```python
@pytest.fixture
def time_machine():
    """Provide time travel capability."""
    from freezegun import freeze_time

    class TimeMachine:
        def __init__(self):
            self.frozen = None

        def travel_to(self, dt):
            if self.frozen:
                self.frozen.stop()
            self.frozen = freeze_time(dt)
            self.frozen.start()
            return dt

        def stop(self):
            if self.frozen:
                self.frozen.stop()

    machine = TimeMachine()
    yield machine
    machine.stop()


# Usage
def test_time_travel(time_machine, user_factory):
    time_machine.travel_to("2024-01-01")
    user = user_factory()

    time_machine.travel_to("2024-06-01")
    assert user.account_age_days == 152
```

## Parametrization

### Simple Parameters

```python
@pytest.mark.parametrize("status,expected", [
    ("pending", True),
    ("completed", False),
    ("cancelled", False),
])
def test_order_can_cancel(order_factory, status, expected):
    order = order_factory(status=status)
    assert order.can_cancel() == expected
```

### Factory Parameters

```python
@pytest.mark.parametrize("is_staff,expected_status", [
    (True, 200),
    (False, 403),
])
def test_admin_access(api_client, user_factory, is_staff, expected_status):
    user = user_factory(is_staff=is_staff)
    api_client.force_authenticate(user)

    response = api_client.get("/admin/users/")

    assert response.status_code == expected_status
```

### Indirect Fixtures

```python
@pytest.fixture
def user_type(request, user_factory):
    """Create user based on parameter."""
    user_types = {
        "regular": {},
        "staff": {"is_staff": True},
        "admin": {"is_staff": True, "is_superuser": True},
    }
    return user_factory(**user_types[request.param])


@pytest.mark.parametrize("user_type", ["regular", "staff", "admin"], indirect=True)
def test_user_permissions(user_type):
    # user_type is now the created user
    pass
```

## Async Testing

```python
import pytest


@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_async_service():
    result = await AsyncService.fetch_data()
    assert result is not None
```

## Database Queries

### Query Counting

```python
@pytest.fixture
def query_counter(django_assert_num_queries):
    """Provide query counter."""
    return django_assert_num_queries


# Usage
def test_efficient_query(query_counter, user_factory):
    users = user_factory.create_batch(10)

    with query_counter(1):  # Should only take 1 query
        list(User.objects.all())
```

### Query Logging

```python
@pytest.fixture
def log_queries(settings, caplog):
    """Log all database queries."""
    import logging
    settings.DEBUG = True
    logging.getLogger("django.db.backends").setLevel(logging.DEBUG)
    yield
    # Queries logged in caplog
```

## Cache Control

```python
@pytest.fixture
def clear_cache():
    """Clear cache before and after test."""
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def mock_cache(mocker):
    """Mock cache to avoid side effects."""
    cache_mock = mocker.MagicMock()
    mocker.patch("django.core.cache.cache", cache_mock)
    return cache_mock
```

## Celery Tasks

```python
@pytest.fixture
def celery_eager(settings):
    """Run Celery tasks synchronously."""
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True


@pytest.fixture
def mock_celery_task(mocker):
    """Mock specific Celery task."""
    return mocker.patch("apps.myapp.tasks.send_notification.delay")


# Usage
def test_task_called(mock_celery_task, user_factory):
    user = user_factory()
    UserService.activate(user)

    mock_celery_task.assert_called_once_with(user.id)
```

## Custom Markers

```python
# conftest.py
import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow")
    config.addinivalue_line("markers", "integration: mark as integration test")
    config.addinivalue_line("markers", "e2e: mark as end-to-end test")


@pytest.fixture(autouse=True)
def skip_slow(request):
    """Skip slow tests unless --runslow is given."""
    if request.node.get_closest_marker("slow"):
        if not request.config.getoption("--runslow"):
            pytest.skip("need --runslow option to run")


def pytest_addoption(parser):
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )
```

Usage:

```python
@pytest.mark.slow
def test_large_data_processing():
    # This test takes a long time
    pass


@pytest.mark.integration
def test_external_service():
    # This test requires external services
    pass
```

## Test Coverage

```bash
# Run with coverage
pytest --cov=apps --cov-report=html --cov-report=term-missing

# Fail if coverage below threshold
pytest --cov=apps --cov-fail-under=80
```

`pyproject.toml`:

```toml
[tool.coverage.run]
source = ["apps"]
omit = [
    "*/migrations/*",
    "*/tests/*",
    "*/__pycache__/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
```
