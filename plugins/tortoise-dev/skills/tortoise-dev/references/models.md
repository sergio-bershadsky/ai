# Models — Detailed Patterns

Deep dive into Tortoise ORM model definition under the project's five hard rules.

## Field Reference (the ones you actually use)

| Field | When | Notes |
|-------|------|-------|
| `IntField` | autoinc PK only when you have no UUID requirement | `primary_key=True` |
| `BigIntField` | high-write tables | |
| `UUIDField` | **default PK choice** | `primary_key=True`; no DB extension needed on PG |
| `CharField(max_length=...)` | bounded strings | always set `max_length` |
| `TextField` | unbounded text | indexable on PG only with expression index |
| `BooleanField` | | |
| `DatetimeField` | timestamps | `auto_now_add=True` / `auto_now=True` |
| `DateField` / `TimeField` | | |
| `DecimalField(max_digits=, decimal_places=)` | **money** — never use `FloatField` for currency | |
| `FloatField` | scientific only | |
| `JSONField` | semi-structured payloads | indexable as JSONB on PG |
| `BinaryField` | blobs (avoid; use object storage) | |
| `IntEnumField(MyEnum)` / `CharEnumField(MyEnum)` | typed enums | |
| `ForeignKeyField("models.Other", on_delete=...)` | many-to-one | always specify `on_delete` and `related_name` |
| `OneToOneField("models.Other", on_delete=...)` | one-to-one | |
| `ManyToManyField("models.Other", through="t")` | M2M | name the through table explicitly |

Always type-annotate the field. The annotation helps mypy and serves as a self-documenting
contract for the abstract base:

```python
amount: Decimal = fields.DecimalField(max_digits=12, decimal_places=2)
```

For relations, use the relation type helpers — they cooperate with mypy and IDEs:

```python
customer: fields.ForeignKeyRelation["Customer"] = fields.ForeignKeyField(...)
invoices: fields.ReverseRelation["Invoice"]                          # declared, not assigned
participants: fields.ManyToManyRelation["Team"] = fields.ManyToManyField(...)
```

## Meta options worth knowing

| Option | Use |
|--------|-----|
| `abstract = True` | required on every `Base*` class |
| `table = "snake_case"` | always set; do not rely on auto-naming |
| `table_description = "..."` | becomes a SQL `COMMENT` — free documentation |
| `ordering = ["-created_at"]` | default sort; Pydantic creator respects it |
| `indexes = (("col_a", "col_b"),)` | compound non-unique indexes |
| `unique_together = (("col_a", "col_b"),)` | compound unique |
| `constraints = [UniqueConstraint(...), CheckConstraint(...)]` | named constraints — survive migrations cleanly |
| `manager = CustomManager()` | override default manager |
| `schema = "billing"` | PG schema namespacing |

```python
from tortoise.migrations.constraints import CheckConstraint, UniqueConstraint

class Meta:
    table = "invoice"
    table_description = "Customer invoices issued by the billing app"
    ordering = ["-created_at"]
    indexes = (("paid", "created_at"),)
    constraints = [
        UniqueConstraint(fields=("customer_id", "number"), name="uq_invoice_customer_number"),
        CheckConstraint(check="amount >= 0", name="ck_invoice_amount_nonneg"),
    ]
```

## The Base/Concrete Pair (Rule 2)

Every concrete model has exactly one direct abstract parent named `Base<Name>`. The pair lives
in the same file.

```python
# apps/users/models/user.py
from __future__ import annotations

from tortoise import fields

from .base import BaseModel


class BaseUser(BaseModel):
    """Abstract interface for users.

    Used as:
    - Mock base in unit tests (subclass + stub methods, no DB).
    - Transition model during schema rewrites.
    - Type hint for service-layer functions.
    """

    class Meta:
        abstract = True

    email: str = fields.CharField(max_length=320, unique=True)
    is_active: bool = fields.BooleanField(default=True)

    def __str__(self) -> str:
        return self.email

    def _normalize_email(self) -> str:
        return self.email.strip().lower()

    def display_name(self) -> str:
        return self._normalize_email().split("@", 1)[0]


class User(BaseUser):
    class Meta:
        table = "user"
        ordering = ["-created_at"]

    # relations go on the concrete model — they reference other concrete models
    profile: fields.OneToOneRelation["Profile"]

    def __repr__(self) -> str:
        return f"<User {self.email}>"
```

### Using `BaseUser` for mocks (Rule 2 in action)

```python
# tests/test_user_service.py
from apps.users.models import BaseUser

class FakeUser(BaseUser):
    class Meta:
        abstract = True   # never hits a DB

    # override anything that would touch the DB
    async def save(self, *a, **kw): pass

def test_display_name_strips_and_lowers():
    u = FakeUser(email="  Foo@Bar.COM  ")
    assert u.display_name() == "foo"
```

No `Tortoise.init`, no SQLite, no fixtures. Pure logic.

### Using `BaseUser` for a transition model

When you need to rewrite `User` (new columns, dropped columns) without downtime:

```python
# apps/users/models/user_v2.py
class UserV2(BaseUser):
    class Meta:
        table = "user_v2"

    # new shape, new relations
```

Services that accept `BaseUser` keep working on both during dual-write.

## Inheritance Rules

- A concrete model inherits **exactly one** `Base*` (its own).
- Cross-cutting mixins (e.g. `BaseModel` with `id`, `created_at`, `updated_at`) are inherited
  by the `Base*`, **not** by the concrete model.
- Don't deep-nest — two levels of inheritance is the practical limit.

```
BaseModel (abstract, cross-cutting)
  └─ BaseInvoice (abstract, per-entity)
       └─ Invoice (concrete)
```

## Class Member Order (Rule 4 — full version)

```python
class Foo(BaseFoo):
    # 1. class Meta — ALWAYS first
    class Meta:
        ...

    # 2. Fields (definition order matches business importance, not alphabetical)
    name = fields.CharField(max_length=255)
    score = fields.IntField(default=0)

    # 3. Relations (separated from fields for readability)
    owner: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField(...)

    # 4. Custom manager (if any)
    objects = MyManager()

    # 5. Class / private / dunder methods (alphabetical within group)
    @classmethod
    def from_payload(cls, data: dict) -> "Foo": ...

    def __repr__(self) -> str: ...

    def __str__(self) -> str: ...

    def _internal_helper(self) -> int: ...

    # 6. Public methods (alphabetical)
    def activate(self) -> None: ...

    def archive(self) -> None: ...
```

> **Properties** (`@property`) count as public methods for ordering purposes; place them
> alphabetically among the public methods.

## Custom Managers

```python
from tortoise.manager import Manager

class ActiveManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class User(BaseUser):
    class Meta:
        table = "user"
        manager = ActiveManager()
```

Define the manager in `apps/<app>/managers/<entity>.py` and import it. Don't inline managers
in the model file.

## What NOT to put on the model

- HTTP serializers → use Pydantic creators in `schemas/`.
- Business workflows → put in `services/`.
- DB query helpers spanning multiple models → put in `repositories/`.

The model owns: shape, constraints, lifecycle hooks (signals are external but coupled), and
**pure** instance helpers (no I/O).
