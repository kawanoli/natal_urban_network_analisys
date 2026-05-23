"""
m2_metricas.py — Cálculo de métricas estruturais com NetworkX
──────────────────────────────────────────────────────────────
Métricas obrigatórias calculadas:
  1. Grau dos nós (in/out/total no grafo dirigido; grau no não-dirigido)
  2. Distribuição de grau
  3. Hubs (nós com maior grau)
  4. Betweenness centrality
  5. Closeness centrality
  6. Core number
  7. K-core decomposition

Escolha de conversão:
  • Betweenness, Closeness e K-core são calculados sobre o grafo
    NÃO-DIRIGIDO simplificado (G_ud), pois:
    - São métricas clássicas definidas para grafos não-dirigidos.
    - Vias de mão dupla em Natal representam a maioria das ruas,
      então a perda de informação direcional é pequena.
    - Simplificar arestas paralelas (MultiGraph → Graph) evita
      distorções no betweenness por múltiplas arestas redundantes.
  • O grau é calculado também no grafo dirigido original para
    preservar informação de in-degree e out-degree.
"""

import networkx as nx
import numpy as np
from collections import Counter


# ─────────────────────────────────────────────
# PARÂMETROS
# ─────────────────────────────────────────────
N_HUBS          = 20    # quantos hubs reportar
BETWEENNESS_K   = 500   # amostragem para betweenness (None = exato, lento)
                        # Em Natal ~10k nós, k=500 é bom equilíbrio custo/precisão


def calcular_metricas(G: nx.MultiDiGraph) -> tuple:
    """
    Calcula todas as métricas obrigatórias e as adiciona como
    atributos dos nós no grafo original.

    Parameters
    ----------
    G : nx.MultiDiGraph
        Grafo dirigido retornado pelo m1_coleta.

    Returns
    -------
    G : nx.MultiDiGraph
        Mesmo grafo, agora com atributos por nó:
        grau, grau_in, grau_out, betweenness, closeness, core_number.
    metricas : dict
        Dicionário com todas as métricas brutas e rankings.
    """

    # ── 1. Converter para grafo não-dirigido simples ──────────
    print("  → Convertendo para grafo não-dirigido simples...")
    G_ud = nx.Graph(G.to_undirected())   # MultiDiGraph → Graph (arestas paralelas colapsadas)
    print(f"     {G_ud.number_of_nodes()} nós, {G_ud.number_of_edges()} arestas")

    # ── 2. GRAU ───────────────────────────────────────────────
    print("  → Calculando grau...")
    grau      = dict(G_ud.degree())
    grau_in   = dict(G.in_degree())
    grau_out  = dict(G.out_degree())

    # ── 3. DISTRIBUIÇÃO DE GRAU ───────────────────────────────
    valores_grau     = list(grau.values())
    dist_grau        = Counter(valores_grau)
    grau_medio       = np.mean(valores_grau)
    grau_max         = max(valores_grau)
    grau_min         = min(valores_grau)

    # ── 4. HUBS (top N por grau) ──────────────────────────────
    hubs_grau = sorted(grau.items(), key=lambda x: x[1], reverse=True)[:N_HUBS]

    # ── 5. BETWEENNESS CENTRALITY ─────────────────────────────
    print(f"  → Calculando betweenness (k={BETWEENNESS_K}, amostragem)...")
    print("     (pode levar 1-3 minutos para a rede de Natal)")
    betweenness = nx.betweenness_centrality(G_ud, k=BETWEENNESS_K, normalized=True, seed=42)
    hubs_betweenness = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:N_HUBS]

    # ── 6. CLOSENESS CENTRALITY ───────────────────────────────
    print("  → Calculando closeness centrality...")
    closeness = nx.closeness_centrality(G_ud)
    hubs_closeness = sorted(closeness.items(), key=lambda x: x[1], reverse=True)[:N_HUBS]

    # ── 7. CORE NUMBER ────────────────────────────────────────
    print("  → Calculando core number (k-core decomposition)...")
    core_number = nx.core_number(G_ud)
    k_max       = max(core_number.values())
    dist_core   = Counter(core_number.values())

    # ── 8. Adicionar atributos ao grafo original ──────────────
    print("  → Adicionando métricas como atributos dos nós...")
    for n in G.nodes():
        G.nodes[n]["grau"]         = grau.get(n, 0)
        G.nodes[n]["grau_in"]      = grau_in.get(n, 0)
        G.nodes[n]["grau_out"]     = grau_out.get(n, 0)
        G.nodes[n]["betweenness"]  = round(betweenness.get(n, 0.0), 8)
        G.nodes[n]["closeness"]    = round(closeness.get(n, 0.0), 6)
        G.nodes[n]["core_number"]  = core_number.get(n, 0)

    # ── 9. Montar dicionário de retorno ───────────────────────
    metricas = {
        # Métricas brutas (dict nó → valor)
        "grau":           grau,
        "grau_in":        grau_in,
        "grau_out":       grau_out,
        "betweenness":    betweenness,
        "closeness":      closeness,
        "core_number":    core_number,

        # Estatísticas de distribuição de grau
        "dist_grau":      dist_grau,
        "grau_medio":     grau_medio,
        "grau_max":       grau_max,
        "grau_min":       grau_min,
        "valores_grau":   valores_grau,

        # Rankings
        "hubs_grau":        hubs_grau,
        "hubs_betweenness": hubs_betweenness,
        "hubs_closeness":   hubs_closeness,

        # K-core
        "k_max":    k_max,
        "dist_core": dist_core,

        # Grafo não-dirigido (usado em m4 e m3)
        "G_ud": G_ud,
    }

    _imprimir_resumo_metricas(metricas)
    return G, metricas


def _imprimir_resumo_metricas(m: dict):
    """Exibe sumário das métricas calculadas."""
    print("\n  ┌─ Resumo das métricas ────────────────────────────")
    print(f"  │  Grau médio:          {m['grau_medio']:.2f}")
    print(f"  │  Grau máximo:         {m['grau_max']}")
    print(f"  │  Grau mínimo:         {m['grau_min']}")
    print(f"  │  K-core máximo:       {m['k_max']}")
    print(f"  │  Top-1 hub (grau):    nó {m['hubs_grau'][0][0]}  (grau={m['hubs_grau'][0][1]})")
    print(f"  │  Top-1 betweenness:   nó {m['hubs_betweenness'][0][0]}  (bw={m['hubs_betweenness'][0][1]:.5f})")
    print("  └───────────────────────────────────────────────────")
