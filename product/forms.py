from product.models import Product
from django import forms


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ("parent", )
        labels = {
            "name": "Nomi",
            "price": "Narxi",
            "desc": "Tavsifi",
            "image": "Rasm",
            "category": "Kategoriya",
            "is_active": "Faolmi",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "desc": forms.Textarea(attrs={"class": "form-control", "row": 5}),
            "image": forms.FileInput(attrs={'class': 'form-control dropify'}),
            "category": forms.Select(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            if self.instance.image:
                print(self.instance.image.path)
                self.fields['image'].widget = forms.FileInput(
                    attrs={
                        'class': 'form-control dropify',
                        'data-default-file': self.instance.image.url
                    }
                )

    def save(self, commit=True, *args, **kwargs):
        model = super().save(commit=False)
        if commit:
            model.save()
        return model
