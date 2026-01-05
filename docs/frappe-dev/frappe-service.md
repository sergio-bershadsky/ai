# frappe-service

Design and implement service layer classes with proper business logic separation.

## Usage

```
/frappe-service <service_name> [--doctype <doctype>] [--operations <op1,op2>]
```

## Examples

```bash
# Basic CRUD service
/frappe-service OrderProcessing --doctype "Sales Order"

# Custom operations
/frappe-service InventoryManagement --operations allocate,release,transfer

# Integration service
/frappe-service PaymentGateway
```

## Service Patterns

| Pattern | Use Case | Example |
|---------|----------|---------|
| CRUD | Basic operations | `CustomerService` |
| Workflow | State transitions | `ApprovalService` |
| Integration | External APIs | `PaymentGatewayService` |
| Orchestration | Multi-DocType | `OrderFulfillmentService` |
| Batch | Bulk operations | `BulkImportService` |

## Architecture

```
┌─────────────────────┐
│   Controller/API    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│      Service        │  ← Business Logic
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    Repository       │  ← Data Access
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│     Database        │
└─────────────────────┘
```

## Service Implementation

```python
class OrderProcessingService(BaseService):
    """Service for order processing business logic."""

    def __init__(self, user: Optional[str] = None):
        super().__init__(user)
        self.repo = SalesOrderRepository()

    @require_permission("Sales Order", "create")
    @with_transaction
    @log_operation("create_order")
    def create(self, data: dict) -> dict:
        # 1. Validate
        self._validate_create_data(data)

        # 2. Apply business rules
        data = self._apply_defaults(data)

        # 3. Create via repository
        doc = self.repo.create(data)

        # 4. Post-creation actions
        self._on_create(doc)

        return doc.get_summary()
```

## Decorators

### Permission Check

```python
@require_permission("Sales Order", "write")
def update(self, name: str, data: dict):
    # Only executes if user has write permission
    pass
```

### Transaction Management

```python
@with_transaction
def bulk_update(self, names: list, status: str):
    # Auto-commit on success, rollback on error
    for name in names:
        self.update(name, {"status": status})
```

### Operation Logging

```python
@log_operation("process_payment")
def process_payment(self, order_id: str):
    # Logs start, completion, and errors
    pass
```

## Complex Operations

### Workflow Processing

```python
def process_workflow(self, name: str, action: str, comment: str = None):
    doc = self.repo.get_or_throw(name, for_update=True)

    # Validate action
    allowed = self._get_allowed_workflow_actions(doc)
    if action not in allowed:
        frappe.throw(f"Action '{action}' not allowed")

    # Apply workflow
    from frappe.model.workflow import apply_workflow
    apply_workflow(doc, action)

    if comment:
        doc.add_comment("Workflow", f"{action}: {comment}")

    return doc.get_summary()
```

### Bulk Operations

```python
def bulk_operation(self, names: list, operation: str, **kwargs):
    results = {"success": [], "failed": []}

    for name in names:
        try:
            if operation == "submit":
                self.submit(name)
            elif operation == "cancel":
                self.cancel(name, kwargs.get("reason"))

            results["success"].append(name)
        except Exception as e:
            results["failed"].append({"name": name, "error": str(e)})

    return results
```

## Integration Service

For external API integrations:

```python
class PaymentGatewayService:
    def __init__(self):
        self.api_key = frappe.db.get_single_value(
            "Payment Settings", "api_key"
        )
        self.base_url = "https://api.payment.com"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential())
    def _make_request(self, method: str, endpoint: str, data=None):
        response = requests.request(
            method=method,
            url=f"{self.base_url}/{endpoint}",
            json=data,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    def create_payment(self, amount: float, currency: str):
        return self._make_request("POST", "payments", {
            "amount": amount,
            "currency": currency
        })
```

## Factory Function

For dependency injection and testing:

```python
def get_order_service(user: Optional[str] = None) -> OrderProcessingService:
    """Factory for OrderProcessingService."""
    return OrderProcessingService(user=user)

# Usage
service = get_order_service()
service.create(data)
```

## Best Practices

| Rule | Description |
|------|-------------|
| Single Responsibility | One service per domain |
| No Direct DB | Use repositories |
| Transaction Boundaries | Use `@with_transaction` |
| Permission First | Check at service boundary |
| Validate First | Before any logic |
| Factory Pattern | For easier testing |
