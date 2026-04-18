import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh  # Nova importação
import os

# Configuração da página
st.set_page_config(page_title="Dashboard Térmico", layout="wide")

# FAZ A PÁGINA REFRESCAR SOZINHA A CADA 2 SEGUNDOS (2000 milissegundos)
st_autorefresh(interval=2000, key="datarefresh")


# --- FUNÇÃO DO GAUGE ---
def exibir_gauge(temperatura_atual):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=temperatura_atual,
        title={'text': "Temperatura Atual (°C)"},
        gauge={
            'axis': {'range': [0, 50]},
            'steps': [
                {'range': [0, 20], 'color': "#00e5ff"},
                {'range': [20, 30], 'color': "#00c853"},
                {'range': [30, 50], 'color': "#ff1744"}
            ],
            'threshold': {'line': {'color': "black", 'width': 4}, 'value': 40}
        }
    ))
    fig.update_layout(height=300, margin=dict(l=30, r=30, t=50, b=0))
    return fig


st.title("🌡️ Monitoramento NTC 10K")

# Verificação do arquivo
if os.path.exists("historico_temperatura.csv"):
    df = pd.read_csv("historico_temperatura.csv")

    if not df.empty:
        ultima_temp = df['Temperatura_C'].iloc[-1]
        temp_max = df['Temperatura_C'].max()
        temp_min = df['Temperatura_C'].min()

        # Layout em Colunas
        col1, col2 = st.columns([1, 2])

        with col1:
            # Sem o loop while, não haverá erro de chaves duplicadas
            st.plotly_chart(exibir_gauge(ultima_temp), use_container_width=True)

        with col2:
            st.write("### Estatísticas da Sessão")
            m1, m2 = st.columns(2)
            m1.metric("Máxima", f"{temp_max} °C")
            m2.metric("Mínima", f"{temp_min} °C")
            st.info(f"Última leitura às: {df['Hora'].iloc[-1]}")

        st.subheader("Histórico de Variação")
        st.line_chart(df.set_index('Hora')['Temperatura_C'])


        # --- BOTÃO PARA MOSTRAR A TABELA ---
        st.divider()  # Adiciona uma linha sutil de separação

        # Usando um checkbox como botão de alternância (Toggle)
        if st.checkbox('📋 Mostrar tabela de registros (últimos 50)'):
            st.subheader("Dados brutos do CSV")

            # Mostra os últimos 50 registros invertidos (o mais recente no topo)
            df_reverso = df.iloc[::-1].head(50)

            st.dataframe(
                df_reverso,
                use_container_width=True,
                column_config={
                    "Data": st.column_config.TextColumn("Data"),
                    "Hora": st.column_config.TextColumn("Horário"),
                    "Temperatura_C": st.column_config.NumberColumn("Temp (°C)", format="%.2f")
                }
            )

            # Botão opcional para baixar o arquivo direto do navegador
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar histórico completo (CSV)",
                data=csv_data,
                file_name='historico_temperatura_exportado.csv',
                mime='text/csv',
            )
else:
    st.error("Aguardando o arquivo CSV ser gerado pelo main.py...")