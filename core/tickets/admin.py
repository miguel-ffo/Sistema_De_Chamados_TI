from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group

# Importe os modelos da sua aplicação de autenticação e de tickets
from authentication.models import Usuario
from .models import Categoria, Subcategoria, Chamado, Comentario, Anexo, LogTecnico, TipoAcao

# --- Admin Site Personalizado ---
class CustomAdminSite(admin.AdminSite):
    def index(self, request, extra_context=None):
        chamados_abertos = Chamado.objects.filter(status=Chamado.Status.ABERTO).count()
        chamados_em_atendimento = Chamado.objects.filter(status=Chamado.Status.EM_ATENDIMENTO).count()
        chamados_concluidos = Chamado.objects.filter(status=Chamado.Status.CONCLUIDO).count()
        chamados_fechados = Chamado.objects.filter(status=Chamado.Status.FECHADO).count()
        extra_context = extra_context or {}
        extra_context['stats'] = {
            'abertos': chamados_abertos,
            'em_atendimento': chamados_em_atendimento,
            'concluidos': chamados_concluidos,
            'fechados': chamados_fechados,
        }
        return super().index(request, extra_context=extra_context)

custom_admin_site = CustomAdminSite(name='myadmin')


# --- Configurações de Visualização ---
class CustomUserAdmin(UserAdmin):
    # Herda tudo do UserAdmin padrão, mas podemos personalizar no futuro
    pass

class LogTecnicoInline(admin.TabularInline):
    # ... (código existente, sem alterações) ...
    model = LogTecnico
    extra = 0
    readonly_fields = ('data_evento', 'tecnico', 'tipo_acao', 'detalhes')
    can_delete = False
    def has_add_permission(self, request, obj=None): return False

class ChamadoAdmin(admin.ModelAdmin):
    inlines = [LogTecnicoInline]

# --- Modelos da App 'authentication' ---
custom_admin_site.register(Usuario, CustomUserAdmin)

# --- Modelos Nativos do Django ---
custom_admin_site.register(Group, GroupAdmin) # <-- REGISTA OS GRUPOS

# --- Modelos da App 'tickets' ---
custom_admin_site.register(Categoria)
custom_admin_site.register(Subcategoria)
custom_admin_site.register(Chamado, ChamadoAdmin)
custom_admin_site.register(Comentario)
custom_admin_site.register(Anexo)
custom_admin_site.register(TipoAcao)
# LogTecnico não precisa ser registrado aqui pois já é um inline em ChamadoAdmin