import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np 
import folium
from streamlit_folium import st_folium
import json

# --- 1. Configurações Visuais (Cores e Fontes) ---
CORES_SITUACAO = {
    'Confirmados': '#d62728',     
    'Em Investigação': '#ff7f0e', 
    'Descartados': '#1f77b4'     
}

CORES_COMPOSICAO = {
    'Dengue Clássico': '#FDBAAB',
    'Sinais de Alarme': '#F3674C',
    'Grave': '#D7263D',
    'Em Investigação': '#ff7f0e',
    'Descartado': '#1f77b4'
}

FONTE_TITULO = 24
FONTE_SUBTITULO = 18
FONTE_GERAL = 16
FONTE_LEGENDA = 16

# --- 2. Configuração da Página ---
st.set_page_config(layout="wide", page_title="Dashboard de Dengue - Santa Maria/RS")

# --- 3. Carregamento Automático dos Dados ---
NOME_ARQUIVO = 'dados_dengue.csv'
try:
    df = pd.read_csv(NOME_ARQUIVO)
    # Filtro inicial e definitivo para remover qualquer linha de totalização na carga
    df = df[~df['BAIRRO'].str.contains('Total', case=False, na=False)].copy()
except FileNotFoundError:
    st.error(f"Erro: O arquivo '{NOME_ARQUIVO}' não foi encontrado.")
    st.warning(f"Por favor, certifique-se de que o arquivo '{NOME_ARQUIVO}' está na mesma pasta que o script Python.")
    st.stop()
except Exception as e:
    st.error(f"Ocorreu um erro ao ler o arquivo: {e}")
    st.stop()

# --- Cálculos Preliminares ---
df['Confirmados'] = df['DENGUE CLÁSSICO'] + df['DENGUE COM SINAIS DE ALARME'] + df['DENGUE GRAVE']
df['Casos de Risco'] = df['DENGUE COM SINAIS DE ALARME'] + df['DENGUE GRAVE']

# --- 4. Título Principal ---
st.title("Dashboard de Monitoramento da Dengue - Santa Maria/RS")
st.markdown(f"Análise dos casos notificados de Dengue por bairro de residência (Jan-Dez/2024).")
st.markdown("---")

# --- 5. Visão Geral do Município ---
st.header("📍 Visão Geral do Município")
col1, col2 = st.columns([1, 2])
with col1:
    st.markdown(f"<h3 style='font-size: {FONTE_SUBTITULO}px;'>Situação Atual das Notificações</h3>", unsafe_allow_html=True)
    total_confirmados = df['Confirmados'].sum()
    total_investigacao = df['EM INVESTIGAÇÃO'].sum()
    total_descartados = df['DESCARTADO'].sum()
    df_pizza = pd.DataFrame({'Categoria': ['Confirmados', 'Em Investigação', 'Descartados'],'Total': [total_confirmados, total_investigacao, total_descartados]})
    fig_pie = px.pie(df_pizza, names='Categoria', values='Total', hole=0.5, title='Proporção das Notificações', color='Categoria', color_discrete_map=CORES_SITUACAO)
    fig_pie.update_traces(textinfo='percent+label', textfont_size=FONTE_GERAL + 2)
    fig_pie.update_layout(title_font_size=FONTE_TITULO, showlegend=True, legend=dict(font=dict(size=FONTE_LEGENDA)))
    st.plotly_chart(fig_pie, use_container_width=True)
with col2:
    st.markdown(f"<h3 style='font-size: {FONTE_SUBTITULO}px;'>Bairros Mais Afetados</h3>", unsafe_allow_html=True)
    df_top10 = df.nlargest(10, 'Confirmados').sort_values('Confirmados', ascending=True)
    fig_bar = px.bar(df_top10, x='Confirmados', y='BAIRRO', orientation='h', title='Top 10 Bairros por Casos Confirmados', text='Confirmados')
    fig_bar.update_traces(marker_color=CORES_SITUACAO['Confirmados'], textfont_size=FONTE_GERAL, textposition='outside')
    fig_bar.update_layout(yaxis_title=None, xaxis_title="Nº de Casos Confirmados", title_font_size=FONTE_TITULO, yaxis_tickfont_size=FONTE_GERAL, xaxis_tickfont_size=FONTE_GERAL)
    st.plotly_chart(fig_bar, use_container_width=True)
st.markdown("---")


### --- NOVA SEÇÃO: ANÁLISE ESTRATÉGICA --- ###
st.header("🎯 Análise Estratégica para Gestão")

# --- Dashboard 1: Matriz de Risco ---
st.subheader("Matriz de Risco: Volume vs. Gravidade")
st.markdown("Este quadrante ajuda a priorizar ações, cruzando o número total de casos com a proporção de casos que apresentam risco (Sinais de Alarme + Grave).")

df_bairros = df.copy() # Usamos o df já filtrado no início
df_bairros['Taxa de Risco (%)'] = (df_bairros['Casos de Risco'] / df_bairros['Confirmados'].replace(0, 1)) * 100
media_confirmados = df_bairros['Confirmados'].mean()
media_taxa_risco = df_bairros['Taxa de Risco (%)'].mean()

# Cria a coluna 'Label' para a rotulagem inteligente
df_bairros['Label'] = np.where(
    (df_bairros['Confirmados'] > media_confirmados) | (df_bairros['Taxa de Risco (%)'] > media_taxa_risco),
    df_bairros['BAIRRO'],
    ""
)

# Gráfico com escala LINEAR e rotulagem INTELIGENTE
fig_scatter = px.scatter(
    df_bairros,
    x='Confirmados',
    y='Taxa de Risco (%)',
    text='Label',
    size='Casos de Risco',
    color='Casos de Risco',
    color_continuous_scale=px.colors.sequential.Reds,
    hover_name='BAIRRO',
    hover_data={'Confirmados': True, 'Taxa de Risco (%)': ':.2f', 'Casos de Risco': True, 'Label': False},
    title="Quadrante de Risco dos Bairros"
)
fig_scatter.update_traces(textposition='top center', textfont_size=12, marker=dict(sizemin=5, opacity=0.7))
fig_scatter.add_vline(x=media_confirmados, line_dash="dash", line_color="gray", annotation_text=f"Média Casos ({media_confirmados:.0f})")
fig_scatter.add_hline(y=media_taxa_risco, line_dash="dash", line_color="gray", annotation_text=f"Média Risco ({media_taxa_risco:.1f}%)")
fig_scatter.add_annotation(x=media_confirmados, y=media_taxa_risco, text="<b>ALTA PRIORIDADE</b>", showarrow=True, arrowhead=1, ax=100, ay=-50, font=dict(color="#d62728"))
fig_scatter.add_annotation(x=media_confirmados, y=media_taxa_risco, text="<b>MONITORAR VOLUME</b>", showarrow=True, arrowhead=1, ax=100, ay=50, font=dict(color="#ff7f0e"))
fig_scatter.add_annotation(x=media_confirmados, y=media_taxa_risco, text="<b>ALERTA DE GRAVIDADE</b>", showarrow=True, arrowhead=1, ax=-100, ay=-50, font=dict(color="#ff7f0e"))
fig_scatter.add_annotation(x=media_confirmados, y=media_taxa_risco, text="<b>Baixo Risco</b>", showarrow=True, arrowhead=1, ax=-100, ay=50, font=dict(color="#1f77b4"))
fig_scatter.update_layout(height=700, title_font_size=FONTE_TITULO)
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# --- 6. Análise Detalhada por Bairro ---
st.header("🔬 Análise por Bairro")
bairros_ordenados = sorted(df['BAIRRO'].unique())
bairro_selecionado = st.selectbox("Selecione um bairro para ver os detalhes:", bairros_ordenados)
df_bairro = df[df['BAIRRO'] == bairro_selecionado]

if not df_bairro.empty:
    st.markdown(f"<h3 style='font-size: {FONTE_SUBTITULO}px;'>Números de: {bairro_selecionado}</h3>", unsafe_allow_html=True)
    confirmados = int(df_bairro['Confirmados'].iloc[0])
    classico = int(df_bairro['DENGUE CLÁSSICO'].iloc[0])
    alarme = int(df_bairro['DENGUE COM SINAIS DE ALARME'].iloc[0])
    grave = int(df_bairro['DENGUE GRAVE'].iloc[0])
    investigacao = int(df_bairro['EM INVESTIGAÇÃO'].iloc[0])
    descartado = int(df_bairro['DESCARTADO'].iloc[0])

    metric_cols = st.columns(5)
    metric_cols[0].metric("Total Confirmado", f"{confirmados}")
    metric_cols[1].metric("Clássico", f"{classico}")
    metric_cols[2].metric("Sinais de Alarme", f"{alarme}", delta=alarme if alarme > 0 else None, delta_color="inverse")
    metric_cols[3].metric("Grave", f"{grave}", delta=grave if grave > 0 else None, delta_color="inverse")
    metric_cols[4].metric("Em Investigação", f"{investigacao}")

    st.markdown("---")

    ### --- CÓDIGO DO GRÁFICO DE PIZZA --- ###
    categorias_bairro = ['Dengue Clássico', 'Sinais de Alarme', 'Grave', 'Em Investigação', 'Descartado']
    valores_bairro = [classico, alarme, grave, investigacao, descartado]
    
    df_pizza_bairro = pd.DataFrame({'Categoria': categorias_bairro, 'Quantidade': valores_bairro})
    df_pizza_bairro = df_pizza_bairro[df_pizza_bairro['Quantidade'] > 0]

    if not df_pizza_bairro.empty:
        fig_pie_bairro = px.pie(
            df_pizza_bairro,
            names='Categoria',
            values='Quantidade',
            title=f"Composição das Notificações em {bairro_selecionado}",
            hole=0.5,
            color='Categoria',
            color_discrete_map=CORES_COMPOSICAO
        )
        fig_pie_bairro.update_traces(textinfo='percent+value', textfont_size=FONTE_GERAL + 2, sort=False)
        fig_pie_bairro.update_layout(title_font_size=FONTE_TITULO, showlegend=True, legend=dict(font=dict(size=FONTE_LEGENDA)))
        st.plotly_chart(fig_pie_bairro, use_container_width=True)
    else:
        st.info("Não há notificações registradas para este bairro.")

st.markdown("---")

# --- 7. Tabela de Dados Completa ---
with st.expander("Clique para ver a tabela de dados completa"):
    st.dataframe(df.drop(columns=['Confirmados', 'Casos de Risco'], errors='ignore'), use_container_width=True)