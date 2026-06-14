# Pipeline de Dados Utilizando Dados Fornecidos pela OpenWeather

#### Projeto desenvolvido para extrair, através de uma API, dados climáticos da cidade de Videira, transformar esses dados e disponibilizá-los em um data warehouse para visualização ou análise.
<br>
<div align="center">
  <img  width="750" height="460" alt="Diagrama-de-Infraestrutura" src="https://github.com/user-attachments/assets/b6d1d6ec-8f94-4a79-8972-1d96e152727f" />
</div>
<br>
<br>

#### O sistema coleta automaticamete a cada hora dados de uma API externa, organiza-os em um Data Lake, modela os dados e faz a carga em um Data Warehouse modelado baseado no esquema dimensional Star Schema, e disponibiliza as informações em uma aplicação Web.

## Arquitetura e Tecnologias

A infraestrutura foi construída utilizando o conceito de **Infrastructure as Code (IaC)** com Docker Compose, garantindo a reprodutibilidade do ambiente. Todo o fluxo é orquestrado de forma autônoma e paralela.

* **Fonte de Dados:** OpenWeather API (Current Weather e 5-Day Forecast)
* **Orquestração:** Apache Airflow
* **Linguagem Principal:** Python
* **Camada Raw (Data Lake):** MinIO (Object Storage S3-Compatible)
* **Camada Trusted (Processamento):** Python/Pandas
* **Camada Refined (Data Warehouse):** PostgreSQL
* **Modelagem de Dados:** Star Schema (Fatos e Dimensões)
* **Visualização (Frontend):** Streamlit - Poderia ter utilizado também o Metabase ou PowerBI, porém o foco deste projeto é a construção da infraestrutura e o processo de ETL.

## Fluxo de Dados (ETL)

1. **Extract:** O Airflow aciona as DAGs de extração que se conectam à API da OpenWeather. Os dados brutos (JSON) são ingeridos e salvos no MinIO, particionados por ano/mes/dia.
2. **Transform:** Scripts em Python/Pandas acessam o Data Lake, achatam os dicionários, e aplicam regras de negócios (como conversão de Kelvin para Celsius e ajustes de fuso horário UTC para GMT-3) e preparam os dados para o modelo relacional. É possível utilizar parâmetros diretamente na API para formatar as informações, porém por escolha própria, resolvi fazer o tratamento durante o processo de transformação.
3. **Load:** Utilizando o PostgresHook, os dados são carregados no PostgreSQL, alimentando as tabelas de dimensão (`dim_tempo`, `dim_localidade`, `dim_condicao`) e as tabelas fato (`fato_clima_atual`, `fato_previsao`).
4. **Visualização:** O Streamlit se conecta diretamente ao Data Warehouse realizando consultas SQL para apresentar os dados na tela, aplicando filtros de interface para exibir previsões a cada 6 horas e simplificar a probabilidade de chuva.

## Como Executar o Projeto Localmente

Este projeto foi construído para ser facilmente reproduzível em qualquer máquina, independente do sistema operacional, graças à conteinerização.

### Pré-requisitos

Antes de começar, você precisará ter as seguintes ferramentas instaladas em sua máquina:
* [Git](https://git-scm.com/)
* [Docker](https://www.docker.com/products/docker-desktop) e **Docker Compose**
* Uma chave de API gratuita da [OpenWeather](https://home.openweathermap.org/api_keys) caso ainda não seja cadastrado, será necessário criar uma conta.

### Passo a Passo da Instalação

**1. Clone o repositório**

Abra o terminal, dentro do repositório que você deseja deixar a pasta do projeto, e baixe o código fonte:

```bash
git clone git@github.com:Matheus-Franca/open-weather-data-pipeline.git
 ```
Agora entre no repositório do projeto baixado na sua máquina:
```bash
cd open-weather-data-pipeline
 ```

**2. Crie e configure o arquivo .env**

Agora você precisará criar um arquivo com o nome `.env` e configurar os dados das suas chaves de acesso 

```bash

_AIRFLOW_WWW_USER_PASSWORD= Coloque aqui a senha que você deseja utilizar para acessar o AirFlow

USER_MINIO=Coloque_aqui_o_usuário_que_você_deseja_utilizar_para_acessar_o_minIO
PASSWD_MINIO=Coloque_aqui_a_senha_que_você_deseja_utilizar_para_acessar_o_minIO

dw_user=Coloque_aqui_o_usuário_que_você_deseja_utilizar_para_acessar_o_Data_Warehouse
dw_password=Coloque_aqui_a_senha_que_você_deseja_utilizar_para_acessar_o_Data_Warehouse
dw_db=weather_db

API_KEY_OPENWEATHER=Cole_aqui_sua_api_key_gerada_no_site_openweather

 ```

**3. Suba a Infraestrutura**

Com as variáveis configuradas, no terminal, execute:

```bash
docker compose up -d --build
 ```
Deixe o Docker construir os contêineres, baixar as dependências do Python e criar as redes isoladas. A primeira execução pode levar alguns minutos enquanto o Docker baixa as imagens oficiais.

**4. Acesse as Plataformas**

Com a infraestrutura de pé, acesse os serviços pelo seu navegador:

Dashboard (Streamlit): http://localhost:8501

O Produto de Dados final com a visualização do clima.

🎼 Orquestrador (Airflow): http://localhost:8080

Usuário padrão: admin | Senha: admin ou aquela que você definiu no arquivo .env

Aqui você pode ativar a DAG etl_clima_videira para rodar a primeira extração manual.

🗄️ Data Lake (MinIO): http://localhost:9001

Onde os arquivos JSON brutos ficam salvos.

**5. Encerrando o Projeto**

Para parar todos os serviços e liberar a memória do seu computador, execute:

```bash
docker compose down
 ```
Se desejar resetar as informações e apagar o histórico salvo, adicione a flag -v 

```bash
docker compose down -v
 ```











