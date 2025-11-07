CREATE TABLE IF NOT EXISTS clima (
    id SERIAL PRIMARY KEY,
    cidade VARCHAR(100) NOT NULL,
    pais VARCHAR(10) NOT NULL,
    temperatura_c REAL,
    sensacao_termica_c REAL,
    temp_min_c REAL,
    temp_max_c REAL,
    umidade_pct INTEGER,
    descricao VARCHAR(255),
    velocidade_vento_ms REAL,
    timestamp_coleta BIGINT,
    data_insercao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
