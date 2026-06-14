create table dim_tempo (
    id_tempo int primary key,
    data_registro date,
    hora_registro time,
    dia_semana varchar,
    mes int,
    ano int
);

create table dim_localidade (
    id_localidade int primary key,
    nome_cidade varchar,
    pais varchar,
    latitude float,
    longitude float
);

create table dim_condicao (
    id_condicao int primary key,
    id_api_weather int,
    grupo_clima varchar,
    descricao_detalhada varchar
);
    
create table fato_clima_atual (
    id_tempo int,
    id_localidade int,
    id_condicao int,
    temperatura_real float,
    sensacao_termica float,
    umidade_real int,
    velocidade_vento float,
    foreign key (id_tempo) references dim_tempo(id_tempo),
    foreign key (id_localidade) references dim_localidade(id_localidade),
    foreign key (id_condicao) references dim_condicao(id_condicao)
);

create table fato_previsao (
    id_tempo_geracao int,
    id_tempo_previsto int,
    id_localidade int,
    id_condicao int,
    temperatura_prevista float,
    temp_minima float,
    temp_maxima float,
    sensacao_termica float,
    prob_chuva float,
    umidade_prevista int,
    pressao_hpa int,
    cobertura_nuvens_pct int,
    velocidade_vento_kmh float,
    direcao_vento_graus int,
    foreign key (id_tempo_geracao) references dim_tempo(id_tempo),
    foreign key (id_tempo_previsto) references dim_tempo(id_tempo),
    foreign key (id_localidade) references dim_localidade(id_localidade),
    foreign key (id_condicao) references dim_condicao(id_condicao)
);