from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Registro, Despesa, Receita, Item, Grupo
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import datetime
from .forms import ItemForm
from django.http import Http404
from django.views.decorators.http import require_POST

def get_itens_do_usuario(user):
    return Item.objects.filter(
        Q(despesa__registro__user=user) |
        Q(receita__registro__user=user) |
        Q(grupo__despesa__registro__user=user) |
        Q(grupo__receita__registro__user=user)
    ).values_list('nome', flat=True).distinct()


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

# @login_required
# def adicionar_despesa(request):
#     registro_id = request.GET.get('registro')
#     registro = get_object_or_404(Registro, pk=registro_id, user=request.user)

#     if request.method == 'POST':
#         nome = request.POST.get('nome')
#         valor = float(request.POST.get('valor'))
#         item = Item.objects.create(nome=nome, valor=valor, checked=True)
#         Despesa.objects.create(registro=registro, item=item)
#         return redirect('registro', pk=registro.id)

#     return render(request, 'core/form_item.html', {
#         'tipo': 'despesa',
#         'registro': registro,
#     })

@login_required
def adicionar_despesa(request):
    registro_id = request.GET.get('registro')
    registro = get_object_or_404(Registro, pk=registro_id, user=request.user)

    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            Despesa.objects.create(registro=registro, item=item)
            return redirect('registro', pk=registro.id)
    else:
        form = ItemForm()

    return render(request, 'core/form_item.html', {
        'form': form,
        'registro': registro,
        'tipo': 'despesa',
    })

# @login_required
# def adicionar_receita(request):
#     registro_id = request.GET.get('registro')
#     registro = get_object_or_404(Registro, pk=registro_id, user=request.user)

#     if request.method == 'POST':
#         nome = request.POST.get('nome')
#         valor = float(request.POST.get('valor'))
#         item = Item.objects.create(nome=nome, valor=valor, checked=True)
#         Receita.objects.create(registro=registro, item=item)
#         return redirect('registro', pk=registro.id)

#     return render(request, 'core/form_item.html', {
#         'tipo': 'receita',
#         'registro': registro,
#     })
@login_required
def adicionar_receita(request):
    registro_id = request.GET.get('registro')
    registro = get_object_or_404(Registro, pk=registro_id, user=request.user)

    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            Receita.objects.create(registro=registro, item=item)
            return redirect('registro', pk=registro.id)
    else:
        form = ItemForm()

    return render(request, 'core/form_item.html', {
        'form': form,
        'registro': registro,
        'tipo': 'receita',
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

# @login_required
# def adicionar_item(request):
#     tipo = request.GET.get('tipo')
#     registro_id = request.GET.get('registro')
#     registro = get_object_or_404(Registro, pk=registro_id, user=request.user)

#     if request.method == 'POST':
#         nome = request.POST.get('nome')
#         valor = float(request.POST.get('valor'))
#         item = Item.objects.create(nome=nome, valor=valor)
        
#         if tipo == 'despesa':
#             Despesa.objects.create(registro=registro, item=item)
#         else:
#             Receita.objects.create(registro=registro, item=item)
        
#         return redirect('registro', pk=registro.id)

#     return render(request, 'core/form_item.html', {
#         'tipo': tipo,
#         'registro': registro,
#     })


@login_required
def adicionar_item(request):
    tipo = request.GET.get('tipo')
    registro_id = request.GET.get('registro')
    registro = get_object_or_404(Registro, pk=registro_id, user=request.user)

    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            if tipo == 'despesa':
                Despesa.objects.create(registro=registro, item=item)
            else:
                Receita.objects.create(registro=registro, item=item)
            return redirect('registro', pk=registro.id)
    else:
        form = ItemForm()

    sugestoes = get_itens_do_usuario(request.user)
    return render(request, 'core/form_item.html', {
        'form': form,
        'registro': registro,
        'tipo': tipo,
        'sugestoes': sugestoes,
    })


# @login_required
# def editar_item(request, pk):
#     item = get_object_or_404(Item, pk=pk)
#     # procura onde esse item está (despesa ou receita)
#     despesa = Despesa.objects.filter(item=item).first()
#     receita = Receita.objects.filter(item=item).first()
#     registro = despesa.registro if despesa else receita.registro if receita else None

#     if request.method == 'POST':
#         item.nome = request.POST.get('nome')
#         item.valor = float(request.POST.get('valor'))
#         item.checked = request.POST.get('checked') == 'on'
#         item.save()
#         return redirect('registro', pk=registro.id)

#     return render(request, 'core/form_item.html', {
#         'tipo': 'despesa' if despesa else 'receita',
#         'registro': registro,
#         'item': item
#     })

@login_required
def editar_item(request, pk):
    """
    Agora filtrando para garantir que o item pertença a um registro do usuário.
    """
    # Verifica se o item está vinculado a alguma despesa ou receita do user.
    despesa = Despesa.objects.filter(item__pk=pk, registro__user=request.user).first()
    receita = Receita.objects.filter(item__pk=pk, registro__user=request.user).first()

    # Se não encontrou nem despesa nem receita pertencente ao usuário, 404:
    if not despesa and not receita:
        raise Http404("Item não encontrado para este usuário.")

    # Identifica qual deles está presente
    tipo = 'despesa' if despesa else 'receita'
    item = despesa.item if despesa else receita.item
    registro = despesa.registro if despesa else receita.registro

    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('registro', pk=registro.pk)
    else:
        form = ItemForm(instance=item)

    return render(request, 'core/form_item.html', {
        'form': form,
        'registro': registro,
        'tipo': tipo,
    })



@login_required
@require_POST
def atualizar_checked_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)

    # Proteção extra: só deixa atualizar se o item pertence ao usuário
    is_owner = Despesa.objects.filter(item=item, registro__user=request.user).exists() or \
               Receita.objects.filter(item=item, registro__user=request.user).exists() or \
               Grupo.objects.filter(itens=item, despesa__registro__user=request.user).exists() or \
               Grupo.objects.filter(itens=item, receita__registro__user=request.user).exists()

    if not is_owner:
        raise Http404("Item não pertence a este usuário.")

    item.checked = 'checked' in request.POST
    item.save()

    # Redirecionar para onde veio (header 'Referer') ou home
    return redirect(request.META.get('HTTP_REFERER', 'home'))


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
    """
    Valida se o grupo realmente pertence a algum registro do user logado.
    """
    grupo_obj = get_object_or_404(Grupo, pk=pk)

    despesa = Despesa.objects.filter(grupo=grupo_obj, registro__user=request.user).first()
    receita = Receita.objects.filter(grupo=grupo_obj, registro__user=request.user).first()
    if not despesa and not receita:
        raise Http404("Grupo não encontrado para este usuário.")

    registro = despesa.registro if despesa else receita.registro
    total = grupo_obj.valor_total()

    return render(request, 'core/grupo.html', {
        'grupo': grupo_obj,
        'total': total,
        'registro': registro
    })


@login_required
def grupo_adicionar_item(request, pk):
    grupo_obj = get_object_or_404(Grupo, pk=pk)
    despesa = Despesa.objects.filter(grupo=grupo_obj, registro__user=request.user).first()
    receita = Receita.objects.filter(grupo=grupo_obj, registro__user=request.user).first()
    if not despesa and not receita:
        raise Http404("Grupo não encontrado para este usuário.")

    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            grupo_obj.itens.add(item)
            return redirect('grupo', pk=grupo_obj.id)
    else:
        form = ItemForm()

    sugestoes = get_itens_do_usuario(request.user)
    return render(request, 'core/form_item_grupo.html', {
        'form': form,
        'grupo': grupo_obj,
        'sugestoes': sugestoes,
    })


@login_required
def grupo_excluir_item(request, pk, item_id):
    """
    Garante que o grupo pertence ao user logado antes de remover item.
    """
    grupo_obj = get_object_or_404(Grupo, pk=pk)
    despesa = Despesa.objects.filter(grupo=grupo_obj, registro__user=request.user).first()
    receita = Receita.objects.filter(grupo=grupo_obj, registro__user=request.user).first()
    if not despesa and not receita:
        raise Http404("Grupo não encontrado para este usuário.")

    item = get_object_or_404(Item, pk=item_id)
    # Se quiser validar também que o item pertence a este grupo especificamente:
    if item not in grupo_obj.itens.all():
        raise Http404("Item não pertence a este grupo.")

    if request.method == 'POST':
        grupo_obj.itens.remove(item)
        item.delete()
        return redirect('grupo', pk=grupo_obj.id)

    return render(request, 'core/confirm_delete.html', {
        'obj': item,
        'url_cancelar': 'grupo',
        'pk': grupo_obj.id
    })

@login_required
def grupo_editar_item(request, grupo_id, item_id):
    grupo_obj = get_object_or_404(Grupo, pk=grupo_id)

    # Verifica se o grupo pertence ao user
    despesa = Despesa.objects.filter(grupo=grupo_obj, registro__user=request.user).first()
    receita = Receita.objects.filter(grupo=grupo_obj, registro__user=request.user).first()
    if not despesa and not receita:
        raise Http404("Grupo não encontrado ou não pertence a este usuário.")

    # Verifica se o item pertence ao grupo
    item = get_object_or_404(Item, pk=item_id)
    if item not in grupo_obj.itens.all():
        raise Http404("Item não pertence a este grupo.")

    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('grupo', pk=grupo_obj.id)
    else:
        form = ItemForm(instance=item)

    return render(request, 'core/form_item_grupo.html', {
        'grupo': grupo_obj,
        'form': form,
        'editando': True,
    })


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
    print(receitas)

    if item_nome:
        despesas = despesas.filter(Q(item__nome__icontains=item_nome) | Q(grupo__nome__icontains=item_nome))
        receitas = receitas.filter(Q(item__nome__icontains=item_nome) | Q(grupo__nome__icontains=item_nome))

    total_despesa = sum(d.item.valor if d.item else d.grupo.valor_total() for d in despesas)
    total_receita = sum(r.item.valor if r.item else r.grupo.valor_total() for r in receitas)
    print(total_receita)
    saldo = total_receita - total_despesa
    print(saldo)
    # valores únicos para os filtros
    anos = Registro.objects.filter(user=request.user) \
                          .values_list('ano_ref', flat=True).distinct().order_by('ano_ref')
    meses = Registro.objects.filter(user=request.user) \
                           .values_list('mes_ref', flat=True).distinct().order_by('mes_ref')
    itens = Item.objects.values_list('nome', flat=True).distinct().order_by('nome')



    from decimal import Decimal
    from collections import defaultdict


    # Top 5 Despesas (considerando itens + grupos)
    top_dict = defaultdict(Decimal)
    for d in despesas:
        if d.item:
            top_dict[d.item.nome] += d.item.valor
        elif d.grupo:
            top_dict[d.grupo.nome] += Decimal(d.grupo.valor_total())

    top_despesas = sorted(
        [{'nome': nome, 'total': valor} for nome, valor in top_dict.items()],
        key=lambda x: x['total'],
        reverse=True
    )[:5]

    # Top 5 Receitas (considerando itens + grupos)
    top_dict = defaultdict(Decimal)
    for r in receitas:
        if r.item:
            top_dict[r.item.nome] += r.item.valor
        elif r.grupo:
            top_dict[r.grupo.nome] += Decimal(r.grupo.valor_total())

    top_receitas = sorted(
        [{'nome': nome, 'total': valor} for nome, valor in top_dict.items()],
        key=lambda x: x['total'],
        reverse=True
    )[:5]


    

    despesas_repetidas = despesas.values('item__nome') \
                                 .annotate(qtd=Count('registro__mes_ref', distinct=True)) \
                                 .filter(qtd__gt=1)

    print(total_receita)
    print(saldo)
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

def bye(request):
    return render(request, 'core/bye.html')

