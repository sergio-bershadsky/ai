# Frappe Dev Plugin

Professional Frappe Framework v15 development toolkit with multi-layer architecture patterns.

## Overview

The `frappe-dev` plugin provides a comprehensive set of skills for building production-ready Frappe applications following enterprise best practices:

- **Multi-layer architecture** (Controller → Service → Repository)
- **Frappe v15 compatibility** with type annotations
- **REST API v2** patterns and security
- **Comprehensive testing** with factories and fixtures

## Installation

```bash
# Add marketplace
/plugin marketplace add sergio-bershadsky/ai

# Install plugin
/plugin install frappe-dev@bershadsky-claude-tools
```

## Skills

| Skill | Description | Trigger |
|-------|-------------|---------|
| [frappe-app](/frappe-dev/frappe-app) | Scaffold new Frappe application | `/frappe-app` |
| [frappe-doctype](/frappe-dev/frappe-doctype) | Create DocType with service layer | `/frappe-doctype` |
| [frappe-api](/frappe-dev/frappe-api) | Build REST API endpoints | `/frappe-api` |
| [frappe-service](/frappe-dev/frappe-service) | Design service layer classes | `/frappe-service` |
| [frappe-test](/frappe-dev/frappe-test) | Generate test suites | `/frappe-test` |

## Architecture Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                    API / Controller Layer                    │
│              (HTTP handling, routing, auth)                  │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Service Layer                           │
│         (Business logic, validation, orchestration)          │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Repository Layer                          │
│              (Data access, queries, ORM)                     │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Database                               │
│                    (MariaDB/MySQL)                           │
└─────────────────────────────────────────────────────────────┘
```

## Frappe v15 Features

This plugin leverages Frappe v15 specific features:

- **Type Annotations** — Auto-generated Python type hints for IDE support
- **API v2** — RESTful endpoints with `/api/v2/` prefix
- **Server Scripts Disabled** — Security-first approach
- **New Permission Model** — "Desk User" role separation
- **Vue 3 Support** — Modern frontend compatibility

## Quick Start

### 1. Create New App

```
/frappe-app inventory_pro --module Inventory
```

Creates:
```
inventory_pro/
├── inventory_pro/
│   ├── hooks.py
│   ├── modules.txt
│   ├── inventory/
│   │   ├── services/
│   │   │   └── base.py
│   │   ├── repositories/
│   │   │   └── base.py
│   │   └── doctype/
│   └── tests/
└── pyproject.toml
```

### 2. Create DocType

```
/frappe-doctype Stock Entry --submittable
```

Creates DocType with:
- Controller with lifecycle hooks
- Service layer for business logic
- Repository for data access
- Test file with coverage

### 3. Add API Endpoints

```
/frappe-api stock_operations --doctype "Stock Entry"
```

Creates REST API with:
- CRUD operations
- Permission checks
- Input validation
- Pagination support

### 4. Generate Tests

```
/frappe-test StockEntry --type integration
```

Creates:
- Integration tests with database
- Unit tests for pure logic
- Factory patterns for test data
- Pytest fixtures

## Resources

- [Frappe v15 Docs](https://docs.frappe.io/framework/v15)
- [Migration Guide](https://github.com/frappe/frappe/wiki/Migrating-to-version-15)
- [API Reference](https://docs.frappe.io/framework/v15/user/en/api/rest)
- [Testing Guide](https://docs.frappe.io/framework/user/en/testing)
