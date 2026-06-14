import pandas as pd
from airflow.providers.postgres.hooks.postgres import PostgresHook

def _inserir_dimensoes(hook, arquivos_dimensoes):
    """
    Lê os arquivos de dimensão, converte tipos do Pandas para tipos nativos
    do Python e insere no banco fazendo UPSERT.
    """
    for config in arquivos_dimensoes:
        df = pd.read_csv(config['arquivo'])
        if df.empty:
            continue
            
        # Tratamento rigoroso de tipagem: troca NaN por None e remove o formato NumPy
        df = df.where(pd.notna(df), None)
        registros = [tuple(x) for x in df.values.tolist()]
        
        hook.insert_rows(
            table=config['tabela'],
            rows=registros,
            target_fields=config['colunas'],
            replace=True,                  
            replace_index=config['pk'],    
            commit_every=100
        )

def carregar_clima_atual(**kwargs):
    """Lê os CSVs temporários e insere nas tabelas de dimensão e na fato_clima_atual."""
    print("Iniciando a carga do Clima Atual no PostgreSQL...")
    hook = PostgresHook(postgres_conn_id='postgres_dw')
    
    dimensoes = [
        {
            'arquivo': '/tmp/dim_tempo_atual.csv', 
            'tabela': 'dim_tempo', 
            'colunas': ['id_tempo', 'data_registro', 'hora_registro', 'dia_semana', 'mes', 'ano'], 
            'pk': 'id_tempo'
        },
        {
            'arquivo': '/tmp/dim_localidade.csv', 
            'tabela': 'dim_localidade', 
            'colunas': ['id_localidade', 'nome_cidade', 'pais', 'latitude', 'longitude'], 
            'pk': 'id_localidade'
        },
        {
            'arquivo': '/tmp/dim_condicao_atual.csv', 
            'tabela': 'dim_condicao', 
            'colunas': ['id_condicao', 'id_api_weather', 'grupo_clima', 'descricao_detalhada'], 
            'pk': 'id_condicao'
        }
    ]
    
    _inserir_dimensoes(hook, dimensoes)
    
    df_fato = pd.read_csv('/tmp/fato_clima_atual.csv')
    # Tratamento da tabela Fato
    df_fato = df_fato.where(pd.notna(df_fato), None)
    registros_fato = [tuple(x) for x in df_fato.values.tolist()]
    
    hook.insert_rows(
        table='fato_clima_atual',
        rows=registros_fato,
        target_fields=['id_tempo', 'id_localidade', 'id_condicao', 'temperatura_real', 'sensacao_termica', 'umidade_real', 'velocidade_vento'],
        commit_every=100
    )
    print("✅ Dados do clima atual carregados com sucesso no Star Schema!")

def carregar_previsao(**kwargs):
    """Lê os CSVs temporários e insere nas tabelas de dimensão e na fato_previsao."""
    print("Iniciando a carga da Previsão no PostgreSQL...")
    hook = PostgresHook(postgres_conn_id='postgres_dw')
    
    dimensoes = [
        {
            'arquivo': '/tmp/dim_tempo_previsao.csv', 
            'tabela': 'dim_tempo', 
            'colunas': ['id_tempo', 'data_registro', 'hora_registro', 'dia_semana', 'mes', 'ano'], 
            'pk': 'id_tempo'
        },
        {
            'arquivo': '/tmp/dim_localidade_previsao.csv', 
            'tabela': 'dim_localidade', 
            'colunas': ['id_localidade', 'nome_cidade', 'pais', 'latitude', 'longitude'], 
            'pk': 'id_localidade'
        },
        {
            'arquivo': '/tmp/dim_condicao_previsao.csv', 
            'tabela': 'dim_condicao', 
            'colunas': ['id_condicao', 'id_api_weather', 'grupo_clima', 'descricao_detalhada'], 
            'pk': 'id_condicao'
        }
    ]
    
    _inserir_dimensoes(hook, dimensoes)
    
    df_fato = pd.read_csv('/tmp/fato_previsao.csv')
    # Tratamento da tabela Fato
    df_fato = df_fato.where(pd.notna(df_fato), None)
    registros_fato = [tuple(x) for x in df_fato.values.tolist()]
    
    hook.insert_rows(
        table='fato_previsao',
        rows=registros_fato,
        target_fields=[
            'id_tempo_geracao', 'id_tempo_previsto', 'id_localidade', 'id_condicao', 
            'temperatura_prevista', 'temp_minima', 'temp_maxima', 'sensacao_termica', 
            'prob_chuva', 'umidade_prevista', 'pressao_hpa', 'cobertura_nuvens_pct', 
            'velocidade_vento_kmh', 'direcao_vento_graus'
        ],
        commit_every=100
    )
    print("✅ Dados da previsão carregados com sucesso no Star Schema!")