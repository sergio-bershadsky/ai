# Migrations — Aerich

[Aerich](https://github.com/tortoise/aerich) is the official Tortoise migration tool. Always
use it; never call `Tortoise.generate_schemas()` in anything that touches production data.

## One-time setup

```bash
uv add aerich

# Tell aerich where the config dict lives.
uv run aerich init -t config.tortoise.TORTOISE_ORM

# Generate the initial migration and apply it.
uv run aerich init-db
```

This creates:
- `pyproject.toml` `[tool.aerich]` section
- `migrations/<app>/0_*_init.py`
- `aerich` table in the DB

## Per-change workflow

```bash
# After you've changed model fields:
uv run aerich migrate --name add_invoice_due_at

# Review the generated migrations/<app>/<n>_*.py file. Always.
uv run aerich upgrade

# Roll back the last applied migration in dev:
uv run aerich downgrade
```

**Never** hand-edit a migration that's already been applied in any shared environment. Write a
new one.

## Data migrations (RunPython)

Auto-generated migrations only handle schema changes. For data backfills, write a manual
migration:

```python
# migrations/models/3_20260101_backfill_paid.py
from tortoise.migrations import RunPython
from tortoise.migrations.migration import Migration


async def backfill(apps, schema_editor):
    Invoice = apps.get_model("models", "Invoice")
    await Invoice.filter(amount=0).update(paid=True)


async def reverse(apps, schema_editor):
    Invoice = apps.get_model("models", "Invoice")
    await Invoice.filter(amount=0).update(paid=False)


class Migration(Migration):
    dependencies = [("models", "0002_initial")]
    operations = [RunPython(code=backfill, reverse_code=reverse)]
```

Rules:
- Never combine schema + data in one auto-generated migration. Split into two files.
- Always write a reverse where feasible. If genuinely irreversible, document why in a comment.
- Use `apps.get_model(...)` — don't import the model directly, because its current shape may
  differ from the shape at migration time.

## Zero-downtime patterns

| Change | Pattern |
|--------|---------|
| Add column | Migration A: add nullable. Migration B (after deploy): backfill. Migration C (next release): make NOT NULL. |
| Drop column | Stop writing it (release N). Drop in release N+1. |
| Rename column | Add new → backfill → dual-write → switch reads → drop old. **Four migrations**. |
| Drop table | Stop reading/writing first. Drop later. |
| Change type | Add new column → backfill → switch → drop old. |

Aerich's auto-detect will happily emit a `DROP COLUMN`. Read the migration before applying.

## CI integration

```yaml
# .github/workflows/deploy.yml — sketch
- name: Run migrations
  run: uv run aerich upgrade
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

Run **before** the new app version takes traffic. If a migration fails, the deploy aborts.

## Troubleshooting

- **"No changes detected"** — Aerich diffs against `migrations/<app>/models.py` snapshot. If
  you reverted a model but forgot to regenerate, the snapshot lies. Re-run `aerich migrate`.
- **Conflict on merge** — two devs added migrations with the same number. Renumber the later
  one and update its `dependencies = [...]`.
- **Drift from manual SQL** — never apply manual DDL. If you must, follow up with a
  no-op-on-prod migration that brings Aerich's state in sync.
