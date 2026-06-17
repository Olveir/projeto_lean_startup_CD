import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Relatório de Burnout", layout="wide")

st.title("Painel Preditivo: Risco de Burnout")
st.markdown("Modelo de detecção antecipada de esgotamento profissional.")

# Carregar dados
@st.cache_data
def carregar_dados():
    df_pred = pd.read_csv('predicao.csv')
    df_test = pd.read_csv('test_limpo.csv')
    return pd.merge(df_pred, df_test, on='Employee ID', how='left')

try:
    df = carregar_dados()
    
    # 1. Linha de KPIs
    col1, col2, col3 = st.columns(3)
    total_alto = len(df[df['Risco'] == 'Alto'])
    total_medio = len(df[df['Risco'] == 'Medio'])
    total_baixo = len(df[df['Risco'] == 'Baixo'])

    col1.metric("🔴 Risco Crítico", f"{total_alto}", "Ação Imediata Necessária", delta_color="inverse")
    col2.metric("🟡 Atenção", f"{total_medio}", "Monitoramento Constante", delta_color="off")
    col3.metric("🟢 Seguro", f"{total_baixo}", "Saudável", delta_color="normal")

    st.divider()

    # 2. Gráficos Interativos (Plotly)
    col_grafico1, col_grafico2 = st.columns(2)

    with col_grafico1:
        with st.container(border=True):
            st.subheader("Distribuição de Risco")
            fig1 = px.pie(df, names='Risco', title="Colaboradores por Nível", 
                          color='Risco', color_discrete_map={'Alto':'#dc2626', 'Medio':'#d97706', 'Baixo':'#059669'},
                          hole=0.4)
            st.plotly_chart(fig1, use_container_width=True)

    with col_grafico2:
        with st.container(border=True):
            st.subheader("Importância das Variáveis")
            features = pd.DataFrame({
                'Variável': ['Fadiga Mental (Mental Fatigue Score)', 'Alocação Recursos (Resource Allocation)', 'Senioridade (Designation)', 'Home Office (WFH Setup Available)'],
                'Impacto (%)': [38, 35, 15, 12]
            })
            fig2 = px.bar(features, x='Impacto (%)', y='Variável', orientation='h')
            fig2.update_traces(marker_color='#2563eb')
            st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # 3. Filtros e Tabela Interativa
    with st.container(border=True):
        st.subheader("Lista Prioritária de Colaboradores")
        filtro_risco = st.selectbox("Filtrar por Risco:", ["Todos", "Alto", "Medio", "Baixo"])

        if filtro_risco != "Todos":
            df_filtrado = df[df['Risco'] == filtro_risco]
        else:
            df_filtrado = df

        df_mostrar = df_filtrado[['Employee ID', 'Burn Rate previsto', 'Risco', 'Mental Fatigue Score']].sort_values(by='Burn Rate previsto', ascending=False)
        df_mostrar['Score (0-100)'] = df_mostrar['Burn Rate previsto'] * 100

        st.dataframe(df_mostrar[['Employee ID', 'Score (0-100)', 'Risco', 'Mental Fatigue Score']].head(100), use_container_width=True)

except Exception as e:
    st.error(f"Erro ao carregar dados. Verifique se predicao.csv e test_limpo.csv estão na mesma pasta. Detalhe: {e}")
