import streamlit as st
import pandas as pd
import psycopg2
import os   

# 1. Configuração da Página
st.set_page_config(page_title="Dashboard Clima - Videira", page_icon="🌤️", layout="wide")
st.title("🌤️ Previsão do Tempo Oficial - Videira/SC")
st.markdown("Dados atualizados automaticamente pelo pipeline de Engenharia de Dados.")

# 2. Conexão Segura com o Data Warehouse (PostgreSQL)
# DICA: Em um ambiente real, essas senhas ficariam em um arquivo .env oculto
@st.cache_data # Isso faz o Streamlit guardar o resultado para não sobrecarregar o banco
def buscar_dados():
    # Puxa as variáveis de ambiente que o Docker injetou no contêiner
    # O nome entre aspas deve ser exatamente igual ao que está no seu arquivo .env
    usuario = os.getenv("dw_user") 
    senha = os.getenv("dw_password")

    conexao = psycopg2.connect(
        host="postgres-dw", 
        database="weather_db",
        user=usuario,
        password=senha,
        port="5432"
    )   
    
    # 3. A Consulta SQL cruzando a Tabela Fato com as Dimensões
    query = """
        SELECT 
            dt.data_registro,
            dt.hora_registro,
            dc.descricao_detalhada as condicao,
            fp.temperatura_prevista,
            fp.temp_minima,
            fp.temp_maxima,
            fp.prob_chuva,
            fp.velocidade_vento_kmh
        FROM fato_previsao fp
        JOIN dim_tempo dt ON fp.id_tempo_previsto = dt.id_tempo
        JOIN dim_condicao dc ON fp.id_condicao = dc.id_condicao
        ORDER BY dt.id_tempo ASC;
    """
    df = pd.read_sql(query, conexao)
    conexao.close()
    return df

# 4. Buscando os dados do Data Warehouse (vem de 3 em 3 horas)
df_previsao = buscar_dados()

# --- FILTRO DE 6 EM 6 HORAS NO FRONTEND ---
# Converte a coluna de hora para texto e filtra as horas específicas
df_previsao['hora_str'] = df_previsao['hora_registro'].astype(str)
df_previsao = df_previsao[df_previsao['hora_str'].str.startswith(('00', '06', '12', '18'))].reset_index(drop=True)

# --- NOVO: REMOVE AS DUPLICATAS (Mantém só a previsão mais atualizada) ---
df_previsao = df_previsao.drop_duplicates(subset=['data_registro', 'hora_registro'], keep='last').reset_index(drop=True)

# Remove a coluna de texto temporária
df_previsao = df_previsao.drop(columns=['hora_str'])

# 5. Criando a Interface Web
st.divider()

# Criando 3 colunas para destacar os dados das próximas 3 horas
st.subheader("Previsão para as próximas horas")
colunas = st.columns(3)

for i in range(3):
    with colunas[i]:
        hora = df_previsao.iloc[i]['hora_registro']
        temp = df_previsao.iloc[i]['temperatura_prevista']
        condicao = df_previsao.iloc[i]['condicao'].capitalize()
        vento = df_previsao.iloc[i]['velocidade_vento_kmh']
        
        st.metric(label=f"Hoje às {hora}", value=f"{temp} °C", delta=condicao, delta_color="off")
        st.caption(f"🌬️ Vento: {vento} km/h")

st.divider()

# 6. Gráfico de Linha Interativo da Temperatura
st.subheader("Variação de Temperatura nos próximos 5 dias")
# Prepara a data e hora para o eixo X do gráfico
df_previsao['Data_Hora'] = df_previsao['data_registro'].astype(str) + " " + df_previsao['hora_registro'].astype(str)

# Desenha o gráfico nativo do Streamlit
st.line_chart(
    data=df_previsao,
    x='Data_Hora',
    y=['temperatura_prevista', 'temp_minima'],
    color=["#0068C9", "#29B5E8"]
)

# 7. Tabela Completa (Raw Data) para quem quiser explorar
with st.expander("Ver base de dados completa do Data Warehouse"):
    st.dataframe(df_previsao, use_container_width=True) 