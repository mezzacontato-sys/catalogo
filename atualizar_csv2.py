# -*- coding: utf-8 -*-
import csv

CSV = r"C:\Users\Lucas\Desktop\catalogo\catalogo_produtos_base.csv"

# Alteracoes em produtos existentes
UPDATES = {
    # Porta Lateral Colmeia → Janela Lateral Colmeia (com fotos novas)
    3:  {"nome": "Janela Lateral Colmeia", "categoria": "Janelas",
         "subcategoria": "Especial",
         "foto_arquivo": "janela Lateral Colmeia.jpg",
         "fotos_extras": "janela-Lateral Colmeia simulacao.png"},

    # Simulacoes novas encontradas na pasta
    8:  {"fotos_extras": "almofada sacada simulaçao.png"},
    10: {"fotos_extras": "itaparica simulaçao.png"},
    12: {"fotos_extras": "Londres 2 vidros simulacao.png"},
    27: {"fotos_extras": "Colmeia Almofada simulaçao.png"},
    28: {"fotos_extras": "colmeia reta simulacao.png"},
    29: {"foto_arquivo": "Colmeia c Veneziana.jpg",
         "fotos_extras": "Colmeia c Veneziana simulacao.png"},
    30: {"fotos_extras": "Colméia Trabalhada Reta c Almofada simulacao.png"},

    # Porta Colmeia Reta Correr: remover almofada (vira produto separado)
    32: {"fotos_extras": "Colmeia Reta Correr Simulação.png"},

    # Porta Colmeia Quadrada em Teca → Porta Londres 1 Vidro
    22: {"nome": "Porta Londres 1 Vidro", "subcategoria": "Sólidas",
         "descricao": "Porta Londres com vidro central. Beleza clássica com entrada de luz natural.",
         "foto_arquivo": "Londres 1 Vidro.jpg",
         "fotos_extras": "Londres 1 Vidro simulacao.png"},

    # Desativar: Janela Tabicao Correr e Lambri
    44: {"ativo": "nao"},
    56: {"ativo": "nao"},

    # Janela Tabicao (id 59): atualizar fotos (jane 8.jpg foi substituida)
    59: {"foto_arquivo": "Janela Tabicao.jpg",
         "fotos_extras": "Janela Tabicao Aberta.png|Janela Tabicao Simulação.png"},
}

# Novo produto: Porta Colmeia Reta Almofada Correr (era extra do id 32)
NOVO = {
    "id": "60",
    "nome": "Porta Colmeia Reta Almofada Correr",
    "categoria": "Portas",
    "subcategoria": "Colmeia",
    "descricao": "Porta colmeia reta com almofada central em 4 folhas tipo correr. Elegância para grandes vãos.",
    "unidade": "cj",
    "destaque": "sim",
    "ativo": "sim",
    "foto_arquivo": "Colmeia Reta Almofada Correr.jpg",
    "badge": "",
    "fotos_extras": "Colmeia Reta Almofada Correr Simulação.png",
}

# Ler CSV
rows = []
fieldnames = []
with open(CSV, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        pid = int(row["id"])
        if pid in UPDATES:
            row.update(UPDATES[pid])
        rows.append(row)

# Adicionar novo produto
rows.append({k: NOVO.get(k, "") for k in fieldnames})

# Escrever
with open(CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("Alteracoes aplicadas:")
print("  id  3 → Janela Lateral Colmeia (categoria: Janelas)")
print("  id 22 → Porta Londres 1 Vidro")
print("  id 32 → Colmeia Reta Correr separado da Almofada")
print("  id 44 → desativado (Janela Tabicao Correr)")
print("  id 56 → desativado (Lambri)")
print("  id 59 → fotos atualizadas (Janela Tabicao)")
print("  id 60 → NOVO: Porta Colmeia Reta Almofada Correr")
print("  + 7 simulacoes novas linkadas (ids 8,10,12,27,28,29,30)")
print("\nPronto!")
