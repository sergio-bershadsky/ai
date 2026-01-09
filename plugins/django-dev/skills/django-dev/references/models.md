# Advanced Model Patterns

Detailed patterns for Django models beyond the basics.

## Relationships

### One-to-Many

```python
# models/order.py
from django.db import models
from .base import BaseModel


class Order(BaseModel):
    user = models.ForeignKey(
        "User",
        on_delete=models.PROTECT,
        related_name="orders",
    )
    total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "orders"
```

### Many-to-Many with Through Model

Create separate file for the through model:

```python
# models/product_tag.py
from django.db import models
from .base import BaseModel


class ProductTag(BaseModel):
    """Through model for Product-Tag relationship."""
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    tag = models.ForeignKey("Tag", on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "product_tags"
        unique_together = [("product", "tag")]
        ordering = ["order"]
```

```python
# models/product.py
class Product(BaseModel):
    name = models.CharField(max_length=255)
    tags = models.ManyToManyField(
        "Tag",
        through="ProductTag",
        related_name="products",
    )
```

## Virtual Models

Virtual models are not persisted to the database. Use for calculated/aggregated data:

```python
# models/virtual_cart.py
from dataclasses import dataclass
from decimal import Decimal
from typing import List


@dataclass
class VirtualCartItem:
    """In-memory cart item."""
    product_id: str
    quantity: int
    unit_price: Decimal

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass
class VirtualCart:
    """In-memory shopping cart."""
    items: List[VirtualCartItem]

    @property
    def total(self) -> Decimal:
        return sum(item.subtotal for item in self.items)

    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items)
```

## Proxy Models

Proxy models add behavior without new database tables:

```python
# models/proxy_active_user.py
from .user import User
from ..managers.active_user import ActiveUserManager


class ProxyActiveUser(User):
    """Proxy for active users only."""

    # 1. class Meta - ALWAYS FIRST
    class Meta:
        proxy = True
        verbose_name = "Active User"

    # 2. Manager
    objects = ActiveUserManager()

    # 3. Private/dunder methods (alphabetical)
    def __str__(self) -> str:
        return f"Active: {self.email}"

    # 4. Public methods (alphabetical)
    def deactivate(self) -> None:
        self.is_active = False
        self.save(update_fields=["is_active"])

    def send_reminder(self) -> None:
        # Delegate to service
        pass
```

## Database Constraints

Add constraints in Meta class:

```python
from django.db import models
from django.db.models import Q, CheckConstraint, UniqueConstraint


class Product(BaseModel):
    """Product model with database constraints."""

    # 1. class Meta - ALWAYS FIRST
    class Meta:
        db_table = "products"
        constraints = [
            CheckConstraint(
                check=Q(price__gte=0),
                name="product_price_positive",
            ),
            CheckConstraint(
                check=Q(sale_price__isnull=True) | Q(sale_price__lt=models.F("price")),
                name="sale_price_less_than_price",
            ),
            UniqueConstraint(
                fields=["sku"],
                condition=Q(deleted_at__isnull=True),
                name="unique_active_sku",
            ),
        ]

    # 2. Fields
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    sku = models.CharField(max_length=50)
```

## Indexes

Define indexes for query optimization:

```python
class Order(BaseModel):
    """Order model with indexes."""

    # 1. class Meta - ALWAYS FIRST
    class Meta:
        db_table = "orders"
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(
                fields=["status"],
                name="pending_orders_idx",
                condition=Q(status="pending"),
            ),
        ]

    # 2. Fields
    user = models.ForeignKey("User", on_delete=models.PROTECT)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
```

## Model Methods & Class Member Ordering

Keep models focused. Complex logic goes in services. **Always follow strict member ordering:**

1. **`class Meta`** - ALWAYS FIRST in the class
2. **Fields** - Class attributes (model fields)
3. **Managers** - `objects = Manager()`
4. **Properties** (`@property`) - Alphabetical order
5. **Private/dunder methods** (`_method`, `__str__`) - Alphabetical order
6. **Public methods** - Alphabetical order

```python
class User(BaseModel):
    """User account model."""

    # 1. class Meta - ALWAYS FIRST
    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    # 2. Fields
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)

    # 3. Manager
    objects = UserManager()

    # 4. Properties (alphabetical)
    @property
    def display_name(self) -> str:
        return self.name or self.email.split("@")[0]

    @property
    def is_verified(self) -> bool:
        return self.email_verified_at is not None

    # 5. Private/dunder methods (alphabetical)
    def __repr__(self) -> str:
        return f"<User {self.email}>"

    def __str__(self) -> str:
        return self.email

    def _calculate_account_score(self) -> int:
        return len(self.orders.filter(status="completed"))

    def _validate_email_domain(self) -> bool:
        return "@" in self.email

    # 6. Public methods (alphabetical)
    def activate(self) -> None:
        self.is_active = True
        self.save(update_fields=["is_active"])

    def can_place_order(self) -> bool:
        return self.is_active and not self.is_deleted

    def deactivate(self) -> None:
        self.is_active = False
        self.save(update_fields=["is_active"])

    def verify_email(self) -> None:
        from django.utils import timezone
        self.email_verified_at = timezone.now()
        self.save(update_fields=["email_verified_at"])

    # Complex logic goes to services
    # DON'T: def send_welcome_email(self): ...
    # DO: UserService.send_welcome_email(user)
```

## Signals

Avoid signals when possible. Prefer explicit service calls. When necessary, place in `signals.py`:

```python
# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User


@receiver(post_save, sender=User)
def user_created(sender, instance, created, **kwargs):
    if created:
        # Minimal logic only
        pass
```

Register in `apps.py`:

```python
class MyAppConfig(AppConfig):
    def ready(self):
        from . import signals  # noqa
```

## Migration Best Practices

1. One migration per logical change
2. Name migrations descriptively: `0002_add_user_phone_field.py`
3. Always include `reverse_code` for data migrations
4. Test migrations both forward and backward

```python
# migrations/0002_add_user_phone_field.py
from django.db import migrations, models


def populate_phone(apps, schema_editor):
    User = apps.get_model("myapp", "User")
    User.objects.filter(phone__isnull=True).update(phone="")


def reverse_phone(apps, schema_editor):
    pass  # No action needed


class Migration(migrations.Migration):
    dependencies = [("myapp", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="user",
            name="phone",
            field=models.CharField(max_length=20, blank=True, default=""),
        ),
        migrations.RunPython(populate_phone, reverse_phone),
    ]
```
