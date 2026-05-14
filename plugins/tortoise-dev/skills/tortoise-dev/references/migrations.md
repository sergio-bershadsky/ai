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

## Runtime integration — migration service/hook

CI-level migration runs are great for centralized deploys, but most production setups also
need migrations to run when the container boots in dev/staging or when someone runs
`helm upgrade` directly. **Detect the deployment style and propose the right shape:**

### Docker Compose

A dedicated one-shot `migrate` service that exits 0 on success:

```yaml
services:
  migrate:
    build: { context: .., dockerfile: docker/Dockerfile }
    command: ["uv", "run", "aerich", "upgrade"]
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

Use a Helm hook Job, not an init container, so migrations run **once per release** instead
of once per pod:

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
        - name: aerich-upgrade
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          command: ["uv", "run", "aerich", "upgrade"]
          envFrom:
            - secretRef: { name: {{ include "app.fullname" . }}-db }
```

Key flags:
- `backoffLimit: 0` — a failed migration aborts the release; you do **not** want retries
  silently masking a broken migration.
- `hook-delete-policy: before-hook-creation,hook-succeeded` — clean up old hook Jobs but
  keep a failed one around for debugging.
- `activeDeadlineSeconds` — prevent a runaway migration from blocking the deploy forever.

### Init-container fallback

When Helm hooks aren't available (raw kustomize, ArgoCD without sync hooks, plain
manifests):

```yaml
spec:
  template:
    spec:
      initContainers:
        - name: aerich-upgrade
          image: <same as app>
          command: ["uv", "run", "aerich", "upgrade"]
          envFrom: [{ secretRef: { name: app-db } }]
```

Trade-off: this runs on **every pod start**, including HPA scale-ups. Aerich serializes via
PG advisory locks, so concurrent runners are safe, but it's wasted work. Prefer the Job
approach when you can.

### Procfile (Heroku/Render/Fly)

```
release: uv run aerich upgrade
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

If at least one exists **and** there is no `aerich upgrade` invocation in it yet, propose
adding the appropriate hook from the patterns above. Show the user a diff before writing.

## Troubleshooting

- **"No changes detected"** — Aerich diffs against `migrations/<app>/models.py` snapshot. If
  you reverted a model but forgot to regenerate, the snapshot lies. Re-run `aerich migrate`.
- **Conflict on merge** — two devs added migrations with the same number. Renumber the later
  one and update its `dependencies = [...]`.
- **Drift from manual SQL** — never apply manual DDL. If you must, follow up with a
  no-op-on-prod migration that brings Aerich's state in sync.
