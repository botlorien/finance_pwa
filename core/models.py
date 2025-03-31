from django.db import models
from django.contrib.auth.models import User

class Registro(models.Model):
    SITUACAO_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('QUITADA', 'Quitada'),
    ]

    nome = models.CharField(max_length=100, default='Novo Registro')
    ano_ref = models.IntegerField()
    mes_ref = models.IntegerField()
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    situacao = models.CharField(max_length=10, choices=SITUACAO_CHOICES, default='PENDENTE')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome



class Item(models.Model):
    nome = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    checked = models.BooleanField(default=True)

    def __str__(self):
        return self.nome

class Grupo(models.Model):
    nome = models.CharField(max_length=100)
    itens = models.ManyToManyField(Item)

    def valor_total(self):
        return sum(item.valor for item in self.itens.filter(checked=True))

    def __str__(self):
        return self.nome

class Despesa(models.Model):
    registro = models.ForeignKey(Registro, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True)
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.registro.nome} - {self.item.nome if self.item else self.grupo.nome if self.grupo else "Sem Item"}'

class Receita(models.Model):
    registro = models.ForeignKey(Registro, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True)
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.registro.nome} - {self.item.nome if self.item else self.grupo.nome if self.grupo else "Sem Item"}'
