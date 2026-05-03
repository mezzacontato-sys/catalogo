import requests
from datetime import datetime, timezone

PROJECT_ID = "catalogos-43589"
BASE = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"

def add(titulo, tipo, categoria, conteudo):
    doc = {"fields": {
        "titulo":    {"stringValue": titulo},
        "tipo":      {"stringValue": tipo},
        "categoria": {"stringValue": categoria},
        "conteudo":  {"stringValue": conteudo},
        "createdAt": {"timestampValue": datetime.now(timezone.utc).isoformat()},
    }}
    r = requests.post(f"{BASE}/assets", json=doc)
    status = "OK" if r.status_code == 200 else f"ERRO ({r.status_code})"
    print(f"[{status}] {titulo}")
    if r.status_code != 200:
        print(f"   Detalhe: {r.text[:200]}")

assets = [

    # ── LINKS ───────────────────────────────────────────────────
    ("Demo do Catálogo",
     "Link", "CatálogoPro",
     "https://catalogoweb-ten.vercel.app/catalogos/demo-catalogo/"),

    ("Página de Seleção de Produtos (cliente seleciona itens)",
     "Link", "CatálogoPro",
     "https://catalogoweb-ten.vercel.app/selecao.html"),

    ("Admin Dashboard",
     "Link", "CatálogoPro",
     "https://catalogoweb-ten.vercel.app/admin/"),

    ("Vercel — Deploy & Logs",
     "Link", "Ferramentas",
     "https://vercel.com/dashboard"),

    ("GitHub — Repositório do catálogo",
     "Link", "Ferramentas",
     "https://github.com/mezzacontato-sys/catalogo"),

    ("Firebase Console — Firestore",
     "Link", "Ferramentas",
     "https://console.firebase.google.com/project/catalogos-43589/firestore"),

    # ── CÓDIGO ──────────────────────────────────────────────────
    ("Comando: gerar catálogo para cliente",
     "Código", "Processo",
     "py gerar.py [slug-do-cliente]\n\n# Exemplos:\npy gerar.py safra\npy gerar.py madeireira-joao\n\n# O script já faz git add + commit + push automaticamente"),

    ("Pasta do projeto (abrir no Explorer)",
     "Código", "Processo",
     "C:\\Users\\Lucas\\Desktop\\catalogo"),

    # ── GUIAS ───────────────────────────────────────────────────
    ("Como criar catálogo para novo cliente — passo a passo",
     "Guia", "Processo",
     """Passo 1 — Criar pasta do cliente
  Dentro de catalogos/, criar pasta com o slug do cliente
  Exemplo: catalogos/madeireira-joao/
  Copiar o index.html de catalogos/safra/ como base

Passo 2 — Preparar CSV de produtos
  Abrir catalogo_produtos_base.csv no Google Sheets
  Ajustar produtos para o cliente (ativar/desativar, editar descrições)
  Baixar: Arquivo > Fazer download > .csv
  Salvar como catalogos/[slug]/produtos.csv

Passo 3 — Organizar fotos
  Nomear fotos seguindo a convenção (ver asset "Convenção de nomes")
  Copiar para a pasta fotos/ na raiz do projeto

Passo 4 — Rodar o gerador
  Abrir terminal na pasta do projeto:
  C:\\Users\\Lucas\\Desktop\\catalogo
  Rodar: py gerar.py [slug]
  O script gera o HTML, faz commit e push automaticamente

Passo 5 — Verificar no ar
  Aguardar ~1 minuto para o Vercel fazer o deploy
  Acessar: https://catalogoweb-ten.vercel.app/catalogos/[slug]/

Passo 6 — Entregar para o cliente
  Enviar o link pelo WhatsApp
  Cadastrar o cliente na aba Clientes do Admin"""),

    ("Convenção de nomes das fotos",
     "Guia", "Processo",
     """Foto principal:
  Formato: {id}. {nome}.jpg
  Exemplo: 1. Porta Londres.jpg
           12. Janela Pivotante.jpg

Fotos extras (aparecem no carrossel do modal):
  Formato: {id}.1 {nome}.jpg, {id}.2 {nome}.jpg ...
  Exemplo: 5.1 Porta Ripada extra.jpg
           5.2 Porta Ripada detalhe.jpg

No CSV, coluna fotos_extras:
  Separar com | (pipe), sem espaço antes/depois
  Exemplo: 5.1 Porta Ripada extra.jpg|5.2 Porta Ripada detalhe.jpg

Onde ficam as fotos:
  C:\\Users\\Lucas\\Desktop\\catalogo\\fotos\\
  (essa pasta é commitada e vai para o Vercel)"""),

    ("Como editar produtos do catálogo",
     "Guia", "Processo",
     """Usar Google Sheets (não Excel — Excel quebra encoding):

1. Abrir o arquivo CSV no Google Sheets
   Arquivo > Importar > selecionar o .csv
   Separador: vírgula, Encoding: UTF-8

2. Editar os produtos
   Colunas principais: id, nome, categoria, subcategoria,
   descricao, unidade, destaque, ativo, foto_arquivo, badge, fotos_extras

3. Exportar de volta
   Arquivo > Fazer download > .csv

4. Substituir o arquivo na pasta do cliente

5. Rodar o gerador
   py gerar.py [slug]

Dica: campo "ativo" = 1 mostra o produto, 0 oculta sem excluir
Dica: campo "destaque" = 1 coloca badge no card do produto"""),

    ("Colunas do CSV de produtos — referência rápida",
     "Nota", "Processo",
     """id           — número único do produto (1, 2, 3...)
nome         — nome do produto
categoria    — categoria principal (Portas, Janelas, Pisos...)
subcategoria — subcategoria (Internas, Externas, Ripadas...)
descricao    — texto descritivo que aparece no modal
unidade      — unidade de venda (m², un, m, kit...)
destaque     — 1 = mostra badge, 0 = sem badge
ativo        — 1 = aparece no catálogo, 0 = oculto
foto_arquivo — nome do arquivo: "1. Porta Londres.jpg"
badge        — texto do badge (ex: "Novo", "Destaque")
fotos_extras — fotos adicionais separadas por pipe |"""),
]

print(f"Adicionando {len(assets)} assets ao Firebase...\n")
for a in assets:
    add(*a)
print("\nConcluído!")
