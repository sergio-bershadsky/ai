# frappe-test

Create comprehensive test suites for Frappe Framework v15 applications.

## Usage

```
/frappe-test <target> [--type <unit|integration|e2e>] [--coverage]
```

## Examples

```bash
# Full test suite for DocType
/frappe-test SalesOrder

# Unit tests only
/frappe-test inventory_service --type unit

# With coverage report
/frappe-test api.orders --type integration --coverage
```

## Test Structure

```
<app>/tests/
├── conftest.py           # Pytest fixtures
├── factories/            # Test data factories
│   └── <doctype>_factory.py
├── unit/                 # No database
│   └── test_<module>.py
├── integration/          # With database
│   └── test_<module>.py
└── e2e/                  # End-to-end
    └── test_workflows.py
```

## Factory Pattern

Generate test data with factories:

```python
from app.tests.factories.sales_order_factory import SalesOrderFactory

# Create with defaults
doc = SalesOrderFactory.create()

# Custom values
doc = SalesOrderFactory.create(title="Custom", status="Completed")

# Build without saving (for unit tests)
doc = SalesOrderFactory.build()

# Create multiple
docs = SalesOrderFactory.create_batch(5)

# Create submitted
doc = SalesOrderFactory.create_submitted()
```

### Factory Implementation

```python
@dataclass
class SalesOrderFactory:
    title: str = field(default_factory=lambda: f"Test {random_string(8)}")
    date: str = field(default_factory=today)
    status: str = "Draft"

    @classmethod
    def build(cls, **kwargs) -> Any:
        factory = cls(**kwargs)
        return frappe.get_doc({
            "doctype": "Sales Order",
            "title": factory.title,
            "date": factory.date,
            "status": factory.status
        })

    @classmethod
    def create(cls, **kwargs) -> Any:
        doc = cls.build(**kwargs)
        doc.insert(ignore_permissions=True)
        return doc
```

## Pytest Fixtures

```python
# conftest.py

@pytest.fixture(scope="module")
def test_user():
    """Create test user for module."""
    email = "test@example.com"
    if not frappe.db.exists("User", email):
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": "Test"
        }).insert(ignore_permissions=True)
        user.add_roles("System Manager")
    yield email


@pytest.fixture
def as_user(test_user):
    """Run test as specific user."""
    original = frappe.session.user
    frappe.set_user(test_user)
    yield test_user
    frappe.set_user(original)


@pytest.fixture
def rollback_db():
    """Rollback after test."""
    frappe.db.begin()
    yield
    frappe.db.rollback()
```

## Integration Tests

```python
class TestSalesOrderIntegration(IntegrationTestCase):

    def test_create_document(self):
        """Test document creation."""
        data = {"title": "Test", "date": today()}

        result = self.service.create(data)

        self.assertIsNotNone(result.get("name"))
        self.assertTrue(frappe.db.exists("Sales Order", result["name"]))

    def test_submit_workflow(self):
        """Test submission workflow."""
        doc = SalesOrderFactory.create()

        result = self.service.submit(doc.name)

        self.assertEqual(result["status"], "Completed")
        docstatus = frappe.db.get_value("Sales Order", doc.name, "docstatus")
        self.assertEqual(docstatus, 1)

    def test_unauthorized_access_denied(self):
        """Test permission enforcement."""
        frappe.set_user("Guest")

        with self.assertRaises(frappe.PermissionError):
            self.service.create({"title": "Test"})
```

## Unit Tests

No database access:

```python
class TestValidationUnit(UnitTestCase):

    def test_title_cannot_be_empty(self):
        """Test empty title validation."""
        invalid_titles = ["", "   ", None]

        for title in invalid_titles:
            with self.subTest(title=title):
                is_valid = bool(title and str(title).strip())
                self.assertFalse(is_valid)

    @patch("frappe.db.exists")
    def test_repository_exists_check(self, mock_exists):
        """Test with mocked database."""
        mock_exists.return_value = True

        repo = MyRepository()
        self.assertTrue(repo.exists("TEST-001"))
```

## Running Tests

```bash
# All tests
bench --site test_site run-tests --app <app>

# Specific module
bench --site test_site run-tests --module <app>.tests.integration.test_orders

# Specific test
bench --site test_site run-tests --app <app> -k "test_create"

# With verbose output
bench --site test_site run-tests --app <app> -v

# With coverage
bench --site test_site run-tests --app <app> --coverage
```

## Test Best Practices

| Practice | Description |
|----------|-------------|
| Isolation | Each test independent, use `rollback_db` |
| Factories | Never hardcode test data |
| AAA Pattern | Arrange → Act → Assert |
| Meaningful Names | `test_cannot_submit_without_items` |
| Permission Tests | Test both authorized and unauthorized |
| Edge Cases | Empty, null, large inputs |
