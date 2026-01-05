# frappe-app

Scaffold a new Frappe Framework v15 application with multi-layer architecture.

## Usage

```
/frappe-app <app_name> [--module <module_name>]
```

## Examples

```bash
# Basic app
/frappe-app inventory_management

# App with custom module
/frappe-app hr_extension --module "Human Resources"
```

## Generated Structure

```
<app_name>/
├── <app_name>/
│   ├── __init__.py
│   ├── hooks.py                    # App hooks and integrations
│   ├── modules.txt                 # Module definitions
│   ├── patches.txt                 # Database migrations
│   ├── <module_name>/              # Primary module
│   │   ├── doctype/                # DocType definitions
│   │   ├── api/                    # REST API endpoints
│   │   ├── services/               # Business logic layer
│   │   │   └── base.py
│   │   ├── repositories/           # Data access layer
│   │   │   └── base.py
│   │   └── report/                 # Custom reports
│   ├── public/                     # Static assets
│   ├── templates/                  # Jinja templates
│   ├── www/                        # Portal pages
│   └── tests/
│       └── test_utils.py
├── pyproject.toml                  # Python package config
├── README.md
└── license.txt
```

## Features

### Multi-Layer Architecture

The generated app follows the Controller → Service → Repository pattern:

- **Controllers** (doctype/) — Handle HTTP, call services
- **Services** (services/) — Business logic, validation
- **Repositories** (repositories/) — Database queries

### Base Classes

**BaseService** — Common service functionality:
```python
class BaseService:
    def check_permission(self, doctype, ptype, doc=None, throw=True)
    def validate_mandatory(self, data, fields)
    def log_activity(self, doctype, docname, action, details=None)
```

**BaseRepository** — Data access patterns:
```python
class BaseRepository:
    def get(self, name, for_update=False)
    def get_or_throw(self, name, for_update=False)
    def exists(self, name)
    def get_list(self, filters, fields, order_by, limit, offset)
    def create(self, data)
    def update(self, name, data)
    def delete(self, name)
```

### v15 Compatibility

- Type annotations enabled in hooks.py
- pyproject.toml (no setup.py)
- Python 3.10+ required

## After Creation

```bash
# Install the app
bench get-app /path/to/<app_name>
bench --site <site> install-app <app_name>

# Run tests
bench --site <site> run-tests --app <app_name>
```
