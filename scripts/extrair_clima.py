import requests
import json
import os
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv # ⬅️ Importar
from pathlib import Path # ⬅️ Importar

# --- Configuração ---
# Encontra o caminho para o arquivo .env na raiz do projeto
# (sobe 2 níveis: /scripts -> /weather_project)
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path) # ⬅️ Carrega o .env

print("Variáveis de ambiente carregadas.")

# Pega as variáveis do ambiente (carregadas do .env)
API_KEY = os.environ.get("API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
DB_NAME = os.environ.get("POSTGRES_DB")
DB_USER = os.environ.get("POSTGRES_USER")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
DB_HOST = "localhost" # ⬅️ Correto! O script local acessa a porta exposta
DB_PORT = os.environ.get("DB_PORT", "5432")

# Checagem de segurança
if not API_KEY:
    raise ValueError("API_KEY não encontrada. Verifique seu arquivo .env")
if not DB_PASSWORD:
    raise ValueError("DB_PASSWORD não encontrado. Verifique seu arquivo .env")

def buscar_dados_climaticos(cidade):
    """
    Busca dados climáticos para uma cidade específica usando a API OpenWeather.
    """
    
    # Parâmetros dinâmicos para a URL
    params = {
        'q': cidade,            
        'appid': API_KEY,       
        'units': 'metric',      
        'lang': 'pt_br'         
    }

    print(f"Buscando dados para a cidade: {cidade}...")

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status() 
        dados = response.json()
        return dados

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 401:
            print("Erro: Chave de API inválida ou não ativada.")
        elif response.status_code == 404:
            print(f"Erro: Cidade '{cidade}' não encontrada.")
        else:
            print(f"Erro HTTP: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Erro na requisição: {req_err}")
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        
    return None

def extrair_info_interesse(dados_completos):
    """
    Filtra e extrai apenas os dados que queremos armazenar.
    """
    if dados_completos is None:
        return None

    try:
        info_extraida = {
            "cidade": dados_completos['name'],
            "pais": dados_completos['sys']['country'],
            "temperatura_c": dados_completos['main']['temp'],
            "sensacao_termica_c": dados_completos['main']['feels_like'],
            "temp_min_c": dados_completos['main']['temp_min'],
            "temp_max_c": dados_completos['main']['temp_max'],
            "umidade_pct": dados_completos['main']['humidity'],
            "descricao": dados_completos['weather'][0]['description'],
            "velocidade_vento_ms": dados_completos['wind']['speed'],
            "timestamp_coleta": dados_completos['dt']
        }
        return info_extraida

    except KeyError as e:
        print(f"Erro ao extrair dados do JSON. Chave não encontrada: {e}")
        return None

def salvar_dados_no_bd(dados):
    """
    Conecta ao banco PostgreSQL e insere os dados climáticos.
    """
    if dados is None:
        print("Nenhum dado para salvar.")
        return

    conn = None
    cursor = None
    try:
        # 1. Conectar ao banco
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        # 2. Criar um cursor
        cursor = conn.cursor()

        # 3. Definir a query de inserção
        # Os nomes das colunas DEVEM bater com a tabela criada no SQL
        query = """
        INSERT INTO clima 
        (cidade, pais, temperatura_c, sensacao_termica_c, temp_min_c, 
         temp_max_c, umidade_pct, descricao, velocidade_vento_ms, timestamp_coleta)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # 4. Criar a tupla de valores NA ORDEM CORRETA da query
        # Isso usa os dados do dicionário 'dados'
        valores = (
            dados['cidade'], dados['pais'], dados['temperatura_c'], 
            dados['sensacao_termica_c'], dados['temp_min_c'], dados['temp_max_c'],
            dados['umidade_pct'], dados['descricao'], dados['velocidade_vento_ms'],
            dados['timestamp_coleta']
        )

        # 5. Executar a query
        cursor.execute(query, valores)
        
        # 6. Salvar (commit) a transação
        conn.commit()
        
        print("----------------------------------")
        print(f"Dados de '{dados['cidade']}' salvos no banco com sucesso!")
        print("----------------------------------")

    except Error as e:
        print(f"Erro ao salvar no banco de dados: {e}")
        if conn:
            conn.rollback() # Desfaz a transação em caso de erro

    finally:
        # 7. Fechar a conexão
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --- Execução Principal (Atualizada) ---
if __name__ == "__main__":
    cidade_para_buscar = "Florianópolis" 
    
    dados_brutos = buscar_dados_climaticos(cidade_para_buscar)
    
    if dados_brutos:
        dados_filtrados = extrair_info_interesse(dados_brutos)
        
        if dados_filtrados:
            print("\n--- Dados Climáticos Extraídos ---")
            for chave, valor in dados_filtrados.items():
                print(f"{chave.capitalize().replace('_', ' ')}: {valor}")
            
            # 8. Chamamos a nova função!
            salvar_dados_no_bd(dados_filtrados)
