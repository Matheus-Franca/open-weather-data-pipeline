from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from scripts.extract_minio import extrair_clima_atual, extrair_previsao
from scripts.transform_pandas import transformar_clima_atual, transformar_previsao
from scripts.load_postgres import carregar_clima_atual, carregar_previsao

default_args = {
    'owner': 'Matheus-Franca',
    'retries': 1, 
    'retry_delay': timedelta(minutes=5), 
}

with DAG(
    dag_id='etl_clima_videira',
    default_args=default_args,
    start_date=datetime(2026, 6, 13), 
    schedule='@hourly',      
    catchup=False,                    
    tags=['ETL', 'Clima', 'Videira']
) as dag:

    # --- CAMADA RAW (Extração) ---
    task_extracao_atual = PythonOperator(
        task_id='extrair_atual_minio',
        python_callable=extrair_clima_atual
    )

    task_extracao_previsao = PythonOperator(
        task_id='extrair_previsao_minio',
        python_callable=extrair_previsao
    )

    # --- CAMADA TRUSTED (Transformação) ---
    task_transformacao_atual = PythonOperator(
        task_id='transformar_atual_pandas',
        python_callable=transformar_clima_atual
    )

    task_transformacao_previsao = PythonOperator(
        task_id='transformar_previsao_pandas',
        python_callable=transformar_previsao
    )

    # --- CAMADA REFINED (Carga no DW) ---
    task_carga_atual = PythonOperator(
        task_id='carregar_atual_postgres',
        python_callable=carregar_clima_atual
    )

    task_carga_previsao = PythonOperator(
        task_id='carregar_previsao_postgres',
        python_callable=carregar_previsao
    )
    # ---------------------------------------------------------
    # ORDEM DE EXECUÇÃO (Dependências Finais)
    # ---------------------------------------------------------
    # Fluxo 1: Clima Atual
    task_extracao_atual >> task_transformacao_atual >> task_carga_atual
    
    # Fluxo 2: Previsão
    task_extracao_previsao >> task_transformacao_previsao >> task_carga_previsao