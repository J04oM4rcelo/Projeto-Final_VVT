# Sistema VV&T — Login + Gerenciamento de Usuários + CRUD de Notícias

Projeto da disciplina de **Verificação, Validação & Testes (VV&T)**.

Sistema web completo com controle de acesso (login/autenticação), gerenciamento de usuários, CRUD de notícias e 3 tipos de testes automatizados (Pytest).

---

## Tecnologias utilizadas

| Camada       | Tecnologia                          |
|--------------|-------------------------------------|
| Backend      | Python 3.11+ / Flask               |
| Frontend     | HTML5, CSS3, JavaScript puro        |
| Banco de dados | MySQL 8.0+                        |
| Testes       | Pytest                              |
| Conector MySQL | mysqlclient (Flask-MySQLdb)       |

---

## Pré-requisitos (instale antes de começar)

| Software       | Para que serve                      | Download                                    |
|----------------|--------------------------------------|---------------------------------------------|
| Python 3.11+   | Rodar o backend e os testes          | https://www.python.org/downloads/           |
| MySQL 8.0+     | Banco de dados                       | https://dev.mysql.com/downloads/installer/  |
| Git            | Controle de versão                   | https://git-scm.com/downloads               |

> **Dica Windows:** ao instalar o Python, marque a opção **"Add python.exe to PATH"**.

> **Dica MySQL:** durante a instalação, anote a senha do usuário root — você vai precisar dela.

---

## Como rodar o projeto

### 1. Clone o repositório

```bash
git clone https://github.com/J04oM4rcelo/Projeto-Final_VVeT.git
cd Projeto-Final_VVeT
```

### 2. Crie o ambiente virtual e instale as dependências

```bash
cd backend
python -m venv venv
```

**Ative o ambiente virtual:**

```bash
# Windows (CMD):
venv\Scripts\activate

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Linux / macOS:
source venv/bin/activate
```

> Confirme que apareceu `(venv)` no início da linha do terminal.

```bash
pip install -r requirements.txt
```

### 3. Configure o arquivo .env

```bash
# Windows:
copy .env.example .env

# Linux/macOS:
cp .env.example .env
```

Abra o arquivo `.env` e preencha com a senha do **seu** MySQL:

```
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=sua_senha_do_mysql_aqui
MYSQL_DB=vvt_news
MYSQL_PORT=3306
SECRET_KEY=uma-chave-secreta-qualquer
```

### 4. Crie o banco de dados automaticamente

```bash
python setup_db.py
```

Saída esperada:
```
[OK] Conectado ao MySQL
[OK] Banco 'vvt_news' criado (ou já existia)
[OK] Tabela 'usuarios' criada (ou já existia)
[OK] Tabela 'noticias' criada (ou já existia)
[OK] Admin criado:
     Email: admin@exemplo.com
     Senha: admin123
SETUP CONCLUÍDO COM SUCESSO!
```

### 5. Inicie o servidor

```bash
python app.py
```

O Flask serve **API + frontend** na mesma porta:

```
* Running on http://127.0.0.1:5000
```

### 6. Acesse no navegador

| Página                              | URL                                    |
|--------------------------------------|----------------------------------------|
| Página pública (notícias)            | http://localhost:5000                  |
| Tela de login                        | http://localhost:5000/login.html       |
| Área administrativa                  | http://localhost:5000/admin.html       |

### 7. Credenciais de acesso padrão

| Campo | Valor              |
|-------|---------------------|
| Email | admin@exemplo.com  |
| Senha | admin123           |

---

## Como rodar os testes

Os testes usam **Pytest** e estão na pasta `backend/tests/`.

```bash
# Certifique-se de estar na pasta backend com o venv ativado:
cd backend
pytest -v
```

Saída esperada:
```
tests/test_bloqueio.py::test_rota_protegida_sem_autenticacao PASSED
tests/test_bloqueio.py::test_somente_admin_lista_usuarios PASSED
tests/test_bloqueio.py::test_usuario_comum_nao_acessa_usuarios PASSED
tests/test_bloqueio.py::test_usuario_desativado_nao_consegue_login PASSED
tests/test_e2e.py::test_fluxo_e2e_noticia_e_usuario PASSED
tests/test_login.py::test_login_campos_vazios PASSED
tests/test_login.py::test_login_usuario_inexistente PASSED
tests/test_login.py::test_login_senha_errada PASSED
tests/test_login.py::test_login_sucesso_retorna_usuario PASSED
tests/test_login.py::test_logout_limpa_sessao PASSED

10 passed
```

### Descrição dos testes

| Arquivo              | Teste                                          | O que valida                                                |
|----------------------|------------------------------------------------|--------------------------------------------------------------|
| test_login.py        | test_login_campos_vazios                       | Login com campos vazios retorna 400                          |
| test_login.py        | test_login_usuario_inexistente                 | Login com email inexistente retorna 401                      |
| test_login.py        | test_login_senha_errada                        | Login com senha errada retorna 401                           |
| test_login.py        | test_login_sucesso_retorna_usuario             | Login correto retorna 200 + dados do usuário                 |
| test_login.py        | test_logout_limpa_sessao                       | Após logout, /api/me retorna 401                             |
| test_bloqueio.py     | test_rota_protegida_sem_autenticacao           | Rotas protegidas retornam 401 sem login                      |
| test_bloqueio.py     | test_somente_admin_lista_usuarios              | Admin logado acessa /api/usuarios (200)                      |
| test_bloqueio.py     | test_usuario_comum_nao_acessa_usuarios         | Usuário comum recebe 403 em /api/usuarios                    |
| test_bloqueio.py     | test_usuario_desativado_nao_consegue_login     | Usuário desativado recebe 403 no login                       |
| test_e2e.py          | test_fluxo_e2e_noticia_e_usuario               | Fluxo completo: criar notícia, desativar, verificar pública  |

---

## Regras de negócio importantes

- **Senhas** são armazenadas em hash (nunca em texto puro)
- **Notícias e usuários** nunca são excluídos — apenas desativados (soft delete)
- **Usuário comum** só pode editar/desativar notícias que **ele próprio criou**
- **Admin** pode editar/desativar qualquer notícia e gerenciar todos os usuários
- **Usuário desativado** não consegue fazer login

---

## Estrutura do projeto

```
Projeto-Final_VVeT/
├── backend/
│   ├── app.py               # API Flask + serve o frontend
│   ├── models.py            # Funções de acesso ao banco de dados
│   ├── setup_db.py          # Cria banco + tabelas + admin automaticamente
│   ├── requirements.txt     # Dependências Python
│   ├── .env.example         # Modelo de configuração (vai pro GitHub)
│   ├── frontend/            # HTML / CSS / JS (servido pelo Flask)
│   │   ├── index.html       # Página pública de notícias
│   │   ├── login.html       # Tela de login
│   │   ├── admin.html       # Área administrativa
│   │   ├── css/style.css    # Estilos
│   │   └── js/app.js        # Lógica do frontend
│   ├── uploads/             # Imagens de notícias (não versionado)
│   └── tests/
│       ├── conftest.py      # Configuração do Pytest (fixtures)
│       ├── test_login.py    # Teste 1: autenticação
│       ├── test_bloqueio.py # Teste 2: bloqueio de acesso
│       └── test_e2e.py      # Teste 3: fluxo E2E
├── database/
│   └── schema.sql           # Estrutura das tabelas (referência)
├── .gitignore               # Arquivos ignorados pelo Git
└── README.md                # Este arquivo
```
