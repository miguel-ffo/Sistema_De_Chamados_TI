import os
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

Usuario = settings.AUTH_USER_MODEL

class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome")

    def __str__(self):
        return self.nome

class Subcategoria(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome")
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="subcategorias")

    def __str__(self):
        return f"{self.categoria.nome} - {self.nome}"

class Chamado(models.Model):
    class Prioridade(models.TextChoices):
        BAIXA = 'BAIXA', 'Baixa'
        MEDIA = 'MEDIA', 'Média'
        ALTA = 'ALTA', 'Alta'

    class Status(models.TextChoices):
        ABERTO = 'ABERTO', 'Aberto'
        EM_ATENDIMENTO = 'EM_ATENDIMENTO', 'Em Atendimento'
        AGUARDANDO_RESPOSTA = 'AGUARDANDO_RESPOSTA', 'Aguardando Resposta'
        AGUARDANDO_TERCEIROS = 'AGUARDANDO_TERCEIROS', 'Aguardando Terceiros'
        CONCLUIDO = 'CONCLUIDO', 'Concluído'
        FECHADO = 'FECHADO', 'Fechado'
        CANCELADO = 'CANCELADO', 'Cancelado'

    # --- Campos e Relacionamentos ---
    usuario = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name="chamados_criados", verbose_name="Usuário Solicitante")
    tecnico = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name="chamados_atendidos", verbose_name="Técnico Responsável")
    subcategoria = models.ForeignKey(Subcategoria, on_delete=models.PROTECT, verbose_name="Subcategoria")
    observacao = models.TextField(blank=True, null=True, verbose_name="Observação")
    prioridade = models.CharField(max_length=20, choices=Prioridade.choices, default=Prioridade.BAIXA, verbose_name="Prioridade")
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.ABERTO, verbose_name="Status")
    data_abertura = models.DateTimeField(auto_now_add=True, verbose_name="Data de Abertura")
    data_conclusao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Conclusão")

    # --- Métodos do Modelo ---
    def __str__(self):
        return f"Chamado #{self.id} ({self.subcategoria.nome}) - Status: {self.get_status_display()}"

    @property
    def esta_finalizado(self):
        return self.status in [
            self.Status.CONCLUIDO,
            self.Status.FECHADO,
            self.Status.CANCELADO,
        ]

class Comentario(models.Model):
    chamado = models.ForeignKey(Chamado, on_delete=models.CASCADE, related_name="comentarios")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, verbose_name="Autor do Comentário")
    conteudo = models.TextField(verbose_name="Conteúdo")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")

    def __str__(self):
        return f"Comentário de {self.usuario.username} no Chamado #{self.chamado.id}"

class Anexo(models.Model):
    chamado = models.ForeignKey(Chamado, on_delete=models.CASCADE, related_name="anexos")
    caminho = models.CharField(max_length=512, help_text="Caminho de rede para o anexo")
    usuario_upload = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, help_text="Usuário que fez o upload")
    data_upload = models.DateTimeField(auto_now_add=True, verbose_name="Data do Upload")

    def __str__(self):
        return os.path.basename(self.caminho)

class Avaliacao(models.Model):
    chamado = models.OneToOneField(Chamado, on_delete=models.CASCADE, related_name="avaliacao")
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, verbose_name="Avaliador")
    nota = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Nota de 1 a 5"
    )
    descricao = models.TextField(blank=True, null=True, verbose_name="Comentário da Avaliação")
    data_avaliacao = models.DateTimeField(auto_now_add=True, verbose_name="Data da Avaliação")

    def __str__(self):
        return f"Avaliação do Chamado #{self.chamado.id} - Nota: {self.nota}"


class TipoAcao(models.Model):
    nome = models.CharField(max_length=50, unique=True, help_text="Nome interno, ex: ACEITE_TECNICO")
    nome_exibicao = models.CharField(max_length=100, help_text="Nome amigável, ex: 'Técnico aceitou o chamado'")

    def __str__(self):
        return self.nome_exibicao

class LogTecnico(models.Model):
    chamado = models.ForeignKey(Chamado, on_delete=models.CASCADE, related_name="logs")
    tecnico = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    tipo_acao = models.ForeignKey(TipoAcao, on_delete=models.PROTECT)
    data_evento = models.DateTimeField(auto_now_add=True)
    detalhes = models.TextField(blank=True, null=True)

    class Meta:
        # Ordena os logs do mais recente para o mais antigo por padrão
        ordering = ['-data_evento']

    def __str__(self):
        return f"{self.data_evento.strftime('%d/%m/%Y %H:%M')} - {self.tecnico.username} - {self.tipo_acao.nome_exibicao}"