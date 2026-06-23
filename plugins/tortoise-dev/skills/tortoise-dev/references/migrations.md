# Migrations — built-in Tortoise CLI (never Aerich)

> **Aerich is forbidden in this codebase.** Tortoise ORM ≥ 1.1 ships a built-in migration
> system and `tortoise` CLI. The [official docs](https://tortoise.github.io/migration.html)
> call it the recommended path and label Aerich "a legacy alternative." Do **not** add
> `aerich`, an `aerich.models` app, a `[tool.aerich]` section, or any `aerich upgrade` call.
>
> **First, confirm the version.** Check `tortoise.__version__` and the latest on PyPI / the live
> migration docs (<https://tortoise.github.io/migration.html>) — the migration CLI requires ≥ 1.1,
> and command/flag details can shift between releases. If the live docs differ from this reference,
> follow the docs.

The built-in migrator auto-detects model changes, writes plain-Python migration files, and
applies/rolls them back through the `tortoise` CLI. It supports schema operations plus
`RunPython` / `RunSQL` data migrations.

## Wiring it up

Migrations are configured **per app** with a `"migrations"` package key in `TORTOISE_ORM` —
there is no separate `aerich.models` app:

```python
# config/tortoise.py
TORTOISE_ORM = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {
        "models": {
            "models": ["apps.billing.models", "apps.users.models"],
            "default_connection": "default",
            "migrations": "migrations",   # package that holds this app's migration files
        }
    },
    "use_tz": True,
    "timezone": "UTC",
}
```

The CLI resolves config from `-c/--config` (a dotted path to the `TORTOISE_ORM` dict),
`--config-file`, or a `[tool.tortoise]` section in `pyproject.toml`. This skill standardizes
on the explicit `-c config.tortoise.TORTOISE_ORM` form so commands are copy/paste safe. The
global flag comes **before** the subcommand.

## One-time setup

```bash
uv add "tortoise-orm[asyncpg]>=1.1"   # the `tortoise` CLI ships with tortoise-orm; no aerich

# Create the migrations package(s) for every configured app.
uv run tortoise -c config.tortoise.TORTOISE_ORM init

# Generate the initial migration and apply it.
uv run tortoise -c config.tortoise.TORTOISE_ORM makemigrations
uv run tortoise -c config.tortoise.TORTOISE_ORM migrate
```

This creates the `migrations/` package, a `migrations/0001_initial.py`, and the migration
history table in the DB.

## Per-change workflow

```bash
# After you've changed model fields:
uv run tortoise -c config.tortoise.TORTOISE_ORM makemigrations --name add_invoice_due_at

# Review the generated migrations/<n>_*.py file. Always.
uv run tortoise -c config.tortoise.TORTOISE_ORM migrate

# Roll back the last applied migration of an app in dev (app label = the Tortoise app key):
uv run tortoise -c config.tortoise.TORTOISE_ORM downgrade models

# Roll back to a specific migration:
uv run tortoise -c config.tortoise.TORTOISE_ORM downgrade models 0001_initial
```

`migrate` and `upgrade` are aliases — this skill uses `migrate`.

**Never** hand-edit a migration that's already been applied in any shared environment. Write a
new one.

## CLI reference

| Command | Purpose |
|---|---|
| `tortoise -c <cfg> init` | Create migrations packages for configured apps |
| `tortoise -c <cfg> makemigrations [--name X] [--empty]` | Autodetect changes, write a new migration (`--empty` for a hand-written one) |
| `tortoise -c <cfg> migrate [app] [migration]` | Apply migrations (`upgrade` is an alias) |
| `tortoise -c <cfg> downgrade <app> [migration]` | Unapply migrations for an app |
| `tortoise -c <cfg> history` | List applied migrations from the DB |
| `tortoise -c <cfg> heads` | List on-disk migration heads |
| `tortoise -c <cfg> sqlmigrate <app> <migration> [--backward]` | Print a migration's SQL without executing it |

`python3 -m tortoise -c <cfg> <subcommand>` works identically when an entrypoint isn't on PATH.

## Migration file shape

Migration files are plain Python modules exposing a `Migration` class with `dependencies` and
`operations`. Operations serialize via `deconstruct()` so they can be re-imported and replayed.

```python
# migrations/0001_initial.py
from tortoise import fields
from tortoise.migrations import CreateModel
from tortoise.migrations.migration import Migration


class Migration(Migration):
    dependencies = []
    operations = [
        CreateModel(
            name="Post",
            fields={
                "id": fields.IntField(pk=True),
                "title": fields.CharField(max_length=200),
            },
            options={},
        ),
    ]
```

## Data migrations (RunPython / RunSQL)

Auto-generated migrations only handle schema. For data backfills, write a manual migration —
generate the empty scaffold with `makemigrations --empty`, then fill in the operation.

**`RunPython`** — for logic that needs conditionals, spans multiple models, or wants ORM/type
safety. Use the **historical** models handed in via `apps.get_model(...)`; never import the
runtime model class, because its current shape may differ from the shape at migration time.

```python
# migrations/0003_backfill_paid.py
from tortoise.migrations import RunPython
from tortoise.migrations.migration import Migration


async def forwards(apps, schema_editor):
    Invoice = apps.get_model("models", "Invoice")
    await Invoice.filter(amount=0).update(paid=True)


async def backwards(apps, schema_editor):
    Invoice = apps.get_model("models", "Invoice")
    await Invoice.filter(amount=0).update(paid=False)


class Migration(Migration):
    dependencies = [("models", "0002_add_paid")]
    operations = [RunPython(code=forwards, reverse_code=backwards)]
```

**`RunSQL`** — for simple, performance-critical, or database-specific UPDATE/INSERT/DELETE.
Supports parameterized and multiple statements:

```python
from tortoise.migrations import RunSQL
from tortoise.migrations.migration import Migration


class Migration(Migration):
    dependencies = [("models", "0001_initial")]
    operations = [
        RunSQL(
            sql="UPDATE post SET title = 'Migrated' WHERE title IS NULL",
            reverse_sql="UPDATE post SET title = NULL WHERE title = 'Migrated'",
        ),
        RunSQL(
            sql=[
                ("INSERT INTO post (title) VALUES (?)", ["First"]),
                ("INSERT INTO post (title) VALUES (?)", ["Second"]),
            ],
            reverse_sql="DELETE FROM post WHERE title IN ('First', 'Second')",
        ),
    ]
```

**Choosing:** `RunPython` when logic needs conditionals/calculations, spans multiple tables,
must stay database-portable, or wants ORM features. `RunSQL` when a plain statement suffices,
performance is critical on large datasets, or a database-specific feature is needed.

Rules:
- Never combine schema + data in one auto-generated migration. Split into two files.
- Always write a reverse where feasible. To mark a step **irreversible**, set
  `reverse_code=None` (RunPython) or omit `reverse_sql` (RunSQL) — a downgrade attempt then
  raises instead of silently doing nothing. Document *why* in a comment.
- Use the historical `apps.get_model(...)`, never a direct model import.

### Atomic control

`RunPython` and `RunSQL` take `atomic` (default `True`) to control transaction wrapping. Set
`atomic=False` for SQLite `RunSQL` (avoids connection deadlocks) and for PostgreSQL
`CREATE INDEX CONCURRENTLY`, which cannot run inside a transaction.

## Zero-downtime patterns

| Change | Pattern |
|--------|---------|
| Add column | Migration A: add nullable. Migration B (after deploy): backfill. Migration C (next release): make NOT NULL. |
| Drop column | Stop writing it (release N). Drop in release N+1. |
| Rename column | Add new → backfill → dual-write → switch reads → drop old. **Four migrations**. |
| Drop table | Stop reading/writing first. Drop later. |
| Change type | Add new column → backfill → switch → drop old. |

Autodetect will happily emit a destructive `DROP COLUMN`. Read the migration (or its
`sqlmigrate` output) before applying.

## CI integration

```yaml
# .github/workflows/deploy.yml — sketch
- name: Run migrations
  run: uv run tortoise -c config.tortoise.TORTOISE_ORM migrate
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

Run **before** the new app version takes traffic. If a migration fails, the deploy aborts.

## Runtime integration — migration service/hook

CI-level migration runs cover centralized deploys, but most production setups also need
migrations to run when the container boots in dev/staging or when someone runs `helm upgrade`
directly. **Detect the deployment style and propose the right shape.** The migrate command is
always `uv run tortoise -c config.tortoise.TORTOISE_ORM migrate`.

### Docker Compose

A dedicated one-shot `migrate` service that exits 0 on success:

```yaml
services:
  migrate:
    build: { context: .., dockerfile: docker/Dockerfile }
    command: ["uv", "run", "tortoise", "-c", "config.tortoise.TORTOISE_ORM", "migrate"]
    env_file: ../.env
    depends_on:
      db: { condition: service_healthy }
    restart: "no"

  app:
    depends_on:
      migrate: { condition: service_completed_successfully }
      db:      { condition: service_healthy }
```

Why a separate service and not an entrypoint script:
- Re-running `docker compose up app` won't re-run the migration unless explicitly invoked.
- Logs are isolated — a failed migration shows up in its own container.
- `restart: "no"` prevents migrate from looping on success.

### Helm (preferred for Kubernetes)

Use a Helm hook Job, not an init container, so migrations run **once per release** instead of
once per pod:

```yaml
# templates/migrate-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "app.fullname" . }}-migrate-{{ .Release.Revision }}
  annotations:
    "helm.sh/hook": pre-install,pre-upgrade
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  backoffLimit: 0
  activeDeadlineSeconds: 600
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: tortoise-migrate
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          command: ["uv", "run", "tortoise", "-c", "config.tortoise.TORTOISE_ORM", "migrate"]
          envFrom:
            - secretRef: { name: {{ include "app.fullname" . }}-db }
```

Key flags:
- `backoffLimit: 0` — a failed migration aborts the release; you do **not** want retries
  silently masking a broken migration.
- `hook-delete-policy: before-hook-creation,hook-succeeded` — clean up old hook Jobs but keep
  a failed one around for debugging.
- `activeDeadlineSeconds` — prevent a runaway migration from blocking the deploy forever.

### Init-container fallback

When Helm hooks aren't available (raw kustomize, ArgoCD without sync hooks, plain manifests):

```yaml
spec:
  template:
    spec:
      initContainers:
        - name: tortoise-migrate
          image: <same as app>
          command: ["uv", "run", "tortoise", "-c", "config.tortoise.TORTOISE_ORM", "migrate"]
          envFrom: [{ secretRef: { name: app-db } }]
```

Trade-off: this runs on **every pod start**, including HPA scale-ups — wasted work, and
concurrent runners race. Prefer the Job approach, which runs once per release.

### Procfile (Heroku/Render/Fly)

```
release: uv run tortoise -c config.tortoise.TORTOISE_ORM migrate
web:     uv run uvicorn main:app --host 0.0.0.0 --port $PORT
```

`release` phase runs before traffic switches. Failure aborts the release.

### Detection checklist for the skill

When opening a project, look for any of:
- `docker-compose*.y*ml`, `compose.yaml`
- `Chart.yaml`, `helm/`, `charts/`, `values*.yaml`
- `kustomization.yaml`
- `Procfile`, `app.json` (Heroku), `fly.toml`, `render.yaml`
- `.github/workflows/deploy*.yml`, `.gitlab-ci.yml` with deploy stages

If at least one exists **and** there is no `tortoise ... migrate` invocation in it yet, propose
adding the appropriate hook from the patterns above. Show the user a diff before writing.

## Troubleshooting (from the official FAQ)

- **"Migrations are not found" / "App `<label>` has no migrations configured"** — the app
  config is missing a `"migrations": "<pkg>"` key, or the package doesn't exist yet. Add the
  key and run `tortoise ... init`.
- **"No module named `<app>.migrations`"** — the migrations package isn't importable on
  `PYTHONPATH`. Ensure it has an `__init__.py` and is on the path.
- **CLI shows no changes** — the models aren't imported by the configured app, or you ran with
  a different config source. Make sure the model modules are listed under the app and that you
  pass the same `-c` / `--config-file`.
- **Data migration fails to import models** — you imported a runtime model class. Use the
  historical model from `apps.get_model(...)` inside `RunPython` instead.
- **Making a migration irreversible** — set `reverse_code=None` (RunPython) or omit
  `reverse_sql` (RunSQL); a downgrade attempt then raises rather than corrupting data.
- **Merge conflict on numbers** — two devs added migrations with the same number. Renumber the
  later one and fix its `dependencies = [...]`.
