# frappe-api

Create secure REST API endpoints for Frappe Framework v15.

## Usage

```
/frappe-api <endpoint_name> [--doctype <doctype>] [--public]
```

## Examples

```bash
# CRUD API for DocType
/frappe-api orders --doctype "Sales Order"

# Custom operations
/frappe-api dashboard_stats

# Public endpoint (no auth)
/frappe-api health_check --public
```

## Generated Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `.get` | Get single document |
| GET | `.get_list` | List with pagination |
| POST | `.create` | Create document |
| PUT | `.update` | Update document |
| DELETE | `.delete` | Delete document |
| POST | `.submit` | Submit for processing |
| POST | `.cancel` | Cancel document |
| POST | `.bulk_update_status` | Bulk operations |
| GET | `.ping` | Health check (public) |

## Authentication

### Token Auth (Recommended)

```bash
curl -X GET "https://site.com/api/method/app.module.api.endpoint.get?name=DOC-001" \
     -H "Authorization: token api_key:api_secret"
```

### Session Auth

```bash
# Login first
curl -X POST "https://site.com/api/method/login" \
     -d "usr=user@example.com&pwd=password"

# Use session cookie
curl -X GET "https://site.com/api/method/app.module.api.endpoint.get?name=DOC-001" \
     --cookie "sid=..."
```

## Endpoint Pattern

```python
@frappe.whitelist()
def get(name: str) -> dict:
    """
    Get document by name.

    Args:
        name: Document name/ID

    Returns:
        Document data
    """
    _check_permission("DocType", "read")

    service = MyService()
    return {
        "success": True,
        "data": service.get(name)
    }


@frappe.whitelist(methods=["POST"])
def create(title: str, date: Optional[str] = None) -> dict:
    """Create new document."""
    _check_permission("DocType", "create")

    # Validate
    if not title or not title.strip():
        frappe.throw("Title is required", frappe.ValidationError)

    service = MyService()
    result = service.create({"title": title, "date": date})

    frappe.db.commit()

    return {
        "success": True,
        "data": result
    }
```

## Security Best Practices

### Always Check Permissions

```python
def _check_permission(doctype: str, ptype: str, doc=None):
    if not frappe.has_permission(doctype, ptype, doc=doc):
        frappe.throw("Permission denied", frappe.PermissionError)
```

### Validate Input Types (v15)

```python
# Type hints are validated automatically in v15
@frappe.whitelist()
def update(name: str, status: str) -> dict:
    # name and status are validated as strings
    pass
```

### Sanitize Input

```python
from frappe.utils import cint, cstr, flt

@frappe.whitelist()
def get_list(limit: int = 20):
    limit = min(cint(limit) or 20, 100)  # Cap at 100
```

## Public Endpoints

Use sparingly for truly public data:

```python
@frappe.whitelist(allow_guest=True)
def ping() -> dict:
    """Health check - no auth required."""
    return {
        "success": True,
        "message": "pong",
        "timestamp": frappe.utils.now()
    }
```

## Pagination Pattern

```python
@frappe.whitelist()
def get_list(
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
) -> dict:
    limit = min(cint(limit) or 20, 100)
    offset = max(cint(offset), 0)

    filters = {}
    if status:
        filters["status"] = status

    data = service.repo.get_list(
        filters=filters,
        limit=limit,
        offset=offset
    )
    total = service.repo.get_count(filters)

    return {
        "success": True,
        "data": data,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total
        }
    }
```

## API v2 (Frappe v15)

New RESTful endpoints available:

```
/api/v2/document/<doctype>/<name>
/api/v2/doctype/<doctype>
/api/v2/method/<dotted.path>
```

## Testing APIs

```python
def test_get_returns_document(self):
    from app.module.api.endpoint import get

    frappe.set_user(self.test_user.name)
    result = get(self.test_doc.name)

    self.assertTrue(result.get("success"))
    self.assertIsNotNone(result.get("data"))
```
