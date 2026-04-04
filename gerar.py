#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gerar.py — Gerador de catálogo digital

Uso:
  python gerar.py "Nome da Empresa" "11999999999" "selecao-cliente.csv"
  python gerar.py "Nome da Empresa" "11999999999" "selecao-cliente.csv" "https://link-do-logo.png"

Exemplos:
  python gerar.py "Madeireira São João" "11999999999" "selecao.csv"
  python gerar.py "Madeireira São João" "11999999999" "selecao.csv" "https://i.imgur.com/logo.png"
"""

import csv
import json
import sys
import os
import re
import unicodedata
from pathlib import Path

# ─── Configuração ────────────────────────────────────────────────────────────
VERCEL_URL    = "https://catalogoweb-ten.vercel.app"
TEMPLATE_PATH = Path("catalogos/safra/index.html")
# ─────────────────────────────────────────────────────────────────────────────


def slugify(texto):
    """Converte 'Madeireira São João' → 'madeireira-sao-joao'"""
    texto = unicodedata.normalize('NFKD', texto)
    texto = texto.encode('ascii', 'ignore').decode('ascii')
    texto = texto.lower()
    texto = re.sub(r'[^a-z0-9]+', '-', texto)
    return texto.strip('-')


def ler_csv(caminho):
    """Lê o CSV com fallback de encoding (UTF-8, latin-1, Windows-1252)."""
    for enc in ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']:
        try:
            with open(caminho, newline='', encoding=enc) as f:
                reader = csv.DictReader(f)
                produtos = [r for r in reader if r.get('id') and r.get('nome')]
            if produtos:
                return produtos
        except Exception:
            continue
    return []


def gerar(nome_empresa, whatsapp, csv_path, logo_url=""):
    # ── Validações ────────────────────────────────────────────
    if not TEMPLATE_PATH.exists():
        print(f"\nERRO: Template não encontrado em '{TEMPLATE_PATH}'")
        print("Certifique-se de rodar este script dentro da pasta do projeto.")
        sys.exit(1)

    if not Path(csv_path).exists():
        print(f"\nERRO: Arquivo CSV não encontrado: '{csv_path}'")
        sys.exit(1)

    # ── Ler template ──────────────────────────────────────────
    print(f"\nLendo template...")
    with open(TEMPLATE_PATH, 'r', encoding='utf-8', errors='replace') as f:
        html = f.read()

    # ── Ler produtos do CSV ───────────────────────────────────
    print(f"Lendo produtos do CSV...")
    produtos_raw = ler_csv(csv_path)

    if not produtos_raw:
        print(f"\nERRO: Nenhum produto encontrado em '{csv_path}'")
        print("Verifique se o arquivo tem as colunas: id, nome, categoria, subcategoria, descricao, unidade, foto_arquivo")
        sys.exit(1)

    # ── Montar array de produtos JavaScript ───────────────────
    produtos_js = []
    for p in produtos_raw:
        foto_arquivo = p.get('foto_arquivo', '').strip()
        badge        = p.get('badge', '').strip()

        produtos_js.append({
            "id":       int(p['id']) if str(p['id']).isdigit() else p['id'],
            "nome":     p.get('nome', '').strip(),
            "cat":      p.get('categoria', '').strip(),
            "sub":      p.get('subcategoria', '').strip(),
            "desc":     p.get('descricao', '').strip(),
            "un":       p.get('unidade', '').strip(),
            "foto":     f"/fotos/{foto_arquivo}",
            "destaque": badge,
        })

    # ── Substituir NOME_EMPRESA ───────────────────────────────
    html = re.sub(
        r'var NOME_EMPRESA\s*=\s*"[^"]*"',
        f'var NOME_EMPRESA = "{nome_empresa}"',
        html
    )

    # ── Substituir WHATSAPP ───────────────────────────────────
    html = re.sub(
        r'var WHATSAPP\s*=\s*"[^"]*"',
        f'var WHATSAPP     = "{whatsapp}"',
        html
    )

    # ── Substituir LOGO_URL ───────────────────────────────────
    html = re.sub(
        r'var LOGO_URL\s*=\s*"[^"]*"',
        f'var LOGO_URL     = "{logo_url}"',
        html
    )

    # ── Substituir PRODUCTS (pode ter base64 enorme) ──────────
    marker_inicio = 'var PRODUCTS = ['
    marker_fim    = '];'

    idx_inicio = html.find(marker_inicio)
    if idx_inicio == -1:
        print("\nERRO: Não foi possível encontrar 'var PRODUCTS' no template.")
        sys.exit(1)

    idx_fim = html.find(marker_fim, idx_inicio) + len(marker_fim)
    products_json = json.dumps(produtos_js, ensure_ascii=False)
    html = html[:idx_inicio] + f'var PRODUCTS = {products_json};' + html[idx_fim:]

    # ── Salvar ────────────────────────────────────────────────
    slug       = slugify(nome_empresa)
    output_dir = Path("catalogos") / slug
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "index.html"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    # ── Resultado ─────────────────────────────────────────────
    print(f"""
✅ Catálogo gerado com sucesso!
   Empresa  : {nome_empresa}
   WhatsApp : {whatsapp}
   Produtos : {len(produtos_js)}
   Arquivo  : {output_file}

📋 Próximos passos:
   1. git add catalogos/{slug}/
   2. git commit -m "add: catálogo {nome_empresa}"
   3. git push

🔗 URL do cliente (após push):
   {VERCEL_URL}/catalogos/{slug}/
""")


# ── Ponto de entrada ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__)
        print("ERRO: Argumentos insuficientes.\n")
        sys.exit(1)

    nome  = sys.argv[1]
    tel   = re.sub(r'\D', '', sys.argv[2])   # remove tudo que não é número
    arq   = sys.argv[3]
    logo  = sys.argv[4] if len(sys.argv) > 4 else ""

    # Garantir DDI 55 (Brasil)
    if not tel.startswith('55'):
        tel = '55' + tel

    gerar(nome, tel, arq, logo)
