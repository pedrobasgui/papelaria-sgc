#  Papelaria SGC — Sistema de Gestão Comercial

Sistema de gestão comercial para a **Papelaria Mundo Letrado**, desenvolvido como projeto da disciplina **Desenvolvimento Web**.

![Stack](https://img.shields.io/badge/python-3.11+-blue) ![Django](https://img.shields.io/badge/django-5.0-green) ![DRF](https://img.shields.io/badge/DRF-3.15-red) ![JWT](https://img.shields.io/badge/auth-JWT-orange) ![Tests](https://img.shields.io/badge/testes-40%20passando-brightgreen)

---

##  Sobre o projeto

A Papelaria Mundo Letrado é um pequeno comércio de bairro especializado em material escolar e de escritório. O SGC automatiza:

- Cadastro de clientes e produtos
- Registro de vendas com baixa automática de estoque
- Geração de relatórios gerenciais (com gráfico anual)
- Controle de acesso por perfis (Administrador / Funcionário)

##  Arquitetura

Arquitetura em camadas (View → Service → Repository → Model) com separação backend (API REST) / frontend (Django Templates):

```
┌──────────────────────────────────────────┐
│   Browser (Bootstrap + Chart.js)         │
└────────────────┬─────────────────────────┘
                 │ HTTPS / JSON + JWT
┌────────────────▼─────────────────────────┐
│   Django Templates (apps.web)            │
└────────────────┬─────────────────────────┘
                 │ Fetch API
┌────────────────▼─────────────────────────┐
│   API REST (Django REST Framework)       │
│   ┌──────────────────────────────────┐   │
│   │ ViewSets / Serializers           │   │
│   ├──────────────────────────────────┤   │
│   │ Service Layer                    │   │
│   ├──────────────────────────────────┤   │
│   │ Repositories (Django ORM)        │   │
│   ├──────────────────────────────────┤   │
│   │ Models                           │   │
│   └──────────────────────────────────┘   │
└────────────────┬─────────────────────────┘
                 ▼
         PostgreSQL / SQLite
```

### Padrões de projeto aplicados

| Padrão | Onde |
|---|---|
| **Repository** | `apps/*/repositories.py` — encapsula consultas ORM |
| **Service Layer** | `apps/*/services.py` — regras de negócio |
| **Strategy** | `apps/relatorios/strategies.py` — relatórios intercambiáveis |
| **DTO** | Serializers do DRF |
| **Decorator** | `@action`, `@permission_classes` |
| **Singleton** | settings, services injetáveis |
| **Observer** | preparado via signals do Django |

## 🚀 Como executar

### 1. Pré-requisitos
- Python **3.11+**
- Git
- (opcional) PostgreSQL 13+

### 2. Clonar & instalar

```bash
git clone https://github.com/pedrobasgui/papelaria-sgc.git
cd papelaria-sgc

# Ambiente virtual
python3 -m venv .venv
source .venv/bin/activate    # Linux/Mac
# .venv\Scripts\activate     # Windows

# Dependências
pip install -r requirements.txt
```

### 3. Banco de dados & dados iniciais

```bash
python manage.py migrate
python manage.py popular_dados        # cria admin, clientes e produtos
```

> **Login padrão:** `admin` / `admin123`
> Funcionário de teste: `joao.silva` / `senha123`

### 4. Rodar o servidor

```bash
python manage.py runserver
```

Acesse:

| URL | O que tem |
|---|---|
| http://localhost:8000/ | Tela de login |
| http://localhost:8000/dashboard/ | Dashboard com KPIs e gráfico |
| http://localhost:8000/api/docs/ | Swagger UI |
| http://localhost:8000/api/schema/ | Schema OpenAPI |
| http://localhost:8000/admin/ | Django Admin |

### 5. Rodar os testes

```bash
pytest tests/ -v
```

Resultado esperado: **40 testes passando**.

##  Estrutura do projeto

```
papelaria-sgc/
├── manage.py
├── requirements.txt
├── pytest.ini
├── README.md
│
├── papelaria_sgc/         ← config Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── apps/
│   ├── core/              ← exceções, permissões, handlers
│   │   ├── exceptions.py
│   │   ├── handlers.py
│   │   ├── permissions.py
│   │   └── management/commands/popular_dados.py
│   │
│   ├── usuarios/          ← auth + JWT + perfil
│   ├── clientes/          ← CRUD + Service + Repository
│   ├── produtos/          ← CRUD + estoque
│   ├── vendas/            ← Venda + ItemVenda (transação atômica)
│   ├── relatorios/        ← Strategies de relatório
│   └── web/               ← views Django (templates)
│
├── templates/             ← HTML (Bootstrap 5 + Chart.js)
│   ├── base.html
│   ├── dashboard.html
│   ├── registration/login.html
│   ├── clientes/, produtos/, vendas/, relatorios/
│
├── static/
│   ├── css/style.css      ← identidade visual (navy + gold)
│   └── js/api.js          ← cliente JS da API com JWT
│
├── database/
│   └── script.sql         ← script PostgreSQL completo
│
├── docs/
│   ├── Entrega1_Documentacao.pdf
│   ├── Entrega2_Documentacao.pdf
│   ├── diagrama_dominio.png
│   ├── diagrama_classes.png
│   └── diagrama_banco.png
│
└── tests/                 ← pytest
    ├── conftest.py
    ├── test_auth.py
    ├── test_clientes.py
    ├── test_produtos.py
    └── test_vendas.py
```

##  API REST

Todas as rotas exigem `Authorization: Bearer <access_token>` exceto `/api/auth/login/`.

### Auth
- `POST /api/auth/login/` — `{username, password}` → `{access, refresh, usuario}`
- `POST /api/auth/refresh/` — renova access token
- `POST /api/auth/logout/` — blacklist refresh
- `GET  /api/auth/me/` — dados do usuário logado
- `POST /api/auth/trocar-senha/`
- `POST /api/auth/recuperar-senha/` *(stub p/ Entrega 3)*

### Clientes
- `GET    /api/clientes/?busca=...`
- `POST   /api/clientes/`
- `GET    /api/clientes/{id}/`
- `PUT    /api/clientes/{id}/`
- `DELETE /api/clientes/{id}/`

### Produtos
- `GET    /api/produtos/?busca=...&ativos=true`
- `GET    /api/produtos/estoque-baixo/`
- `POST   /api/produtos/` *(ADMIN)*
- `PUT    /api/produtos/{id}/` *(ADMIN)*
- `DELETE /api/produtos/{id}/` *(ADMIN)*

### Vendas
- `GET  /api/vendas/?cliente_id=&status=&data_inicio=&data_fim=`
- `GET  /api/vendas/{id}/`
- `POST /api/vendas/`  → cria venda (transação atômica, débito de estoque)
- `POST /api/vendas/{id}/cancelar/`  → devolve estoque
- `POST /api/vendas/por-periodo/`
- `GET  /api/vendas/por-cliente/{id}/`

### Relatórios *(ADMIN)*
- `POST /api/relatorios/por-periodo/`
- `GET  /api/relatorios/por-cliente/{id}/`
- `GET  /api/relatorios/anual/?ano=YYYY`
- `GET  /api/relatorios/top-produtos/?limite=N`

##  Segurança

- Senhas armazenadas com **PBKDF2-SHA256** (default Django)
- **JWT** com expiração de 60 min (access) e 7 dias (refresh)
- **CORS** configurável por ambiente
- Permissões por perfil (`IsAdmin`, `IsAdminOrFuncionario`, `IsAdminOrReadOnly`)
- Validação de CPF com dígito verificador
- Constraints no banco (CHECK em preço, estoque, status)

##  Cobertura de testes

| Módulo | Quantidade |
|---|---|
| Auth (JWT) | 5 |
| Clientes | 12 |
| Produtos | 11 |
| Vendas | 11 |
| **Total** | **40 testes** |

##  Equipe

- **Pedro Henrique Bastos Guimarães** — 22303912
- **Raphael Damião Seabra Rosano** — 22303595
