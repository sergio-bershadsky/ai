# Form Patterns

Django form organization following 1-file-per-form pattern.

## Form Structure

```
forms/
├── __init__.py
├── base.py           # Base form classes
├── user.py           # UserForm, UserRegistrationForm
├── product.py        # ProductForm
└── order.py          # OrderForm, OrderItemForm
```

## Base Forms

Create reusable base forms in `forms/base.py`:

```python
from django import forms


class BaseForm(forms.Form):
    """Base form with common functionality."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_css_classes()

    def _add_css_classes(self):
        """Add Tailwind/Unfold CSS classes to form fields."""
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_classes} form-input".strip()


class BaseModelForm(forms.ModelForm):
    """Base model form with common functionality."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_css_classes()

    def _add_css_classes(self):
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_classes} form-input".strip()
```

## Model Form Template

Each form in its own file (`forms/user.py`):

```python
from django import forms
from django.core.exceptions import ValidationError
from .base import BaseModelForm
from ..models import User


class UserForm(BaseModelForm):
    """Form for creating/editing users."""

    # 1. class Meta - ALWAYS FIRST
    class Meta:
        model = User
        fields = ["email", "name", "is_active"]
        widgets = {
            "email": forms.EmailInput(attrs={"placeholder": "user@example.com"}),
            "name": forms.TextInput(attrs={"placeholder": "Full Name"}),
        }

    # 2. Methods
    def clean_email(self):
        email = self.cleaned_data.get("email", "").lower().strip()

        # Check uniqueness excluding current instance
        qs = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise ValidationError("This email is already registered.")

        return email


class UserRegistrationForm(BaseModelForm):
    """Form for user registration with password."""

    # 1. class Meta - ALWAYS FIRST
    class Meta:
        model = User
        fields = ["email", "name", "password"]

    # 2. Additional fields
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)

    # 3. Methods
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
```

## Form Init Re-exports

In `forms/__init__.py`:

```python
from .base import BaseForm, BaseModelForm
from .user import UserForm, UserRegistrationForm
from .product import ProductForm

__all__ = [
    "BaseForm",
    "BaseModelForm",
    "UserForm",
    "UserRegistrationForm",
    "ProductForm",
]
```

## Formsets

For related objects, use formsets:

```python
# forms/order.py
from django import forms
from django.forms import inlineformset_factory
from .base import BaseModelForm
from ..models import Order, OrderItem


class OrderForm(BaseModelForm):
    class Meta:
        model = Order
        fields = ["user", "notes"]


class OrderItemForm(BaseModelForm):
    class Meta:
        model = OrderItem
        fields = ["product", "quantity", "unit_price"]


# Create inline formset
OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)
```

## Custom Widgets

Place custom widgets in `forms/widgets.py`:

```python
from django import forms


class DatePickerWidget(forms.DateInput):
    """Date picker with JavaScript integration."""

    template_name = "widgets/datepicker.html"

    def __init__(self, attrs=None):
        default_attrs = {
            "class": "datepicker-input",
            "data-datepicker": "true",
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, format="%Y-%m-%d")


class MoneyWidget(forms.NumberInput):
    """Money input with currency formatting."""

    def __init__(self, currency="USD", attrs=None):
        self.currency = currency
        default_attrs = {
            "class": "money-input",
            "step": "0.01",
            "min": "0",
            "data-currency": currency,
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
```

## Form Validation Patterns

### Field-level validation

```python
def clean_phone(self):
    phone = self.cleaned_data.get("phone", "")
    # Remove non-digits
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) < 10:
        raise ValidationError("Phone number must have at least 10 digits.")
    return digits
```

### Cross-field validation

```python
def clean(self):
    cleaned_data = super().clean()
    start_date = cleaned_data.get("start_date")
    end_date = cleaned_data.get("end_date")

    if start_date and end_date and start_date > end_date:
        raise ValidationError({
            "end_date": "End date must be after start date."
        })

    return cleaned_data
```

### Conditional validation

```python
def clean(self):
    cleaned_data = super().clean()

    if cleaned_data.get("requires_shipping"):
        if not cleaned_data.get("shipping_address"):
            raise ValidationError({
                "shipping_address": "Shipping address is required."
            })

    return cleaned_data
```

## Form Mixins

Create reusable mixins for common patterns:

```python
# forms/mixins.py

class SlugMixin:
    """Auto-generate slug from name field."""

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if name and not self.cleaned_data.get("slug"):
            from django.utils.text import slugify
            self.cleaned_data["slug"] = slugify(name)
        return name


class AuditMixin:
    """Track who created/modified the record."""

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            if not instance.pk:
                instance.created_by = self.user
            instance.updated_by = self.user
        if commit:
            instance.save()
        return instance
```

Usage:

```python
class ProductForm(SlugMixin, AuditMixin, BaseModelForm):
    class Meta:
        model = Product
        fields = ["name", "slug", "price"]
```
