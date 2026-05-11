# FastAPI Integration

The official path is `tortoise.contrib.fastapi` + the `lifespan` context manager.

## Lifespan-style init (recommended)

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
    title="Billing API",
    lifespan=lifespan,
    exception_handlers=tortoise_exception_handlers(),
)
```

`tortoise_exception_handlers()` maps:
- `DoesNotExist` → 404
- `IntegrityError` → 422
- `ValidationError` → 422

You don't need to write try/except for these in routers.

## `register_tortoise` (legacy / dev only)

```python
from tortoise.contrib.fastapi import register_tortoise

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=False,            # NEVER True in prod
    add_exception_handlers=True,
)
```

Use lifespan above for new code. Keep `register_tortoise` only for legacy projects you can't
restructure yet.

## Pydantic v2 schemas

Two creators:

```python
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

from apps.billing.models import Invoice

InvoiceOut = pydantic_model_creator(Invoice, name="InvoiceOut")
InvoiceIn = pydantic_model_creator(
    Invoice,
    name="InvoiceIn",
    exclude_readonly=True,            # drop id / auto fields
)
InvoiceList = pydantic_queryset_creator(Invoice)
```

Use them in routes:

```python
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("/", response_model=InvoiceList)
async def list_invoices():
    return await InvoiceList.from_queryset(Invoice.all())


@router.get("/{invoice_id}", response_model=InvoiceOut)
async def get_invoice(invoice_id: str):
    return await InvoiceOut.from_queryset_single(Invoice.get(id=invoice_id))


@router.post("/", response_model=InvoiceOut, status_code=201)
async def create_invoice(payload: InvoiceIn):
    obj = await Invoice.create(**payload.model_dump())
    return await InvoiceOut.from_tortoise_orm(obj)
```

## Dependency-injected transactions

For endpoints that need a transactional unit-of-work:

```python
from fastapi import Depends
from tortoise.transactions import in_transaction


async def tx():
    async with in_transaction() as conn:
        yield conn


@router.post("/settle/{invoice_id}")
async def settle(invoice_id: str, conn=Depends(tx)):
    inv = await Invoice.select_for_update().using_db(conn).get(id=invoice_id)
    inv.paid = True
    await inv.save(using_db=conn)
```

Don't share transactions across HTTP requests. One request = one transaction (at most).

## Don't put DB calls in middleware

Middleware runs on every request — it's the wrong place to fetch users, log audits, or
prime caches. Use endpoint dependencies for those.

## Connection pool sizing

For PostgreSQL via asyncpg, set pool bounds in your URL or config:

```python
{
    "engine": "tortoise.backends.asyncpg",
    "credentials": {
        "host": "...",
        "port": 5432,
        "user": "...",
        "password": "...",
        "database": "...",
        "minsize": 5,
        "maxsize": 20,
        "statement_cache_size": 0,    # required when behind pgbouncer transaction-pooling
    },
}
```

Rule of thumb: `maxsize` ≤ `(postgres max_connections / number_of_app_workers) - 2`.

## Health checks

```python
@app.get("/healthz")
async def healthz():
    from tortoise import connections
    conn = connections.get("default")
    await conn.execute_query("SELECT 1")
    return {"ok": True}
```

Don't rely on `Tortoise._inited` — it's a private flag and lies during teardown.
