"""Streamlit app para visualizar resultados de extração e análises."""
import json
from pathlib import Path

import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Extração - GoodLaw", layout="wide")

st.title("📊 Análise de Extração - GoodLaw")
st.markdown(
    "Visualização estatística dos dados extraídos do pipeline de classificação Lei do Bem"
)

# Carregar relatório
@st.cache_data
def carregar_relatorio():
    """Carrega relatório de extração."""
    path = Path("data/relatorio_extracao.json")
    if not path.exists():
        st.error("⚠️ Relatório não encontrado. Execute scripts/gerar_relatorio.py primeiro.")
        st.stop()
    
    with open(path) as f:
        return json.load(f)

relatorio = carregar_relatorio()

# ============================================================================
# RESUMO EXECUTIVO
# ============================================================================
st.header("📋 Resumo Executivo")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total de Cards", f"{relatorio['total_cards']:,}")
with col2:
    st.metric("Entidades Únicas", relatorio['entidades']['total_entidades_unicas'])
with col3:
    alta = relatorio['qualidade']['cards_alta_confianca']
    pct = relatorio['qualidade']['pct_alta']
    st.metric("Alta Confiança", f"{alta:,}", f"{pct:.1f}%")
with col4:
    orfaos = sum(1 for _ in [
        relatorio['hierarquia']['cards_orfaos'],
        relatorio['hierarquia']['cards_solitarios']
    ])
    st.metric("Órfãos/Solitários", f"{relatorio['hierarquia']['cards_orfaos']:,} / {relatorio['hierarquia']['cards_solitarios']:,}")

# ============================================================================
# NATUREZA DA ATIVIDADE
# ============================================================================
st.header("🏷️  Natureza da Atividade")

col1, col2 = st.columns(2)

with col1:
    # Gráfico de pizza
    natureza_data = relatorio['natureza']
    naturezas = list(natureza_data['distribuicao'].keys())
    contagens = list(natureza_data['distribuicao'].values())
    
    fig_natureza = go.Figure(
        data=[go.Pie(
            labels=naturezas,
            values=contagens,
            hovertemplate="<b>%{label}</b><br>%{value} cards (%{percent})<extra></extra>",
        )]
    )
    fig_natureza.update_layout(height=400, showlegend=True)
    st.plotly_chart(fig_natureza, use_container_width=True)

with col2:
    # Tabela com confiança
    st.subheader("Distribuição e Confiança")
    rows = []
    for nat in sorted(natureza_data['distribuicao'].keys(), 
                      key=lambda x: -natureza_data['distribuicao'][x]):
        cont = natureza_data['distribuicao'][nat]
        pct = natureza_data['distribuicao_pct'][nat]
        conf = natureza_data['confianca_media_por_natureza'].get(nat, 0)
        rows.append({
            "Natureza": nat,
            "Count": cont,
            "% Total": f"{pct:.1f}%",
            "Confiança Média": f"{conf:.3f}"
        })
    
    st.dataframe(rows, use_container_width=True)

# ============================================================================
# ENTIDADES (SIGLAS)
# ============================================================================
st.header("🔤 Entidades Extraídas (Siglas)")

st.subheader(f"Total de {relatorio['entidades']['total_entidades_unicas']} siglas únicas em {relatorio['entidades']['total_mencoes']:,} menções")

col1, col2 = st.columns(2)

with col1:
    # Top 20 siglas
    siglas_data = relatorio['entidades']['siglas_mais_comuns'][:20]
    siglas_nomes = [s[0] for s in siglas_data]
    siglas_counts = [s[1] for s in siglas_data]
    
    fig_siglas = go.Figure(
        data=[go.Bar(
            x=siglas_counts,
            y=siglas_nomes,
            orientation='h',
            marker_color='steelblue',
            hovertemplate="<b>%{y}</b>: %{x} menções<extra></extra>",
        )]
    )
    fig_siglas.update_layout(
        title="Top 20 Siglas Mais Comuns",
        xaxis_title="Menções",
        yaxis_title="",
        height=500,
        margin=dict(l=100)
    )
    st.plotly_chart(fig_siglas, use_container_width=True)

with col2:
    # Top entidades
    st.subheader("Top 20 Entidades Únicas")
    entidades_data = relatorio['entidades']['top_entidades'][:20]
    rows = []
    for ent in entidades_data:
        rows.append({
            "Entidade": ent['entidade'],
            "Menções": ent['contagem'],
            "% Total": f"{ent['percentual']:.2f}%"
        })
    st.dataframe(rows, use_container_width=True)

# ============================================================================
# TEXTO
# ============================================================================
st.header("📝 Análise de Texto")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        "Comprimento médio - Cerne",
        f"{relatorio['texto']['comprimento_medio_cerne']:.1f} chars"
    )
    st.metric(
        "Cernes vazios",
        relatorio['texto']['cernes_vazios']
    )
with col2:
    st.metric(
        "Comprimento médio - Título",
        f"{relatorio['texto']['comprimento_medio_titulo']:.1f} chars"
    )
    st.metric(
        "Descrições vazias",
        relatorio['texto']['descricoes_vazias']
    )
with col3:
    st.metric(
        "Comprimento médio - Descrição",
        f"{relatorio['texto']['comprimento_medio_descricao']:.1f} chars"
    )

st.subheader("Palavras Mais Comuns (top 20)")
palavras_data = relatorio['texto']['palavras_comuns_top_20']
palavras = [p['palavra'] for p in palavras_data]
contagens = [p['contagem'] for p in palavras_data]

fig_palavras = px.bar(
    x=contagens,
    y=palavras,
    orientation='h',
    labels={"x": "Ocorrências", "y": ""},
    title="Frequência de Palavras",
)
fig_palavras.update_layout(height=500, margin=dict(l=150))
st.plotly_chart(fig_palavras, use_container_width=True)

# ============================================================================
# HIERARQUIA
# ============================================================================
st.header("🌳 Estrutura Hierárquica")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Profundidade Média", f"{relatorio['hierarquia']['profundidade_media']:.2f}")
    st.metric("Profundidade Máxima", relatorio['hierarquia']['profundidade_maxima'])
with col2:
    st.metric("OKRs (Raiz)", relatorio['hierarquia']['okrs_raiz'])
    st.metric("Initiatives/OKR (média)", f"{relatorio['hierarquia']['initiatives_por_okr_media']:.2f}")
with col3:
    st.metric("Histórias/Initiative (média)", f"{relatorio['hierarquia']['historias_por_initiative_media']:.2f}")

col1, col2 = st.columns(2)

with col1:
    # Distribuição de profundidade
    profundidade_data = relatorio['hierarquia']['distribuicao_profundidade']
    profundidades = sorted(int(p) for p in profundidade_data.keys())
    contagens_prof = [profundidade_data[str(p)] for p in profundidades]
    
    fig_prof = go.Figure(
        data=[go.Bar(
            x=profundidades,
            y=contagens_prof,
            marker_color='teal',
            hovertemplate="Profundidade %{x}: %{y} cards<extra></extra>",
        )]
    )
    fig_prof.update_layout(
        title="Distribuição de Profundidade Hierárquica",
        xaxis_title="Nível de Profundidade",
        yaxis_title="Quantidade de Cards",
        height=400,
    )
    st.plotly_chart(fig_prof, use_container_width=True)

with col2:
    # Relacionamentos
    st.subheader("Relacionamentos")
    relacionamentos = [
        ("Com Pai", relatorio['hierarquia']['cards_com_pai']),
        ("Órfãos", relatorio['hierarquia']['cards_orfaos']),
        ("Com Filhos", relatorio['hierarquia']['cards_com_filhos']),
        ("Solitários", relatorio['hierarquia']['cards_solitarios']),
    ]
    
    fig_rel = go.Figure(
        data=[go.Bar(
            y=[r[0] for r in relacionamentos],
            x=[r[1] for r in relacionamentos],
            orientation='h',
            marker_color=['green', 'red', 'blue', 'orange'],
            hovertemplate="%{y}: %{x} cards<extra></extra>",
        )]
    )
    fig_rel.update_layout(
        showlegend=False,
        xaxis_title="Quantidade de Cards",
        height=300,
        margin=dict(l=150)
    )
    st.plotly_chart(fig_rel, use_container_width=True)

# ============================================================================
# CONFIANÇA
# ============================================================================
st.header("🎯 Distribuição de Confiança")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Tipo (média)", f"{relatorio['confianca']['confianca_media_tipo']:.3f}")
with col2:
    st.metric("Cerne (média)", f"{relatorio['confianca']['confianca_media_cerne']:.3f}")
with col3:
    st.metric("Natureza (média)", f"{relatorio['confianca']['confianca_media_natureza']:.3f}")
with col4:
    st.metric("Hierarquia (média)", f"{relatorio['confianca']['confianca_media_hierarquia']:.3f}")

col1, col2 = st.columns(2)

with col1:
    # Distribuição de confiança tipo
    conf_tipo = relatorio['confianca']['distribuicao_confianca_tipo']
    faixas = sorted(conf_tipo.keys())
    contagens_tipo = [conf_tipo[f] for f in faixas]
    
    fig_conf_tipo = go.Figure(
        data=[go.Bar(
            x=faixas,
            y=contagens_tipo,
            marker_color='mediumslateblue',
            hovertemplate="Faixa %{x}: %{y} cards<extra></extra>",
        )]
    )
    fig_conf_tipo.update_layout(
        title="Distribuição de Confiança - Tipo",
        xaxis_title="Faixa de Confiança",
        yaxis_title="Quantidade de Cards",
        height=400,
    )
    st.plotly_chart(fig_conf_tipo, use_container_width=True)

with col2:
    # Penalidades
    st.subheader("Penalidades por Orfandade")
    st.metric("Penalidade Média", f"{relatorio['confianca']['penalidade_media']:.3f}")
    st.metric("Cards com Penalidade", relatorio['confianca']['cards_com_penalidade'])
    
    penalidade_pct = (relatorio['confianca']['cards_com_penalidade'] / relatorio['total_cards']) * 100
    st.info(f"**{penalidade_pct:.1f}%** dos cards sofrem penalidade por orfandade ou isolamento")

# ============================================================================
# QUALIDADE GERAL
# ============================================================================
st.header("✅ Avaliação de Qualidade Geral")

qualidade = relatorio['qualidade']
fig_qual = go.Figure(
    data=[go.Pie(
        labels=["Alta (>0.8)", "Média (0.5-0.8)", "Baixa (<0.5)"],
        values=[
            qualidade['cards_alta_confianca'],
            qualidade['cards_media_confianca'],
            qualidade['cards_baixa_confianca'],
        ],
        marker=dict(colors=['#2ecc71', '#f39c12', '#e74c3c']),
        hovertemplate="<b>%{label}</b><br>%{value} cards (%{percent})<extra></extra>",
    )]
)
fig_qual.update_layout(height=400)
st.plotly_chart(fig_qual, use_container_width=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.success(f"**{qualidade['cards_alta_confianca']:,}** ({qualidade['pct_alta']:.1f}%) Alta qualidade")
with col2:
    st.warning(f"**{qualidade['cards_media_confianca']:,}** ({qualidade['pct_media']:.1f}%) Média qualidade")
with col3:
    st.error(f"**{qualidade['cards_baixa_confianca']:,}** ({qualidade['pct_baixa']:.1f}%) Baixa qualidade")

# ============================================================================
# INSIGHTS E RECOMENDAÇÕES
# ============================================================================
st.header("💡 Insights e Recomendações")

col1, col2 = st.columns(2)

with col1:
    st.subheader("✓ Pontos Fortes")
    st.markdown("""
    - **Extração de Cerne**: 95% de confiança (textos bem estruturados)
    - **Tipagem**: 81.5% de confiança (hierarquia claramente definida)
    - **Qualidade Geral**: 41.6% em alta confiança
    - **Cobertura de Entidades**: 3,041 siglas únicas extraídas
    """)

with col2:
    st.subheader("⚠️ Pontos de Atenção")
    st.markdown(f"""
    - **Natureza Indefinida**: {qualidade['cards_media_confianca']} cards (35.2%) sem classificação clara
    - **Orfandade**: {relatorio['hierarquia']['cards_orfaos']:,} cards órfãos ({(relatorio['hierarquia']['cards_orfaos']/relatorio['total_cards']*100):.1f}%)
    - **Solitários**: {relatorio['hierarquia']['cards_solitarios']:,} cards sem filhos ({(relatorio['hierarquia']['cards_solitarios']/relatorio['total_cards']*100):.1f}%)
    - **Descrições Vazias**: {relatorio['texto']['descricoes_vazias']} cards sem descrição
    """)

st.markdown("---")
st.markdown("📊 **Próximas Etapas:** Implementação do Stage 2 (Exclusões Lei do Bem) com base nesta análise")
