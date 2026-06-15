# backend/tests/conftest.py
import pytest
from app import app as flask_app

@pytest.fixture
def app():
    """Fornece a aplicação Flask em modo TESTING."""
    flask_app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
    })
    yield flask_app

@pytest.fixture
def client(app):
    """Cliente de teste que faz requisições HTTP simuladas."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """CLI runner (caso queira testar comandos cli)."""
    return app.test_cli_runner()

# fixture auxiliar: um usuário admin já conectado
@pytest.fixture
def admin_logado(client):
    """Retorna um cliente já autenticado como admin.
    Requer que admin@exemplo.com / admin123 exista no banco de dados (banco de testes).
    """
    client.post("/api/login", json={
        "email": "admin@exemplo.com",
        "senha": "admin123",
    })
    return client
