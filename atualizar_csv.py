# -*- coding: utf-8 -*-
import csv, os

CSV_IN  = r"C:\Users\Lucas\Desktop\catalogo\catalogo_produtos_base.csv"
CSV_OUT = r"C:\Users\Lucas\Desktop\catalogo\catalogo_produtos_base.csv"
FOTOS   = r"C:\Users\Lucas\Desktop\catalogo\fotos"

# Alteracoes por id: {id: {campo: valor}}
# Regras:
#  - id 42 desativado (janela 12.jpg removida)
#  - Simulacoes adicionadas como fotos_extras
#  - id 7: foto principal trocada para .png (jpg nao existe mais)
#  - id 33: foto principal atualizada para nome mais descritivo

UPDATES = {
    6:  {"fotos_extras": "Porta Ondulada Simulação.png"},
    7:  {"foto_arquivo": "almofada arqueada.png",
         "fotos_extras": "almofada arqueada simulaçao.png"},
    13: {"fotos_extras": "Londe 2 Vidros 2 Laterais Veneziana Simulaçao.png"},
    15: {"fotos_extras": "Portao de Madeira Simulaçao.png"},
    16: {"fotos_extras": "Putit Simulaçao.png"},
    31: {"fotos_extras": "Colmeia com Vidro Simulação.png"},
    32: {"fotos_extras": "Colmeia Reta Almofada Correr.jpg|Colmeia Reta Correr Simulação.png|Colmeia Reta Almofada Correr Simulação.png"},
    33: {"foto_arquivo": "Janela Colmeia com Veneziana.jpg",
         "fotos_extras": "Janela Colmeia com Veneziana Simulaçao.png"},
    35: {"fotos_extras": "Janela Colmeia Tabicao Aberta.jpg|Janela Colmeia Tabicao Aberta Simulaçao.png"},
    36: {"fotos_extras": "Janela Com arco Simulaçao.png"},
    37: {"fotos_extras": "Janela Europeia 2.jpg|jane 8.jpg|Janela Europeia Simulação.png"},
    38: {"fotos_extras": "Janela Pivotante Aberta.jpg|Janela Pivotante Aberta Simulaçao.png"},
    42: {"ativo": "nao"},
    43: {"fotos_extras": "Tabicao 4 bandas aberto.jpg|tabicao 4 bandas de lado.jpg|Tabicao 4 bandas aberto simulaçao.png"},
    46: {"fotos_extras": "Concrem Branca Simulação.jpg"},
    47: {"fotos_extras": "Concrem Cinza Simulação.jpg"},
    48: {"fotos_extras": "Revestida 2 Frisos Simulaçao.jpg"},
    49: {"fotos_extras": "Revestida 4 Frisos Simulação.png"},
    53: {"fotos_extras": "Mesa Madeira Angelim simulaçao.png"},
}

# Verificar quais arquivos existem na pasta fotos
arquivos_existentes = set(os.listdir(FOTOS))

def checar(nome):
    if not nome:
        return True
    for f in nome.split("|"):
        f = f.strip()
        if f and f not in arquivos_existentes:
            return f
    return True

# Ler e atualizar CSV
rows = []
with open(CSV_IN, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        pid = int(row["id"])
        if pid in UPDATES:
            for campo, valor in UPDATES[pid].items():
                row[campo] = valor
        rows.append(row)

# Escrever CSV atualizado
with open(CSV_OUT, "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("CSV atualizado!\n")
print("Verificando fotos_extras de cada produto:")
print("-" * 55)

for row in rows:
    pid = int(row["id"])
    extras = row.get("fotos_extras", "").strip()
    foto   = row.get("foto_arquivo", "").strip()

    # Checar foto principal
    if foto and foto not in arquivos_existentes:
        print(f"[AVISO] id {pid:2d} - foto principal nao encontrada: {foto}")

    # Checar extras
    if extras:
        for f in extras.split("|"):
            f = f.strip()
            if f and f not in arquivos_existentes:
                print(f"[AVISO] id {pid:2d} - extra nao encontrado: {f}")
        print(f"  id {pid:2d} ({row['nome'][:28]}): {len(extras.split('|'))} extra(s)")

print("\nPronto!")
