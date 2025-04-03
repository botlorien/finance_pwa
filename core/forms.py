from django import forms
from .models import Item

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['nome', 'valor', 'checked']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'list': 'sugestoes'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor'}),
            'checked': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Só aplica default=True se o campo não foi preenchido no POST
        if not self.is_bound:
            self.fields['checked'].initial = True