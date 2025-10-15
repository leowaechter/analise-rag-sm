import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go # Importação necessária para a linha de tendência
import locale

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Dashboard de Repasses da Enfermagem",
    page_icon="💉",
    layout="wide"
)

# --- FUNÇÕES AUXILIARES ---

# Função para formatar números como moeda brasileira
def formatar_moeda(valor):
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        return locale.currency(valor, grouping=True)
    except (ValueError, TypeError):
        return "R$ 0,00"

# Função para carregar e preparar os dados (com cache para performance)
@st.cache_data
def carregar_dados(caminho_arquivo):
    df = pd.read_csv(caminho_arquivo)
    colunas_valores = ['SMS', 'UPA', 'SAMU', 'GESTÃO DUPLA', 'TOTAL']
    
    for col in colunas_valores:
        df[col] = df[col].astype(str).str.replace('R$', '', regex=False)
        df[col] = df[col].str.replace('.', '', regex=False)
        df[col] = df[col].str.replace(',', '.', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df = df[['MESES DE REFERÊNCIA'] + colunas_valores]
    return df

# --- CARREGAMENTO DOS DADOS ---
try:
    df = carregar_dados('dados_pgto_enf.csv')
except FileNotFoundError:
    st.error("Arquivo 'dados_pgto_enf.csv' não encontrado. Por favor, certifique-se de que ele está na mesma pasta que o script `app.py`.")
    st.stop()

# --- BARRA LATERAL (SIDEBAR) COM FILTROS ---
st.sidebar.image("https://logodownload.org/wp-content/uploads/2014/02/sus-logo-2.png", width=150)
st.sidebar.title("Filtros Interativos")
st.sidebar.markdown("Use os filtros abaixo para explorar os dados.")

meses_selecionados = st.sidebar.multiselect(
    'Selecione o(s) Mês(es):',
    options=df['MESES DE REFERÊNCIA'].unique(),
    default=df['MESES DE REFERÊNCIA'].unique()
)

df_filtrado = df[df['MESES DE REFERÊNCIA'].isin(meses_selecionados)]

# --- TÍTULO PRINCIPAL ---
st.title("💉 Dashboard de Repasses para o Piso da Enfermagem - Santa Maria/RS")
st.markdown(f"Análise interativa dos valores recebidos. Dados de **{df['MESES DE REFERÊNCIA'].iloc[0]}** a **{df['MESES DE REFERÊNCIA'].iloc[-1]}**.")

# --- VERIFICAÇÃO SE O DATAFRAME FILTRADO NÃO ESTÁ VAZIO ---
if df_filtrado.empty:
    st.warning("Nenhum dado selecionado. Por favor, escolha pelo menos um mês no filtro da barra lateral.")
else:
    # --- CÁLCULO E EXIBIÇÃO DOS TOTAIS ---
    st.markdown("---")
    st.subheader("Resumo dos Totais (Período Selecionado)")

    total_sms_gestao = df_filtrado['SMS'].sum() + df_filtrado['GESTÃO DUPLA'].sum()
    total_upa_samu = df_filtrado['UPA'].sum() + df_filtrado['SAMU'].sum()
    total_geral = df_filtrado['TOTAL'].sum()
    total_estadual = df_filtrado['GESTÃO DUPLA'].sum()
    total_federal = total_geral - total_estadual

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Geral Recebido", value=formatar_moeda(total_geral))
    with col2:
        st.metric(label="SMS + Gestão Dupla", value=formatar_moeda(total_sms_gestao))
        st.metric(label="UPA + SAMU", value=formatar_moeda(total_upa_samu))
    with col3:
        st.metric(label="Repasse Federal (Estimado)", value=formatar_moeda(total_federal))
        st.metric(label="Repasse Estadual", value=formatar_moeda(total_estadual))

    # --- ABAS COM OS DASHBOARDS ---
    tab_geral, tab_categorias, tab_estrategica, tab_dados = st.tabs(["Visão Geral 📊", "Análise por Categoria 📈", "Análise Estratégica 🎯", "Dados Completos 📋"])

    with tab_geral:
        st.header("Evolução dos Repasses Totais")
        fig_linha = px.line(df_filtrado, x='MESES DE REFERÊNCIA', y='TOTAL', markers=True, text=df_filtrado['TOTAL'].apply(lambda x: f'R${x/1000:.1f}k'), title='Valor Total Recebido por Mês')
        fig_linha.update_traces(textposition="top center")
        st.plotly_chart(fig_linha, use_container_width=True)

    with tab_categorias:
        st.header("Distribuição dos Valores por Categoria")
        col_bar, col_pie = st.columns(2)
        with col_bar:
            df_melted = df_filtrado.melt(id_vars='MESES DE REFERÊNCIA', value_vars=['SMS', 'UPA', 'SAMU', 'GESTÃO DUPLA'], var_name='Categoria', value_name='Valor')
            fig_barras = px.bar(df_melted, x='MESES DE REFERÊNCIA', y='Valor', color='Categoria', title='Composição dos Repasses por Mês')
            st.plotly_chart(fig_barras, use_container_width=True)
        with col_pie:
            df_soma_categorias = df_filtrado[['SMS', 'UPA', 'SAMU', 'GESTÃO DUPLA']].sum().reset_index()
            df_soma_categorias.columns = ['Categoria', 'Valor']
            fig_pizza = px.pie(df_soma_categorias, names='Categoria', values='Valor', title='Distribuição Percentual por Categoria (Total)')
            st.plotly_chart(fig_pizza, use_container_width=True)

    ### --- NOVA ABA: ANÁLISE ESTRATÉGICA --- ###
    with tab_estrategica:
        st.header("Análises para Tomada de Decisão")

        # 1. Dashboard de Performance Mensal (vs. a Média)
        st.subheader("Performance Mensal em Relação à Média")
        st.markdown("Cada card abaixo mostra o total do mês e a diferença percentual em relação à média de todos os meses selecionados.")
        media_mensal = df_filtrado['TOTAL'].mean()
        cols = st.columns(4)
        for i, row in df_filtrado.iterrows():
            col_index = i % 4
            with cols[col_index]:
                delta_percentual = ((row['TOTAL'] - media_mensal) / media_mensal) * 100
                st.metric(label=row['MESES DE REFERÊNCIA'], value=formatar_moeda(row['TOTAL']), delta=f"{delta_percentual:.2f}% vs. Média", help=f"A média do período foi {formatar_moeda(media_mensal)}")
        
        st.markdown("---")
        
        # 2. Análise Proporcional (%)
        st.subheader("Análise da Composição Percentual dos Repasses")
        st.markdown("Este gráfico mostra a participação de cada categoria no total de cada mês.")
        df_percentual = df_filtrado.copy()
        categorias = ['SMS', 'UPA', 'SAMU', 'GESTÃO DUPLA']
        df_percentual[categorias] = df_percentual[categorias].div(df_percentual['TOTAL'], axis=0) * 100
        df_percentual_melted = df_percentual.melt(id_vars='MESES DE REFERÊNCIA', value_vars=categorias, var_name='Categoria', value_name='Percentual')
        fig_barras_100 = px.bar(df_percentual_melted, x='MESES DE REFERÊNCIA', y='Percentual', color='Categoria', title='Composição Percentual dos Repasses por Mês', text=df_percentual_melted['Percentual'].apply(lambda x: f'{x:.1f}%'))
        st.plotly_chart(fig_barras_100, use_container_width=True)

        st.markdown("---")

        # 3. Análise de Destaque e Tendência
        st.subheader("Destaques e Tendência Geral")
        mes_maior_valor = df_filtrado.loc[df_filtrado['TOTAL'].idxmax()]
        mes_menor_valor = df_filtrado.loc[df_filtrado['TOTAL'].idxmin()]
        col_destaque1, col_destaque2 = st.columns(2)
        with col_destaque1:
            st.success(f"📈 **Mês de Maior Repasse:** {mes_maior_valor['MESES DE REFERÊNCIA']} ({formatar_moeda(mes_maior_valor['TOTAL'])})")
        with col_destaque2:
            st.error(f"📉 **Mês de Menor Repasse:** {mes_menor_valor['MESES DE REFERÊNCIA']} ({formatar_moeda(mes_menor_valor['TOTAL'])})")
        
        fig_tendencia = px.bar(df_filtrado, x='MESES DE REFERÊNCIA', y='TOTAL', title='Valores Totais com Linha de Tendência (Média Móvel)')
        fig_tendencia.add_trace(go.Scatter(x=df_filtrado['MESES DE REFERÊNCIA'], y=df_filtrado['TOTAL'].rolling(window=3, center=True, min_periods=1).mean(), mode='lines', name='Média Móvel (3 meses)', line=dict(color='orange', width=4)))
        st.plotly_chart(fig_tendencia, use_container_width=True)

    with tab_dados:
        st.header("Tabela de Dados Detalhada")
        st.dataframe(df_filtrado.style.format(formatar_moeda, subset=['SMS', 'UPA', 'SAMU', 'GESTÃO DUPLA', 'TOTAL']), use_container_width=True)