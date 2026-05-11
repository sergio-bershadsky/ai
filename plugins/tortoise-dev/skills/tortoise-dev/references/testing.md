# Testing Tortoise ORM Code

Two distinct layers — test them differently.

## Layer 1: Pure logic on `Base*` (preferred, fast)

Rule 2 makes this possible: business logic accepts the abstract interface, so unit tests can
subclass it without any DB.

```python
# tests/unit/test_invoice_logic.py
from datetime import datetime, timezone
from decimal import Decimal

from apps.billing.models import BaseInvoice


class FakeInvoice(BaseInvoice):
    class Meta:
        abstract = True

    async def save(self, *args, **kwargs):  # block accidental DB hits
        raise AssertionError("FakeInvoice must not save")


def test_overdue_when_past_due_and_unpaid():
    inv = FakeInvoice(
        number="INV-1",
        amount=Decimal("100"),
        paid=False,
        due_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    today = datetime(2026, 5, 1, tzinfo=timezone.utc)
    assert inv.is_overdue(today) is True


def test_not_overdue_when_paid():
    inv = FakeInvoice(
        number="INV-2",
        amount=Decimal("100"),
        paid=True,
        due_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    assert inv.is_overdue(datetime(2026, 5, 1, tzinfo=timezone.utc)) is False
```

No `Tortoise.init`, no event loop juggling. Aim for **80%+ of your tests at this layer**.

## Layer 2: Integration with a real DB

Use Tortoise 1.0's `tortoise_test_context()` — **not** the legacy `tortoise.contrib.test.TestCase`
or `initializer`/`finalizer` shims (those still work but are deprecated).

```python
# tests/conftest.py
import pytest
import pytest_asyncio
from tortoise.contrib.test import tortoise_test_context

from config.tortoise import TORTOISE_ORM


@pytest_asyncio.fixture(scope="function")
async def db():
    # Per-test isolation: clean SQLite memory DB each test.
    test_config = {
        **TORTOISE_ORM,
        "connections": {"default": "sqlite://:memory:"},
    }
    async with tortoise_test_context(config=test_config):
        yield
```

```python
# tests/integration/test_invoice_repo.py
import pytest
from decimal import Decimal

from apps.billing.models import Invoice, Customer


@pytest.mark.asyncio
async def test_create_invoice(db):
    customer = await Customer.create(email="x@y.z")
    invoice = await Invoice.create(
        number="INV-1",
        amount=Decimal("100"),
        customer=customer,
    )
    assert (await Invoice.get(id=invoice.id)).number == "INV-1"
```

### Postgres-backed integration (when SQLite differs from prod)

Use [testcontainers-python](https://testcontainers-python.readthedocs.io/) so CI gets a real
PG container per session:

```python
@pytest_asyncio.fixture(scope="session")
async def pg_url():
    from testcontainers.postgres import PostgresContainer
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg.get_connection_url().replace("postgresql+psycopg2", "postgres")
```

Then build `test_config` using `pg_url` and the same `tortoise_test_context` pattern.

## `pyproject.toml` test config

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

## Factories

Use `factory_boy` or hand-roll. Factories belong in `tests/factories/<entity>.py`.

```python
# tests/factories/invoice.py
from decimal import Decimal
import factory

from apps.billing.models import Invoice


class InvoiceFactory(factory.Factory):
    class Meta:
        model = Invoice

    number = factory.Sequence(lambda n: f"INV-{n:05}")
    amount = Decimal("100")
    paid = False
```

`factory_boy` is sync; for async create, use `await InvoiceFactory.build()` then `.save()`,
or wrap with `factory.use_strategy("build")`.

## What NOT to do

- Don't use `unittest.mock.patch("apps.x.models.Invoice")` — mock the **service**, not the
  ORM. If you find yourself patching Tortoise internals, your service has the wrong shape.
- Don't share DB state across tests. Each test gets a clean DB.
- Don't run `aerich upgrade` in unit/integration tests — use `generate_schemas()` via the
  test context. Migrations are tested separately in a deploy-rehearsal job.
- Don't `asyncio.run()` inside tests — use `pytest-asyncio` with `asyncio_mode = "auto"`.
