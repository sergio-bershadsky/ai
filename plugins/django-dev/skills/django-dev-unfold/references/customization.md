# Unfold Admin Customization

Advanced patterns for Unfold admin customization with HTMX.

## Custom Dashboard

Create a custom dashboard view:

```python
# admin/dashboard.py
from django.urls import path
from django.template.response import TemplateResponse
from django.contrib.admin import site as admin_site


def dashboard_view(request):
    """Custom admin dashboard."""
    from ..models import User, Order, Product

    context = {
        **admin_site.each_context(request),
        "title": "Dashboard",
        "stats": {
            "total_users": User.objects.count(),
            "active_users": User.objects.filter(is_active=True).count(),
            "total_orders": Order.objects.count(),
            "pending_orders": Order.objects.filter(status="pending").count(),
            "total_products": Product.objects.count(),
        },
        "recent_orders": Order.objects.select_related("user")[:10],
    }
    return TemplateResponse(request, "admin/dashboard.html", context)


# Register URL
def get_urls():
    urls = super().get_urls()
    custom_urls = [
        path("dashboard/", dashboard_view, name="dashboard"),
    ]
    return custom_urls + urls
```

Dashboard template:

```html
<!-- templates/admin/dashboard.html -->
{% extends "admin/base_site.html" %}
{% load i18n %}

{% block content %}
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
    <!-- Stats Cards -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="text-sm text-gray-500 dark:text-gray-400">Total Users</div>
        <div class="text-2xl font-bold">{{ stats.total_users }}</div>
    </div>

    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="text-sm text-gray-500 dark:text-gray-400">Active Users</div>
        <div class="text-2xl font-bold text-green-600">{{ stats.active_users }}</div>
    </div>

    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="text-sm text-gray-500 dark:text-gray-400">Total Orders</div>
        <div class="text-2xl font-bold">{{ stats.total_orders }}</div>
    </div>

    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="text-sm text-gray-500 dark:text-gray-400">Pending Orders</div>
        <div class="text-2xl font-bold text-yellow-600">{{ stats.pending_orders }}</div>
    </div>
</div>

<!-- Recent Orders Table -->
<div class="bg-white dark:bg-gray-800 rounded-lg shadow">
    <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-lg font-semibold">Recent Orders</h2>
    </div>
    <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order ID</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
            </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            {% for order in recent_orders %}
            <tr>
                <td class="px-6 py-4 whitespace-nowrap">{{ order.id|truncatechars:8 }}</td>
                <td class="px-6 py-4 whitespace-nowrap">{{ order.user.email }}</td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="px-2 py-1 text-xs rounded-full
                        {% if order.status == 'completed' %}bg-green-100 text-green-800
                        {% elif order.status == 'pending' %}bg-yellow-100 text-yellow-800
                        {% else %}bg-gray-100 text-gray-800{% endif %}">
                        {{ order.status }}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">${{ order.total|floatformat:2 }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
```

## HTMX Patterns

### Dynamic Field Updates

```python
# admin/product.py
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path


@admin.register(Product)
class ProductAdmin(BaseModelAdmin):
    change_form_template = "admin/product/change_form.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "calculate-price/",
                self.admin_site.admin_view(self.calculate_price),
                name="product_calculate_price",
            ),
        ]
        return custom_urls + urls

    def calculate_price(self, request):
        """HTMX endpoint for price calculation."""
        cost = float(request.POST.get("cost", 0))
        margin = float(request.POST.get("margin", 0))
        price = cost * (1 + margin / 100)
        return JsonResponse({"price": f"{price:.2f}"})
```

Template with HTMX:

```html
<!-- templates/admin/product/change_form.html -->
{% extends "admin/change_form.html" %}

{% block after_field_sets %}
<div id="price-calculator" class="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg mb-4">
    <h3 class="text-lg font-semibold mb-4">Price Calculator</h3>

    <div class="grid grid-cols-3 gap-4">
        <div>
            <label class="block text-sm font-medium mb-1">Cost</label>
            <input type="number" name="cost" step="0.01"
                   class="form-input w-full"
                   hx-post="{% url 'admin:product_calculate_price' %}"
                   hx-trigger="change delay:300ms"
                   hx-target="#calculated-price"
                   hx-include="[name='cost'], [name='margin']">
        </div>

        <div>
            <label class="block text-sm font-medium mb-1">Margin %</label>
            <input type="number" name="margin" step="1"
                   class="form-input w-full"
                   hx-post="{% url 'admin:product_calculate_price' %}"
                   hx-trigger="change delay:300ms"
                   hx-target="#calculated-price"
                   hx-include="[name='cost'], [name='margin']">
        </div>

        <div>
            <label class="block text-sm font-medium mb-1">Calculated Price</label>
            <div id="calculated-price" class="text-2xl font-bold text-green-600">
                $0.00
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### Inline Actions

```python
@admin.register(Order)
class OrderAdmin(BaseModelAdmin):
    list_display = ["id", "user", "status", "order_actions"]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<uuid:order_id>/mark-completed/",
                self.admin_site.admin_view(self.mark_completed),
                name="order_mark_completed",
            ),
        ]
        return custom_urls + urls

    def mark_completed(self, request, order_id):
        """HTMX action to mark order completed."""
        order = Order.objects.get(id=order_id)
        order.status = "completed"
        order.save()

        return HttpResponse(
            '<span class="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">'
            'completed</span>'
        )

    def order_actions(self, obj):
        if obj.status == "pending":
            return format_html(
                '''<button
                    hx-post="{}"
                    hx-target="closest tr"
                    hx-swap="outerHTML"
                    class="btn btn-sm btn-success">
                    Mark Completed
                </button>''',
                reverse("admin:order_mark_completed", args=[obj.id]),
            )
        return "-"
```

### Modal Dialogs

```html
<!-- templates/admin/partials/modal.html -->
<div id="modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-lg w-full mx-4">
        <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold">{{ title }}</h3>
        </div>
        <div class="px-6 py-4">
            {{ content }}
        </div>
        <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-2">
            <button onclick="document.getElementById('modal').remove()"
                    class="btn btn-secondary">Cancel</button>
            <button hx-post="{{ action_url }}"
                    hx-target="#modal"
                    class="btn btn-primary">{{ action_label }}</button>
        </div>
    </div>
</div>
```

Trigger modal:

```python
def show_confirmation(self, request, object_id):
    return render(request, "admin/partials/modal.html", {
        "title": "Confirm Action",
        "content": "Are you sure you want to proceed?",
        "action_url": reverse("admin:confirm_action", args=[object_id]),
        "action_label": "Confirm",
    })
```

### Live Search

```html
<input type="search"
       name="q"
       placeholder="Search..."
       class="form-input"
       hx-get="{% url 'admin:myapp_model_changelist' %}"
       hx-trigger="keyup changed delay:300ms"
       hx-target="#result-list"
       hx-push-url="true">
```

## Custom Widgets

### Date Range Picker

```python
# admin/widgets.py
from django import forms


class DateRangeWidget(forms.MultiWidget):
    template_name = "admin/widgets/date_range.html"

    def __init__(self, attrs=None):
        widgets = [
            forms.DateInput(attrs={"type": "date", "class": "form-input"}),
            forms.DateInput(attrs={"type": "date", "class": "form-input"}),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.start, value.end]
        return [None, None]
```

### Rich Text Editor

```python
# admin/widgets.py
class RichTextWidget(forms.Textarea):
    template_name = "admin/widgets/rich_text.html"

    class Media:
        js = ("admin/js/trix.js",)
        css = {"all": ("admin/css/trix.css",)}
```

## Custom Actions

### Bulk Actions

```python
from unfold.decorators import action


@admin.register(Order)
class OrderAdmin(BaseModelAdmin):

    @action(description="Export selected orders")
    def export_orders(self, request, queryset):
        # Generate CSV
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="orders.csv"'
        writer = csv.writer(response)
        writer.writerow(["ID", "User", "Status", "Total"])
        for order in queryset:
            writer.writerow([order.id, order.user.email, order.status, order.total])
        return response

    @action(description="Mark as shipped")
    def mark_shipped(self, request, queryset):
        updated = queryset.update(status="shipped")
        self.message_user(request, f"{updated} orders marked as shipped.")
```

### Row Actions

```python
@admin.register(Order)
class OrderAdmin(BaseModelAdmin):
    list_display = ["id", "user", "status", "actions_column"]

    def actions_column(self, obj):
        return format_html(
            '''
            <div class="flex gap-2">
                <a href="{}" class="btn btn-sm btn-primary">View</a>
                <a href="{}" class="btn btn-sm btn-secondary">Invoice</a>
            </div>
            ''',
            reverse("admin:myapp_order_change", args=[obj.id]),
            reverse("admin:order_invoice", args=[obj.id]),
        )

    actions_column.short_description = "Actions"
```

## Theming

### Custom Colors

```python
UNFOLD = {
    "COLORS": {
        "primary": {
            "50": "239 246 255",   # blue-50
            "500": "59 130 246",   # blue-500
            "900": "30 58 138",    # blue-900
        },
    },
}
```

### Dark Mode

Unfold supports dark mode automatically. Customize with:

```css
/* static/admin/css/custom.css */
:root {
    --color-primary-500: 59 130 246;
}

.dark {
    --color-primary-500: 96 165 250;
}
```

## Charts

Using Chart.js with Unfold:

```html
<!-- templates/admin/dashboard.html -->
{% block extrahead %}
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
{% endblock %}

{% block content %}
<canvas id="salesChart" class="mb-8"></canvas>

<script>
const ctx = document.getElementById('salesChart');
new Chart(ctx, {
    type: 'line',
    data: {
        labels: {{ chart_labels|safe }},
        datasets: [{
            label: 'Sales',
            data: {{ chart_data|safe }},
            borderColor: 'rgb(59, 130, 246)',
            tension: 0.1
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: { display: false }
        }
    }
});
</script>
{% endblock %}
```
