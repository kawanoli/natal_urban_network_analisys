"""
m1_coleta.py — Coleta da rede viária de Natal/RN via OSMnx
─────────────────────────────────────────────────────────────
Responsabilidades:
  • Baixar o grafo dirigido de vias (network_type="drive")
  • Garantir que os atributos x/y (lon/lat) estejam presentes nos nós
  • Salvar uma cópia bruta em .graphml para referência
  • Retornar o grafo NetworkX para os demais módulos

Nota sobre a escolha network_type="drive":
  Utilizamos "drive" porque o objetivo é analisar mobilidade urbana
  de ônibus e metrô, que compartilham a infraestrutura viária de
  veículos motorizados. Ciclovias e trilhas não são relevantes aqui.
"""

import os
import osmnx as ox
import networkx as nx


# ─────────────────────────────────────────────
# CONFIGURAÇÕES
# ─────────────────────────────────────────────
CIDADE        = "Natal, Rio Grande do Norte, Brazil"
NETWORK_TYPE  = "drive"
ARQUIVO_BRUTO = "natal_drive_bruto.graphml"
ARQUIVO_SAIDA = "natal_drive.graphml"    # versão com atributos calculados (gerada pelo m5)


def coletar_rede() -> nx.MultiDiGraph:
    """
    Baixa a malha viária de Natal via OSMnx.

    Returns
    -------
    G : nx.MultiDiGraph
        Grafo dirigido com atributos geográficos (x, y) em cada nó.
    """

    # ── 1. Verificar cache ────────────────────────────────────
    if os.path.exists(ARQUIVO_BRUTO):
        print(f"  → Carregando grafo do cache '{ARQUIVO_BRUTO}'...")
        G = ox.load_graphml(ARQUIVO_BRUTO)
        print(f"  ✓ Grafo carregado: {G.number_of_nodes()} nós, {G.number_of_edges()} arestas.")
        return G

    # ── 2. Download via OSMnx ─────────────────────────────────
    print(f"  → Baixando rede viária de '{CIDADE}'...")
    print("     (primeira execução pode levar alguns minutos)")

    G = ox.graph_from_place(
        CIDADE,
        network_type=NETWORK_TYPE,
        simplify=True,       # Simplifica interseções intermediárias
        retain_all=False,    # Remove componentes isolados
    )

    print(f"  ✓ Download concluído: {G.number_of_nodes()} nós, {G.number_of_edges()} arestas.")

    # ── 3. Garantir atributos geográficos x/y ─────────────────
    # OSMnx já preenche 'x' (longitude) e 'y' (latitude) por padrão.
    # A verificação abaixo é uma garantia extra.
    nos_sem_geo = [n for n, d in G.nodes(data=True) if "x" not in d or "y" not in d]
    if nos_sem_geo:
        print(f"  ⚠ {len(nos_sem_geo)} nós sem coordenadas geográficas — removendo...")
        G.remove_nodes_from(nos_sem_geo)

    # ── 4. Salvar cache local ─────────────────────────────────
    print(f"  → Salvando cache em '{ARQUIVO_BRUTO}'...")
    ox.save_graphml(G, ARQUIVO_BRUTO)
    print("  ✓ Cache salvo.")

    # ── 5. Resumo da rede ─────────────────────────────────────
    _imprimir_resumo(G)

    return G


def _imprimir_resumo(G: nx.MultiDiGraph):
    """Exibe informações básicas da rede coletada."""
    componentes = nx.number_weakly_connected_components(G)
    maior_comp  = max(nx.weakly_connected_components(G), key=len)

    print("\n  ┌─ Resumo da rede ──────────────────────────────")
    print(f"  │  Nós (interseções):  {G.number_of_nodes():>8,}")
    print(f"  │  Arestas (vias):     {G.number_of_edges():>8,}")
    print(f"  │  Componentes fracos: {componentes:>8,}")
    print(f"  │  Maior componente:   {len(maior_comp):>8,} nós")
    print(f"  │  Grafo dirigido:     {'Sim':>8}")
    print("  └───────────────────────────────────────────────")
