from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def login_redirect_view(request):
    """
    Verifica o grupo do usuário e redireciona para o dashboard correto na app 'tickets'.
    """
    if request.user.groups.filter(name='CPD').exists():
        # Redireciona para a view 'dashboard_tecnico' DENTRO da app 'tickets'
        return redirect('tickets:dashboard_tecnico')
    else:
        # Redireciona para a view 'dashboard_usuario' DENTRO da app 'tickets'
        return redirect('tickets:dashboard_usuario')