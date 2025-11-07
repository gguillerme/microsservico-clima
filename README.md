# 🚀 Microsserviço de Coleta de Dados Climáticos

Este projeto é um microsserviço completo que demonstra um pipeline de dados simples:
1.  **Coleta (ETL):** Busca dados meteorológicos atuais da API OpenWeatherMap.
2.  **Armazenamento:** Salva os dados tratados em um banco de dados PostgreSQL.
3.  **Exposição (API):** Expõe os dados armazenados através de uma API RESTful (FastAPI).

O ambiente é totalmente conteinerizado usando Docker e Docker Compose.

---

## 🛠️ Tecnologias Utilizadas

* **Backend:** Python 3.10
* **Framework da API:** FastAPI
* **Banco de Dados:** PostgreSQL
* **Conteinerização:** Docker & Docker Compose
* **Fonte de Dados:** API OpenWeatherMap

---

## 🏁 Como Executar o Projeto

**Pré-requisitos:**
* [Docker](https://www.docker.com/products/docker-desktop/)
* [Docker Compose](https://docs.docker.com/compose/install/)
* Git

**1. Clone o Repositório**
```bash
git clone https://github.com/gguillerme/microsservico-clima.git
cd microsservico-clima
```

**2. Crie seu Arquivo de Ambiente**
Copie o arquivo de exemplo e preencha com suas chaves e senhas:
```bash
# Copie o exemplo
cp .env.example .env
```
Agora, edite o arquivo `.env` e adicione sua `API_KEY` (Obrigatório) Adicione sua chave de API válida do OpenWeatherMap. `POSTGRES_PASSWORD`(Obrigatório) Defina qualquer senha de sua escolha (ex: senha-segura-123). O ambiente Docker usará esta senha do .env para criar e autenticar o banco de dados, a API e o script automaticamente.

**3. Suba o Ambiente Docker**
Este comando irá construir a imagem da API, iniciar o contêiner do banco de dados e iniciar a API.
```bash
docker-compose up --build -d
```
O banco estará acessível em `localhost:5432` e a API em `http://localhost:8000`.

**4. Execute o Script de Coleta**
Para popular o banco de dados pela primeira vez, execute o script de coleta (você precisará ter Python 3 e as bibliotecas `requests`, `psycopg2-binary`, `python-dotenv` instaladas localmente):

```bash
# Navegue até a pasta de scripts
cd scripts

# Instale as dependências (se necessário)
# pip3 install -r requirements.txt  <-- (Opcional, se você criar um requirements.txt para ele)

# Execute a coleta
python3 extrair_clima.py
```
Você verá a mensagem `Dados de 'SuaCidade' salvos no banco com sucesso!`.

---

## Acessando a API

A API estará disponível em `http://localhost:8000`.

### Documentação Interativa (Swagger)

A melhor forma de testar a API é através da documentação interativa gerada automaticamente:

👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

### Endpoints Disponíveis

* `GET /clima`: Retorna todos os registros climáticos salvos no banco, ordenados do mais recente para o mais antigo.
* `GET /clima/{cidade}`: Retorna todos os registros para uma cidade específica (busca parcial, ex: "Florian").

---
