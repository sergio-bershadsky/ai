# frappe-doctype

Create a Frappe v15 DocType with controller, service layer, repository, and tests.

## Usage

```
/frappe-doctype <doctype_name> [--module <module>] [--submittable] [--child]
```

## Examples

```bash
# Standard DocType
/frappe-doctype Sales Order

# Submittable DocType (Draft → Submitted → Cancelled)
/frappe-doctype Purchase Request --submittable

# Child Table DocType
/frappe-doctype Invoice Item --child
```

## Generated Files

```
<module>/doctype/<doctype_folder>/
├── <doctype_name>.json       # DocType definition
├── <doctype_name>.py         # Controller with hooks
├── <doctype_name>.js         # Client-side script
└── test_<doctype_name>.py    # Test cases

<module>/services/
└── <doctype_name>_service.py # Business logic

<module>/repositories/
└── <doctype_name>_repository.py # Data access
```

## Controller Features

### v15 Type Annotations

```python
class SalesOrder(Document):
    if TYPE_CHECKING:
        from frappe.types import DF
        title: DF.Data
        date: DF.Date
        status: DF.Literal["Draft", "Pending", "Completed"]
```

### Lifecycle Hooks

| Hook | Trigger | Use Case |
|------|---------|----------|
| `before_validate` | Before validation | Set defaults |
| `validate` | Before save | Business rules |
| `before_save` | Before DB write | Final modifications |
| `after_insert` | After new doc | Notifications |
| `on_submit` | After submission | Create linked records |
| `on_cancel` | After cancellation | Reverse effects |

### Controller Pattern

```python
class SalesOrder(Document):
    def validate(self):
        self._validate_business_rules()

    def on_submit(self):
        self._process_submission()

    # Private methods for logic
    def _validate_business_rules(self):
        if not self.title:
            frappe.throw("Title is required")
```

## Service Layer

Business logic separated from controller:

```python
class SalesOrderService(BaseService):
    def __init__(self):
        self.repo = SalesOrderRepository()

    def create(self, data: dict) -> dict:
        self.check_permission("Sales Order", "create")
        self.validate_mandatory(data, ["title", "date"])
        doc = self.repo.create(data)
        return doc.get_summary()

    def submit(self, name: str) -> dict:
        doc = self.repo.get_or_throw(name)
        self._validate_submission(doc)
        doc.submit()
        return doc.get_summary()
```

## Repository Layer

Clean data access:

```python
class SalesOrderRepository(BaseRepository):
    doctype = "Sales Order"

    def get_by_status(self, status: str) -> list[dict]:
        return self.get_list(filters={"status": status})

    def get_recent(self, days: int = 7) -> list[dict]:
        from_date = add_days(today(), -days)
        return self.get_list(filters={"creation": [">=", from_date]})
```

## DocType Types

| Type | `is_submittable` | `istable` | Use Case |
|------|------------------|-----------|----------|
| Standard | 0 | 0 | Regular CRUD |
| Submittable | 1 | 0 | Workflow documents |
| Child Table | 0 | 1 | Embedded items |
| Single | — | — | Configuration |

## After Creation

```bash
# Create database table
bench --site <site> migrate

# Run tests
bench --site <site> run-tests --doctype "<DocType Name>"
```
