import pandas as pd
import json
from datetime import datetime, timedelta, timezone
from airflow.hooks.base import BaseHook
from minio import Minio

def _obter_cliente_minio():
    conexao_minio = BaseHook.get_connection('minio_raw')
    return Minio(
        endpoint=f"{conexao_minio.host}:{conexao_minio.port}",
        access_key=conexao_minio.login,
        secret_key=conexao_minio.password,
        secure=False
    )

def ler_json_do_minio(pasta):
    cliente_minio = _obter_cliente_minio()
    agora = datetime.now()
    caminho_arquivo = f"{pasta}/{agora.strftime('%Y/%m/%d')}/{agora.strftime('%H_00')}.json"
    
    resposta = cliente_minio.get_object("raw-weather-data", caminho_arquivo)
    dados = json.loads(resposta.read().decode('utf-8'))
    resposta.close()
    resposta.release_conn()
    return dados

def extrair_dimensoes(dados_api, dt_obj):
    # Dimensão Tempo (Fuso Horário GMT-3 Aplicado)
    dim_tempo = {
        'id_tempo': int(dt_obj.strftime('%Y%m%d%H')),
        'data_registro': dt_obj.strftime('%Y-%m-%d'),
        'hora_registro': dt_obj.strftime('%H:%M:%S'),
        'dia_semana': dt_obj.strftime('%A'),
        'mes': dt_obj.month,
        'ano': dt_obj.year
    }
    
    # Dimensão Condição
    dim_condicao = {
        'id_condicao': dados_api['weather'][0]['id'],
        'id_api_weather': dados_api['weather'][0]['id'],
        'grupo_clima': dados_api['weather'][0]['main'],
        'descricao_detalhada': dados_api['weather'][0]['description']
    }
    return dim_tempo, dim_condicao

def transformar_clima_atual(**kwargs):
    print("Iniciando transformação dimensional do Clima Atual...")
    dados = ler_json_do_minio('clima_atual')
    
    # Avisa que é UTC e diminui 3 horas (GMT-3)
    dt_medicao = datetime.fromtimestamp(dados['dt'], timezone.utc) - timedelta(hours=3)
    
    dim_tempo, dim_condicao = extrair_dimensoes(dados, dt_medicao)
    
    dim_localidade = {
        'id_localidade': dados['id'],
        'nome_cidade': dados['name'],
        'pais': dados['sys']['country'],
        'latitude': dados['coord']['lat'],
        'longitude': dados['coord']['lon']
    }
    
    fato_clima = {
        'id_tempo': dim_tempo['id_tempo'],
        'id_localidade': dim_localidade['id_localidade'],
        'id_condicao': dim_condicao['id_condicao'],
        'temperatura_real': round(dados['main']['temp'] - 273.15, 2),
        'sensacao_termica': round(dados['main']['feels_like'] - 273.15, 2),
        'umidade_real': dados['main']['humidity'],
        'velocidade_vento': round(dados['wind']['speed'] * 3.6, 2)
    }
    
    pd.DataFrame([dim_tempo]).to_csv('/tmp/dim_tempo_atual.csv', index=False)
    pd.DataFrame([dim_localidade]).to_csv('/tmp/dim_localidade.csv', index=False)
    pd.DataFrame([dim_condicao]).to_csv('/tmp/dim_condicao_atual.csv', index=False)
    pd.DataFrame([fato_clima]).to_csv('/tmp/fato_clima_atual.csv', index=False)
    print("✅ Transformação do clima atual concluída.")

def transformar_previsao(**kwargs):
    print("Iniciando transformação dimensional da Previsão ENRIQUECIDA...")
    dados = ler_json_do_minio('previsao')
    
    # Momento em que a previsão foi gerada (GMT-3)
    dt_geracao = datetime.now(timezone.utc) - timedelta(hours=3)
    dim_tempo_geracao = {
        'id_tempo': int(dt_geracao.strftime('%Y%m%d%H')),
        'data_registro': dt_geracao.strftime('%Y-%m-%d'),
        'hora_registro': dt_geracao.strftime('%H:%M:%S'),
        'dia_semana': dt_geracao.strftime('%A'),
        'mes': dt_geracao.month,
        'ano': dt_geracao.year
    }
    
    dim_localidade = {
        'id_localidade': dados['city']['id'],
        'nome_cidade': dados['city']['name'],
        'pais': dados['city']['country'],
        'latitude': dados['city']['coord']['lat'],
        'longitude': dados['city']['coord']['lon']
    }
    
    lista_fatos = []
    lista_tempos_previstos = []
    lista_condicoes = []
    
    for item in dados['list']:
        dt_previsto = datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S')
        dt_previsto = dt_previsto - timedelta(hours=3) # Ajuste para GMT-3
        
        dim_tempo_prev, dim_cond_prev = extrair_dimensoes(item, dt_previsto)
        
        lista_tempos_previstos.append(dim_tempo_prev)
        lista_condicoes.append(dim_cond_prev)
        
        fato_prev = {
            'id_tempo_geracao': dim_tempo_geracao['id_tempo'],
            'id_tempo_previsto': dim_tempo_prev['id_tempo'],
            'id_localidade': dim_localidade['id_localidade'],
            'id_condicao': dim_cond_prev['id_condicao'],
            
            # Temperaturas (Aplicando K para C)
            'temperatura_prevista': round(item['main']['temp'] - 273.15, 2),
            'temp_minima': round(item['main']['temp_min'] - 273.15, 2),
            'temp_maxima': round(item['main']['temp_max'] - 273.15, 2),
            'sensacao_termica': round(item['main']['feels_like'] - 273.15, 2),
            
            # Atmosfera
            'prob_chuva': item.get('pop', 0.0), 
            'umidade_prevista': item['main']['humidity'],
            'pressao_hpa': item['main']['pressure'],
            'cobertura_nuvens_pct': item['clouds']['all'],
            
            # Vento (Aplicando m/s para km/h)
            'velocidade_vento': round(item['wind']['speed'] * 3.6, 2),
            'direcao_vento_graus': item['wind']['deg']
        }
        lista_fatos.append(fato_prev)
        
    df_tempos = pd.DataFrame([dim_tempo_geracao] + lista_tempos_previstos).drop_duplicates(subset=['id_tempo'])
    df_condicoes = pd.DataFrame(lista_condicoes).drop_duplicates(subset=['id_condicao'])
    
    df_tempos.to_csv('/tmp/dim_tempo_previsao.csv', index=False)
    pd.DataFrame([dim_localidade]).to_csv('/tmp/dim_localidade_previsao.csv', index=False)
    df_condicoes.to_csv('/tmp/dim_condicao_previsao.csv', index=False)
    pd.DataFrame(lista_fatos).to_csv('/tmp/fato_previsao.csv', index=False)
    print("✅ Transformação da previsão enriquecida concluída.")