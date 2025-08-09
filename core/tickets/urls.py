from django.urls import path
from . import views

app_name = 'tickets' 

urlpatterns = [
    # --- URLs para todos os usuários logados ---
    path('', views.lista_chamados, name='lista'),
    path('<int:chamado_id>/', views.detalhe_chamado, name='detalhe'),
    path('historico/', views.historico_chamados, name='historico'),

    # --- URLs para USUÁRIOS normais ---
    path('criar/', views.criar_chamado, name='criar'),
    path('<int:chamado_id>/cancelar/', views.cancelar_chamado, name='cancelar'),

    # --- URLs para TÉCNICOS ---
    path('<int:chamado_id>/aceitar/', views.aceitar_chamado, name='aceitar'),
    path('<int:chamado_id>/atualizar_status/', views.atualizar_status, name='atualizar_status'),
    path('<int:chamado_id>/resolver/', views.resolver_chamado, name='resolver'),

    # --- URLs para ações específicas ---
    path('<int:chamado_id>/avaliar/', views.avaliar_e_fechar_chamado, name='avaliar_e_fechar'),
    path('<int:chamado_id>/adicionar_anexo/', views.adicionar_anexo, name='adicionar_anexo'),
    path('<int:chamado_id>/adicionar_comentario/', views.adicionar_comentario, name='adicionar_comentario'),

    # URLs para dashboards
    path('dashboard/usuario/', views.dashboard_usuario, name='dashboard_usuario'),
    path('dashboard/tecnico/', views.dashboard_tecnico, name='dashboard_tecnico'),



]