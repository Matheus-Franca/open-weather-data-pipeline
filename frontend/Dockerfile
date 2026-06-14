FROM python:3.11-slim

WORKDIR /app

# Copia os requisitos e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da página
COPY app_clima.py .

# Expõe a porta padrão do Streamlit
EXPOSE 8501

# Comando para rodar a página
CMD ["streamlit", "run", "app_clima.py", "--server.port=8501", "--server.address=0.0.0.0"]