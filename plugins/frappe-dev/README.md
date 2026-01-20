# Frappe Dev Plugin

Professional Frappe Framework v15 development toolkit with multi-layer architecture patterns, DocType scaffolding, REST API v2 development, and comprehensive testing.

## Installation

```bash
claude mcp add-from-marketplace bershadsky-claude-tools/frappe-dev
```

## Overview

This plugin provides scaffolding and best practices for Frappe Framework v15 development following enterprise architecture patterns:

- **Multi-Layer Architecture** — Controller → Service → Repository pattern
- **v15 Type Annotations** — Full Python type hints with `TYPE_CHECKING`
- **Comprehensive Testing** — Unit, integration, and E2E test patterns

## Skills

### /frappe-app

Scaffold a new Frappe application with production-ready structure.

```
/frappe-app <app_name> [--module <module_name>]
```

**Examples:**
```
/frappe-app inventory_management
/frappe-app hr_extension --module Human Resources
```

**Creates:**
```
<app_name>/
├── <app_name>/
│   ├── hooks.py
│   ├── modules.txt
│   └── <module>/
│       ├── api/           # REST endpoints
│       ├── services/      # Business logic
│       ├── repositories/  # Data access
│       └── doctype/       # DocTypes
├── pyproject.toml
└── README.md
```

### /frappe-doctype

Create a DocType with controller, service layer, repository, and tests.

```
/frappe-doctype <doctype_name> [--module <module>] [--submittable] [--child]
```

**Examples:**
```
/frappe-doctype Sales Order
/frappe-doctype Invoice Item --child
/frappe-doctype Purchase Request --submittable
```

**DocType Types:**
- Standard — Regular CRUD document
- Submittable — Draft → Submitted → Cancelled workflow
- Child Table — Embedded in parent documents
- Single — Configuration/settings document

**Generated Files:**
- `<doctype>.json` — DocType definition
- `<doctype>.py` — Controller with lifecycle hooks
- `<doctype>_service.py` — Business logic layer
- `<doctype>_repository.py` — Data access layer
- `test_<doctype>.py` — Test coverage

### /frappe-api

Create secure REST API endpoints with authentication and validation.

```
/frappe-api <endpoint_name> [--doctype <doctype>] [--public]
```

**Examples:**
```
/frappe-api get_dashboard_stats
/frappe-api create_order --doctype "Sales Order"
/frappe-api webhook_handler --public
```

**Authentication Types:**
- Token — API Key + Secret
- Session — Cookie-based
- OAuth 2.0
- Public — No auth (use sparingly)

### /frappe-service

Create service layer classes for complex business logic.

```
/frappe-service <service_name> [--doctype <doctype>] [--operations <op1,op2>]
```

**Examples:**
```
/frappe-service OrderProcessing --doctype "Sales Order"
/frappe-service InventoryManagement --operations allocate,release,transfer
/frappe-service PaymentGateway
```

**Service Patterns:**
| Pattern | Use Case |
|---------|----------|
| CRUD Service | Basic DocType operations |
| Workflow Service | State transitions, approvals |
| Integration Service | External API calls |
| Orchestration Service | Multi-DocType coordination |
| Batch Service | Bulk operations |

### /frappe-test

Create comprehensive test suites with fixtures and factories.

```
/frappe-test <target> [--type <unit|integration|e2e>] [--coverage]
```

**Examples:**
```
/frappe-test SalesOrder
/frappe-test inventory_service --type unit
/frappe-test api.orders --type integration --coverage
```

**Test Structure:**
```
<app>/tests/
├── conftest.py          # Pytest fixtures
├── factories/           # Test data factories
├── unit/                # No database
├── integration/         # With database
└── e2e/                 # End-to-end
```

## Architecture Pattern

```
┌─────────────────────────────────────────────────┐
│                   Controller                     │
│         (DocType hooks, HTTP handlers)          │
└────────────────────────┬────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────┐
│                    Service                       │
│    (Business logic, validation, orchestration)  │
└────────────────────────┬────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────┐
│                   Repository                     │
│        (Database queries, data access)          │
└─────────────────────────────────────────────────┘
```

**Rules:**
1. Controllers call Services, never Repositories directly
2. Services implement business logic, never raw SQL
3. Repositories handle all database operations
4. No business logic in Controllers or Repositories

## v15 Features

### Type Annotations

All generated code includes proper type hints:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from frappe.types import DF

class SalesOrder(Document):
    if TYPE_CHECKING:
        customer: DF.Link
        total: DF.Currency
        status: DF.Literal["Draft", "Submitted", "Cancelled"]
```

### DocStatus Helper

Use v15's DocStatus helper for readable status checks:

```python
from frappe.model.docstatus import DocStatus

if self.docstatus.is_draft():
    # Draft document
elif self.docstatus.is_submitted():
    # Submitted document
elif self.docstatus.is_cancelled():
    # Cancelled document
```

### Query Builder

Use Frappe's query builder for type-safe queries:

```python
from frappe.query_builder import DocType

dt = DocType("Sales Order")
orders = (
    frappe.qb.from_(dt)
    .select(dt.name, dt.customer, dt.total)
    .where(dt.status == "Draft")
    .run()
)
```

## References

- [Frappe v15 Docs](https://docs.frappe.io/framework/v15)
- [Migration Guide to v15](https://github.com/frappe/frappe/wiki/Migrating-to-version-15)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

## License

[Unlicense](LICENSE) - Public Domain
