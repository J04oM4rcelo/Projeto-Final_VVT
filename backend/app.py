import os
import sys
from datetime import datetime
from functools import wraps
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
from flask import Flask, jsonify, request, session, send_from_directory
from flask_mysqldb import MySQL
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

load_dotenv(BASE_DIR / ".env")

UPLOAD_FOLDER = BASE_DIR / "uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)
FRONTEND_FOLDER = BASE_DIR / "frontend"
ALLOWED_EXT = {"png", "jpg", "jpeg", "gif", "webp"}

app = Flask(__name__)
app.config["MYSQL_HOST"] = os.getenv("MYSQL_HOST")
app.config["MYSQL_USER"] = os.getenv("MYSQL_USER")
app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD")
app.config["MYSQL_DB"] = os.getenv("MYSQL_DB")
app.config["MYSQL_PORT"] = int(os.getenv("MYSQL_PORT", "3306"))
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "mudar-em-producao")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

mysql = MySQL(app)


# ========== DECORATORS ==========
def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "usuario_id" not in session:
            return jsonify({"erro": "Autenticação necessária"}), 401
        return fn(*args, **kwargs)
    return wrapper


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "usuario_id" not in session:
            return jsonify({"erro": "Autenticação necessária"}), 401
        if session.get("usuario_tipo") != "admin":
            return jsonify({"erro": "Apenas administradores podem acessar"}), 403
        return fn(*args, **kwargs)
    return wrapper


# ========== AUTENTICAÇÃO ==========
@app.post("/api/login")
def login():
    import models
    body = request.get_json(force=True, silent=True) or {}
    email = (body.get("email") or "").strip().lower()
    senha = body.get("senha") or ""
    if not email or not senha:
        return jsonify({"erro": "Informe email e senha"}), 400
    usuario = models.buscar_usuario_por_email(email)
    if not usuario:
        return jsonify({"erro": "Credenciais inválidas"}), 401
    if not usuario["ativo"]:
        return jsonify({"erro": "Usuário desativado"}), 403
    if not check_password_hash(usuario["senha"], senha):
        return jsonify({"erro": "Credenciais inválidas"}), 401
    session["usuario_id"] = usuario["id"]
    session["usuario_nome"] = usuario["nome"]
    session["usuario_email"] = usuario["email"]
    session["usuario_tipo"] = usuario["tipo"]
    return jsonify({
        "id": usuario["id"], "nome": usuario["nome"],
        "email": usuario["email"], "tipo": usuario["tipo"],
    })


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify({"ok": True})


@app.get("/api/me")
@login_required
def me():
    return jsonify({
        "id": session["usuario_id"], "nome": session["usuario_nome"],
        "email": session["usuario_email"], "tipo": session["usuario_tipo"],
    })


# ========== USUÁRIOS (admin) ==========
@app.get("/api/usuarios")
@admin_required
def listar_usuarios():
    import models
    return jsonify(models.listar_usuarios())


@app.post("/api/usuarios")
@admin_required
def criar_usuario():
    import models
    b = request.get_json(force=True, silent=True) or {}
    nome = (b.get("nome") or "").strip()
    email = (b.get("email") or "").strip().lower()
    senha = b.get("senha") or ""
    tipo = b.get("tipo") or "comum"
    if not nome or not email or not senha or tipo not in ("admin", "comum"):
        return jsonify({"erro": "Dados inválidos"}), 400
    if len(senha) < 6:
        return jsonify({"erro": "Senha deve ter pelo menos 6 caracteres"}), 400
    if models.buscar_usuario_por_email(email):
        return jsonify({"erro": "E-mail já cadastrado"}), 409
    uid = models.criar_usuario(nome, email, senha, tipo)
    return jsonify({"id": uid, "nome": nome, "email": email, "tipo": tipo}), 201


@app.put("/api/usuarios/<int:uid>")
@admin_required
def atualizar_usuario(uid):
    import models
    b = request.get_json(force=True, silent=True) or {}
    nome = (b.get("nome") or "").strip()
    email = (b.get("email") or "").strip().lower()
    tipo = b.get("tipo") or "comum"
    senha = b.get("senha")
    if not nome or not email or tipo not in ("admin", "comum"):
        return jsonify({"erro": "Dados inválidos"}), 400
    if senha is not None and len(senha) < 6:
        return jsonify({"erro": "Senha deve ter pelo menos 6 caracteres"}), 400
    models.atualizar_usuario(uid, nome, email, tipo, senha)
    return jsonify({"ok": True})


@app.post("/api/usuarios/<int:uid>/desativar")
@admin_required
def desativar_usuario(uid):
    import models
    if uid == session["usuario_id"]:
        return jsonify({"erro": "Você não pode desativar a si mesmo"}), 400
    models.desativar_usuario(uid)
    return jsonify({"ok": True})


# ========== NOTÍCIAS ==========
@app.get("/api/noticias/publicas")
def noticias_publicas():
    import models
    return jsonify(models.listar_noticias(apenas_ativas=True))


@app.get("/api/noticias")
@login_required
def listar_noticias_admin():
    import models
    return jsonify(models.listar_noticias(apenas_ativas=False))


@app.get("/api/noticias/<int:nid>")
@login_required
def buscar_noticia(nid):
    import models
    n = models.buscar_noticia(nid)
    if not n:
        return jsonify({"erro": "Notícia não encontrada"}), 404
    return jsonify(n)


@app.post("/api/noticias")
@login_required
def criar_noticia():
    import models
    titulo = (request.form.get("titulo") or "").strip()
    data_noticia = request.form.get("data_noticia") or ""
    texto = (request.form.get("texto") or "").strip()
    if not titulo or not data_noticia or not texto:
        return jsonify({"erro": "Preencha título, data e texto"}), 400
    try:
        datetime.strptime(data_noticia, "%Y-%m-%d")
    except ValueError:
        return jsonify({"erro": "Data inválida (use AAAA-MM-DD)"}), 400
    nome_arquivo = None
    arquivo = request.files.get("imagem")
    if arquivo and arquivo.filename:
        ext = Path(secure_filename(arquivo.filename)).suffix.lower().lstrip(".")
        if ext not in ALLOWED_EXT:
            return jsonify({"erro": "Formato de imagem não permitido"}), 400
        nome_arquivo = "noticia_" + datetime.utcnow().strftime("%Y%m%d%H%M%S") + "." + ext
        arquivo.save(UPLOAD_FOLDER / nome_arquivo)
    nid = models.criar_noticia(titulo, data_noticia, texto, nome_arquivo,
                                session["usuario_id"])
    return jsonify({"id": nid, "titulo": titulo, "imagem": nome_arquivo}), 201


@app.put("/api/noticias/<int:nid>")
@login_required
def atualizar_noticia(nid):
    import models
    # --- Verifica se o usuário pode editar esta notícia ---
    noticia = models.buscar_noticia(nid)
    if not noticia:
        return jsonify({"erro": "Notícia não encontrada"}), 404
    # Usuário comum só pode editar suas PRÓPRIAS notícias
    if session.get("usuario_tipo") != "admin" and noticia["autor_id"] != session["usuario_id"]:
        return jsonify({"erro": "Você só pode editar notícias que você criou"}), 403

    titulo = (request.form.get("titulo") or "").strip()
    data_noticia = request.form.get("data_noticia") or ""
    texto = (request.form.get("texto") or "").strip()
    if not titulo or not data_noticia or not texto:
        return jsonify({"erro": "Preencha título, data e texto"}), 400
    try:
        datetime.strptime(data_noticia, "%Y-%m-%d")
    except ValueError:
        return jsonify({"erro": "Data inválida"}), 400
    nome_arquivo = None
    arquivo = request.files.get("imagem")
    if arquivo and arquivo.filename:
        ext = Path(secure_filename(arquivo.filename)).suffix.lower().lstrip(".")
        if ext not in ALLOWED_EXT:
            return jsonify({"erro": "Formato de imagem não permitido"}), 400
        nome_arquivo = "noticia_" + str(nid) + "_" + datetime.utcnow().strftime("%Y%m%d%H%M%S") + "." + ext
        arquivo.save(UPLOAD_FOLDER / nome_arquivo)
    models.atualizar_noticia(nid, titulo, data_noticia, texto, nome_arquivo)
    return jsonify({"ok": True})


@app.post("/api/noticias/<int:nid>/desativar")
@login_required
def desativar_noticia(nid):
    import models
    # --- Verifica se o usuário pode desativar esta notícia ---
    noticia = models.buscar_noticia(nid)
    if not noticia:
        return jsonify({"erro": "Notícia não encontrada"}), 404
    # Usuário comum só pode desativar suas PRÓPRIAS notícias
    if session.get("usuario_tipo") != "admin" and noticia["autor_id"] != session["usuario_id"]:
        return jsonify({"erro": "Você só pode desativar notícias que você criou"}), 403

    models.desativar_noticia(nid)
    return jsonify({"ok": True})


# ========== UPLOADS ==========
@app.get("/uploads/<nome>")
def serve_upload(nome):
    return send_from_directory(UPLOAD_FOLDER, nome)


# ========== FRONTEND (HTML/CSS/JS) ==========
@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND_FOLDER, "index.html")


@app.route("/<path:filename>")
def serve_frontend(filename):
    file_path = FRONTEND_FOLDER / filename
    if file_path.is_file():
        return send_from_directory(FRONTEND_FOLDER, filename)
    return send_from_directory(FRONTEND_FOLDER, "index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
