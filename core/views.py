from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Registro, Despesa, Receita, Item, Grupo
from django.utils import timezone


@login_required
def home(request):
    registros = Registro.objects.filter(user=request.user)
    return render(request, 'core/home.html', {'registros': registros})

@login_required
def adicionar_registro(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        ano = int(request.POST.get('ano'))
        mes = int(request.POST.get('mes'))
        situacao = request.POST.get('situacao')

        novo = Registro.objects.create(
            nome=nome,
            ano_ref=ano,
            mes_ref=mes,
            saldo=0,
            situacao=situacao,
            user=request.user
        )
        return redirect('registro', pk=novo.pk)

    return render(request, 'core/form_registro.html')

@login_required
def editar_registro(request, pk):
    registro = get_object_or_404(Registro, pk=pk, user=request.user)

    if request.method == 'POST':
        registro.nome = request.POST.get('nome')
        registro.ano_ref = int(request.POST.get('ano'))
        registro.mes_ref = int(request.POST.get('mes'))
        registro.situacao = request.POST.get('situacao')
        registro.save()
        return redirect('registro', pk=registro.pk)

    return render(request, 'core/form_registro.html', {'registro': registro})

@login_required
def adicionar_despesa(request):
    registro_id = request.GET.get('registro')
    registro = get_object_or_404(Registro, pk=registro_id, user=request.user)

    if request.method == 'POST':
        nome = request.POST.get('nome')
        valor = float(request.POST.get('valor'))
        item = Item.objects.create(nome=nome, valor=valor, checked=True)
        Despesa.objects.create(registro=registro, item=item)
        return redirect('registro', pk=registro.id)

    return render(request, 'core/form_item.html', {
        'tipo': 'despesa',
        'registro': registro,
    })

@login_required
def adicionar_receita(request):
    registro_id = request.GET.get('registro')
    registro = get_object_or_404(Registro, pk=registro_id, user=request.user)

    if request.method == 'POST':
        nome = request.POST.get('nome')
        valor = float(request.POST.get('valor'))
        item = Item.objects.create(nome=nome, valor=valor, checked=True)
        Receita.objects.create(registro=registro, item=item)
        return redirect('registro', pk=registro.id)

    return render(request, 'core/form_item.html', {
        'tipo': 'receita',
        'registro': registro,
    })


@login_required
def registro(request, pk):
    reg = get_object_or_404(Registro, pk=pk, user=request.user)

    despesas = Despesa.objects.filter(registro=reg)
    receitas = Receita.objects.filter(registro=reg)

    total_despesas = sum(
        d.item.valor if d.item else d.grupo.valor_total() for d in despesas
    )
    total_receitas = sum(
        r.item.valor if r.item else r.grupo.valor_total() for r in receitas
    )
    saldo = total_receitas - total_despesas

    reg.saldo = saldo
    reg.save()

    return render(request, 'core/registro.html', {
        'registro': reg,
        'despesas': despesas,
        'receitas': receitas,
        'total_despesas': total_despesas,
        'total_receitas': total_receitas,
        'saldo': saldo,
    })

@login_required
def adicionar_item(request):
    tipo = request.GET.get('tipo')
    registro_id = request.GET.get('registro')
    registro = get_object_or_404(Registro, pk=registro_id, user=request.user)

    if request.method == 'POST':
        nome = request.POST.get('nome')
        valor = float(request.POST.get('valor'))
        item = Item.objects.create(nome=nome, valor=valor)
        
        if tipo == 'despesa':
            Despesa.objects.create(registro=registro, item=item)
        else:
            Receita.objects.create(registro=registro, item=item)
        
        return redirect('registro', pk=registro.id)

    return render(request, 'core/form_item.html', {
        'tipo': tipo,
        'registro': registro,
    })

@login_required
def editar_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    # procura onde esse item está (despesa ou receita)
    despesa = Despesa.objects.filter(item=item).first()
    receita = Receita.objects.filter(item=item).first()
    registro = despesa.registro if despesa else receita.registro if receita else None

    if request.method == 'POST':
        item.nome = request.POST.get('nome')
        item.valor = float(request.POST.get('valor'))
        item.checked = request.POST.get('checked') == 'on'
        item.save()
        return redirect('registro', pk=registro.id)

    return render(request, 'core/form_item.html', {
        'tipo': 'despesa' if despesa else 'receita',
        'registro': registro,
        'item': item
    })

@login_required
def criar_grupo(request):
    tipo = request.GET.get('tipo')
    registro_id = request.GET.get('registro')
    registro = get_object_or_404(Registro, pk=registro_id, user=request.user)

    if request.method == 'POST':
        nome = request.POST.get('nome')
        grupo = Grupo.objects.create(nome=nome)

        if tipo == 'despesa':
            Despesa.objects.create(registro=registro, grupo=grupo)
        else:
            Receita.objects.create(registro=registro, grupo=grupo)

        return redirect('grupo', pk=grupo.pk)

    return render(request, 'core/form_grupo.html', {
        'tipo': tipo,
        'registro': registro
    })



@login_required
def grupo(request, pk):
    grupo = get_object_or_404(Grupo, pk=pk)

    # descobrir de onde esse grupo veio (despesa ou receita)
    despesa = Despesa.objects.filter(grupo=grupo).first()
    receita = Receita.objects.filter(grupo=grupo).first()

    # obtém o registro relacionado
    registro = despesa.registro if despesa else receita.registro if receita else None

    total = grupo.valor_total()

    return render(request, 'core/grupo.html', {
        'grupo': grupo,
        'total': total,
        'registro': registro
    })


@login_required
def grupo_adicionar_item(request, pk):
    grupo = get_object_or_404(Grupo, pk=pk)

    if request.method == 'POST':
        nome = request.POST.get('nome')
        valor = float(request.POST.get('valor'))
        checked = request.POST.get('checked') == 'on'

        item = Item.objects.create(nome=nome, valor=valor, checked=checked)
        grupo.itens.add(item)

        return redirect('grupo', pk=grupo.id)

    return render(request, 'core/form_item_grupo.html', {'grupo': grupo})

@login_required
def grupo_excluir_item(request, pk, item_id):
    grupo = get_object_or_404(Grupo, pk=pk)
    item = get_object_or_404(Item, pk=item_id)

    if request.method == 'POST':
        grupo.itens.remove(item)
        item.delete()
        return redirect('grupo', pk=grupo.id)

    return render(request, 'core/confirm_delete.html', {
        'obj': item,
        'url_cancelar': 'grupo',
        'pk': grupo.id
    })

from django.db.models import Sum, Count, Q
from datetime import datetime

@login_required
def dashboard(request):
    ano = request.GET.get('ano')
    mes = request.GET.get('mes')
    item_nome = request.GET.get('item')

    registros = Registro.objects.filter(user=request.user)

    if ano:
        registros = registros.filter(ano_ref=ano)
    if mes:
        registros = registros.filter(mes_ref=mes)

    despesas = Despesa.objects.filter(registro__in=registros)
    receitas = Receita.objects.filter(registro__in=registros)

    if item_nome:
        despesas = despesas.filter(Q(item__nome__icontains=item_nome) | Q(grupo__nome__icontains=item_nome))
        receitas = receitas.filter(Q(item__nome__icontains=item_nome) | Q(grupo__nome__icontains=item_nome))

    total_despesa = sum(d.item.valor if d.item else d.grupo.valor_total() for d in despesas)
    total_receita = sum(r.item.valor if r.item else r.grupo.valor_total() for r in receitas)
    saldo = total_receita - total_despesa

    # valores únicos para os filtros
    anos = Registro.objects.filter(user=request.user).values_list('ano_ref', flat=True).distinct().order_by('ano_ref')
    meses = Registro.objects.filter(user=request.user).values_list('mes_ref', flat=True).distinct().order_by('mes_ref')
    itens = Item.objects.values_list('nome', flat=True).distinct().order_by('nome')

    top_despesas = despesas.values('item__nome').annotate(total=Sum('item__valor')).order_by('-total')[:5]
    top_receitas = receitas.values('item__nome').annotate(total=Sum('item__valor')).order_by('-total')[:5]
    despesas_repetidas = despesas.values('item__nome').annotate(qtd=Count('registro__mes_ref', distinct=True)).filter(qtd__gt=1)

    return render(request, 'core/dashboard.html', {
        'ano': ano,
        'mes': mes,
        'item_nome': item_nome,
        'anos': anos,
        'meses': meses,
        'itens': itens,
        'total_despesa': total_despesa,
        'total_receita': total_receita,
        'saldo': saldo,
        'top_despesas': top_despesas,
        'top_receitas': top_receitas,
        'despesas_repetidas': despesas_repetidas
    })


@login_required
def deletar_despesa(request, pk):
    despesa = get_object_or_404(Despesa, pk=pk, registro__user=request.user)
    registro_id = despesa.registro.id
    if request.method == 'POST':
        despesa.delete()
        return redirect('registro', pk=registro_id)
    return render(request, 'core/confirm_delete.html', {
        'obj': despesa,
        'url_cancelar': 'registro',
        'pk': registro_id
    })

@login_required
def deletar_receita(request, pk):
    receita = get_object_or_404(Receita, pk=pk, registro__user=request.user)
    registro_id = receita.registro.id
    if request.method == 'POST':
        receita.delete()
        return redirect('registro', pk=registro_id)
    return render(request, 'core/confirm_delete.html', {
        'obj': receita,
        'url_cancelar': 'registro',
        'pk': registro_id
    })

@login_required
def deletar_registro(request, pk):
    registro = get_object_or_404(Registro, pk=pk, user=request.user)

    if request.method == 'POST':
        registro.delete()
        return redirect('home')

    return render(request, 'core/confirm_delete.html', {
        'obj': registro,
        'url_cancelar': 'registro',
        'pk': registro.id
    })

def offline(request):
    return render(request, 'core/offline.html')
