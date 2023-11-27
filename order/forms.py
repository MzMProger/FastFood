from order.choices import OrderStatus
from order.models import Order
from django import forms


class OrderChatForm(forms.Form):
    text = forms.CharField(
        max_length=255,
        label="Xabar",
        widget=forms.Textarea(attrs={"class": "form-control", "row": 5}),
    )


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("status", )
        labels = {
            "status": "Status",
        }
        widgets = {
            "status": forms.Select(attrs={"class": "form-control"}),
        }

    def save(self, commit=True, *args, **kwargs):
        old_status = kwargs.get("old_status")
        model = super().save(commit=False)
        if commit:
            allowed_changes = get_allowed_status_changes(status=old_status, order_type=model.order_type)
            if model.status in allowed_changes:
                model.save()
            else:
                model = None
        return model


def get_allowed_status_changes(status, order_type):
    if order_type == "delivery":
        status_change_map = {
            OrderStatus.PENDING.value: [OrderStatus.DENIED.value, OrderStatus.PREPARING.value],
            OrderStatus.PREPARING.value: [OrderStatus.DENIED.value, OrderStatus.PREPARED.value],
            OrderStatus.PREPARED.value: [OrderStatus.DENIED.value, OrderStatus.DELIVERING.value],
            OrderStatus.DELIVERING.value: [OrderStatus.DENIED.value, OrderStatus.DELIVERED.value],
        }
    else:
        status_change_map = {
            OrderStatus.PENDING.value: [OrderStatus.DENIED.value, OrderStatus.PREPARING.value],
            OrderStatus.PREPARING.value: [OrderStatus.DENIED.value, OrderStatus.PREPARED.value],
            OrderStatus.PREPARED.value: [OrderStatus.DENIED.value, OrderStatus.DELIVERED.value],
        }
    return status_change_map.get(status, [])
