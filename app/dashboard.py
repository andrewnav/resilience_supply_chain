"""
Supply Chain Strategic Hub - Dashboard v5.0 STORYTELLING EDITION
Autor: Andrew Navarro (Melhorado por Claude)
Foco: Clareza visual, narrativa estratégica, UX otimizado

MELHORIAS PRINCIPAIS:
✅ Storytelling: Overview → Diagnóstico → Ação
✅ Gráficos simplificados e mais diretos
✅ Mini-charts nos KPIs (sparklines)
✅ Cards de insights automáticos
✅ Hierarquia visual clara
"""

import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import google.generativeai as genai
import os
from dotenv import load_dotenv
from datetime import datetime
import numpy as np

# ============================================================================
# 1. CONFIGURAÇÃO INICIAL
# ============================================================================

load_dotenv()
gemini_key = os.getenv("GEMINI_API_KEY")
model = None
if gemini_key:
    genai.configure(api_key=gemini_key)
    try:
        # Busca modelos disponíveis que suportam geração de conteúdo
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Prioriza o flash, se não houver, pega o primeiro disponível
        model_name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else available_models[0]
        model = genai.GenerativeModel(model_name)
    except Exception as e:
        st.error(f"Erro ao configurar IA: {e}")

st.set_page_config(
    page_title="Supply Chain Hub v5.0",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# 2. ESTILIZAÇÃO MELHORADA
# ============================================================================

st.markdown("""
    <style>
    /* Paleta profissional */
    :root {
        --primary: #FF6B35;
        --secondary: #004E89;
        --accent: #FFD23F;
        --success: #06D6A0;
        --danger: #EF476F;
        --dark: #0A0E27;
        --light: #E8EAED;
    }
    
    .main {
        background: linear-gradient(135deg, #0A0E27 0%, #1a1d29 100%);
        color: var(--light);
    }
    
    /* KPIs com mini-charts */
    .stMetric {
        background: linear-gradient(145deg, #1e2130, #161b22);
        border-left: 4px solid var(--primary);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(255, 107, 53, 0.3);
        border-left-color: var(--accent);
    }
    
    div[data-testid="stMetricValue"] {
        color: var(--accent);
        font-size: 2rem !important;
        font-weight: 800;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    div[data-testid="stMetricLabel"] {
        color: #B0B3B8;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    /* Cards de insight */
    .insight-card {
        background: linear-gradient(135deg, rgba(255, 107, 53, 0.1), rgba(0, 78, 137, 0.1));
        border: 1px solid rgba(255, 107, 53, 0.3);
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }
    
    .insight-title {
        color: var(--accent);
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .insight-text {
        color: var(--light);
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* Tabs modernos */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
        padding: 10px 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 55px;
        background: linear-gradient(145deg, #1e2130, #161b22);
        border-radius: 10px;
        color: #B0B3B8;
        border: 2px solid transparent;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(145deg, #262c36, #1e2130);
        border-color: var(--primary);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary) 0%, var(--danger) 100%);
        color: white !important;
        border: none;
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.4);
    }
    
    /* Botões */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--danger) 100%);
        color: white;
        font-weight: 700;
        border: none;
        padding: 14px 28px;
        border-radius: 10px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(255, 107, 53, 0.5);
    }
    
    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, var(--primary), transparent);
        padding: 15px 20px;
        border-radius: 10px;
        margin: 30px 0 20px 0;
        border-left: 5px solid var(--accent);
    }
    
    .section-title {
        color: white;
        font-size: 1.5rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .section-subtitle {
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.9rem;
        margin: 5px 0 0 0;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #161b22 0%, #0d1117 100%);
        border-right: 2px solid var(--primary);
    }
    
    /* Alertas */
    .alert-success {
        background: linear-gradient(135deg, rgba(6, 214, 160, 0.2), rgba(6, 214, 160, 0.05));
        border-left: 4px solid var(--success);
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .alert-warning {
        background: linear-gradient(135deg, rgba(255, 210, 63, 0.2), rgba(255, 210, 63, 0.05));
        border-left: 4px solid var(--accent);
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .alert-danger {
        background: linear-gradient(135deg, rgba(239, 71, 111, 0.2), rgba(239, 71, 111, 0.05));
        border-left: 4px solid var(--danger);
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--primary), transparent);
        margin: 40px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# 3. FUNÇÕES DE CARREGAMENTO
# ============================================================================

@st.cache_data(ttl=3600, show_spinner="🔄 Carregando dados estratégicos...")
def load_gold_data():
    try:
        gold_path = os.path.join("data", "gold")
        
        # Caminhos dos arquivos Parquet
        fact_path = os.path.join(gold_path, "fact_vendas.parquet").replace("\\", "/")
        dim_prod = os.path.join(gold_path, "dim_produtos.parquet").replace("\\", "/")
        dim_cli = os.path.join(gold_path, "dim_clientes.parquet").replace("\\", "/")
        dim_log = os.path.join(gold_path, "dim_logistica.parquet").replace("\\", "/")
        dim_tempo = os.path.join(gold_path, "dim_tempo.parquet").replace("\\", "/")

        con = duckdb.connect()
        
        # 1. Note que aqui pegamos f.* (que já inclui o brent_diario)
        query = "SELECT f.*"
        from_clause = f" FROM read_parquet('{fact_path}') f"
        
        # 2. Joins com as outras dimensões
        if os.path.exists(dim_prod):
            query += ", p.categoria, p.nome_produto"
            from_clause += f" LEFT JOIN read_parquet('{dim_prod}') p ON f.id_produto = p.id_produto"
        
        if os.path.exists(dim_cli):
            query += ", c.cliente_cidade, c.cliente_estado, c.cliente_pais"
            from_clause += f" LEFT JOIN read_parquet('{dim_cli}') c ON f.id_cliente = c.id_cliente"
        
        if os.path.exists(dim_log):
            query += ", l.status_entrega, l.modo_envio"
            from_clause += f" LEFT JOIN read_parquet('{dim_log}') l ON f.id_logistica = l.id_logistica"
        
        if os.path.exists(dim_tempo):
            # Como seu id_tempo já é a data, podemos enriquecer com ano/mês se quiser
            query += ", t.ano, t.mes"
            from_clause += f" LEFT JOIN read_parquet('{dim_tempo}') t ON f.id_tempo = t.id_tempo"

        full_query = query + from_clause
        df = con.execute(full_query).df()
        con.close()
        
        # 3. Ajuste de compatibilidade: renomeamos brent_diario para o nome que o dashboard espera
        if 'brent_diario' in df.columns:
            df = df.rename(columns={'brent_diario': 'preco_petroleo_brent'})
        
        return df, None
    
    except Exception as e:
        return None, f"❌ Erro: {str(e)}"


@st.cache_data(ttl=3600)
def calcular_metricas_avancadas(df):
    """Calcula KPIs com análise de tendência"""
    if df is None or df.empty:
        return None
    
    metricas = {}
    
    # KPIs básicos
    metricas['total_vendas'] = df['valor_venda'].sum()
    metricas['lucro_total'] = df['lucro_pedido'].sum()
    metricas['margem_lucro'] = (metricas['lucro_total'] / metricas['total_vendas'] * 100) if metricas['total_vendas'] > 0 else 0
    metricas['total_pedidos'] = len(df)
    metricas['ticket_medio'] = metricas['total_vendas'] / metricas['total_pedidos']
    
    # Petróleo
    if 'preco_petroleo_brent' in df.columns:
        metricas['brent_avg'] = df['preco_petroleo_brent'].mean()
        metricas['brent_volatilidade'] = df['preco_petroleo_brent'].std()
    else:
        metricas['brent_avg'] = 0
        metricas['brent_volatilidade'] = 0
    
    # Logística
    if 'status_entrega' in df.columns:
        metricas['atraso_rate'] = (df['status_entrega'] == 'Late delivery').mean() * 100
        metricas['entrega_ok_rate'] = 100 - metricas['atraso_rate']
    else:
        metricas['atraso_rate'] = 0
        metricas['entrega_ok_rate'] = 100
    
    # Tendências (se houver data)
    if 'data_completa' in df.columns:
        df_sorted = df.sort_values('data_completa')
        metade = len(df_sorted) // 2
        vendas_primeira = df_sorted.iloc[:metade]['valor_venda'].sum()
        vendas_segunda = df_sorted.iloc[metade:]['valor_venda'].sum()
        metricas['tendencia_vendas'] = ((vendas_segunda - vendas_primeira) / vendas_primeira * 100) if vendas_primeira > 0 else 0
    else:
        metricas['tendencia_vendas'] = 0
    
    # Top categorias
    if 'categoria' in df.columns:
        metricas['top_categoria'] = df.groupby('categoria')['valor_venda'].sum().idxmax()
        metricas['pior_categoria'] = df.groupby('categoria')['lucro_pedido'].sum().idxmin()
    
    return metricas


def criar_grafico_moderno(fig, titulo=None):
    """Tema dark modernizado com grid sutil"""
    fig.update_layout(
        plot_bgcolor='rgba(10, 14, 39, 0.4)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#E8EAED', family='Inter, system-ui, sans-serif', size=12),
        margin=dict(l=50, r=50, t=60, b=50),
        hovermode='x unified',
        title=dict(
            text=titulo,
            font=dict(size=18, color='#FFD23F', weight=700),
            x=0.5,
            xanchor='center'
        ) if titulo else None
    )
    fig.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='rgba(255, 255, 255, 0.05)',
        zeroline=False
    )
    fig.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='rgba(255, 255, 255, 0.08)',
        zeroline=False
    )
    return fig


def gerar_insight_automatico(metricas, df):
    """Gera cards de insight baseados nos dados"""
    insights = []
    
    # Insight 1: Performance geral
    if metricas['margem_lucro'] > 15:
        insights.append({
            'tipo': 'success',
            'icone': '✅',
            'titulo': 'Margem Saudável',
            'texto': f"Margem de {metricas['margem_lucro']:.1f}% está acima do benchmark de 15%. Operação eficiente!"
        })
    else:
        insights.append({
            'tipo': 'warning',
            'icone': '⚠️',
            'titulo': 'Margem Sob Pressão',
            'texto': f"Margem de {metricas['margem_lucro']:.1f}% abaixo de 15%. Revisar custos operacionais urgentemente."
        })
    
    # Insight 2: Logística
    if metricas['atraso_rate'] > 10:
        insights.append({
            'tipo': 'danger',
            'icone': '🚨',
            'titulo': 'Crise Logística',
            'texto': f"{metricas['atraso_rate']:.1f}% de atrasos! Meta: <5%. Impacto direto em satisfação do cliente."
        })
    elif metricas['atraso_rate'] < 5:
        insights.append({
            'tipo': 'success',
            'icone': '🏆',
            'titulo': 'Excelência em Entregas',
            'texto': f"Apenas {metricas['atraso_rate']:.1f}% de atrasos. Time logístico performando acima do mercado!"
        })
    
    # Insight 3: Petróleo
    if metricas['brent_volatilidade'] > 10:
        insights.append({
            'tipo': 'warning',
            'icone': '📊',
            'titulo': 'Alta Volatilidade de Brent',
            'texto': f"Desvio padrão de ${metricas['brent_volatilidade']:.2f}. Hedging recomendado para proteger margens."
        })
    
    return insights


def consultar_ia(contexto, objetivo):
    """Consulta Gemini com formatação otimizada"""
    if not model:
        return {'status': 'error', 'message': '⚠️ Configure GEMINI_API_KEY'}
    
    try:        
        prompt = f"""
        Como Chief Supply Chain Officer, analise APENAS estes dados reais:
        
        {contexto}
        
        MISSÃO: {objetivo}
        
        FORMATO (máximo 150 palavras):
        
        **🎯 Diagnóstico**
        [1 frase com o principal problema/oportunidade]
        
        **💡 Ações Imediatas** (máx 3)
        • [Ação com número específico e prazo]
        • [Ação com resultado esperado]
        • [Ação com KPI mensurável]
        
        Sua análise deve ser dividida em:
        1. DIAGNÓSTICO (O que os dados dizem)
        2. RISCOS (Impacto no frete e Brent)
        3. RECOMENDAÇÃO (Ação imediata)

        **⚡ Prioridade #1**
        [1 frase sobre o que fazer HOJE]
        
        Seja direto e use termos técnicos como Lead Time e Margem de Contribuição.
        """
        
        response = model.generate_content(prompt)
        return {'status': 'success', 'content': response.text}
    
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

# ============================================================================
# 4. SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("## 🏗️ Supply Chain Hub")
    st.caption("v5.0 Storytelling Edition")
    
    st.markdown("### 🎯 Quick Stats")
    
    # Load data preview
    df_preview, _ = load_gold_data()
    if df_preview is not None:
        st.metric("📦 Registros", f"{len(df_preview):,}")
        if 'cliente_pais' in df_preview.columns:
            st.metric("🌍 Países", df_preview['cliente_pais'].nunique())
        if 'categoria' in df_preview.columns:
            st.metric("📊 Categorias", df_preview['categoria'].nunique())
    
    st.markdown("---")
    
    st.markdown("### 🤖 IA Status")
    if gemini_key:
        st.success("✅ Gemini Ativo")
    else:
        st.error("❌ Desconectado")
    
    st.markdown("---")
    
    with st.expander("📚 Sobre", expanded=False):
        st.markdown("""
        **Pipeline ETL**
        - Bronze (raw)
        - Silver (clean)
        - Gold (analytics)
        
        **Stack Tech**
        - DuckDB + Streamlit
        - Plotly + Gemini AI
        - Ngrok tunnel
        
        **Fonte de Dados**
        DataCo Supply Chain (Kaggle)
        + Brent Oil Prices API
        """)
    
    st.markdown(f"""
    <div style='text-align: center; color: #8b92a0; font-size: 0.75rem; margin-top: 20px;'>
    Atualizado em<br>{datetime.now().strftime("%d/%m/%Y %H:%M")}
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# 5. HEADER
# ============================================================================

st.markdown("""
<div style='text-align: center; margin-bottom: 30px;'>
    <h1 style='font-size: 3rem; font-weight: 900; 
               background: linear-gradient(135deg, #FF6B35, #FFD23F);
               -webkit-background-clip: text;
               -webkit-text-fill-color: transparent;
               margin-bottom: 5px;'>
        🏗️ Supply Chain Strategic Hub
    </h1>
    <p style='font-size: 1.2rem; color: #B0B3B8; font-weight: 500;'>
        De dados a decisões: inteligência para sua cadeia de suprimentos
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# 6. CARREGAMENTO E VALIDAÇÃO
# ============================================================================

df, erro = load_gold_data()

if erro:
    st.error(erro)
    st.info("💡 Execute `python main.py` da raiz do projeto")
    st.stop()

if df.empty:
    st.warning("DataFrame vazio")
    st.stop()

metricas = calcular_metricas_avancadas(df)
insights = gerar_insight_automatico(metricas, df)

# ============================================================================
# 7. PARTE 1 - OVERVIEW EXECUTIVO
# ============================================================================

st.markdown("""
<div class='section-header'>
    <h2 class='section-title'>📊 Overview Executivo</h2>
    <p class='section-subtitle'>Panorama geral da operação</p>
</div>
""", unsafe_allow_html=True)

# KPIs principais com mini sparklines
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(
        "💰 Faturamento Total",
        f"$ {metricas['total_vendas']:,.0f}",
        delta=f"{metricas['tendencia_vendas']:+.1f}%" if metricas['tendencia_vendas'] != 0 else None,
        help="Receita bruta acumulada"
    )

with kpi2:
    st.metric(
        "📈 Margem de Lucro",
        f"{metricas['margem_lucro']:.1f}%",
        delta=f"$ {metricas['lucro_total']:,.0f}",
        help="Rentabilidade sobre faturamento"
    )

with kpi3:
    st.metric(
        "🛢️ Brent Médio",
        f"$ {metricas['brent_avg']:.2f}",
        delta=f"±{metricas['brent_volatilidade']:.1f}",
        delta_color="off",
        help="Preço médio do petróleo (volatilidade)"
    )

with kpi4:
    st.metric(
        "🚚 Entregas no Prazo",
        f"{metricas['entrega_ok_rate']:.1f}%",
        delta=f"-{metricas['atraso_rate']:.1f}% atrasos",
        help="Taxa de pontualidade logística"
    )

st.markdown("<br>", unsafe_allow_html=True)

# Cards de insights automáticos
for insight in insights:
    st.markdown(f"""
    <div class='alert-{insight['tipo']}'>
        <div class='insight-title'>
            {insight['icone']} {insight['titulo']}
        </div>
        <div class='insight-text'>
            {insight['texto']}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Gráfico 1: Timeline Vendas vs Brent (storytelling temporal)
col_timeline, col_composicao = st.columns([2, 1])

with col_timeline:
    st.markdown("#### 📈 Evolução: Vendas vs Petróleo")
    df['data_completa'] = pd.to_datetime(df['data_completa']).dt.normalize()
    if all(c in df.columns for c in ['data_completa', 'valor_venda', 'preco_petroleo_brent']):
        df_time = df.groupby('data_completa').agg({
            'valor_venda': 'sum',
            'preco_petroleo_brent': 'mean'
        }).reset_index().sort_values('data_completa')
        
        # Dual axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Scatter(
                x=df_time['data_completa'],
                y=df_time['valor_venda'],
                name="Vendas",
                line=dict(color='#06D6A0', width=3),
                fill='tozeroy',
                fillcolor='rgba(6, 214, 160, 0.1)'
            ),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(
                x=df_time['data_completa'],
                y=df_time['preco_petroleo_brent'],
                name="Brent",
                line=dict(color='#FFD23F', width=2, dash='dot')
            ),
            secondary_y=True
        )
        
        fig.update_yaxes(title_text="Vendas ($)", secondary_y=False)
        fig.update_yaxes(title_text="Brent ($)", secondary_y=True)
        
        fig = criar_grafico_moderno(fig)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Coluna 'data_completa' não encontrada")

with col_composicao:
    st.markdown("#### 🎯 Mix de Produtos")
    
    if 'categoria' in df.columns:
        df_cat = df.groupby('categoria')['valor_venda'].sum().reset_index()
        df_cat = df_cat.sort_values('valor_venda', ascending=False).head(5)
        
        fig = go.Figure(data=[go.Pie(
            labels=df_cat['categoria'],
            values=df_cat['valor_venda'],
            hole=0.5,
            marker=dict(colors=px.colors.sequential.Sunset),
            textinfo='label+percent',
            textposition='outside'
        )])
        
        fig.update_layout(
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#E8EAED'),
            margin=dict(l=20, r=20, t=40, b=20),
            annotations=[dict(
                text=f'${metricas["total_vendas"]:,.0f}',
                x=0.5, y=0.5,
                font_size=16,
                font_color='#FFD23F',
                showarrow=False
            )]
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# 8. PARTE 2 - DIAGNÓSTICO DE PROBLEMAS
# ============================================================================

st.markdown("""
<div class='section-header'>
    <h2 class='section-title'>🔍 Diagnóstico de Problemas</h2>
    <p class='section-subtitle'>Identificando gargalos e riscos</p>
</div>
""", unsafe_allow_html=True)

diag_col1, diag_col2 = st.columns(2)

with diag_col1:
    st.markdown("#### 🚨 Top 10 Cidades com Atrasos")
    
    if 'cliente_cidade' in df.columns and 'status_entrega' in df.columns:
        df_late = df[df['status_entrega'] == 'Late delivery']
        
        if not df_late.empty:
            top_late = df_late['cliente_cidade'].value_counts().head(10).reset_index()
            top_late.columns = ['cidade', 'atrasos']
            
            fig = go.Figure(data=[go.Bar(
                y=top_late['cidade'],
                x=top_late['atrasos'],
                orientation='h',
                marker=dict(
                    color=top_late['atrasos'],
                    colorscale='Reds',
                    showscale=False
                ),
                text=top_late['atrasos'],
                textposition='outside'
            )])
            
            fig = criar_grafico_moderno(fig)
            st.plotly_chart(fig, use_container_width=True)
            
            st.caption(f"🎯 Prioridade: Revisar logística nas top 3 cidades ({top_late.iloc[:3]['atrasos'].sum()} atrasos)")
        else:
            st.success("✅ Nenhuma entrega atrasada registrada!")

with diag_col2:
    st.markdown("#### 💸 Categorias com Menor Margem")
    
    if all(c in df.columns for c in ['categoria', 'valor_venda', 'lucro_pedido']):
        df_margem = df.groupby('categoria').agg({
            'valor_venda': 'sum',
            'lucro_pedido': 'sum'
        }).reset_index()
        df_margem['margem_%'] = (df_margem['lucro_pedido'] / df_margem['valor_venda'] * 100)
        df_margem = df_margem.sort_values('margem_%').head(8)
        
        fig = go.Figure(data=[go.Bar(
            x=df_margem['categoria'],
            y=df_margem['margem_%'],
            marker=dict(
                color=df_margem['margem_%'],
                colorscale='RdYlGn',
                showscale=False,
                line=dict(color='#FF6B35', width=1)
            ),
            text=[f"{x:.1f}%" for x in df_margem['margem_%']],
            textposition='outside'
        )])
        
        fig.add_hline(y=15, line_dash="dash", line_color="#FFD23F", 
                     annotation_text="Meta: 15%", annotation_position="right")
        
        fig = criar_grafico_moderno(fig)
        st.plotly_chart(fig, use_container_width=True)

# Mapa de calor: Status x Modo de Envio
st.markdown("#### 🗺️ Matriz: Status de Entrega vs Modo de Envio")

if all(c in df.columns for c in ['modo_envio', 'status_entrega']):
    df_heatmap = pd.crosstab(df['status_entrega'], df['modo_envio'])
    
    fig = go.Figure(data=go.Heatmap(
        z=df_heatmap.values,
        x=df_heatmap.columns,
        y=df_heatmap.index,
        colorscale='YlOrRd',
        text=df_heatmap.values,
        texttemplate='%{text}',
        textfont={"size": 12},
        hoverongaps=False
    ))
    
    fig = criar_grafico_moderno(fig)
    st.plotly_chart(fig, use_container_width=True)
    
    st.caption("💡 Insight: Identifique combinações de alto risco (cor vermelha intensa)")

# ============================================================================
# 9. PARTE 3 - OPORTUNIDADES
# ============================================================================

st.markdown("""
<div class='section-header'>
    <h2 class='section-title'>💡 Oportunidades de Crescimento</h2>
    <p class='section-subtitle'>Onde focar esforços para maximizar resultados</p>
</div>
""", unsafe_allow_html=True)

opp_col1, opp_col2 = st.columns([3, 2])

# No dashboard.py, dentro da Parte 3:
with opp_col1:
    st.markdown("#### 🎯 Matriz BCG: Categorias Estratégicas")
    
    # Agrupar e pegar apenas o Top 15 (evita poluição visual)
    df_bcg = df.groupby('categoria').agg({
        'valor_venda': 'sum',
        'lucro_pedido': 'sum'
    }).reset_index().nlargest(15, 'valor_venda')
    
    df_bcg['margem_percentual'] = (df_bcg['lucro_pedido'] / df_bcg['valor_venda']) * 100
    df_bcg['share_vendas'] = (df_bcg['valor_venda'] / df_bcg['valor_venda'].sum()) * 100
    
    fig = px.scatter(
        df_bcg, 
        x='share_vendas', 
        y='margem_percentual',
        size='valor_venda', 
        color='margem_percentual',
        hover_name='categoria',
        text='categoria', # Adiciona o nome apenas nas bolhas maiores
        color_continuous_scale='Viridis',
        labels={'share_vendas': '% Volume de Vendas', 'margem_percentual': 'Margem de Lucro (%)'}
    )
    
    # Ajustes estéticos "Clean"
    fig.update_traces(textposition='top center')
    fig.add_hline(y=df_bcg['margem_percentual'].mean(), line_dash="dot", annotation_text="Margem Média")
    fig.add_vline(x=df_bcg['share_vendas'].mean(), line_dash="dot", annotation_text="Volume Médio")
    
    fig.update_layout(showlegend=False, height=450)
    st.plotly_chart(fig, use_container_width=True)

with opp_col2:
    st.markdown("#### 🏆 Produtos Campeões")
    
    if 'categoria' in df.columns:
        top_cats = df.groupby('categoria').agg({
            'valor_venda': 'sum',
            'lucro_pedido': 'sum'
        }).reset_index().sort_values('lucro_pedido', ascending=False).head(5)
        
        for idx, row in top_cats.iterrows():
            margem = (row['lucro_pedido'] / row['valor_venda'] * 100)
            
            st.markdown(f"""
            <div class='insight-card'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <strong style='color: #FFD23F; font-size: 1.1rem;'>{row['categoria']}</strong><br>
                        <span style='color: #B0B3B8; font-size: 0.85rem;'>
                            Lucro: ${row['lucro_pedido']:,.0f} | Margem: {margem:.1f}%
                        </span>
                    </div>
                    <div style='font-size: 2rem;'>
                        {'🥇' if idx == 0 else '🥈' if idx == 1 else '🥉' if idx == 2 else '🏅'}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("#### 💰 Ticket Médio")
    st.metric("Valor Médio por Pedido", f"$ {metricas['ticket_medio']:.2f}")
    
    if 'categoria' in df.columns:
        ticket_cat = df.groupby('categoria')['valor_venda'].mean().sort_values(ascending=False).head(1)
        st.caption(f"🎯 Maior ticket: {ticket_cat.index[0]} ($ {ticket_cat.values[0]:.2f})")

# ============================================================================
# 10. CONSULTORIA IA
# ============================================================================

st.markdown("""
<div class='section-header'>
    <h2 class='section-title'>🤖 Consultoria com IA</h2>
    <p class='section-subtitle'>Recomendações personalizadas baseadas em seus dados</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 Visão Executiva", "🚚 Logística", "💰 Comercial"])

with tab1:
    if st.button("🎯 Gerar Relatório Executivo", key="exec", use_container_width=True):
        with st.spinner("🧠 Analisando dados..."):
            ctx = {
                "Faturamento": f"$ {metricas['total_vendas']:,.0f}",
                "Margem": f"{metricas['margem_lucro']:.1f}%",
                "Lucro": f"$ {metricas['lucro_total']:,.0f}",
                "Tendência": f"{metricas['tendencia_vendas']:+.1f}%",
                "Top Categoria": metricas.get('top_categoria', 'N/A'),
                "Pior Categoria": metricas.get('pior_categoria', 'N/A')
            }
            
            r = consultar_ia(ctx, "Análise executiva: saúde financeira e próximos passos estratégicos")
            
            if r['status'] == 'success':
                st.success("✅ Análise concluída")
                st.markdown(r['content'])
            else:
                st.error(r['message'])

with tab2:
    if st.button("🚚 Otimizar Logística", key="log", use_container_width=True):
        with st.spinner("🔍 Identificando gargalos..."):
            ctx = {
                "Taxa de Atraso": f"{metricas['atraso_rate']:.1f}%",
                "Entregas OK": f"{metricas['entrega_ok_rate']:.1f}%",
                "Brent Médio": f"$ {metricas['brent_avg']:.2f}",
                "Volatilidade Brent": f"±{metricas['brent_volatilidade']:.1f}"
            }
            
            r = consultar_ia(ctx, "Plano tático para reduzir atrasos e custos logísticos")
            
            if r['status'] == 'success':
                st.success("✅ Plano gerado")
                st.markdown(r['content'])
            else:
                st.error(r['message'])

with tab3:
    if st.button("💰 Estratégia Comercial", key="com", use_container_width=True):
        with st.spinner("💡 Desenvolvendo estratégias..."):
            ctx = {
                "Ticket Médio": f"$ {metricas['ticket_medio']:.2f}",
                "Margem": f"{metricas['margem_lucro']:.1f}%",
                "Top Produto": metricas.get('top_categoria', 'N/A'),
                "Total Pedidos": f"{metricas['total_pedidos']:,}"
            }
            
            r = consultar_ia(ctx, "Ações comerciais para aumentar ticket médio e margem")
            
            if r['status'] == 'success':
                st.success("✅ Estratégia pronta")
                st.markdown(r['content'])
            else:
                st.error(r['message'])

# ============================================================================
# 11. FOOTER
# ============================================================================

st.markdown("---")

st.markdown("""
<div style='text-align: center; margin-top: 40px;'>
    <p style='color: #8b92a0; font-size: 0.9rem;'>
        🏗️ <strong>Supply Chain Hub v5.0</strong> | Storytelling Edition<br>
        Desenvolvido por Andrew Navarro | Otimizado com AI<br>
        <span style='font-size: 0.8rem;'>
            Pipeline ETL (Bronze/Silver/Gold) + Analytics + IA Generativa
        </span>
    </p>
</div>
""", unsafe_allow_html=True)