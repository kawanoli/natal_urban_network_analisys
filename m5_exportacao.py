"""
m5_exportacao.py — Exportação do grafo enriquecido para o Gephi
────────────────────────────────────────────────────────────────
Responsabilidades:
  • Garantir que todos os atributos calculados (grau, betweenness,
    closeness, core_number) estejam nos nós antes de exportar
  • Converter tipos numpy para tipos Python nativos (exigido pelo
    formato graphml / xml)
  • Exportar natal_drive.graphml com atributos prontos para o Gephi
  • Imprimir instruções de uso no Gephi (Geo Layout + ForceAtlas2)

Nota sobre tipos de dados:
  O networkx.write_graphml exige que os atributos dos nós sejam
  tipos Python nativos (int, float, str). Arrays numpy (np.int64,
  np.float64) causam TypeError. Por isso todos os valores são
  convertidos via _limpar_atributos() antes da exportação.
"""

import networkx as nx
import numpy as np
import os


ARQUIVO_SAIDA = "natal_drive_completo.graphml"


def exportar_gephi(G: nx.MultiDiGraph, metricas: dict):
    """
    Prepara e exporta o grafo em formato .graphml para uso no Gephi.

    Parameters
    ----------
    G : nx.MultiDiGraph
        Grafo com atributos já adicionados pelo m2_metricas.
    metricas : dict
        Métricas brutas para garantia de completude dos atributos.
    """

    print(f"  → Preparando grafo para exportação...")

    # ── 1. Garantir que todos os nós têm os atributos ────────
    # (segurança extra caso algum nó tenha sido adicionado depois)
    for n in G.nodes():
        nd = G.nodes[n]
        if "grau" not in nd:
            nd["grau"]        = int(metricas["grau"].get(n, 0))
        if "betweenness" not in nd:
            nd["betweenness"] = float(metricas["betweenness"].get(n, 0.0))
        if "closeness" not in nd:
            nd["closeness"]   = float(metricas["closeness"].get(n, 0.0))
        if "core_number" not in nd:
            nd["core_number"] = int(metricas["core_number"].get(n, 0))

    # ── 2. Converter tipos numpy → Python nativo ─────────────
    print("  → Convertendo tipos de atributos para graphml...")
    G_export = _limpar_atributos(G)

    # ── 3. Exportar ───────────────────────────────────────────
    # IDs únicos nas arestas (evita erro de merge no Gephi)
    for i, (u, v, k) in enumerate(G_export.edges(keys=True)):
        G_export[u][v][k]["id"] = f"e{i}"

    print(f"  → Salvando '{ARQUIVO_SAIDA}'...")
    nx.write_graphml(G_export, ARQUIVO_SAIDA, edge_id_from_attribute="id")

    tamanho_mb = os.path.getsize(ARQUIVO_SAIDA) / (1024 * 1024)
    print(f"  ✓ Arquivo exportado: {ARQUIVO_SAIDA} ({tamanho_mb:.1f} MB)")
    print(f"     Nós:    {G_export.number_of_nodes():,}")
    print(f"     Arestas: {G_export.number_of_edges():,}")

    # ── 4. Instruções para o Gephi ────────────────────────────
    _imprimir_instrucoes_gephi()


def _limpar_atributos(G: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """
    Converte todos os atributos dos nós e arestas para tipos
    Python nativos aceitos pelo formato graphml.

    numpy.int64 → int
    numpy.float64 → float
    numpy.bool_ → bool
    outros → str
    """
    def _converter(val):
        if isinstance(val, np.integer):  return int(val)
        if isinstance(val, np.floating): return float(val)
        if isinstance(val, np.bool_):    return bool(val)
        # Qualquer tipo não primitivo (shapely, listas, dicts…) → string
        if not isinstance(val, (int, float, str, bool)):
            return str(val)
        return val

    # Copiar grafo para não modificar o original em memória
    G2 = G.copy()

    for n, data in G2.nodes(data=True):
        for k, v in list(data.items()):
            data[k] = _converter(v)

    for u, v, k, data in G2.edges(keys=True, data=True):
        for attr, val in list(data.items()):
            data[attr] = _converter(val)

    return G2


def _imprimir_instrucoes_gephi():
    """Imprime passo a passo para uso no Gephi."""
    print("\n" + "=" * 60)
    print("  INSTRUÇÕES DE USO NO GEPHI")
    print("=" * 60)
    instrucoes = """
  1. IMPORTAR O ARQUIVO
     • Abra o Gephi → File → Open → natal_drive.graphml
     • Aceite as configurações padrão de importação.

  2. ATRIBUTOS DISPONÍVEIS NOS NÓS
     • x          → longitude (para Geo Layout)
     • y          → latitude  (para Geo Layout)
     • grau       → grau do nó no grafo não-dirigido
     • betweenness → betweenness centrality (0 a 1)
     • closeness   → closeness centrality
     • core_number → resultado da k-core decomposition

  ─── VISUALIZAÇÃO GEOGRÁFICA ──────────────────────────
  3. INSTALAR PLUGIN GEO LAYOUT
     • Tools → Plugins → Available Plugins
     • Buscar "Geo Layout" → Install → Reiniciar

  4. CONFIGURAR GEO LAYOUT
     • Layout panel → selecionar "Geo Layout"
     • Longitude field → x
     • Latitude field  → y
     • Scale → ajuste até Natal aparecer bem
     • Clique em "Run"

  ─── ENCODINGS VISUAIS ────────────────────────────────
  5. TAMANHO DOS NÓS (proporcional ao grau)
     • Appearance → Nodes → Size → Ranking
     • Atributo: grau
     • Min size: 2 | Max size: 20

  6. COR DOS NÓS (por core number)
     • Appearance → Nodes → Color → Partition ou Ranking
     • Atributo: core_number
     • Paleta sugerida: Sequential (azul→amarelo→vermelho)

  7. DESTACAR BETWEENNESS
     • Crie um filtro: Filters → Attributes → Range
     • Atributo: betweenness
     • Arraste o slider para destacar top 5%

  ─── VISUALIZAÇÃO ESTRUTURAL (ForceAtlas2) ────────────
  8. APLICAR FORCEATLAS2
     • Layout → ForceAtlas2
     • Configurações recomendadas:
       - Scaling: 10
       - Gravity: 1
       - LinLog mode: ON (destaca estrutura de comunidades)
       - Prevent Overlap: ON (após convergência)
     • Rode por 1-3 min até estabilizar

  ─── FILTROS OBRIGATÓRIOS ─────────────────────────────
  9. TOP 10% POR GRAU
     • Filters → Attributes → Range → grau
     • Defina o threshold = percentil 90 dos graus

  10. SUBGRAFO K-CORE
      • Filters → Attributes → Range → core_number
      • Valor mínimo = k escolhido (ver relatorio_analise.txt)
      • Clique em Filter → Select → Extract Subgraph
"""
    print(instrucoes)