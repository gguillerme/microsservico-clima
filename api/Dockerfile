#Imagem base do Python
FROM python:3.10-slim

#Define o diretório de trabalho dentro do contêiner
WORKDIR /app

#Copia o arquivo de dependências
COPY requirements.txt .

#Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

#Copia o resto do código da API
COPY . .

#Expõe a porta que o Uvicorn usará
EXPOSE 8000

#Comando para iniciar a API quando o contêiner rodar
#    host="0.0.0.0" é essencial para ser acessível
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
