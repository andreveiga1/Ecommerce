"""
mock_data.py
============
Dados mockados para o dashboard E-commerce Analytics.
Replica exatamente o schema das 3 tabelas do Supabase:
  - public_gold_sales.vendas_temporais
  - public_gold.clientes_segmentacao
  - public_gold.precos_competitividade

Usado como fallback quando não há conexão com o banco.
"""

import random
import numpy as np
import pandas as pd

# Semente para reprodutibilidade
random.seed(42)
np.random.seed(42)

# ──────────────────────────────────────────────
# CONSTANTES COMPARTILHADAS
# ──────────────────────────────────────────────
CATEGORIAS = ["Eletrônicos", "Roupas", "Casa & Jardim", "Esportes", "Beleza", "Livros", "Brinquedos"]
ESTADOS = ["SP", "RJ", "MG", "RS", "PR", "SC", "BA", "GO", "PE", "CE"]
SEGMENTOS = ["VIP", "Regular", "Novo", "Inativo"]
DIAS_SEMANA = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]

NOMES_CLIENTES = [
    "Ana Lima", "Bruno Silva", "Carla Mendes", "Diego Costa", "Elena Rocha",
    "Felipe Alves", "Gabriela Nunes", "Henrique Souza", "Isabela Ferreira", "João Oliveira",
    "Karina Martins", "Leonardo Pereira", "Marina Castro", "Nicolas Barbosa", "Olivia Gomes",
    "Paulo Ribeiro", "Queila Santos", "Rafael Torres", "Sabrina Carvalho", "Thiago Moura",
    "Ursula Figueiredo", "Vinicius Lopes", "Wanda Correia", "Xavier Dias", "Yasmin Cunha",
    "Zeca Pinto", "Alice Braga", "Bernardo Mello", "Cecília Teixeira", "Danilo Freitas",
    "Eva Nascimento", "Fábio Vieira", "Gisele Araújo", "Hugo Cardoso", "Ivone Monteiro",
    "Júlio César", "Katia Ramos", "Lucas Duarte", "Mariana Borges", "Nelson Machado",
    "Olga Campos", "Pedro Cavalcanti", "Quintino Assis", "Renata Vaz", "Sandro Bezerra",
    "Tatiana Luz", "Ulisses Moraes", "Vera Cruz", "Wagner Paixão", "Xuxa Leite",
]

NOMES_PRODUTOS = [
    "Smartphone Galaxy X12", "Notebook Pro 15", "Fone Bluetooth AirMax",
    "Tênis Running Ultra", "Camiseta Dry-Fit Pro", "Jaqueta Impermeável",
    "Sofá Retrátil 3 Lugares", "Luminária LED Smart", "Panela Elétrica 5L",
    "Halter Ajustável 20kg", "Yoga Mat Premium", "Bicicleta Ergométrica",
    "Shampoo Argan Oil 500ml", "Perfume Noir Intense", "Kit Maquiagem Pro",
    "Box Harry Potter 7 Livros", "Kindle Paperwhite", "Curso Python Completo",
    "LEGO Technic 42150", "Boneca Articulada XL", "Controle Gamer Pro",
    "Smart TV 55 OLED 4K", "Aspirador Robot AI", "Air Fryer 12L Digital",
]

COMPETIDORES = ["Americanas", "Magazine Luiza", "Mercado Livre", "Amazon BR", "Submarino"]


# ──────────────────────────────────────────────
# TABELA 1: vendas_temporais
# ──────────────────────────────────────────────
def make_vendas_temporais() -> pd.DataFrame:
    """
    Gera dados de vendas agregadas por data/hora,
    simulando ~365 dias × 24 horas com variações sazonais realistas.
    """
    records = []
    start = pd.Timestamp("2024-01-01")

    for day_offset in range(365):
        data = start + pd.Timedelta(days=day_offset)
        dia_semana_idx = data.weekday()  # 0=Monday … 6=Sunday
        dia_semana_nome = DIAS_SEMANA[dia_semana_idx]

        # Sazonalidade: fim de semana vende +20%, mês 11-12 vende +40%
        sazonalidade = 1.0
        if dia_semana_idx >= 5:
            sazonalidade *= 1.20
        if data.month in (11, 12):
            sazonalidade *= 1.40
        if data.month in (1, 2):
            sazonalidade *= 0.80

        # Clientes únicos do dia (base ~150, com ruído)
        clientes_unicos_dia = max(50, int(150 * sazonalidade + np.random.normal(0, 20)))

        for hora in range(24):
            # Curva horária: picos ao meio-dia e às 20h
            if 0 <= hora < 6:
                fator_hora = 0.05
            elif 6 <= hora < 9:
                fator_hora = 0.40
            elif 9 <= hora < 12:
                fator_hora = 0.75
            elif 12 <= hora < 14:
                fator_hora = 1.00
            elif 14 <= hora < 18:
                fator_hora = 0.70
            elif 18 <= hora < 22:
                fator_hora = 0.95
            else:
                fator_hora = 0.25

            total_vendas = max(0, int(
                random.randint(5, 30) * sazonalidade * fator_hora
                + np.random.normal(0, 2)
            ))
            if total_vendas == 0:
                continue

            ticket = random.uniform(80, 600)
            receita = round(total_vendas * ticket, 2)
            clientes_hora = max(1, int(clientes_unicos_dia * fator_hora * 0.15))

            records.append({
                "data_venda": data.date(),
                "mes_venda": data.month,
                "dia_semana_nome": dia_semana_nome,
                "hora_venda": hora,
                "total_vendas": total_vendas,
                "receita_total": receita,
                "total_clientes_unicos": clientes_hora,
            })

    df = pd.DataFrame(records)
    df["data_venda"] = pd.to_datetime(df["data_venda"])
    return df


# ──────────────────────────────────────────────
# TABELA 2: clientes_segmentacao
# ──────────────────────────────────────────────
def make_clientes_segmentacao() -> pd.DataFrame:
    """
    Gera perfis de clientes com segmentação RFM simplificada.
    Schema espelhado da view public_gold.clientes_segmentacao.
    """
    n = len(NOMES_CLIENTES)
    records = []

    # Pesos para distribuição realista de segmentos
    seg_weights = {"VIP": 0.15, "Regular": 0.50, "Novo": 0.25, "Inativo": 0.10}
    segmentos_lista = random.choices(
        list(seg_weights.keys()),
        weights=list(seg_weights.values()),
        k=n
    )

    for i, (nome, segmento) in enumerate(zip(NOMES_CLIENTES, segmentos_lista)):
        estado = random.choice(ESTADOS)

        # Receita e ticket variam por segmento
        if segmento == "VIP":
            receita = round(random.uniform(5000, 25000), 2)
            ticket = round(random.uniform(400, 1200), 2)
            total_pedidos = random.randint(15, 60)
        elif segmento == "Regular":
            receita = round(random.uniform(800, 5000), 2)
            ticket = round(random.uniform(120, 400), 2)
            total_pedidos = random.randint(4, 15)
        elif segmento == "Novo":
            receita = round(random.uniform(80, 800), 2)
            ticket = round(random.uniform(80, 200), 2)
            total_pedidos = random.randint(1, 3)
        else:  # Inativo
            receita = round(random.uniform(50, 500), 2)
            ticket = round(random.uniform(50, 150), 2)
            total_pedidos = random.randint(1, 5)

        records.append({
            "cliente_id": i + 1,
            "nome_cliente": nome,
            "estado": estado,
            "segmento_cliente": segmento,
            "total_pedidos": total_pedidos,
            "receita_total": receita,
            "ticket_medio": ticket,
            "ranking_receita": 0,  # preenchido abaixo
        })

    df = pd.DataFrame(records)
    df["ranking_receita"] = df["receita_total"].rank(ascending=False, method="first").astype(int)
    return df


# ──────────────────────────────────────────────
# TABELA 3: precos_competitividade
# ──────────────────────────────────────────────
def make_precos_competitividade() -> pd.DataFrame:
    """
    Gera análise de competitividade de preços por produto × concorrente.
    Schema espelhado da view public_gold.precos_competitividade.
    """
    records = []

    for pid, produto in enumerate(NOMES_PRODUTOS, start=1):
        # Determina categoria baseado no nome/índice
        categoria = CATEGORIAS[pid % len(CATEGORIAS)]

        nosso_preco = round(random.uniform(50, 2000), 2)
        quantidade = random.randint(10, 800)
        receita = round(nosso_preco * quantidade, 2)

        # Preços dos concorrentes (±30% do nosso)
        precos_concorrentes = {
            comp: round(nosso_preco * random.uniform(0.70, 1.30), 2)
            for comp in COMPETIDORES
        }

        preco_min_conc = min(precos_concorrentes.values())
        preco_max_conc = max(precos_concorrentes.values())
        preco_med_conc = round(sum(precos_concorrentes.values()) / len(COMPETIDORES), 2)

        dif_vs_media = round((nosso_preco - preco_med_conc) / preco_med_conc * 100, 2)

        if nosso_preco > preco_max_conc:
            classificacao = "MAIS_CARO_QUE_TODOS"
        elif nosso_preco < preco_min_conc:
            classificacao = "MAIS_BARATO_QUE_TODOS"
        elif nosso_preco > preco_med_conc:
            classificacao = "ACIMA_DA_MEDIA"
        else:
            classificacao = "ABAIXO_DA_MEDIA"

        records.append({
            "produto_id": pid,
            "nome_produto": produto,
            "categoria": categoria,
            "nosso_preco": nosso_preco,
            "preco_minimo_concorrentes": preco_min_conc,
            "preco_maximo_concorrentes": preco_max_conc,
            "preco_medio_concorrentes": preco_med_conc,
            "diferenca_percentual_vs_media": dif_vs_media,
            "classificacao_preco": classificacao,
            "quantidade_total": quantidade,
            "receita_total": receita,
        })

    return pd.DataFrame(records)


# ──────────────────────────────────────────────
# PONTO DE ENTRADA ÚNICO
# ──────────────────────────────────────────────
_CACHE: dict = {}


def get_mock_data(table: str) -> pd.DataFrame:
    """
    Retorna o DataFrame mockado para a tabela informada.
    Os dados são gerados uma única vez e cacheados em memória.

    Tabelas suportadas:
      - 'vendas_temporais'
      - 'clientes_segmentacao'
      - 'precos_competitividade'
    """
    if table not in _CACHE:
        if table == "vendas_temporais":
            _CACHE[table] = make_vendas_temporais()
        elif table == "clientes_segmentacao":
            _CACHE[table] = make_clientes_segmentacao()
        elif table == "precos_competitividade":
            _CACHE[table] = make_precos_competitividade()
        else:
            raise ValueError(f"Tabela desconhecida: '{table}'")
    return _CACHE[table].copy()
