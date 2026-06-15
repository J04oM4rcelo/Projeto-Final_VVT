# backend/tests/test_bloqueio.py
"""
Teste 2 — Bloqueio de acesso
Objetivo: garantir que rotas protegidas sejam realmente inacessíveis
para quem não tem permissão (não autenticado / não admin) e que
usuários desativados não consigam autenticar-se.

Cenários típicos:
  - GET /api/me   sem login          -> 401
  - GET /api/usuarios como comum     -> 403
  - GET /api/usuarios como admin     -> 200
  - POST /api/login com usuário desativado -> 403
  - GET /api/noticias (admin) sem login     -> 401
"""
import uuid


def test_rota_protegida_sem_autenticacao(client):
    """Qualquer rota que usa @login_required deve retornar 401 sem sessão."""
    res = client.get("/api/me")
    assert res.status_code == 401

    res2 = client.get("/api/noticias")
    assert res2.status_code == 401


def test_somente_admin_lista_usuarios(admin_logado):
    """Admin logado deve acessar /api/usuarios e receber 200."""
    res = admin_logado.get("/api/usuarios")
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)


def test_usuario_comum_nao_acessa_usuarios(client):
    """Usuário comum autenticado NÃO pode acessar /api/usuarios -> 403.

    Fluxo completo:
      1) Loga como admin
      2) Cria um usuário do tipo "comum"
      3) Faz logout do admin
      4) Loga como o usuário comum
      5) Tenta acessar GET /api/usuarios -> deve receber 403
    """
    # --- 1. Login como admin ---
    res_admin = client.post("/api/login", json={
        "email": "admin@exemplo.com",
        "senha": "admin123",
    })
    assert res_admin.status_code == 200, "Admin deveria logar com sucesso"

    # --- 2. Cria usuário comum (email único para não conflitar) ---
    email_unico = f"comum_{uuid.uuid4().hex[:8]}@exemplo.com"
    res_criar = client.post("/api/usuarios", json={
        "nome": "Usuário Comum Teste",
        "email": email_unico,
        "senha": "comum123",
        "tipo": "comum",
    })
    assert res_criar.status_code == 201, "Admin deveria criar o usuário comum"

    # --- 3. Logout do admin ---
    client.post("/api/logout")

    # --- 4. Login como o usuário comum ---
    res_comum = client.post("/api/login", json={
        "email": email_unico,
        "senha": "comum123",
    })
    assert res_comum.status_code == 200, "Usuário comum deveria logar"

    # --- 5. Tenta acessar /api/usuarios (rota exclusiva de admin) ---
    res_bloqueio = client.get("/api/usuarios")
    assert res_bloqueio.status_code == 403, (
        "Usuário comum NÃO deve acessar /api/usuarios. "
        f"Recebeu status {res_bloqueio.status_code} ao invés de 403"
    )


def test_usuario_desativado_nao_consegue_login(client):
    """Se um admin desativa um usuário, seu próximo login deve falhar com 403.

    Fluxo completo:
      1) Loga como admin
      2) Cria um usuário comum
      3) Desativa esse usuário
      4) Faz logout do admin
      5) Tenta logar com o usuário desativado -> deve receber 403
    """
    # --- 1. Login como admin ---
    client.post("/api/login", json={
        "email": "admin@exemplo.com",
        "senha": "admin123",
    })

    # --- 2. Cria usuário comum ---
    email_unico = f"desativar_{uuid.uuid4().hex[:8]}@exemplo.com"
    res_criar = client.post("/api/usuarios", json={
        "nome": "Será Desativado",
        "email": email_unico,
        "senha": "senha123",
        "tipo": "comum",
    })
    assert res_criar.status_code == 201
    uid = res_criar.get_json()["id"]

    # --- 3. Desativa o usuário ---
    res_des = client.post(f"/api/usuarios/{uid}/desativar")
    assert res_des.status_code == 200, "Admin deveria conseguir desativar o usuário"

    # --- 4. Logout do admin ---
    client.post("/api/logout")

    # --- 5. Tenta logar com o usuário desativado ---
    res_login = client.post("/api/login", json={
        "email": email_unico,
        "senha": "senha123",
    })
    assert res_login.status_code == 403, (
        "Usuário desativado deveria receber 403, "
        f"mas recebeu {res_login.status_code}"
    )
