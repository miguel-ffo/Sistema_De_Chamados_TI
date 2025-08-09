# chamados/forms.py
from django import forms
from .models import Chamado, Comentario, Avaliacao, Anexo

class ChamadoForm(forms.ModelForm):
    class Meta:
        model = Chamado
        # Simplesmente removemos 'prioridade' da lista
        fields = ['subcategoria', 'observacao']

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['conteudo']
        widgets = {
            'conteudo': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Adicione seu comentário aqui...'}),
        }

class AtualizarStatusForm(forms.ModelForm):
    class Meta:
        model = Chamado
        fields = ['status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Lista de status que o técnico NÃO PODE selecionar manualmente
        status_excluidos = [
            Chamado.Status.ABERTO,
            Chamado.Status.CANCELADO,
            Chamado.Status.FECHADO,
            Chamado.Status.CONCLUIDO,
        ]
        
        todas_as_opcoes = Chamado.Status.choices
        
        # Cria a nova lista de opções, mantendo apenas as permitidas
        opcoes_para_tecnico = [
            opcao for opcao in todas_as_opcoes if opcao[0] not in status_excluidos
        ]
        
        # Atualiza as opções do campo 'status' neste formulário
        self.fields['status'].choices = opcoes_para_tecnico

class AnexoForm(forms.ModelForm):
    class Meta:
        model = Anexo
        fields = ['caminho']
        widgets = {
            'caminho': forms.TextInput(attrs={'placeholder': 'Cole aqui o caminho de rede completo do ficheiro'}),
        }

class AvaliacaoForm(forms.ModelForm):
    nota = forms.ChoiceField(
        label="Nota de Atendimento",
        choices=[(i, str(i)) for i in range(1, 6)], 
        widget=forms.RadioSelect
    )

    class Meta:
        model = Avaliacao
        fields = ['nota', 'descricao']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona a classe do Bootstrap ao campo de descrição
        self.fields['descricao'].widget.attrs.update({
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Deixe um comentário opcional...'
        })