import requests

PROJECT_ID = "catalogos-43589"
BASE = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"

# Buscar o asset do guia para atualizar o link
r = requests.get(f"{BASE}/assets?pageSize=50")
docs = r.json().get("documents", [])

updates = {
    "Como criar catálogo para novo cliente — passo a passo": """Passo 1 — Criar pasta do cliente
  Dentro de catalogos/, criar pasta com o slug do cliente
  Exemplo: catalogos/madeireira-joao/
  Copiar o index.html de catalogos/safra/ como base

Passo 2 — Preparar CSV de produtos
  Abrir catalogo_produtos_base.csv no Google Sheets
  Ajustar produtos para o cliente (ativar/desativar, editar descricoes)
  Baixar: Arquivo > Fazer download > .csv
  Salvar como catalogos/[slug]/produtos.csv

Passo 3 — Organizar fotos
  Nomear fotos seguindo a convencao (ver asset "Convencao de nomes")
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
  Enviar o link do catalogo pelo WhatsApp
  Para o cliente selecionar produtos antes: catalogomadeireira.com.br/selecao.html
  Cadastrar o cliente na aba Clientes do Admin""",

    "Pagina de Selecao de Produtos (cliente seleciona itens)": None,  # link update
}

for doc in docs:
    fields = doc.get("fields", {})
    titulo = fields.get("titulo", {}).get("stringValue", "")
    doc_name = doc["name"]
    doc_id = doc_name.split("/")[-1]

    if titulo == "Como criar catálogo para novo cliente — passo a passo":
        new_content = updates[titulo]
        payload = {"fields": {
            "titulo":    {"stringValue": titulo},
            "tipo":      {"stringValue": fields.get("tipo",{}).get("stringValue","Guia")},
            "categoria": {"stringValue": fields.get("categoria",{}).get("stringValue","Processo")},
            "conteudo":  {"stringValue": new_content},
        }}
        mask = "updateMask.fieldPaths=titulo&updateMask.fieldPaths=tipo&updateMask.fieldPaths=categoria&updateMask.fieldPaths=conteudo"
        r2 = requests.patch(f"{BASE}/assets/{doc_id}?{mask}", json=payload)
        print(f"[{'OK' if r2.status_code==200 else 'ERRO'}] Guia atualizado")

    if titulo == "Página de Seleção de Produtos (cliente seleciona itens)":
        payload = {"fields": {
            "titulo":    {"stringValue": "Pagina de Selecao de Produtos (cliente escolhe itens)"},
            "tipo":      {"stringValue": "Link"},
            "categoria": {"stringValue": "CatalogoPro"},
            "conteudo":  {"stringValue": "https://catalogomadeireira.com.br/selecao.html"},
        }}
        mask = "updateMask.fieldPaths=titulo&updateMask.fieldPaths=tipo&updateMask.fieldPaths=categoria&updateMask.fieldPaths=conteudo"
        r2 = requests.patch(f"{BASE}/assets/{doc_id}?{mask}", json=payload)
        print(f"[{'OK' if r2.status_code==200 else 'ERRO'}] Link selecao.html atualizado")

print("Pronto!")
