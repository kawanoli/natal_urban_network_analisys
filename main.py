"""
main.py — Orquestrador do pipeline de análise de redes urbanas
Projeto: Malha viária de Natal/RN como grafo para planejamento de metrô
"""

import os
import sys

# ─────────────────────────────────────────────
# INSTALAÇÃO DE DEPENDÊNCIAS (Google Colab)
# ─────────────────────────────────────────────
def instalar_dependencias():
    """Instala pacotes necessários no ambiente Colab."""
    import subprocess
    pacotes = ["osmnx", "networkx", "folium", "matplotlib", "seaborn", "geopandas"]
    for pacote in pacotes:
        subprocess.run([sys.executable, "-m", "pip", "install", pacote, "-q"], check=True)
    print("✓ Dependências instaladas.")

# ─────────────────────────────────────────────
# PIPELINE PRINCIPAL
# ─────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  ANÁLISE ESTRUTURAL DA MALHA VIÁRIA DE NATAL/RN")
    print("  Planejamento de Corredores de Metrô via Grafos")
    print("=" * 60)

    # Garante que os módulos do projeto estão acessíveis
    sys.path.insert(0, os.path.dirname(__file__))

    # ── Módulo 1: Coleta da rede viária ──────────────────────
    print("\n[1/6] Coletando rede viária via OSMnx...")
    from m1_coleta import coletar_rede
    G = coletar_rede()

    # ── Módulo 2: Cálculo de métricas ────────────────────────
    print("\n[2/6] Calculando métricas estruturais (NetworkX)...")
    from m2_metricas import calcular_metricas
    G, metricas = calcular_metricas(G)

    # ── Módulo 3: Análise e respostas ─────────────────────────
    print("\n[3/6] Analisando resultados e respondendo perguntas...")
    from m3_analise import analisar_rede
    analisar_rede(G, metricas)

    # ── Módulo 4: Visualizações ───────────────────────────────
    print("\n[4/6] Gerando visualizações (matplotlib + folium)...")
    from m4_visualizacao import gerar_visualizacoes
    gerar_visualizacoes(G, metricas)

    # ── Módulo 5: Exportação para Gephi ──────────────────────
    print("\n[5/6] Exportando .graphml para o Gephi...")
    from m5_exportacao import exportar_gephi
    exportar_gephi(G, metricas)

    # ── Módulo 6: Proposta de estações de metrô ───────────────
    print("\n[6/6] Gerando proposta de estações de metrô...")
    from m6_estacoes import gerar_mapa_metro
    gerar_mapa_metro(G, metricas)

    print("\n" + "=" * 60)
    print("  Pipeline concluído com sucesso!")
    print("  Arquivos gerados:")
    print("    • natal_drive.graphml        → importe no Gephi")
    print("    • mapa_natal.html            → visualização geográfica")
    print("    • mapa_metro_proposto.html   → corredor e estações")
    print("    • graficos/                  → distribuições e subgrafos")
    print("=" * 60)


if __name__ == "__main__":
    # Descomente a linha abaixo se estiver rodando no Colab pela primeira vez
    # instalar_dependencias()
    main()