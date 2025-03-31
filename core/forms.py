from django import forms
from .models import Item

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['nome', 'valor', 'checked']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor'}),
            'checked': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
