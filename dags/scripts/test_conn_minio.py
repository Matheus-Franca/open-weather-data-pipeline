from airflow.hooks.base import BaseHook
from minio import Minio

# Função Python para testar a conexão do Airflow com o MinIO e listar os buckets

def testar_conexao_minio():
    # Busca a variável de ambiente que criamos no docker-compose
    print("Buscando credenciais no cofre do Airflow...")
    conexao = BaseHook.get_connection('minio_raw')
    
    # Monta o cliente do MinIO
    cliente = Minio(
        endpoint=f"{conexao.host}:{conexao.port}",
        access_key=conexao.login,
        secret_key=conexao.password,
        secure=False # Falso porque não estamos usando HTTPS localmente
    )
    
    # Tenta listar todos os buckets existentes para provar que conectou
    print("Conectando ao MinIO e buscando buckets...")
    buckets = cliente.list_buckets()
    
    if buckets:
        print("✅ Sucesso! Buckets encontrados:")
        for bucket in buckets:
            print(f" - {bucket.name}")
    else:
        print("✅ Sucesso! A conexão funcionou, mas o MinIO ainda não tem nenhum bucket.")
