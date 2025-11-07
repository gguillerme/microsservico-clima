# -*- coding: utf-8 -*-
"""
API RESTful (FastAPI) para consultar dados climáticos.

Este módulo usa o FastAPI para criar endpoints que leem
dados de um banco de dados PostgreSQL populado por um script separado.
O ambiente é totalmente gerenciado pelo Docker Compose.
"""

# --- Importações ---
import os
import uvicorn
from fastapi import FastAPI, HTTPException
import psycopg2
from psycopg2 import Error
from psycopg2.extras import RealDictCursor # Para retornar JSON
import psycopg2.extensions # Para Type Hinting

# --- Configuração do Banco de Dados (via Variáveis de Ambiente) ---
# O Docker Compose injeta estes valores a partir do arquivo .env
try:
    DB_NAME = os.environ["POSTGRES_DB"]
    DB_USER = os.environ["POSTGRES_USER"]
    DB_PASSWORD = os.environ["POSTGRES_PASSWORD"]
    DB_HOST = os.environ["DB_HOST"] # 'db' (nome do serviço Docker)
    DB_PORT = os.environ.get("DB_PORT", "5432")
except KeyError as e:
    print(f"Erro: Variável de ambiente não definida: {e}")
    print("Certifique-se de que o .env está configurado e o Docker Compose está lendo.")
    raise

# --- Inicialização da Aplicação FastAPI ---
app = FastAPI(
    title="API de Dados Climáticos",
    description="Uma API RESTful para consultar dados climáticos coletados do OpenWeather e armazenados no PostgreSQL.",
    version="1.0.0"
)

# --- Funções Auxiliares (Conexão com BD) ---
def get_db_connection() -> psycopg2.extensions.connection | None:
    """
    Cria e retorna uma nova conexão com o banco de dados PostgreSQL.
    Retorna None em caso de falha na conexão.
    """
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        print("Conexão com o banco de dados estabelecida com sucesso.")
        return conn
    except Error as e:
        # Em um app de produção, isso seria logado em um sistema de monitoring
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# --- Definição dos Endpoints da API ---

@app.get("/clima", response_model=list)
async def get_clima_todos():
    """
    Endpoint para buscar TODOS os registros climáticos
    armazenados no banco de dados.

    Retorna uma lista de registros, ordenados do mais novo para o mais antigo.
    """
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao banco de dados.")

    try:
        # Usamos RealDictCursor para que o resultado venha como um dicionário
        # (perfeito para converter em JSON automaticamente pelo FastAPI)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        query = "SELECT * FROM clima ORDER BY data_insercao DESC"
        
        cursor.execute(query)
        
        registros_clima = cursor.fetchall()
        
        return registros_clima

    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar o banco de dados: {e}")
    finally:
        # Garante que a conexão seja sempre fechada
        if conn:
            conn.close()
            print("Conexão com o banco de dados fechada.")

@app.get("/clima/{cidade}", response_model=list)
async def get_clima_por_cidade(cidade: str):
    """
    Endpoint para buscar os registros de uma CIDADE específica.
    A busca é case-insensitive (não diferencia maiúsculas/minúsculas).
    """
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Não foi possível conectar ao banco de dados.")

    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Usamos ILIKE para busca case-insensitive
        # Usamos %s para evitar SQL Injection
        query = "SELECT * FROM clima WHERE cidade ILIKE %s ORDER BY data_insercao DESC"
        
        # Passamos a cidade como uma tupla (o f"%{...}%" adiciona os curingas)
        cursor.execute(query, (f"%{cidade}%",)) 
        
        registros = cursor.fetchall()
        
        if not registros:
            # Se a busca não retornar nada, é um 404 (Não Encontrado)
            raise HTTPException(status_code=404, detail=f"Nenhum registro encontrado para a cidade: {cidade}")
            
        return registros
        
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar o banco de dados: {e}")
    finally:
        if conn:
            conn.close()
            print("Conexão com o banco de dados fechada.")


# --- Ponto de Entrada (Para rodar com 'python main.py') ---
if __name__ == "__main__":
    """
    Permite rodar a API diretamente para fins de debug local,
    embora o Dockerfile use o comando 'uvicorn' diretamente.
    """
    print("Iniciando servidor Uvicorn para desenvolvimento...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
