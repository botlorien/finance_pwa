from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('registro/<int:pk>/', views.registro, name='registro'),
    path('registro/<int:pk>/editar/', views.editar_registro, name='editar_registro'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('adicionar-registro/', views.adicionar_registro, name='adicionar_registro'),
    path('adicionar-item/', views.adicionar_item, name='adicionar_item'),
    path('editar-item/<int:pk>/', views.editar_item, name='editar_item'),
    path('item/<int:item_id>/toggle-check/', views.atualizar_checked_item, name='atualizar_checked_item'),
    path('adicionar-receita/', views.adicionar_receita, name='adicionar_receita'),
    path('adicionar-despesa/', views.adicionar_despesa, name='adicionar_despesa'),
    path('criar-grupo/', views.criar_grupo, name='criar_grupo'),
    path('grupo/<int:grupo_id>/editar/', views.grupo_editar, name='grupo_editar'),
    path('grupo/<int:pk>/', views.grupo, name='grupo'),
    path('grupo/<int:pk>/adicionar-item/', views.grupo_adicionar_item, name='grupo_adicionar_item'),
    path('grupo/<int:grupo_id>/editar-item/<int:item_id>/', views.grupo_editar_item, name='grupo_editar_item'),
    path('grupo/<int:pk>/excluir-item/<int:item_id>/', views.grupo_excluir_item, name='grupo_excluir_item'),
    path('deletar-despesa/<int:pk>/', views.deletar_despesa, name='deletar_despesa'),
    path('deletar-receita/<int:pk>/', views.deletar_receita, name='deletar_receita'),
    path('registro/<int:pk>/excluir/', views.deletar_registro, name='deletar_registro'),
    path('offline/', views.offline, name='offline'),
    path('bye/', views.bye, name='bye'),


]
