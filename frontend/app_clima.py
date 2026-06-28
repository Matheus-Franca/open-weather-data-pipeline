import streamlit as st
import pandas as pd
import psycopg2
import os   
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, timedelta, timezone  

# 1. Configuração da Página
st.set_page_config(page_title="Dashboard Clima - Videira", page_icon="🌤️", layout="wide")
st_autorefresh(interval=3600000, key="atualizacao_clima")
st.title("🌤️ Previsão do Tempo Oficial - Videira/SC")
st.markdown("Dados atualizados automaticamente pelo pipeline de Engenharia de Dados.")

# 2. Conexão Segura com o Data Warehouse (PostgreSQL)
@st.cache_data(ttl=1800) # Guarda o resultado por 30 minutos
def buscar_dados(): 
    # Puxa as variáveis de ambiente ocultas
    usuario = os.getenv("dw_user") 
    senha = os.getenv("dw_password")

    conexao = psycopg2.connect(
        host="postgres-dw", 
        database="weather_db",
        user=usuario,
        password=senha,
        port="5432"
    )   
    
    # 3. Consulta SQL cruzando a Tabela Fato com as Dimensões e Regras de Negócio
    query = """
        SELECT          
            dt.data_registro,
            dt.hora_registro,
            dc.descricao_detalhada as condicao,
            fp.temperatura_prevista,
            fp.prob_chuva,
            fp.velocidade_vento_kmh as velocidade_vento
        FROM fato_previsao fp
        JOIN dim_tempo dt ON fp.id_tempo_previsto = dt.id_tempo
        JOIN dim_condicao dc ON fp.id_condicao = dc.id_condicao
        ORDER BY dt.id_tempo ASC;
    """
    df = pd.read_sql(query, conexao)
    conexao.close()
    return df

# 4. Buscando os dados
df_previsao = buscar_dados()

# Transformando a probabilidade de chuva decimal (0.0) em porcentagem visual (0%)
df_previsao['Probabilidade de Chuva'] = (df_previsao['prob_chuva'] * 100).astype(int).astype(str) + '%'
df_previsao = df_previsao.drop(columns=['prob_chuva']) # Remove a coluna decimal bruta

# ==========================================
# 1º FILTRO: ESCONDER O PASSADO
# ==========================================
# Junta as duas colunas em uma só para o Pandas entender como Data/Hora real
df_previsao['Data_Hora'] = df_previsao['data_registro'].astype(str) + " " + df_previsao['hora_registro'].astype(str)
df_previsao['Data_Hora_Obj'] = pd.to_datetime(df_previsao['Data_Hora'])

# Pega o horário atual do Brasil, ajusta as 3 horas e REMOVE o fuso (tzinfo=None)
agora_br = datetime.now(timezone.utc) - timedelta(hours=3)
agora_br_naive = agora_br.replace(tzinfo=None)

# Cria a margem de segurança usando a data compatível com o Pandas
margem = agora_br_naive - timedelta(hours=3)

# Descarta o passado, mantendo só o presente e o futuro
df_previsao = df_previsao[df_previsao['Data_Hora_Obj'] >= margem]

# ==========================================
# 2º FILTRO: DE 6 EM 6 HORAS & DUPLICATAS
# ==========================================
df_previsao['hora_str'] = df_previsao['hora_registro'].astype(str)
df_previsao = df_previsao[df_previsao['hora_str'].str.startswith(('00', '06', '12', '18'))]
df_previsao = df_previsao.drop_duplicates(subset=['data_registro', 'hora_registro'], keep='last').reset_index(drop=True)

# Remove as colunas temporárias para manter a tabela final limpa
df_previsao = df_previsao.drop(columns=['hora_str', 'Data_Hora_Obj'])


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
        vento = df_previsao.iloc[i]['velocidade_vento']
        
        st.metric(label=f"Hoje às {hora}", value=f"{temp} °C", delta=condicao, delta_color="off")
        st.caption(f"🌬️ Vento: {vento} km/h")

st.divider()

# 6. Gráfico de Linha Interativo da Temperatura
st.subheader("Variação de Temperatura nos próximos 5 dias")

# Desenha o gráfico nativo do Streamlit apenas com a Temperatura Prevista
st.line_chart(
    data=df_previsao,
    x='Data_Hora',
    y=['temperatura_prevista'],
    color=["#0068C9"]
)

# 7. Tabela Completa (Raw Data) para quem quiser explorar
with st.expander("Ver alguns dados no Data Warehouse"):
    # Exibe o dataframe removendo a coluna 'Data_Hora' apenas visualmente
    st.dataframe(df_previsao.drop(columns=['Data_Hora']), use_container_width=True) 