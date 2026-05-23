"""
m6_estacoes.py — Proposta de estações de metrô por betweenness + KMeans
────────────────────────────────────────────────────────────────────────
Responsabilidades:
  • Filtrar candidatos a estação pelo top 2% de betweenness
  • Clusterizar geograficamente via KMeans (N grupos = N estações)
  • Selecionar o melhor representante de cada cluster
  • Gerar mapa folium interativo com o corredor proposto

Lógica de seleção:
  Usar apenas betweenness para escolher estações concentraria todas
  no mesmo bairro. O KMeans garante distribuição geográfica — cada
  cluster representa uma região da cidade, e dentro dele escolhemos
  o nó de maior betweenness como representante.
"""

import numpy as np
import networkx as nx
import folium
from sklearn.cluster import KMeans


# ─────────────────────────────────────────────
# CONFIGURAÇÕES
# ─────────────────────────────────────────────
N_ESTACOES      = 12     # número de estações propostas
PERCENTIL_BW    = 98     # top 2% por betweenness como pool de candidatos
MAPA_SAIDA      = "mapa_metro_proposto.html"

CORES_RANK = [
    "#c0392b", "#e74c3c", "#e67e22", "#f39c12", "#f1c40f",
    "#2ecc71", "#27ae60", "#1abc9c", "#3498db", "#2980b9",
    "#9b59b6", "#8e44ad",
]


def gerar_mapa_metro(G: nx.MultiDiGraph, metricas: dict):
    """
    Seleciona candidatos a estação, clusteriza e gera o mapa folium.

    Parameters
    ----------
    G : nx.MultiDiGraph
        Grafo com atributos geográficos (x, y) nos nós.
    metricas : dict
        Dicionário retornado por m2_metricas.calcular_metricas.

    Returns
    -------
    estacoes : list[dict]
        Lista de estações selecionadas, ordenadas por betweenness.
    """

    betweenness = metricas["betweenness"]
    grau        = metricas["grau"]
    core_number = metricas["core_number"]
    kcore_sub   = metricas.get("kcore_sub")   # pode ser None se não calculado
    K_ESCOLHIDO = metricas.get("k_escolhido", 3)

    # ── 1. Filtrar candidatos (top 2% betweenness) ────────────
    p_threshold = np.percentile(list(betweenness.values()), PERCENTIL_BW)
    candidatos = {
        n: betweenness[n]
        for n in G.nodes()
        if betweenness[n] >= p_threshold and "y" in G.nodes[n]
    }
    print(f"  → Candidatos (top {100 - PERCENTIL_BW}% betweenness): {len(candidatos)} nós")

    if len(candidatos) < N_ESTACOES:
        print(f"  ⚠ Poucos candidatos para {N_ESTACOES} clusters.")
        print(f"    Reduzindo para {len(candidatos)} estações.")
        n_clusters = len(candidatos)
    else:
        n_clusters = N_ESTACOES

    # ── 2. Clusterização geográfica (KMeans) ──────────────────
    ids    = list(candidatos.keys())
    coords = np.array([[G.nodes[n]["y"], G.nodes[n]["x"]] for n in ids])

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(coords)

    # ── 3. Selecionar representante de cada cluster ───────────
    # Critério: nó de maior betweenness dentro do cluster
    clusters = {}
    for idx, label in enumerate(kmeans.labels_):
        no = ids[idx]
        bw = candidatos[no]
        if label not in clusters or bw > clusters[label]["bw"]:
            clusters[label] = {
                "no":   no,
                "bw":   bw,
                "lat":  G.nodes[no]["y"],
                "lon":  G.nodes[no]["x"],
                "grau": grau.get(no, 0),
                "core": core_number.get(no, 0),
            }

    estacoes = sorted(clusters.values(), key=lambda e: e["bw"], reverse=True)

    # ── 4. Imprimir tabela de estações ────────────────────────
    _imprimir_tabela(estacoes)

    # ── 5. Gerar mapa folium ──────────────────────────────────
    _gerar_mapa(G, estacoes, kcore_sub, K_ESCOLHIDO)

    return estacoes


def _imprimir_tabela(estacoes: list):
    """Exibe tabela formatada das estações no console."""
    print(f"\n  {'─'*62}")
    print(f"  {'#':<4} {'Betweenness':>12}  {'Grau':>5}  {'Core':>5}  "
          f"{'Lat':>10}  {'Lon':>11}")
    print(f"  {'─'*62}")
    for i, e in enumerate(estacoes, 1):
        print(f"  {i:<4} {e['bw']:>12.6f}  {e['grau']:>5}  {e['core']:>5}  "
              f"{e['lat']:>10.5f}  {e['lon']:>11.5f}")
    print(f"  {'─'*62}")


def _gerar_mapa(G: nx.MultiDiGraph, estacoes: list,
                kcore_sub, K_ESCOLHIDO: int):
    """Constrói e salva o mapa folium com o corredor proposto."""

    lats   = [e["lat"] for e in estacoes]
    lons   = [e["lon"] for e in estacoes]
    centro = [np.mean(lats), np.mean(lons)]

    mapa = folium.Map(location=centro, zoom_start=12,
                      tiles="CartoDB positron")

    # ── Camada 1: K-core como pano de fundo ───────────────────
    if kcore_sub is not None:
        grupo_kcore = folium.FeatureGroup(
            name=f"K-core (k≥{K_ESCOLHIDO}) — espinha dorsal",
            show=True
        )
        for u, v in kcore_sub.edges():
            if u in G.nodes and v in G.nodes:
                if "y" in G.nodes[u] and "y" in G.nodes[v]:
                    folium.PolyLine(
                        [[G.nodes[u]["y"], G.nodes[u]["x"]],
                         [G.nodes[v]["y"], G.nodes[v]["x"]]],
                        color="#bdc3c7", weight=1, opacity=0.5
                    ).add_to(grupo_kcore)
        grupo_kcore.add_to(mapa)

    # ── Camada 2: Linha do corredor proposto ──────────────────
    coords_linha = [[e["lat"], e["lon"]] for e in estacoes]
    folium.PolyLine(
        coords_linha,
        color="#e74c3c", weight=4, opacity=0.85,
        tooltip="Corredor proposto (ordem por betweenness)"
    ).add_to(mapa)

    # ── Camada 3: Marcadores das estações ─────────────────────
    grupo_estacoes = folium.FeatureGroup(name="Estações propostas", show=True)
    for i, e in enumerate(estacoes, 1):
        cor = CORES_RANK[min(i - 1, len(CORES_RANK) - 1)]

        folium.CircleMarker(
            location=[e["lat"], e["lon"]],
            radius=14,
            color="white", weight=2,
            fill=True, fill_color=cor, fill_opacity=0.92,
            popup=folium.Popup(
                f"<b>Estação #{i}</b><br>"
                f"Betweenness: {e['bw']:.6f}<br>"
                f"Grau: {e['grau']}<br>"
                f"Core number: {e['core']}<br>"
                f"({e['lat']:.5f}, {e['lon']:.5f})",
                max_width=220
            ),
            tooltip=f"Estação #{i}  bw={e['bw']:.5f}"
        ).add_to(grupo_estacoes)

        # Número visível sobre o marcador
        folium.Marker(
            location=[e["lat"], e["lon"]],
            icon=folium.DivIcon(
                html=(
                    f'<div style="font-size:10px;font-weight:bold;'
                    f'color:white;text-align:center;margin-top:4px;">'
                    f'{i}</div>'
                ),
                icon_size=(20, 20),
                icon_anchor=(10, 10),
            )
        ).add_to(grupo_estacoes)

    grupo_estacoes.add_to(mapa)

    # ── Legenda ───────────────────────────────────────────────
    legenda_html = """
    <div style="position:fixed;bottom:30px;left:30px;z-index:9999;
                background:white;padding:12px 16px;border-radius:8px;
                box-shadow:0 2px 8px rgba(0,0,0,.2);font-size:12px;">
      <b>Proposta de Metrô — Natal/RN</b><br>
      <span style="color:#e74c3c;">━━━━</span> Corredor proposto<br>
      <span style="color:#e74c3c;">●</span> Estações (por betweenness)<br>
      <span style="color:#bdc3c7;">━━</span> K-core (espinha dorsal)<br>
      <i>Clique nas estações para detalhes</i>
    </div>
    """
    mapa.get_root().html.add_child(folium.Element(legenda_html))

    folium.LayerControl(collapsed=False).add_to(mapa)
    mapa.save(MAPA_SAIDA)
    print(f"\n  ✓ Mapa salvo: '{MAPA_SAIDA}'")
    print("    Abra no navegador — clique em cada estação para ver as métricas.")