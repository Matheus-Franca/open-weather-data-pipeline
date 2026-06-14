from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from datetime import datetime

# Definindo a estrutura básica da DAG

default_args = {
    'owner': 'Matheus-Franca', 
}

with DAG(
    dag_id='teste_conexao_postgres',
    start_date=datetime(2026, 1, 1),
    schedule=None,          
    catchup=False,
    tags=['Infraestrutura', 'Teste'],
    description='DAG para testar a comunicação com o Data Warehouse'
) as dag:

    # Tarefa unificada que executa o comando SQL
    testar_banco = SQLExecuteQueryOperator(
        task_id='rodar_query_teste',
        conn_id='postgres_dw', # Parâmetro atualizado na nova versão
        sql='SELECT 1;'
    )