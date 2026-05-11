# tortoise-dev

Enterprise-grade development toolkit for [Tortoise ORM](https://tortoise.github.io/) — the async Python ORM.

## What it gives you

Opinionated, production-ready patterns enforced on every model you touch:

- **Models live in a subpackage of their sub-app** — never a single `models.py`.
- **One file == one model** — no exceptions.
- **Every concrete model has an abstract `Base*` interface** — usable as a mock base or a transition shim during refactors.
- **Strict class member order** — `class Meta` first, then fields, then class/private methods, then public methods.
- **Aerich** for migrations, **Pydantic v2** for serialization, **pytest + tortoise_test_context** for tests, **FastAPI lifespan** for app wiring.

## Skill

| Skill | Purpose |
|-------|---------|
| `tortoise-dev` | Project structure, models, queries, transactions, signals, migrations, FastAPI integration, testing |

Reference files for deep dives live in `skills/tortoise-dev/references/`.

## Priority of rules

Skills follow this priority when guidance conflicts:

1. **User's project rules** (CLAUDE.md / explicit instructions) — highest
2. **Official Tortoise ORM docs**
3. **Context7-sourced patterns**
4. **Other internet best-practice consensus**
