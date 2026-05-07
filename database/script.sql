-- =====================================================================
-- PAPELARIA SGC - SCRIPT DE CRIACAO DO BANCO DE DADOS
-- Sistema de Gestao Comercial para Papelaria Mundo Letrado
-- SGBD: PostgreSQL (compativel tambem com SQLite com pequenos ajustes)
-- =====================================================================

-- Limpeza opcional (use com cuidado em producao)
DROP TABLE IF EXISTS itens_venda CASCADE;
DROP TABLE IF EXISTS vendas      CASCADE;
DROP TABLE IF EXISTS produtos    CASCADE;
DROP TABLE IF EXISTS clientes    CASCADE;
DROP TABLE IF EXISTS usuarios    CASCADE;

-- =====================================================================
-- TABELA: usuarios
-- Armazena usuarios do sistema (ADMIN ou FUNCIONARIO).
-- A coluna senha_hash recebe o hash gerado pelo PBKDF2 (Django default)
-- ou BCrypt. Nunca armazena senha em texto puro.
-- =====================================================================
CREATE TABLE usuarios (
    id           SERIAL PRIMARY KEY,
    username     VARCHAR(60)  NOT NULL UNIQUE,
    email        VARCHAR(120) NOT NULL UNIQUE,
    senha_hash   VARCHAR(255) NOT NULL,
    perfil       VARCHAR(20)  NOT NULL DEFAULT 'FUNCIONARIO',
    ativo        BOOLEAN      NOT NULL DEFAULT TRUE,
    criado_em    TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_perfil CHECK (perfil IN ('ADMIN', 'FUNCIONARIO'))
);

CREATE INDEX idx_usuarios_username ON usuarios(username);
CREATE INDEX idx_usuarios_email    ON usuarios(email);

-- =====================================================================
-- TABELA: clientes
-- Cadastro de clientes da papelaria. CPF unico para evitar duplicidade.
-- =====================================================================
CREATE TABLE clientes (
    id        SERIAL PRIMARY KEY,
    nome      VARCHAR(120) NOT NULL,
    cpf       VARCHAR(14)  NOT NULL UNIQUE,
    email     VARCHAR(120),
    telefone  VARCHAR(20),
    endereco  VARCHAR(200),
    criado_em    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_cpf_formato CHECK (
        cpf ~ '^[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}$' OR
        cpf ~ '^[0-9]{11}$'
    )
);

CREATE INDEX idx_clientes_cpf  ON clientes(cpf);
CREATE INDEX idx_clientes_nome ON clientes(nome);

-- =====================================================================
-- TABELA: produtos
-- Catalogo de produtos da papelaria. Estoque controlado por triggers
-- da aplicacao. Preco e estoque com checks para garantir consistencia.
-- =====================================================================
CREATE TABLE produtos (
    id              SERIAL PRIMARY KEY,
    nome            VARCHAR(120)  NOT NULL,
    descricao       TEXT,
    preco           NUMERIC(10,2) NOT NULL,
    estoque         INTEGER       NOT NULL DEFAULT 0,
    estoque_minimo  INTEGER       NOT NULL DEFAULT 5,
    ativo           BOOLEAN       NOT NULL DEFAULT TRUE,
    criado_em       TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em   TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_preco_positivo  CHECK (preco >= 0),
    CONSTRAINT chk_estoque_positivo CHECK (estoque >= 0),
    CONSTRAINT chk_estoque_min_pos  CHECK (estoque_minimo >= 0)
);

CREATE INDEX idx_produtos_nome   ON produtos(nome);
CREATE INDEX idx_produtos_ativo  ON produtos(ativo);

-- =====================================================================
-- TABELA: vendas
-- Cabecalho da venda. valor_total recalculado pela aplicacao a cada
-- alteracao nos itens. Status permite cancelamento posterior.
-- =====================================================================
CREATE TABLE vendas (
    id           SERIAL PRIMARY KEY,
    data         TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cliente_id   INTEGER       NOT NULL,
    usuario_id   INTEGER       NOT NULL,
    valor_total  NUMERIC(10,2) NOT NULL DEFAULT 0,
    status       VARCHAR(20)   NOT NULL DEFAULT 'CONCLUIDA',
    observacao   TEXT,

    CONSTRAINT fk_venda_cliente FOREIGN KEY (cliente_id)
        REFERENCES clientes(id)
        ON DELETE RESTRICT,    -- nao deixa deletar cliente com vendas
    CONSTRAINT fk_venda_usuario FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE RESTRICT,
    CONSTRAINT chk_status CHECK (status IN ('CONCLUIDA', 'CANCELADA')),
    CONSTRAINT chk_valor_total CHECK (valor_total >= 0)
);

CREATE INDEX idx_vendas_data     ON vendas(data);
CREATE INDEX idx_vendas_cliente  ON vendas(cliente_id);
CREATE INDEX idx_vendas_usuario  ON vendas(usuario_id);
CREATE INDEX idx_vendas_status   ON vendas(status);

-- =====================================================================
-- TABELA: itens_venda
-- Itens (linhas) de cada venda. preco_unitario e gravado para preservar
-- o valor historico da venda mesmo que o produto mude de preco.
-- =====================================================================
CREATE TABLE itens_venda (
    id              SERIAL PRIMARY KEY,
    venda_id        INTEGER       NOT NULL,
    produto_id      INTEGER       NOT NULL,
    quantidade      INTEGER       NOT NULL,
    preco_unitario  NUMERIC(10,2) NOT NULL,

    CONSTRAINT fk_item_venda  FOREIGN KEY (venda_id)
        REFERENCES vendas(id) ON DELETE CASCADE,
    CONSTRAINT fk_item_produto FOREIGN KEY (produto_id)
        REFERENCES produtos(id) ON DELETE RESTRICT,
    CONSTRAINT chk_quantidade CHECK (quantidade > 0),
    CONSTRAINT chk_preco_unit CHECK (preco_unitario >= 0)
);

CREATE INDEX idx_itens_venda    ON itens_venda(venda_id);
CREATE INDEX idx_itens_produto  ON itens_venda(produto_id);

-- =====================================================================
-- VIEW: vw_vendas_completas
-- Facilita relatorios trazendo dados consolidados da venda
-- =====================================================================
CREATE OR REPLACE VIEW vw_vendas_completas AS
SELECT
    v.id            AS venda_id,
    v.data          AS data_venda,
    c.nome          AS cliente_nome,
    c.cpf           AS cliente_cpf,
    u.username      AS vendedor,
    v.valor_total,
    v.status,
    COUNT(iv.id)    AS qtd_itens
FROM vendas v
JOIN clientes c ON c.id = v.cliente_id
JOIN usuarios u ON u.id = v.usuario_id
LEFT JOIN itens_venda iv ON iv.venda_id = v.id
GROUP BY v.id, c.nome, c.cpf, u.username;

-- =====================================================================
-- DADOS INICIAIS (SEED) - Papelaria Mundo Letrado
-- =====================================================================

-- Usuario administrador inicial (a senha real e definida pelo Django
-- via createsuperuser; o hash abaixo e apenas placeholder)
INSERT INTO usuarios (username, email, senha_hash, perfil) VALUES
    ('admin',     'admin@mundoletrado.com.br',     'pbkdf2_sha256$placeholder', 'ADMIN'),
    ('joao.silva','joao@mundoletrado.com.br',      'pbkdf2_sha256$placeholder', 'FUNCIONARIO'),
    ('maria.santos','maria@mundoletrado.com.br',   'pbkdf2_sha256$placeholder', 'FUNCIONARIO');

-- Clientes de exemplo
INSERT INTO clientes (nome, cpf, email, telefone, endereco) VALUES
    ('Ana Beatriz Souza',   '123.456.789-00', 'ana.souza@email.com',    '(61) 99876-5432', 'Quadra 401 Norte, Brasilia/DF'),
    ('Carlos Eduardo Lima', '987.654.321-99', 'carlos.lima@email.com',  '(61) 99123-4567', 'Lago Sul SHIS QI 23, Brasilia/DF'),
    ('Fernanda Oliveira',   '456.789.123-44', 'fernanda@email.com',     '(61) 98555-1122', 'Asa Sul 308, Brasilia/DF'),
    ('Joao Pedro Castro',   '321.654.987-77', 'joaop@email.com',        '(61) 99888-3344', 'Taguatinga Norte, Brasilia/DF');

-- Produtos do catalogo de papelaria
INSERT INTO produtos (nome, descricao, preco, estoque, estoque_minimo) VALUES
    ('Caderno Universitario 200 folhas', 'Caderno espiral, 200 folhas, capa dura',          24.90,  60, 10),
    ('Caneta Esferografica Azul',        'Caneta esferografica BIC azul',                     2.50, 200, 30),
    ('Caneta Esferografica Preta',       'Caneta esferografica BIC preta',                    2.50, 180, 30),
    ('Lapis HB',                         'Lapis grafite preto HB com borracha',               1.80, 250, 40),
    ('Borracha Branca',                  'Borracha branca tamanho medio',                     1.20, 150, 20),
    ('Apontador com Deposito',           'Apontador com deposito de plastico',                3.50,  90, 15),
    ('Mochila Escolar',                  'Mochila escolar 20L com bolsos laterais',         149.90,  20,  3),
    ('Estojo Triplo',                    'Estojo escolar triplo, varias cores',              45.00,  35,  5),
    ('Tinta Guache 6 Cores',             'Conjunto de tinta guache com 6 cores 15ml',        12.90,  40,  8),
    ('Lapis de Cor 24 Cores',            'Caixa com 24 lapis de cor',                        29.90,  45,  8),
    ('Cola Branca 90g',                  'Cola escolar branca lavavel 90g',                   4.90, 100, 15),
    ('Tesoura sem Ponta',                'Tesoura escolar sem ponta',                         8.50,  60, 10),
    ('Marcador de Texto Amarelo',        'Marca-texto fluorescente amarelo',                  4.20, 110, 20),
    ('Papel Sulfite A4 (resma)',         'Resma com 500 folhas A4 75g',                      29.90,  25,  5),
    ('Pasta Catalogo 50 plasticos',      'Pasta tipo catalogo com 50 plasticos',             18.90,  30,  5);

-- Venda de exemplo (sera apagada apos testes ou ficara como demo)
-- Cliente Ana Beatriz comprou alguns itens
INSERT INTO vendas (cliente_id, usuario_id, valor_total, status) VALUES
    (1, 1,  56.40, 'CONCLUIDA');

INSERT INTO itens_venda (venda_id, produto_id, quantidade, preco_unitario) VALUES
    (1, 1, 1, 24.90),  -- 1 caderno
    (1, 2, 3,  2.50),  -- 3 canetas azuis
    (1, 4, 5,  1.80),  -- 5 lapis HB
    (1, 5, 4,  1.20);  -- 4 borrachas

-- =====================================================================
-- VERIFICACOES POS-INSTALACAO
-- =====================================================================
SELECT 'Tabelas criadas com sucesso' AS status;
SELECT COUNT(*) AS total_usuarios FROM usuarios;
SELECT COUNT(*) AS total_clientes FROM clientes;
SELECT COUNT(*) AS total_produtos FROM produtos;
SELECT COUNT(*) AS total_vendas   FROM vendas;
