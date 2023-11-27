from category.models import Category
from django import forms


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = ("parent", )
        labels = {
            "name": "Nomi",
            "order": "Tartib raqami",
            "is_active": "Faolmi",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def save(self, commit=True, *args, **kwargs):
        model = super().save(commit=False)
        if commit:
            model.save()
        return model
