"""
m4_visualizacao.py — Geração de visualizações da rede viária
──────────────────────────────────────────────────────────────
Gera:
  1. Distribuição de grau (histograma + escala log-log)
  2. Mapa geográfico interativo (folium) com hubs destacados
  3. Visualização do subgrafo k-core sobreposto no mapa
  4. Scatter plot grau × betweenness (relação entre métricas)
  5. Mapa de calor de betweenness sobre a cidade
"""

import os
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")           # backend sem display (compatível com Colab)
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import networkx as nx
import folium
from folium.plugins import HeatMap

# ─────────────────────────────────────────────
# CONFIGURAÇÕES VISUAIS
# ─────────────────────────────────────────────
DIR_GRAFICOS    = "graficos"
MAPA_HTML       = "mapa_natal.html"
COR_HUB         = "#e74c3c"
COR_BW_ALTO     = "#f39c12"
COR_KCORE       = "#8e44ad"
COR_BORDA       = "#2c3e50"
DPI             = 150
os.makedirs(DIR_GRAFICOS, exist_ok=True)


def gerar_visualizacoes(G: nx.MultiDiGraph, metricas: dict):
    """Gera e salva todas as visualizações do projeto."""

    print("  → Figura 1: Distribuição de grau...")
    _plot_distribuicao_grau(metricas)

    print("  → Figura 2: Scatter grau × betweenness...")
    _plot_grau_vs_betweenness(G, metricas)

    print("  → Figura 3: Distribuição de core number...")
    _plot_distribuicao_core(metricas)

    print("  → Mapa interativo (folium)...")
    _gerar_mapa_folium(G, metricas)

    print(f"  ✓ Visualizações salvas em '{DIR_GRAFICOS}/' e '{MAPA_HTML}'")


# ─────────────────────────────────────────────
# FIGURA 1 — DISTRIBUIÇÃO DE GRAU
# ─────────────────────────────────────────────
def _plot_distribuicao_grau(metricas: dict):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Distribuição de Grau — Malha Viária de Natal/RN", fontsize=14, fontweight="bold")

    vals = metricas["valores_grau"]

    # ── Histograma linear ────────────────────
    ax1 = axes[0]
    bins = range(min(vals), max(vals) + 2)
    ax1.hist(vals, bins=bins, color="#3498db", edgecolor="white", linewidth=0.5)
    ax1.axvline(metricas["grau_medio"], color=COR_HUB, linestyle="--",
                linewidth=1.5, label=f"Média: {metricas['grau_medio']:.2f}")
    ax1.set_xlabel("Grau do nó", fontsize=11)
    ax1.set_ylabel("Frequência", fontsize=11)
    ax1.set_title("Escala linear", fontsize=11)
    ax1.legend()
    ax1.grid(axis="y", alpha=0.3)

    # ── Log-log (teste lei de potência) ──────
    ax2 = axes[1]
    from collections import Counter
    contagem = Counter(vals)
    graus_uniq = sorted(contagem.keys())
    freqs = [contagem[g] for g in graus_uniq]
    ax2.scatter(graus_uniq, freqs, color="#e74c3c", s=20, alpha=0.7, zorder=5)
    ax2.set_xscale("log")
    ax2.set_yscale("log")

    # Linha de tendência (regressão log-log)
    log_g = np.log10([g for g in graus_uniq if g > 0])
    log_f = np.log10([f for g, f in zip(graus_uniq, freqs) if g > 0])
    if len(log_g) > 2:
        coef = np.polyfit(log_g, log_f, 1)
        g_fit = np.linspace(min(log_g), max(log_g), 100)
        ax2.plot(10**g_fit, 10**np.polyval(coef, g_fit),
                 "--", color=COR_BW_ALTO, linewidth=1.5,
                 label=f"γ ≈ {abs(coef[0]):.2f}")

    ax2.set_xlabel("Grau (log)", fontsize=11)
    ax2.set_ylabel("Frequência (log)", fontsize=11)
    ax2.set_title("Escala log-log (cauda da distribuição)", fontsize=11)
    ax2.legend()
    ax2.grid(alpha=0.3, which="both")

    plt.tight_layout()
    caminho = os.path.join(DIR_GRAFICOS, "fig1_distribuicao_grau.png")
    plt.savefig(caminho, dpi=DPI, bbox_inches="tight")
    plt.close()


# ─────────────────────────────────────────────
# FIGURA 2 — GRAU vs BETWEENNESS
# ─────────────────────────────────────────────
def _plot_grau_vs_betweenness(G: nx.MultiDiGraph, metricas: dict):
    nos     = list(metricas["grau"].keys())
    graus   = [metricas["grau"][n] for n in nos]
    bws     = [metricas["betweenness"][n] for n in nos]
    cores   = [metricas["core_number"][n] for n in nos]

    fig, ax = plt.subplots(figsize=(10, 7))

    sc = ax.scatter(graus, bws, c=cores, cmap="plasma",
                    s=12, alpha=0.6, linewidths=0,
                    norm=mcolors.Normalize(vmin=0, vmax=metricas["k_max"]))

    # Destacar top-10 betweenness
    for no, bw in metricas["hubs_betweenness"][:10]:
        g = metricas["grau"][no]
        ax.scatter(g, bw, color=COR_HUB, s=80, zorder=10, edgecolors="white", linewidths=0.8)
        ax.annotate(str(no)[:6], (g, bw), textcoords="offset points",
                    xytext=(5, 3), fontsize=7, color=COR_HUB)

    cbar = plt.colorbar(sc, ax=ax)
    cbar.set_label("Core number", fontsize=10)
    ax.set_xlabel("Grau do nó", fontsize=12)
    ax.set_ylabel("Betweenness centrality", fontsize=12)
    ax.set_title("Grau × Betweenness (cor = core number)\nDestaques em vermelho: top-10 betweenness",
                 fontsize=12, fontweight="bold")
    ax.grid(alpha=0.25)

    caminho = os.path.join(DIR_GRAFICOS, "fig2_grau_vs_betweenness.png")
    plt.savefig(caminho, dpi=DPI, bbox_inches="tight")
    plt.close()


# ─────────────────────────────────────────────
# FIGURA 3 — DISTRIBUIÇÃO DE CORE NUMBER
# ─────────────────────────────────────────────
def _plot_distribuicao_core(metricas: dict):
    from collections import Counter
    dist = Counter(metricas["core_number"].values())
    ks   = sorted(dist.keys())
    freq = [dist[k] for k in ks]

    fig, ax = plt.subplots(figsize=(10, 5))

    cores_norm = [k / max(ks) for k in ks]
    cmap = plt.get_cmap("viridis")
    bars = ax.bar(ks, freq, color=[cmap(c) for c in cores_norm], edgecolor="none")

    # Destacar k escolhido
    k_escolhido = max(3, math.ceil(metricas["k_max"] * 0.6))
    for i, k in enumerate(ks):
        if k >= k_escolhido:
            bars[i].set_edgecolor(COR_HUB)
            bars[i].set_linewidth(2)

    ax.set_xlabel("Core number (k)", fontsize=12)
    ax.set_ylabel("Número de nós", fontsize=12)
    ax.set_title(
        f"Distribuição de Core Number — k_max = {metricas['k_max']}\n"
        f"Bordas vermelhas: nós no k-core escolhido (k ≥ {k_escolhido})",
        fontsize=12, fontweight="bold"
    )
    ax.grid(axis="y", alpha=0.3)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=mcolors.Normalize(vmin=0, vmax=max(ks)))
    plt.colorbar(sm, ax=ax, label="Core number")

    caminho = os.path.join(DIR_GRAFICOS, "fig3_distribuicao_core.png")
    plt.savefig(caminho, dpi=DPI, bbox_inches="tight")
    plt.close()


# ─────────────────────────────────────────────
# MAPA INTERATIVO — FOLIUM
# ─────────────────────────────────────────────
def _gerar_mapa_folium(G: nx.MultiDiGraph, metricas: dict):
    """
    Gera mapa HTML interativo com:
      • Camada base: todas as arestas da rede (cinza)
      • Camada k-core: subgrafo do k-core escolhido (roxo)
      • Marcadores: top-20 hubs por betweenness (vermelho)
      • Heatmap: intensidade de betweenness por localização
    """
    k_escolhido = max(3, math.ceil(metricas["k_max"] * 0.6))
    G_ud        = metricas["G_ud"]

    # Centro do mapa (centróide dos nós)
    lats = [d["y"] for _, d in G.nodes(data=True) if "y" in d]
    lons = [d["x"] for _, d in G.nodes(data=True) if "x" in d]
    centro = [np.mean(lats), np.mean(lons)]

    mapa = folium.Map(location=centro, zoom_start=12,
                      tiles="CartoDB positron")

    # ── Camada 1: Arestas da rede completa ───
    grupo_rede = folium.FeatureGroup(name="Rede viária completa", show=False)
    for u, v, data in G.edges(data=True):
        if "y" in G.nodes[u] and "y" in G.nodes[v]:
            folium.PolyLine(
                locations=[[G.nodes[u]["y"], G.nodes[u]["x"]],
                            [G.nodes[v]["y"], G.nodes[v]["x"]]],
                color="#7f8c8d", weight=0.5, opacity=0.4
            ).add_to(grupo_rede)
    grupo_rede.add_to(mapa)

    # ── Camada 2: Subgrafo k-core ─────────────
    kcore_sub   = nx.k_core(G_ud, k=k_escolhido)
    kcore_nos   = set(kcore_sub.nodes())
    grupo_kcore = folium.FeatureGroup(name=f"K-core (k≥{k_escolhido})", show=True)
    for u, v in kcore_sub.edges():
        if u in G.nodes and v in G.nodes:
            if "y" in G.nodes[u] and "y" in G.nodes[v]:
                folium.PolyLine(
                    locations=[[G.nodes[u]["y"], G.nodes[u]["x"]],
                                [G.nodes[v]["y"], G.nodes[v]["x"]]],
                    color=COR_KCORE, weight=1.8, opacity=0.7
                ).add_to(grupo_kcore)
    grupo_kcore.add_to(mapa)

    # ── Camada 3: Heatmap de betweenness ─────
    heat_dados = []
    bw_max = max(metricas["betweenness"].values()) or 1
    for n, bw in metricas["betweenness"].items():
        if n in G.nodes and "y" in G.nodes[n]:
            lat = G.nodes[n]["y"]
            lon = G.nodes[n]["x"]
            peso = bw / bw_max
            if peso > 0.01:   # filtrar ruído
                heat_dados.append([lat, lon, peso])

    grupo_heat = folium.FeatureGroup(name="Heatmap: Betweenness", show=True)
    HeatMap(heat_dados, radius=12, blur=15, max_zoom=14,
            gradient={"0.2": "blue", "0.5": "yellow", "1.0": "red"}
            ).add_to(grupo_heat)
    grupo_heat.add_to(mapa)

    # ── Camada 4: Top-20 hubs (betweenness) ──
    grupo_hubs = folium.FeatureGroup(name="Top-20 hubs (betweenness)", show=True)
    for rank, (no, bw) in enumerate(metricas["hubs_betweenness"][:20], 1):
        if no not in G.nodes or "y" not in G.nodes[no]:
            continue
        lat = G.nodes[no]["y"]
        lon = G.nodes[no]["x"]
        grau = metricas["grau"].get(no, 0)
        cn   = metricas["core_number"].get(no, 0)

        # Tamanho proporcional ao rank (1 = maior)
        raio = max(6, 20 - rank)

        popup_html = f"""
        <b>Rank #{rank} por Betweenness</b><br>
        Nó OSM: {no}<br>
        Betweenness: {bw:.6f}<br>
        Grau: {grau}<br>
        Core number: {cn}<br>
        Coordenadas: {lat:.5f}, {lon:.5f}
        """

        folium.CircleMarker(
            location=[lat, lon],
            radius=raio,
            color="white",
            weight=1.5,
            fill=True,
            fill_color=COR_HUB,
            fill_opacity=0.85,
            popup=folium.Popup(popup_html, max_width=220),
            tooltip=f"#{rank} Hub (bw={bw:.5f})"
        ).add_to(grupo_hubs)

    grupo_hubs.add_to(mapa)

    # ── Camada 5: Top-10 hubs por grau ───────
    grupo_grau = folium.FeatureGroup(name="Top-10 hubs (grau)", show=False)
    for rank, (no, grau) in enumerate(metricas["hubs_grau"][:10], 1):
        if no not in G.nodes or "y" not in G.nodes[no]:
            continue
        lat = G.nodes[no]["y"]
        lon = G.nodes[no]["x"]
        bw  = metricas["betweenness"].get(no, 0)
        cn  = metricas["core_number"].get(no, 0)
        popup_html = f"""
        <b>Rank #{rank} por Grau</b><br>
        Nó OSM: {no}<br>
        Grau: {grau}<br>
        Betweenness: {bw:.6f}<br>
        Core number: {cn}
        """
        folium.CircleMarker(
            location=[lat, lon],
            radius=10,
            color="white",
            weight=1.5,
            fill=True,
            fill_color=COR_BW_ALTO,
            fill_opacity=0.9,
            popup=folium.Popup(popup_html, max_width=220),
            tooltip=f"#{rank} Hub grau={grau}"
        ).add_to(grupo_grau)
    grupo_grau.add_to(mapa)

    # ── Legenda e controle de camadas ─────────
    folium.LayerControl(collapsed=False).add_to(mapa)

    legenda_html = """
    <div style="position:fixed; bottom:30px; left:30px; z-index:9999;
                background:white; padding:12px 16px; border-radius:8px;
                box-shadow:0 2px 8px rgba(0,0,0,0.2); font-size:12px;">
      <b>Legenda</b><br>
      <span style="color:#8e44ad;">━━</span> K-core (núcleo denso)<br>
      <span style="color:#e74c3c;">●</span> Top-20 betweenness<br>
      <span style="color:#f39c12;">●</span> Top-10 grau<br>
      <span style="color:#7f8c8d;">━</span> Rede viária completa<br>
      <i>Clique nos pontos para detalhes</i>
    </div>
    """
    mapa.get_root().html.add_child(folium.Element(legenda_html))

    mapa.save(MAPA_HTML)
