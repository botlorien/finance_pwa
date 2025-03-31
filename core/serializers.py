from rest_framework import serializers
from .models import Registro, Item, Grupo, Despesa, Receita

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

class GrupoSerializer(serializers.ModelSerializer):
    itens = ItemSerializer(many=True, read_only=True)

    class Meta:
        model = Grupo
        fields = '__all__'

class DespesaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Despesa
        fields = '__all__'

class ReceitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receita
        fields = '__all__'

class RegistroSerializer(serializers.ModelSerializer):
    despesas = DespesaSerializer(many=True, read_only=True)
    receitas = ReceitaSerializer(many=True, read_only=True)

    class Meta:
        model = Registro
        fields = '__all__'
