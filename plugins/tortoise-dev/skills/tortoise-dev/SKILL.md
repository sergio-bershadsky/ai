---
name: tortoise-dev
description: |
  Use when the user asks to "create a tortoise model", "new tortoise project", "tortoise orm",
  "async orm", "aerich migration", "fastapi tortoise", "tortoise model abstract", "tortoise base
  class", or mentions Tortoise ORM project structure, model organization, querysets, signals,
  transactions, or testing. Provides opinionated enterprise patterns: model-per-file, abstract
  Base interfaces for mocks/transitions, strict class member ordering, FastAPI lifespan,
  Aerich migrations, Pydantic v2, pytest.
---

# Tortoise ORM Enterprise Patterns

Opinionated, production-grade development patterns for [Tortoise ORM](https://tortoise.github.io/)
(async Python ORM). Apply these to every Tortoise codebase unless the project's own `CLAUDE.md`
overrides them.

## Rule Priority (read first, every time)

When advice conflicts, resolve in this order:

1. **User's project rules** (this repo's `CLAUDE.md`, explicit instructions in the conversation) — highest priority
2. **Official Tortoise ORM docs** (https://tortoise.github.io/)
3. **Context7-sourced patterns** (`/tortoise/tortoise-orm`)
4. **Other internet consensus** (projectrules.ai, blog posts)

If the user states a rule (e.g. "use UUID primary keys"), it wins over everything below.

## The Five Hard Rules (non-negotiable)

These come straight from the user's ruleset and override any pattern below. **Never break them.**

| # | Rule | Why it matters |
|---|------|----------------|
| 0 | **Models live in a `models/` subpackage of the sub-application** (never `models.py`) | Lets the package grow without refactor; mirrors Django/FastAPI conventions |
| 1 | **One file == one model** | Stable git blame, trivial review diffs, no circular-import games |
| 2 | **Every concrete model has an abstract `Base*` interface** usable as a mock base or transition model | Makes business logic testable without a DB; supports zero-downtime model rewrites |
| 3 | **`class Meta` is ALWAYS the first member** of any model class | Reader sees table/index/ordering before any field |
| 4 | **Class member order is enforced:** Meta → fields → class/private methods → public methods | Predictable scan order; reduces review friction |

> Rule 2 is the one most teams skip. Don't. See `references/models.md` for the full pattern,
> including how `Base*` doubles as a Protocol-like interface for service-layer mocking.

## When to Use

- Bootstrapping a new Tortoise ORM project (FastAPI, Starlette, Sanic, Quart, AIOHTTP, Nexios).
- Adding a model, refactoring an existing single-file `models.py`.
- Wiring Aerich migrations into CI.
- Writing tests that need DB isolation without slow integration fixtures.
- Reviewing a PR that touches Tortoise models.

## Project Layout

```
project/
├── pyproject.toml                # uv + dependency groups
├── uv.lock
├── docker/                       # all docker artifacts live here
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── entrypoint.sh
├── config/
│   ├── __init__.py
│   ├── settings.py               # Dynaconf or pydantic-settings
│   └── tortoise.py               # TORTOISE_ORM dict (aerich reads this)
├── apps/
│   └── billing/                  # one sub-application
│       ├── __init__.py
│       ├── models/               # SUBPACKAGE — Rule 0
│       │   ├── __init__.py       # re-exports
│       │   ├── base.py           # cross-cutting abstract base (BaseModel) — never `_base.py`
│       │   ├── invoice.py        # one file == one model — Rule 1
│       │   │                      # contains BaseInvoice + Invoice — Rule 2
│       │   └── payment.py
│       ├── schemas/              # Pydantic v2 in/out DTOs
│       ├── services/             # business logic (depends on Base* interfaces)
│       ├── repositories/         # optional: data-access abstraction
│       └── routers/              # FastAPI / framework routes
├── migrations/                   # aerich-managed
└── tests/
```

### Pin versions

`pyproject.toml`:

```toml
[project]
name = "myproject"
requires-python = ">=3.12"
dependencies = [
    "tortoise-orm[asyncpg]>=0.21",     # use asyncpg for postgres
    "aerich>=0.8",                      # migrations
    "fastapi>=0.115",
    "pydantic>=2.7",
]

[dependency-groups]
dev = ["ruff>=0.5", "mypy>=1.10", "ipython"]
test = ["pytest>=8", "pytest-asyncio>=0.23", "asynctest", "freezegun"]

[tool.aerich]
tortoise_orm = "config.tortoise.TORTOISE_ORM"
location = "./migrations"
src_folder = "./."
```

## Models — Rules 0–4 in Practice

The full pattern lives in `references/models.md`. Here is the shape every model file
**must** take:

```python
# apps/billing/models/invoice.py
"""Invoice model and its abstract interface."""
from __future__ import annotations

from decimal import Decimal
from typing import ClassVar

from tortoise import fields
from tortoise.models import Model

from .base import BaseModel


# Rule 2: abstract interface — used as Mock base AND as a transition model
# during schema rewrites. Service-layer code accepts BaseInvoice, not Invoice.
class BaseInvoice(BaseModel):
    # Rule 3: class Meta ALWAYS first
    class Meta:
        abstract = True

    # Rule 4 step 2: fields
    number: str = fields.CharField(max_length=32, unique=True)
    amount: Decimal = fields.DecimalField(max_digits=12, decimal_places=2)
    paid: bool = fields.BooleanField(default=False)

    # Rule 4 step 3: class / private methods (alphabetical)
    def __str__(self) -> str:
        return self.number

    def _format_amount(self) -> str:
        return f"{self.amount:.2f}"

    # Rule 4 step 4: public methods (alphabetical)
    def is_overdue(self, today) -> bool:  # pure, mockable
        raise NotImplementedError


class Invoice(BaseInvoice):
    class Meta:
        table = "invoice"
        table_description = "Customer invoices"
        ordering = ["-created_at"]
        indexes = (("paid", "created_at"),)

    customer: fields.ForeignKeyRelation["Customer"] = fields.ForeignKeyField(
        "models.Customer",
        related_name="invoices",
        on_delete=fields.OnDelete.RESTRICT,
    )
    due_at = fields.DatetimeField(null=True)

    def __repr__(self) -> str:
        return f"<Invoice {self.number} {self._format_amount()}>"

    def is_overdue(self, today) -> bool:
        return self.due_at is not None and not self.paid and self.due_at < today
```

`models/__init__.py` re-exports both the concrete model and its base so service code can import
the base without reaching into module internals:

```python
from .base import BaseModel
from .invoice import BaseInvoice, Invoice
from .payment import BasePayment, Payment

__all__ = ["BaseModel", "BaseInvoice", "Invoice", "BasePayment", "Payment"]
```

### Why `Base*` matters (Rule 2 deep dive)

`Base*` classes are abstract Tortoise models (`Meta.abstract = True`). They have **no table**,
so they can be:

- **Subclassed by mocks** in tests — give the mock a `Meta` and a hand-rolled `save()` stub.
- **Subclassed by a Transition model** during a schema rewrite — point services at
  `Invoice2` (which inherits `BaseInvoice`) while the old `Invoice` is still around.
- **Used as type hints** for services: `async def settle(inv: BaseInvoice) -> None`. The
  service code doesn't care which concrete subclass it gets.

A `Base*` declares fields, signatures, and pure helpers. The concrete model adds relations,
table config, and overrides behavior that requires the DB.

## Cross-Cutting Base (`base.py`)

```python
# apps/billing/models/base.py
from tortoise import fields
from tortoise.models import Model


class BaseModel(Model):
    class Meta:
        abstract = True

    id = fields.UUIDField(primary_key=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
```

> Don't put soft-delete on the cross-cutting base unless every model in the project actually
> needs it. Prefer a separate `BaseSoftDelete` mixin you opt into per model.

## Configuration

Keep the Tortoise config in one place (Aerich reads it; FastAPI lifespan reads it):

```python
# config/tortoise.py
from config.settings import settings

TORTOISE_ORM = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {
        "models": {
            "models": [
                "apps.billing.models",
                "apps.users.models",
                "aerich.models",         # required for migrations
            ],
            "default_connection": "default",
        }
    },
    "use_tz": True,
    "timezone": "UTC",
}
```

**Never** call `Tortoise.generate_schemas()` in production code paths — it bypasses migrations.
Use it only in test fixtures and SQLite-memory examples.

## FastAPI Integration (lifespan-style only)

```python
# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from tortoise import Tortoise
from tortoise.contrib.fastapi import tortoise_exception_handlers

from config.tortoise import TORTOISE_ORM


@asynccontextmanager
async def lifespan(app: FastAPI):
    await Tortoise.init(config=TORTOISE_ORM)
    yield
    await Tortoise.close_connections()


app = FastAPI(
    lifespan=lifespan,
    exception_handlers=tortoise_exception_handlers(),
)
```

Avoid `register_tortoise(generate_schemas=True)` outside of dev — it'll happily skip your
migrations.

## Querying — fast path summary

Full patterns in `references/queries.md`. The high-leverage rules:

- **Always `prefetch_related` / `select_related`** for relations you'll touch — N+1 is the
  default failure mode.
- **`bulk_create` / `bulk_update`** for >5 rows; never loop `await .save()`.
- **Use `.only()` / `.values()`** when you don't need the full instance.
- **Filter with `Q` and `F`**; do not concatenate raw SQL into `.raw()`.
- **`exists()` / `count()`** before fetching full result sets just to check.

```python
# Good
invoices = await Invoice.filter(paid=False).select_related("customer").prefetch_related("payments")

# Bad — loads everything, N+1 on customer
for inv in await Invoice.all():
    print(inv.customer.name)  # silent extra query each iter (and will fail — relation not awaited)
```

## Transactions

```python
from tortoise.transactions import atomic, in_transaction

@atomic()
async def settle_invoice(invoice_id: str) -> None:
    inv = await Invoice.select_for_update().get(id=invoice_id)
    inv.paid = True
    await inv.save(update_fields=["paid", "updated_at"])
    await Payment.create(invoice=inv, amount=inv.amount)
```

- Use `@atomic()` for whole functions, `async with in_transaction()` for inline blocks.
- **Do not** nest transactions inside `asyncio.gather` — connections are stateful and
  sequential.
- For row-level locking, use `.select_for_update()`.

## Signals (use sparingly)

Signals are great for audit logs and cache invalidation; **don't** put business rules in them
— they're invisible from a model file.

```python
from tortoise.signals import post_save

@post_save(Invoice)
async def _invoice_audit(sender, instance, created, using_db, update_fields):
    await AuditLog.create(entity="invoice", entity_id=instance.id, created=created)
```

## Migrations (Aerich)

```bash
# one-time
uv run aerich init -t config.tortoise.TORTOISE_ORM
uv run aerich init-db

# per change
uv run aerich migrate --name add_invoice_due_at
uv run aerich upgrade
```

- Commit migrations. Review them like code.
- Use `RunPython` for data migrations; never edit schema and data in the same auto-generated migration.
- In CI: `aerich upgrade` runs before the app boots.

Full migration patterns: `references/migrations.md`.

## Testing

Use the modern `tortoise_test_context()` pattern (Tortoise 1.0+), **not** the legacy
`TestCase` / `initializer`. Full setup in `references/testing.md`.

- Unit tests for service-layer logic: target `BaseInvoice` (the abstract interface), no DB needed.
- Integration tests: ephemeral SQLite-memory + `generate_schemas` in a fixture, or testcontainers postgres.

## Anti-patterns (catch these in review)

| Anti-pattern | Why it's bad | Fix |
|---|---|---|
| `models.py` as a single file | Violates Rule 0/1 | Convert to `models/` subpackage |
| Concrete model with no `Base*` | Violates Rule 2; untestable in unit tests | Extract abstract interface |
| `class Meta` not first | Violates Rule 3 | Move it up |
| `Tortoise.init` per request | Connection storm | Init once in lifespan |
| `generate_schemas()` in prod | Bypasses migrations | Use Aerich |
| Raw f-string SQL | SQL injection | Use ORM / parameterized `.raw()` |
| `for x in qs: await x.related` | N+1 | `prefetch_related` / `select_related` |
| Forgetting `await` | Coroutine warnings, silent no-ops | Lint with ruff `ASYNC` rules |
| Catching bare `Exception` | Masks `DoesNotExist`, `IntegrityError` | Catch specific Tortoise exceptions |
| Mutating model in signal handlers | Hidden side effects | Move to explicit service methods |
| Soft delete on every model | Bloats schema | Opt-in via `BaseSoftDelete` mixin |

## Procedure for Creating a New Model

1. **Identify the sub-app.** If it doesn't exist, create `apps/<name>/{models,schemas,services,routers}/` with `__init__.py` in each.
2. **Create `apps/<name>/models/<entity>.py`.**
3. **Define `Base<Entity>`** first — abstract, declares fields + pure helpers. `Meta.abstract = True`. `class Meta` is the first member.
4. **Define `<Entity>`** — inherits `Base<Entity>`, adds relations + concrete `Meta` (table, indexes, ordering).
5. **Order members:** Meta → fields → `__str__`/`__repr__`/private → public methods.
6. **Re-export** `Base<Entity>` and `<Entity>` from `models/__init__.py`.
7. **Register** the models module in `config/tortoise.py` if it's a new app.
8. **`aerich migrate --name add_<entity>`** then `aerich upgrade`.
9. **Add tests** against `Base<Entity>` for pure logic; integration test for the concrete model.

## Reference Files

| File | Topic |
|------|-------|
| `references/models.md` | Field types, relations, inheritance, abstract bases, constraints, indexes |
| `references/queries.md` | QuerySet API, prefetch, F/Q expressions, bulk ops, annotate/aggregate, raw SQL |
| `references/migrations.md` | Aerich setup, data migrations, downgrade strategy, CI integration |
| `references/testing.md` | pytest + tortoise_test_context, fixtures, mocking via Base* |
| `references/fastapi.md` | Lifespan, exception handlers, Pydantic creators, dependency-injected sessions |

## File-Naming Convention

**Never use leading-underscore filenames** (`_base.py`, `_utils.py`, `_helpers.py`). Python's
underscore-prefix convention applies to *symbols* (functions, attributes), not to modules.
A module is public infrastructure — if it's not meant to be imported, it shouldn't exist.

Use plain names: `base.py`, `utils.py`, `helpers.py`. Mark intra-module symbols private with
a leading underscore on the symbol itself (`_internal_helper`), and curate the public
surface with `__all__` in `__init__.py`.

## Rules Recap

1. **User project rules win.** Read `CLAUDE.md` before applying any pattern here.
2. **Rules 0–4 are non-negotiable.** No exceptions, no shortcuts.
3. **No private filenames.** `base.py`, never `_base.py`. Privacy is for symbols, not modules.
4. **Models are testable through their `Base*` interface.** If you can't unit-test it without a DB, the abstraction is wrong.
5. **Migrations are source code.** Commit, review, never hand-edit applied ones.
6. **Async-first.** Every DB call is `await`-ed; never mix sync sessions.
