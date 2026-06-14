# Puxa a imagem original do Airflow com a versão específica
FROM apache/airflow:3.2.2

# Copia o seu arquivo de requisitos para dentro do contêiner
COPY requirements.txt /

# Instala as bibliotecas de forma definitiva
RUN pip install --no-cache-dir -r /requirements.txt