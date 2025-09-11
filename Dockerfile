# Dockerfile para Railway Deploy
FROM python:3.9-slim

WORKDIR /app

# Copiar requirements
COPY paineluniversal/backend/requirements.txt .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY paineluniversal/backend/ .

# Expor porta
EXPOSE 8000

# Comando para iniciar
CMD ["uvicorn", "simple_server:app", "--host", "0.0.0.0", "--port", "8000"]