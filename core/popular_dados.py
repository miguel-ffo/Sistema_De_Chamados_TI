# popular_dados.py
import json
from tickets.models import Categoria, Subcategoria, TipoAcao

print("A iniciar a importação de dados...")

# 1. Popular Categorias e Subcategorias
try:
    with open('categorias.json', 'r', encoding='utf-8') as f:
        dados_categorias = json.load(f)

    for item in dados_categorias:
        cat, created = Categoria.objects.get_or_create(nome=item['categoria_nome'])
        if created: print(f"- Categoria criada: {cat.nome}")

        for sub_nome in item['subcategorias']:
            sub, sub_created = Subcategoria.objects.get_or_create(categoria=cat, nome=sub_nome)
            if sub_created: print(f"  -> Subcategoria criada: {sub_nome}")
    print("Categorias e Subcategorias populadas com sucesso.")

except FileNotFoundError:
    print("ERRO: O ficheiro 'categorias.json' não foi encontrado.")
except Exception as e:
    print(f"Ocorreu um erro ao popular categorias: {e}")


# 2. Popular Tipos de Ação
ACOES_INICIAIS = [
    {'nome': 'CRIACAO', 'nome_exibicao': 'Chamado criado'},
    {'nome': 'ACEITE', 'nome_exibicao': 'Técnico aceitou o chamado'},
    {'nome': 'COMENTARIO', 'nome_exibicao': 'Técnico adicionou um comentário'},
    {'nome': 'STATUS_UPDATE', 'nome_exibicao': 'Técnico alterou o status'},
    {'nome': 'RESOLUCAO', 'nome_exibicao': 'Técnico resolveu o chamado'},
    {'nome': 'FECHAMENTO_USUARIO', 'nome_exibicao': 'Usuário avaliou e fechou o chamado'},
    {'nome': 'ANEXOU_ARQUIVO', 'nome_exibicao': 'Usuário anexou um arquivo'},
    
]

for acao in ACOES_INICIAIS:
    acao_obj, created = TipoAcao.objects.get_or_create(nome=acao['nome'], defaults={'nome_exibicao': acao['nome_exibicao']})
    if created: print(f"- Tipo de Ação criado: {acao['nome_exibicao']}")
print("Tipos de Ação populados com sucesso.")

print("\nImportação de dados concluída!")