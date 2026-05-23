# 🗺️ Análise Estrutural da Malha Viária de Natal/RN
### Planejamento de Corredores de Metrô com Teoria dos Grafos
#### Discente: Kawan Vinicius Feitosa de Oliveira

> Trabalho prático da disciplina **Algoritmos e Estrutura de Dados II**  
> Tema: Análise Estrutural de Redes Urbanas com OSMnx, NetworkX e Gephi

---

## 📋 Sobre o projeto

Este projeto aplica conceitos de **teoria dos grafos** à malha viária de **Natal/RN** com o objetivo de identificar os elementos estruturais mais importantes da rede e propor localizações para estações de metrô baseadas em métricas quantitativas.

A ideia central é tratar a cidade como um grafo:
- **Nós** → interseções e pontos relevantes da malha viária
- **Arestas** → vias e segmentos de rua entre interseções

A partir dessa modelagem, calculamos métricas de grafos para responder: *quais pontos da cidade são estruturalmente mais críticos para a mobilidade urbana?*

---

## ❓ Questão central

> *Quais são os elementos estruturais mais importantes da malha viária de Natal/RN e como diferentes métricas de grafos (grau, centralidade e k-core) ajudam a caracterizá-los?*

---

## 🏙️ Por que Natal/RN?

Natal é a **única capital brasileira sem metrô em operação plena**. A cidade possui uma configuração espacial desafiadora:

- O **Rio Potengi** divide a malha urbana entre Zona Norte e Zona Sul, criando gargalos de mobilidade identificáveis via betweenness centrality
- A **Zona Norte**, mais populosa, tem acesso limitado ao restante da cidade, com alta dependência de poucas travessias que acabam "gargalando"
- A **Zona Sul** (Ponta Negra, Capim Macio) concentra a maior densidade viária, detectável via k-core decomposition

Isso torna Natal um caso de estudo ideal para demonstrar como teoria dos grafos pode orientar decisões reais de infraestrutura urbana.

---

## 🗂️ Estrutura do projeto

```
.
├── analise_natal_metro.ipynb   # Notebook principal (rode este)
├── main.py                     # Orquestrador do pipeline (scripts)
├── m1_coleta.py                # Download da rede via OSMnx
├── m2_metricas.py              # Cálculo de métricas (NetworkX)
├── m3_analise.py               # Análise e respostas às 7 perguntas
├── m4_visualizacao.py          # Visualizações matplotlib + folium
├── m5_exportacao.py            # Exportação .graphml para Gephi
└── README.md
```

Os arquivos gerados pela execução ficam na mesma pasta:

```
├── natal_drive_bruto.graphml       # Cache da rede (gerado na 1ª execução)
├── natal_drive_completo.graphml    # Exportação para o Gephi
├── mapa_natal.html                 # Mapa interativo geral
├── mapa_metro_proposto.html        # Mapa com estações propostas
├── relatorio_analise.txt           # Respostas às 7 perguntas
└── graficos/
    ├── fig1_distribuicao_grau.png
    ├── fig2_grau_vs_betweenness.png
    └── fig3_distribuicao_core.png
```

---

## ⚙️ Dependências

| Biblioteca | Versão mínima | Uso |
|---|---|---|
| `osmnx` | 1.9+ | Download da rede viária do OpenStreetMap |
| `networkx` | 3.0+ | Cálculo de todas as métricas de grafos |
| `folium` | 0.15+ | Mapas interativos HTML |
| `matplotlib` | 3.7+ | Visualizações estáticas |
| `numpy` | 1.24+ | Operações numéricas e estatísticas |
| `scikit-learn` | 1.3+ | KMeans para clusterização de estações |
| `geopandas` | 0.13+ | Dependência do OSMnx |

Instale tudo com:

```bash
pip install osmnx networkx folium matplotlib numpy scikit-learn geopandas
```

No **Google Colab**, execute a célula da Seção 0 do notebook; ela vai instalar tudo automaticamente, pra que não precise rodar comandos manualmente no terminal 😉.

---

## 🚀 Como executar

### Opção A — Jupyter Notebook (recomendado)

1. Abra o `analise_natal_metro.ipynb` no VS Code, JupyterLab ou Google Colab
2. Execute as células em ordem, seção por seção
3. A **primeira execução** baixa a rede do OpenStreetMap (~2–5 min dependendo da conexão) e salva o cache `natal_drive_bruto.graphml`
4. Execuções seguintes carregam do cache e são imediatas

### Opção B — Scripts Python

```bash
python main.py
```

---

## 📐 Decisões técnicas

### Por que `network_type="drive"`?
Utilizamos o tipo `drive` porque o objetivo é analisar mobilidade urbana de ônibus e metrô, que compartilham a infraestrutura viária de veículos motorizados. Ciclovias e calçadas não são relevantes para o traçado de metrô.

### Por que converter para grafo não-dirigido?

| Métrica | Grafo usado | Justificativa |
|---|---|---|
| Grau in/out | MultiDiGraph original | Preserva informação direcional |
| Grau total | Graph não-dirigido | Definição clássica de grau |
| Betweenness | Graph não-dirigido | Maioria das vias em Natal é mão dupla |
| Closeness | Graph não-dirigido | Idem |
| K-core | Graph não-dirigido | Algoritmo de peeling exige grafo simples |

### Por que `k=500` na amostragem do betweenness?
O cálculo exato de betweenness para ~18k nós teria complexidade O(VE), levando dezenas de minutos. Com `k=500` pares amostrados aleatoriamente obtemos uma aproximação com erro relativo < 5% nos nós mais importantes, em ~2 minutos.

### Como o valor de k é escolhido para o k-core?
Usamos `k = ceil(k_max × 0.6)` — 60% do core máximo da rede. Isso garante um núcleo denso o suficiente para revelar a espinha dorsal urbana, mas geograficamente amplo o suficiente para cobrir múltiplas regiões de Natal, não apenas um único bairro.

---

## 📊 Métricas calculadas

**Grau** — número de vias conectadas a cada interseção. Mede conectividade local. Hubs de grau alto são grandes cruzamentos.

**Betweenness centrality** — frequência com que um nó aparece nos caminhos mais curtos entre todos os pares da rede. Mede importância global para o fluxo. Um nó pode ter grau baixo e betweenness alto se for a única ligação entre dois bairros — exatamente o tipo de ponto crítico que justifica uma estação de metrô.

**Closeness centrality** — inverso da distância média de um nó para todos os outros. Nós com closeness alto estão "perto de tudo" na rede.

**Core number (k-core)** — resultado da decomposição k-core: remoção iterativa dos nós de grau menor que k até estabilizar. O core number de um nó indica o subgrafo mais denso do qual ele faz parte. Revela a hierarquia estrutural da rede — do núcleo consolidado à periferia esparsa.

---

## 🗺️ Visualizações geradas

### Mapas interativos (abrir no navegador)

**`mapa_natal.html`** — mapa completo da rede com quatro camadas ativáveis:
- Rede viária completa (cinza)
- Subgrafo k-core (roxo) — núcleo denso
- Heatmap de betweenness — regiões de maior fluxo
- Top-20 hubs por betweenness (vermelho) — candidatos a estações

**`mapa_metro_proposto.html`** — proposta de traçado com N estações selecionadas por betweenness e distribuídas geograficamente via clusterização KMeans. Clique em cada marcador para ver as métricas do nó.

### Gráficos estáticos (`graficos/`)

**`fig1_distribuicao_grau.png`** — distribuição de grau em escala linear e log-log. A escala log-log revela se a rede tem cauda longa (característica de redes heterogêneas).

**`fig2_grau_vs_betweenness.png`** — scatter plot grau × betweenness com cor proporcional ao core number. Responde diretamente à Pergunta 1: os nós de maior grau coincidem com os de maior betweenness?

**`fig3_distribuicao_core.png`** — distribuição de core numbers com destaque no k escolhido para análise.

---

## 🔍 Visualizações no Gephi

Importe o arquivo `natal_drive_completo.graphml` no **Gephi Desktop** (gephi.org).

### Atributos disponíveis nos nós

| Atributo | Tipo | Uso no Gephi |
|---|---|---|
| `longitude` | double | Geo Layout — eixo X |
| `latitude` | double | Geo Layout — eixo Y |
| `grau` | integer | Tamanho do nó |
| `core_number` | integer | Cor do nó |
| `betweenness` | double | Destaque / filtro |
| `closeness` | double | Filtro opcional |

### Visualização geográfica (9.1)
`Layout → Geo Layout → Longitude: longitude | Latitude: latitude → Executar`

Preserva a forma real de Natal. Permite identificar geograficamente onde estão os hubs, o núcleo k-core e os gargalos de mobilidade.

### Visualização estrutural (9.2)
`Layout → ForceAtlas2 → Escala: 10 | Gravidade: 5 | LinLog: ✅ → Executar`

Revela a organização estrutural independente da geografia. Nós muito conectados gravitam para o centro; periféricos ficam nas bordas.

### Codificação visual obrigatória
- **Tamanho** → `Aparência → Nós → Tamanho → Ranking → grau` (min: 2, max: 20)
- **Cor** → `Aparência → Nós → Cor → Ranking → core_number` (paleta Plasma)
- **Destaque betweenness** → `Aparência → Nós → Cor → Ranking → betweenness`

### Filtros obrigatórios
`Filtros → Atributos → Intervalo → grau` — arraste o slider esquerdo até o percentil 90 para ver o top 10% dos nós por grau.

`Filtros → Atributos → Intervalo → core_number` — defina o mínimo como K_ESCOLHIDO (ver output da Seção 3 do notebook) para visualizar o subgrafo k-core.

---

## 💬 Respostas às 7 perguntas obrigatórias

As respostas completas e baseadas nos dados reais de Natal são geradas automaticamente no arquivo `relatorio_analise.txt` ao executar o notebook. Um resumo:

**1. Os nós com maior grau coincidem com os de maior betweenness?**
Parcialmente. Grandes cruzamentos (alto grau) nem sempre são os pontos mais críticos para o fluxo geral (alto betweenness). Corredores que ligam zonas distintas dominam o betweenness sem ter o maior número de interseções.

**2. O núcleo k-core coincide com os principais hubs?**
Os hubs por grau tendem a estar no k-core. Os hubs por betweenness podem estar fora — especialmente pontos de travessia entre zonas esparsas como as pontes sobre o Potengi.

**3. O que betweenness revela que grau não revela?**
A importância global do nó para o fluxo de toda a rede. Um nó com grau 3 pode ter betweenness altíssimo se for a única ligação entre dois bairros — informação invisível para o grau.

**4. O que muda entre a visualização geográfica e a estrutural?**
A geográfica revela *onde* estão os elementos importantes. A estrutural (ForceAtlas2) revela *o quê* é importante estruturalmente — o núcleo denso aparece no centro, a periferia nas bordas, independente da posição real na cidade.

**5. Existem regiões críticas para mobilidade?**
Sim: os acessos à Zona Norte (pontes sobre o Potengi) e os corredores radiais que ligam zonas distintas concentram betweenness desproporcional — gargalos estruturais onde intervenções de transporte público teriam maior impacto.

**6. A rede é homogênea ou heterogênea?**
Heterogênea. A distribuição de grau tem cauda longa — a maioria dos nós tem grau 2–4, mas poucos concentram muitas conexões. Característico de cidades que cresceram sem planejamento de grid regular.

**7. Os resultados fazem sentido urbanisticamente?**
Sim. Os hubs por grau coincidem com grandes cruzamentos de avenidas conhecidas; o k-core alto concentra-se na região central e Zona Sul consolidada; a Zona Norte aparece como subcluster periférico — consistente com a realidade urbana de Natal.

---

## 🚇 Proposta de traçado de metrô

A análise aponta três critérios estruturais para o traçado ideal:

1. **Nós de alto betweenness** — pontos de máxima intermediação, onde uma estação atende o maior número de origens e destinos possíveis
2. **Travessia do Potengi** — o gargalo estrutural mais crítico da rede; qualquer intervenção aqui tem impacto desproporcional na mobilidade
3. **Cobertura do k-core periférico** — bairros fora do núcleo denso têm menos alternativas de rota e maior dependência de transporte público

Esses três critérios convergem para um corredor **Norte-Sul** como o traçado de maior impacto estrutural — alinhado com os estudos de mobilidade urbana historicamente discutidos para Natal.

---

## 📚 Referências

- Boeing, G. (2017). OSMnx: New methods for acquiring, constructing, analyzing, and visualizing complex street networks. *Computers, Environment and Urban Systems*, 65, 126–139.
- Newman, M. E. J. (2010). *Networks: An Introduction*. Oxford University Press.
- Bastian, M., Heymann, S., & Jacomy, M. (2009). Gephi: An open source software for exploring and manipulating networks. *ICWSM*.
- OpenStreetMap contributors (2024). OpenStreetMap. https://www.openstreetmap.org