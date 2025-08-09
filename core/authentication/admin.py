from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

class CustomUserAdmin(UserAdmin):
    # Por agora, vamos usar a configuração padrão, que já é excelente.
    # No futuro, você poderia adicionar campos extras aqui, por exemplo:
    # list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    pass

admin.site.register(Usuario, CustomUserAdmin)