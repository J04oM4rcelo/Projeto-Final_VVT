# backend/tests/test_e2e.py
"""
Teste 3 — Teste automatizado / integração / E2E
Objetivo: exercer um fluxo COMPLETO da API, ponta a ponta, como se
fosse um usuário real:
    1) Admin faz login
    2) Admin cria uma notícia
    3) Admin desativa a mesma notícia
    4) Consulta a página pública e confere que a notícia NÃO aparece
    5) Admin cria um usuário comum
    6) Admin desativa esse usuário
    7) Tenta login do usuário desativado -> deve falhar com 403

Como o Flask test_client já mantém cookies entre requisições, podemos
usá-lo como "browser simulado".
"""

def test_fluxo_e2e_noticia_e_usuario(admin_logado):
    """Exemplo de fluxo E2E. Preencha com os passos reais quando
    me enviar a especificação detalhada."""

    c = admin_logado

    # 1. Cria uma notícia
    from io import BytesIO
    dados = {
        "titulo": "Notícia E2E",
        "data_noticia": "2026-01-01",
        "texto":  "Conteúdo da notícia E2E.",
    }
    res = c.post("/api/noticias", data=dados,
                 content_type="multipart/form-data")
    assert res.status_code in (200, 201)
    id_noticia = res.get_json()["id"]

    # 2. Desativa a notícia
    res2 = c.post(f"/api/noticias/{id_noticia}/desativar")
    assert res2.status_code == 200

    # 3. Página pública NÃO deve mostrar a notícia desativada
    res3 = c.get("/api/noticias/publicas")
    publicas = res3.get_json()
    ids = [n["id"] for n in publicas]
    assert id_noticia not in ids, "Notícia desativada NÃO deve aparecer na página pública"
