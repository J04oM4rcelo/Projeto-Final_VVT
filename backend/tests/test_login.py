# backend/tests/test_login.py
"""
Teste 1 — Autenticação (login)
Objetivo: validar o comportamento da rota POST /api/login em várias
situações: credenciais corretas, senha errada, usuário inexistente,
campos vazios, efeito colateral de sessão e logout.
"""
import pytest

# -------------------------------------------------------------
# TODO (aluno): aqui é onde você descreverá o SEU cenário de
# teste de login. Esta é apenas a ESTRUTURA base.
# Quando me enviar a especificação do teste, eu preencho o
# conteúdo dos casos.
# -------------------------------------------------------------


def test_login_campos_vazios(client):
    """Não deve permitir login sem informar email/senha."""
    res = client.post("/api/login", json={"email": "", "senha": ""})
    assert res.status_code == 400, "Deveria retornar 400 para campos vazios"
    assert "erro" in res.get_json()


def test_login_usuario_inexistente(client):
    """Deve rejeitar login com e-mail que não existe no banco."""
    res = client.post("/api/login", json={
        "email": "ninguem@exemplo.com",
        "senha": "qualquercoisa",
    })
    assert res.status_code == 401, "Deveria retornar 401 para usuário inexistente"


def test_login_senha_errada(client):
    """Deve rejeitar login de usuário existente com senha incorreta."""
    # pré-condição: admin@exemplo.com existe (ver conftest)
    res = client.post("/api/login", json={
        "email": "admin@exemplo.com",
        "senha": "senha-errada",
    })
    assert res.status_code == 401


def test_login_sucesso_retorna_usuario(client):
    """Com credenciais corretas, deve retornar dados do usuário e criar sessão."""
    res = client.post("/api/login", json={
        "email": "admin@exemplo.com",
        "senha": "admin123",
    })
    assert res.status_code == 200
    dados = res.get_json()
    assert dados["email"] == "admin@exemplo.com"
    assert "tipo" in dados


def test_logout_limpa_sessao(client):
    """Após logout, GET /api/me deve retornar 401."""
    client.post("/api/login", json={"email": "admin@exemplo.com", "senha": "admin123"})
    res1 = client.get("/api/me")
    assert res1.status_code == 200, "Antes do logout, /me deve funcionar"

    client.post("/api/logout")
    res2 = client.get("/api/me")
    assert res2.status_code == 401, "Após logout, /me deve retornar 401"
