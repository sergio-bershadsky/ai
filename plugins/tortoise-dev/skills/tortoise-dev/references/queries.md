# Queries — QuerySet Patterns

Tortoise QuerySets are lazy and chainable, evaluated on `await`. Keep queries in
repository/service modules — not in routers.

## Basics

```python
# Single object
inv = await Invoice.get(id=invoice_id)               # raises DoesNotExist
inv = await Invoice.get_or_none(id=invoice_id)       # returns None

# Filtering
qs = Invoice.filter(paid=False, amount__gt=Decimal("100"))
qs = Invoice.filter(customer__email__iexact="x@y.z") # join via __ navigation

# Listing
rows = await qs                                       # awaitable evaluates
rows = await qs.limit(50).offset(100)                 # paginate
exists = await qs.exists()                            # SELECT 1 ... LIMIT 1
count = await qs.count()
first = await qs.first()
```

## Avoid N+1: `select_related` / `prefetch_related`

- `select_related("fk_field")` → SQL JOIN. Use for forward FK / O2O.
- `prefetch_related("reverse_or_m2m")` → second query, batched. Use for reverse FK / M2M.

```python
invoices = (
    await Invoice
    .filter(paid=False)
    .select_related("customer")          # JOIN customer
    .prefetch_related("payments")        # extra batched SELECT
)
for inv in invoices:
    inv.customer.email                   # no extra query
    [p.amount for p in inv.payments]     # no extra query
```

You can navigate into prefetched relations:

```python
.prefetch_related("payments__processor")
```

## Projections — `only` / `values` / `values_list`

```python
# Full model instances, partial columns:
await Invoice.filter(paid=False).only("id", "number")

# Plain dicts:
await Invoice.filter(paid=False).values("id", "number", "customer__email")

# Tuples:
await Invoice.filter(paid=False).values_list("id", "amount", flat=False)
```

Use `values` when you'll serialize directly and don't need model methods.

## Bulk operations

```python
# Insert
await Invoice.bulk_create([
    Invoice(number=n, amount=a, customer_id=c) for n, a, c in rows
], batch_size=500)

# Update
await Invoice.bulk_update(
    invoices,
    fields=["paid", "updated_at"],
    batch_size=500,
)

# Delete
await Invoice.filter(paid=True, created_at__lt=cutoff).delete()
```

Never `for x in items: await x.save()` for batches.

## `get_or_create` / `update_or_create`

```python
inv, created = await Invoice.get_or_create(
    number=number,
    defaults={"amount": amount, "customer": customer},
)
inv, created = await Invoice.update_or_create(
    number=number,
    defaults={"amount": amount, "paid": False},
)
```

Both run inside an implicit transaction. Combine with `select_for_update` if you need
serialization.

## Expressions — `F`, `Q`, `Subquery`, `RawSQL`, `Case/When`

```python
from tortoise.expressions import F, Q, Subquery, Case, When

# F — column references in updates / filters
await Invoice.filter(paid=False).update(amount=F("amount") * Decimal("1.1"))

# Q — boolean composition
await Invoice.filter(Q(paid=False) | Q(amount__gt=1000)).filter(~Q(customer__banned=True))

# Subquery
recent = Invoice.filter(customer_id=OuterRef("id")).order_by("-created_at").values("id")[:1]
await Customer.annotate(latest_invoice_id=Subquery(recent))

# Case/When
await Invoice.annotate(
    tier=Case(
        When(amount__gte=1000, then="gold"),
        When(amount__gte=100, then="silver"),
        default="bronze",
    )
)
```

## Aggregation / Annotation

```python
from tortoise.functions import Count, Sum, Avg, Max, Min, Coalesce, Lower, Trim

await Customer.annotate(invoice_count=Count("invoices")).filter(invoice_count__gte=5)
await Invoice.annotate(total=Sum("amount")).group_by("customer_id").values("customer_id", "total")
```

## Ordering, pagination

```python
qs.order_by("-created_at", "number")
qs.limit(20).offset(40)                  # keyset pagination is better for big tables
```

For large datasets prefer **keyset** (cursor) pagination: `filter(created_at__lt=cursor).order_by("-created_at").limit(N)`.

## Raw SQL (escape hatch)

```python
# Parameterized — safe
rows = await Invoice.raw("SELECT * FROM invoice WHERE amount > $1", [100])

# Free-form SQL via the connection
from tortoise import connections
conn = connections.get("default")
rows = await conn.execute_query_dict("SELECT ... WHERE x = $1", [value])
```

Never interpolate user input with f-strings into SQL. Use parameter placeholders.

## Locking

```python
inv = await Invoice.select_for_update().get(id=invoice_id)        # row lock
inv = await Invoice.select_for_update(skip_locked=True).filter(...)  # skip locked rows
```

Must be inside a transaction.

## Common pitfalls

- `await Model.all()` loads the **entire** table. Add `.filter()` / `.limit()`.
- `.first()` does not raise — always check for `None`.
- `await qs` and `await qs.all()` are the same — pick one style and stick.
- Awaiting a queryset twice runs the query twice. Cache the awaited list.
- `prefetch_related` returns lists, not querysets — chain filters before, not after.
- Forgetting to `await` a relation: `inv.customer` is `None` unless you used
  `select_related` or `await inv.customer`. The Pyright/mypy plugins help here.
