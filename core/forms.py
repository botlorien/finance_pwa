from django import forms
from .models import Item
from django import forms
from .models import Grupo, Item
from .models import Registro
from django.db.models import Q

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['nome', 'valor', 'quantidade', 'checked', 'prioridade']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'list': 'sugestoes'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantidade', 'min':1}),
            'checked': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.registro = kwargs.pop('registro', None)
        self.tipo = kwargs.pop('tipo', None)
        if not self.registro:
            raise ValueError("Você precisa passar o registro para o ItemForm!")
        super().__init__(*args, **kwargs)

        if self.tipo in ('receita', 'criacao'):
            self.fields.pop('prioridade', None)
        else:
            opcoes = [(i, f'Prioridade {i}') for i in range(1, 51)]
            self.fields['prioridade'].widget = forms.Select(
                choices=opcoes,
                attrs={
                    'class': 'form-select select2',  # Adicione a classe select2
                }
            )
    def clean_prioridade(self):
        # Ignora validação se não for despesa
        return self.cleaned_data.get('prioridade')



class GrupoForm(forms.ModelForm):
    class Meta:
        model = Grupo
        fields = ['nome', 'prioridade']

    def __init__(self, *args, **kwargs):
        self.registro = kwargs.pop('registro', None)
        self.tipo = kwargs.pop('tipo', None)
        if not self.registro:
            raise ValueError("Você precisa passar o registro para o ItemForm!")
        super().__init__(*args, **kwargs)

        if self.tipo in ('receita', 'criacao'):
            self.fields.pop('prioridade', None)
        else:
            # Gera uma lista padrão de prioridades de 1 a 50
            opcoes = [(i, f'Prioridade {i}') for i in range(1, 51)]
            self.fields['prioridade'].widget = forms.Select(
                choices=opcoes,
                attrs={
                    'class': 'form-select select2',  # Adicione a classe select2
                }
            )

    def clean_prioridade(self):
        # Sem validação de conflito agora
        return self.cleaned_data.get('prioridade')


