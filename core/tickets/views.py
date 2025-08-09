from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST # Adicione esta importação
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Chamado, Comentario, Anexo, LogTecnico, TipoAcao
from .forms import ChamadoForm, ComentarioForm, AtualizarStatusForm, AnexoForm, AvaliacaoForm
from django.utils import timezone

# View principal que mostra a lista de chamados
@login_required
def lista_chamados(request):
    # Verificamos se o usuário é do grupo 'CPD' (ou seja, se é técnico)
    is_tecnico = request.user.groups.filter(name='CPD').exists()

    if is_tecnico:
        # Se for técnico, mostra todos os chamados
        lista = Chamado.objects.all().order_by('-data_abertura')
    else:
        # Se for um usuário comum, mostra apenas os seus próprios chamados
        lista = Chamado.objects.filter(usuario=request.user).order_by('-data_abertura')

    return render(request, 'tickets/dashboard_tecnico.html', {'chamados': lista, 'is_tecnico': is_tecnico})

# View para ver os detalhes de um chamado específico
@login_required
def detalhe_chamado(request, chamado_id):
    chamado = get_object_or_404(Chamado, id=chamado_id)
    is_tecnico = request.user.groups.filter(name='CPD').exists()

    # Permissão: apenas o criador do chamado ou um técnico podem ver
    if not (chamado.usuario == request.user or is_tecnico):
        return HttpResponseForbidden("Você não tem permissão para ver este chamado.")
    
    # Busca os comentários associados a este chamado
    comentarios = Comentario.objects.filter(chamado=chamado).order_by('data_criacao')
    
    # Prepara o formulário de novo comentário (será processado por outra view)
    form_comentario = ComentarioForm()
    form_status = AtualizarStatusForm(instance=chamado)

    context = {
        'chamado': chamado,
        'is_tecnico': is_tecnico,
        'comentarios': comentarios,
        'form_comentario': ComentarioForm(),
        'form_status': AtualizarStatusForm(instance=chamado),
        'form_anexo': AnexoForm(),
    }

    return render(request, 'tickets/detalhe_chamado.html', context)

# View para um usuário normal criar um chamado

@login_required
def criar_chamado(request):

    # Conta quantos chamados o usuário tem com status 'CONCLUIDO' (pendente de avaliação)
    chamados_pendentes = Chamado.objects.filter(
        usuario=request.user, 
        status=Chamado.Status.CONCLUIDO
    ).count()

    limite = 3
    if chamados_pendentes >= limite:
        # Se o limite foi atingido, mostra uma mensagem de erro em vez do formulário
        return render(request, 'tickets/limite_chamados_atingido.html', {
            'limite': limite, 
            'pendentes': chamados_pendentes
        })

    if request.user.groups.filter(name='TI').exists():
    # Redireciona o técnico para a sua tela principal.
        return redirect('tickets:lista') 
    
    if request.method == 'POST':
        form = ChamadoForm(request.POST, request.FILES)
        if form.is_valid():
            chamado = form.save(commit=False)
            chamado.usuario = request.user
            
            # Exemplo: Se o usuário for do grupo 'Diretoria', a prioridade é alta.
            if request.user.groups.filter(name='Diretoria').exists():
                chamado.prioridade = Chamado.Prioridade.ALTA
            # Exemplo: Se a categoria for 'Parada Geral', a prioridade é alta.
            elif form.cleaned_data['subcategoria'].categoria.nome == 'Parada Geral':
                chamado.prioridade = Chamado.Prioridade.ALTA
            # Se nenhuma regra especial for aplicada, o valor padrão 'BAIXA' será usado.

            
            chamado.save()
            LogTecnico.objects.create(
                chamado=chamado,
                tecnico=request.user, # Aqui, o 'tecnico' é o usuário que fez a ação
                tipo_acao=TipoAcao.objects.get(nome='CRIACAO')
            )
            return redirect('tickets:detalhe', chamado_id=chamado.id)
    else:
        form = ChamadoForm()
    
    return render(request, 'tickets/criar_chamado.html', {'form': form})

# View para um técnico aceitar um chamado
@login_required
def aceitar_chamado(request, chamado_id):
    is_tecnico = request.user.groups.filter(name='CPD').exists()
    if not is_tecnico:
        return HttpResponseForbidden("Apenas técnicos podem aceitar chamados.")

    chamado = get_object_or_404(Chamado, id=chamado_id)
    
    # Lógica para aceitar o chamado (geralmente via POST, mas simplificado aqui)
    chamado.tecnico = request.user
    chamado.status = Chamado.Status.EM_ATENDIMENTO
    chamado.save()

    # ADICIONAR LOG
    LogTecnico.objects.create(
        chamado=chamado,
        tecnico=request.user,
        tipo_acao=TipoAcao.objects.get(nome='ACEITE')
    )
    
    return redirect('tickets:detalhe', chamado_id=chamado.id)

@login_required
def cancelar_chamado(request, chamado_id):
    chamado = get_object_or_404(Chamado, id=chamado_id)

    # Lógica de Permissão: Apenas o criador do chamado pode cancelar.
    if chamado.usuario != request.user:
        return HttpResponseForbidden("Acesso negado. Apenas o criador pode cancelar o chamado.")
    
    # Lógica de Negócio: Apenas chamados 'Abertos' podem ser cancelados.
    if chamado.status != Chamado.Status.ABERTO:
        # Você pode mostrar uma mensagem de erro aqui se quiser
        return redirect('tickets:detalhe', chamado_id=chamado.id)

    if request.method == 'POST':
        # Se o formulário foi submetido, cancela o chamado
        chamado.status = Chamado.Status.CANCELADO
        chamado.save()
        return redirect('tickets:detalhe', chamado_id=chamado.id)

    # Se for um pedido GET, mostra a página de confirmação
    return render(request, 'tickets/cancelar_chamado.html', {'chamado': chamado})

@login_required
def resolver_chamado(request, chamado_id):
    chamado = get_object_or_404(Chamado, id=chamado_id)

    # Lógica de Permissão: Apenas o técnico responsável pode resolver o chamado.
    if chamado.tecnico != request.user:
        return HttpResponseForbidden("Acesso negado. Apenas o técnico responsável pode resolver este chamado.")

    # Lógica de Negócio: O chamado só pode ser resolvido se estiver 'Em Atendimento'.
    if chamado.status != Chamado.Status.EM_ATENDIMENTO:
        # Redireciona de volta se o status não for o correto
        return redirect('tickets:detalhe', chamado_id=chamado.id)

    if request.method == 'POST':
        # Se o formulário foi submetido, resolve o chamado
        chamado.status = Chamado.Status.CONCLUIDO
        chamado.data_conclusao = timezone.now() # Regista a data/hora exata da conclusão
        chamado.save()

        # ADICIONAR LOG
        LogTecnico.objects.create(
            chamado=chamado,
            tecnico=request.user,
            tipo_acao=TipoAcao.objects.get(nome='RESOLUCAO')
        )
        # Adicionar ao log, etc.
        return redirect('tickets:detalhe', chamado_id=chamado.id)

    # Se for um pedido GET, mostra a página de confirmação
    return render(request, 'tickets/resolver_chamado.html', {'chamado': chamado})

# chamados/views.py

# ... (outras importações) ...

@login_required
def dashboard_usuario(request):
    """
    Mostra o painel principal para usuários comuns.
    """
    # Mostra apenas os chamados criados pelo próprio usuário.
    meus_chamados = Chamado.objects.filter(usuario=request.user).exclude(status=Chamado.Status.FECHADO).order_by('-data_abertura')
    return render(request, 'tickets/dashboard_usuario.html', {'chamados': meus_chamados})

@login_required
def dashboard_tecnico(request):
    """
    Mostra o painel principal para técnicos do CPD.
    """
    # Lógica de permissão: apenas membros do CPD podem aceder.
    if not request.user.groups.filter(name='CPD').exists():
        return HttpResponseForbidden("Acesso negado. Esta página é apenas para técnicos.")

    # Mostra chamados abertos e não atribuídos, por exemplo.
    chamados_na_fila = Chamado.objects.filter(status='ABERTO', tecnico__isnull=True).order_by('data_abertura')
# Define a lista de status que representam um chamado finalizado
    status_finalizados = [
        Chamado.Status.CONCLUIDO,
        Chamado.Status.FECHADO,
        Chamado.Status.CANCELADO,
    ]

    # A nova consulta exclui todos os chamados cujo status esteja nessa lista
    meus_atendimentos = Chamado.objects.filter(tecnico=request.user).exclude(status__in=status_finalizados).order_by('data_abertura')

    context = {
        'chamados_na_fila': chamados_na_fila,
        'meus_atendimentos': meus_atendimentos,
    }
    return render(request, 'tickets/dashboard_tecnico.html', context)


    # tickets/views.py



@login_required
@require_POST
def adicionar_comentario(request, chamado_id):
    chamado = get_object_or_404(Chamado, id=chamado_id)
    is_tecnico = request.user.groups.filter(name='CPD').exists()
    pode_comentar = False
    
    # 1. Se o usuário logado for um técnico, ele pode comentar.
    if is_tecnico:
        pode_comentar = True
    # 2. OU, se o usuário logado for o dono do chamado E o status do chamado
    #    for "Aguardando Resposta", ele também pode comentar.
    elif chamado.usuario == request.user and chamado.status == Chamado.Status.AGUARDANDO_RESPOSTA:
        pode_comentar = True
    
    # Se nenhuma das condições acima for verdadeira, negamos o acesso.
    if not pode_comentar:
        return HttpResponseForbidden("Você não tem permissão para comentar neste momento.")

    form = ComentarioForm(request.POST)

    if form.is_valid():
        comentario = form.save(commit=False)
        comentario.chamado = chamado
        comentario.usuario = request.user
        comentario.save()

        # Adiciona o log APENAS se quem comentou for um técnico
        if request.user.groups.filter(name='TI').exists():
            LogTecnico.objects.create(
                chamado=chamado,
                tecnico=request.user,
                tipo_acao=TipoAcao.objects.get(nome='COMENTARIO'),
                detalhes=comentario.conteudo[:100] # Guarda os primeiros 100 caracteres do comentário
            )
        # Lógica Bónus: Se foi um usuário comum que respondeu,
        # mudamos o status de volta para 'Em Atendimento' automaticamente.
        if not is_tecnico:
            chamado.status = Chamado.Status.EM_ATENDIMENTO
            chamado.save()

    # No final, redireciona de volta para a página de detalhes.
    return redirect('tickets:detalhe', chamado_id=chamado.id)


@login_required
@require_POST
def atualizar_status(request, chamado_id):
    chamado = get_object_or_404(Chamado, id=chamado_id)

    # Lógica de permissão
    if chamado.tecnico != request.user:
        return HttpResponseForbidden("Acesso negado.")

    form = AtualizarStatusForm(request.POST, instance=chamado)

    if form.is_valid():
        chamado_atualizado = form.save(commit=False)

        if chamado_atualizado.status == Chamado.Status.CONCLUIDO:
            chamado_atualizado.data_conclusao = timezone.now()

        chamado_atualizado.save()


        LogTecnico.objects.create(
            chamado=chamado_atualizado,
            tecnico=request.user,
            tipo_acao=TipoAcao.objects.get(nome='STATUS_UPDATE'),
            detalhes=f"Status alterado para: {chamado_atualizado.get_status_display()}"
        )

    return redirect('tickets:detalhe', chamado_id=chamado.id)

@login_required
@require_POST
def adicionar_anexo(request, chamado_id):
    chamado = get_object_or_404(Chamado, id=chamado_id)

    if chamado.usuario != request.user or chamado.status != Chamado.Status.AGUARDANDO_RESPOSTA:
        return HttpResponseForbidden("Você não tem permissão para adicionar um anexo neste momento.")
    
    # Não precisamos mais de request.FILES
    form = AnexoForm(request.POST)
    if form.is_valid():
        anexo = form.save(commit=False)
        anexo.chamado = chamado
        anexo.usuario_upload = request.user
        anexo.save()
        LogTecnico.objects.create(
                chamado=chamado,
                tecnico=request.user, # Aqui, o 'tecnico' é o usuário que fez a ação
                tipo_acao=TipoAcao.objects.get(nome='ANEXOU_ARQUIVO')
            )


    return redirect('tickets:detalhe', chamado_id=chamado.id)

@login_required
def avaliar_e_fechar_chamado(request, chamado_id):
    chamado = get_object_or_404(Chamado, id=chamado_id)

    # Permissão: apenas o dono do chamado pode avaliar, e apenas se estiver 'CONCLUIDO'
    if chamado.usuario != request.user or chamado.status != Chamado.Status.CONCLUIDO:
        return HttpResponseForbidden("Ação não permitida.")

    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.chamado = chamado
            avaliacao.usuario = request.user
            avaliacao.save()

            # O passo final: muda o status do chamado para 'FECHADO'
            chamado.status = Chamado.Status.FECHADO
            chamado.save()
            LogTecnico.objects.create(
                chamado=chamado,
                tecnico=request.user, 
                tipo_acao=TipoAcao.objects.get(nome='FECHAMENTO_USUARIO')
            )

            return redirect('tickets:detalhe', chamado_id=chamado.id)
    else:
        form = AvaliacaoForm()

    return render(request, 'tickets/avaliar_chamado.html', {'form': form, 'chamado': chamado})

@login_required
def historico_chamados(request):
    """
    Mostra uma lista de todos os chamados com status 'FECHADO'.
    A lista é filtrada de acordo com o perfil do usuário (comum ou técnico).
    """
    is_tecnico = request.user.groups.filter(name='CPD').exists()

    if is_tecnico:
        # Se for técnico, mostra TODOS os chamados fechados, ordenados pelo mais recente.
        lista_fechados = Chamado.objects.filter(status=Chamado.Status.FECHADO).order_by('-data_conclusao')
    else:
        # Se for um usuário comum, mostra apenas os SEUS chamados fechados.
        lista_fechados = Chamado.objects.filter(
            usuario=request.user, 
            status=Chamado.Status.FECHADO
        ).order_by('-data_conclusao')

    context = {
        'chamados': lista_fechados,
        'is_tecnico': is_tecnico
    }
    
    return render(request, 'tickets/historico_chamados.html', context)