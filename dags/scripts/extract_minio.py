import requests
import json
import io
from datetime import datetime
from airflow.sdk import Variable
from airflow.hooks.base import BaseHook
from minio import Minio

def _obter_cliente_minio():
    """Função auxiliar interna para não repetirmos o código de conexão"""
    conexao_minio = BaseHook.get_connection('minio_raw')
    return Minio(
        endpoint=f"{conexao_minio.host}:{conexao_minio.port}",
        access_key=conexao_minio.login,
        secret_key=conexao_minio.password,
        secure=False
    )

def extrair_clima_atual():
    """Extrai o clima atual da OpenWeather e salva na pasta 'clima_atual'."""
    print("Iniciando extração do clima ATUAL...")
    api_key = Variable.get("openweather_api_key")
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Videira,br&appid={api_key}&lang=pt_br"
    
    resposta = requests.get(url)
    resposta.raise_for_status() 
    dados_json = resposta.json()

    cliente_minio = _obter_cliente_minio()
    json_bytes = json.dumps(dados_json, ensure_ascii=False).encode('utf-8')
    agora = datetime.now()
    caminho_arquivo = f"clima_atual/{agora.strftime('%Y/%m/%d')}/{agora.strftime('%H_00')}.json"

    cliente_minio.put_object(
        bucket_name="raw-weather-data",
        object_name=caminho_arquivo,
        data=io.BytesIO(json_bytes),
        length=len(json_bytes),
        content_type="application/json"
    )
    print(f"✅ Clima atual salvo em: {caminho_arquivo}")

def extrair_previsao():
    """Extrai a previsão de 5 dias da OpenWeather e salva na pasta 'previsao'."""
    print("Iniciando extração da PREVISÃO de 5 dias...")
    api_key = Variable.get("openweather_api_key")
    # ATENÇÃO: A URL mudou de 'weather' para 'forecast'
    url = f"https://api.openweathermap.org/data/2.5/forecast?q=Videira,br&appid={api_key}&lang=pt_br"
    
    resposta = requests.get(url)
    resposta.raise_for_status() 
    dados_json = resposta.json()

    cliente_minio = _obter_cliente_minio()
    json_bytes = json.dumps(dados_json, ensure_ascii=False).encode('utf-8')
    agora = datetime.now()
    # ATENÇÃO: A pasta raiz mudou para 'previsao'
    caminho_arquivo = f"previsao/{agora.strftime('%Y/%m/%d')}/{agora.strftime('%H_00')}.json"

    cliente_minio.put_object(
        bucket_name="raw-weather-data",
        object_name=caminho_arquivo,
        data=io.BytesIO(json_bytes),
        length=len(json_bytes),
        content_type="application/json"
    )
    print(f"✅ Previsão salva em: {caminho_arquivo}")