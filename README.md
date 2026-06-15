# Sistema VV&T — Login + Gerenciamento de Usuários + CRUD de Notícias

Projeto da disciplina de **Verificação, Validação & Testes**.

## Tecnologias
- **Backend:** Python 3.11+ / Flask
- **Frontend:** HTML / CSS / JavaScript
- **Banco de dados:** MySQL 8+
- **Testes:** Pytest

## Pré-requisitos
- Python 3.11 ou superior
- MySQL 8.0 ou superior (rodando)
- Git

## Como rodar

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/trabalho-vvt.git
cd trabalho-vvt
```

### 2. Configure o ambiente Python
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure o banco de dados
```bash
# Copie o modelo de configuração:
copy .env.example .env   # Windows
cp .env.example .env     # Linux/macOS

# Edite o .env e preencha MYSQL_PASSWORD com a senha do seu MySQL

# Rode o setup automático:
python setup_db.py
```

### 4. Inicie o backend
```bash
python app.py
# Rodando em http://localhost:5000
```

### 5. Inicie o frontend (outro terminal)
```bash
cd frontend
python -m http.server 8080
# Acesse http://localhost:8080
```

### 6. Credenciais de acesso
| Campo | Valor |
|-------|-------|
| Email | admin@exemplo.com |
| Senha | admin123 |

## Como rodar os testes
```bash
cd backend
pytest -v
```

## Estrutura do projeto
```
trabalho-vvt/
├── backend/
│   ├── app.py               # API Flask
│   ├── models.py            # Acesso ao banco de dados
│   ├── setup_db.py          # Script de configuração do banco
│   ├── requirements.txt     # Dependências Python
│   ├── .env.example         # Modelo de configuração
│   └── tests/
│       ├── conftest.py      # Configuração do Pytest
│       ├── test_login.py    # Teste 1: autenticação
│       ├── test_bloqueio.py # Teste 2: bloqueio de acesso
│       └── test_e2e.py      # Teste 3: fluxo E2E
├── frontend/
│   ├── index.html           # Página pública
│   ├── login.html           # Tela de login
│   ├── admin.html           # Área administrativa
│   ├── css/style.css
│   └── js/app.js
├── database/
│   └── schema.sql           # Estrutura das tabelas (referência)
├── .gitignore
└── README.md
```
