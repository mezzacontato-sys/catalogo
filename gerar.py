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

  Com logo e cor:
  python gerar.py "Madeireira São João" "11999999999" "selecao.csv" "/fotos/logos/logo-joao.png" "#2D5016"

  A logo deve estar na pasta fotos/logos/ (ou ser uma URL externa).
  A cor é um código hex — ex: #2D5016 (verde), #8B1A1A (vinho), #1A3A5C (azul).
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


def gerar(nome_empresa, whatsapp, csv_path, logo_url="", cor="#111"):
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

    # ── Filtrar apenas produtos ativos ────────────────────────
    produtos_raw = [p for p in produtos_raw
                    if p.get('ativo', 'sim').strip() in ('sim', '1', '')]

    # ── Montar array de produtos JavaScript ───────────────────
    produtos_js = []
    for p in produtos_raw:
        foto_arquivo = p.get('foto_arquivo', '').strip()
        badge        = p.get('badge', '').strip()
        extras_raw   = p.get('fotos_extras', '').strip()

        # Monta lista de fotos: principal + extras separadas por |
        fotos = [f"/fotos/{foto_arquivo}"]
        if extras_raw:
            for extra in extras_raw.split('|'):
                extra = extra.strip()
                if extra:
                    fotos.append(f"/fotos/{extra}")

        produtos_js.append({
            "id":       int(p['id']) if str(p['id']).isdigit() else p['id'],
            "nome":     p.get('nome', '').strip(),
            "cat":      p.get('categoria', '').strip(),
            "sub":      p.get('subcategoria', '').strip(),
            "desc":     p.get('descricao', '').strip(),
            "un":       p.get('unidade', '').strip(),
            "foto":     f"/fotos/{foto_arquivo}",
            "fotos":    fotos,
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

    # ── Normalizar LOGO_URL ───────────────────────────────────
    # Se for caminho local (não URL http), extrai a parte a partir de "fotos/"
    if logo_url and not logo_url.startswith('http'):
        logo_norm = logo_url.replace('\\', '/')
        idx = logo_norm.find('fotos/')
        if idx >= 0:
            logo_url = '/' + logo_norm[idx:]
        elif not logo_url.startswith('/'):
            logo_url = '/' + logo_norm

    html = re.sub(
        r'var LOGO_URL\s*=\s*"[^"]*"',
        f'var LOGO_URL     = "{logo_url}"',
        html
    )

    # ── Substituir texto do banner ────────────────────────────
    html = re.sub(
        r'<div id="banner">[^<]*</div>',
        f'<div id="banner">{nome_empresa}</div>',
        html
    )

    # ── Injetar cor personalizada ─────────────────────────────
    cor_base = cor if cor and cor != "#111" else "#111"
    style = (
        f'<style id="cor-cliente">'
        f'#banner{{background:{cor_base}!important}}'
        f'.chip.active,.sub-chip.active{{background:{cor_base}!important;border-color:{cor_base}!important;color:#fff!important}}'
        f'@media(hover:hover){{.chip:hover,.sub-chip:hover{{border-color:{cor_base}!important;color:{cor_base}!important}}}}'
        f'.card-add{{background:{cor_base}!important}}'
        f'#cart-btn{{background:{cor_base}!important}}'
        f'#search{{border-color:{cor_base}!important}}'
        f'#cart-count{{background:{cor_base}!important}}'
        f'</style>'
    )
    html = html.replace('</head>', style + '\n</head>', 1)

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

    print(f"\nCatalogo gerado: {output_file}")
    print(f"Subindo para o ar automaticamente...\n")

    # ── Git: add, commit, push ────────────────────────────────
    import subprocess

    def git(args, desc):
        result = subprocess.run(["git"] + args, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"ERRO em '{desc}':\n{result.stderr.strip()}")
            sys.exit(1)
        return result.stdout.strip()

    git(["add", f"catalogos/{slug}/"], "git add catalogo")
    git(["add", "fotos/logos/"], "git add logos")   # garante que logos novas sobem
    git(["commit", "-m", f"add: catalogo {nome_empresa}"], "git commit")
    git(["push"], "git push")

    # ── Resultado final ───────────────────────────────────────
    url = f"{VERCEL_URL}/catalogos/{slug}/"
    print(f"""
Catalogo no ar!
   Empresa  : {nome_empresa}
   WhatsApp : {whatsapp}
   Produtos : {len(produtos_js)}

URL do cliente:
   {url}

Aguarde ~30 segundos para a Vercel terminar o deploy, depois envie o link.
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
    cor   = sys.argv[5] if len(sys.argv) > 5 else "#111"

    # Garantir DDI 55 (Brasil)
    if not tel.startswith('55'):
        tel = '55' + tel

    gerar(nome, tel, arq, logo, cor)
