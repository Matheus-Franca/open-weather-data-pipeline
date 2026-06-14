from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from scripts.test_conn_minio import testar_conexao_minio

default_args = {
    'owner': 'Matheus-Franca', 
}

# Estrutura da DAG
with DAG(
    dag_id='teste_conexao_minio',
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=['Infraestrutura', 'Teste'],
    description='DAG para testar a comunicação via Python com o MinIO'
) as dag:

    # Tarefa que chama a nossa função Python
    tarefa_teste_minio = PythonOperator(
        task_id='conectar_e_listar_buckets',
        python_callable=testar_conexao_minio
    )