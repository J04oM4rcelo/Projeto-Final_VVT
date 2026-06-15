import MySQLdb.cursors
from flask import g
from werkzeug.security import generate_password_hash

# ------- HELPERS DE CONEXÃO -------
def get_db():
    """Retorna uma conexão MySQL existente ou cria uma nova (por request)."""
    from app import mysql  # import atrasado para evitar import circular
    if "db" not in g:
        g.db = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    return g.db

def commit():
    from app import mysql
    mysql.connection.commit()


# ------- USUÁRIOS -------
def buscar_usuario_por_email(email: str):
    cur = get_db()
    cur.execute(
        "SELECT id, nome, email, senha, tipo, ativo FROM usuarios WHERE email = %s",
        (email,),
    )
    return cur.fetchone()


def listar_usuarios():
    cur = get_db()
    cur.execute(
        "SELECT id, nome, email, tipo, ativo, criado_em, editado_em "
        "FROM usuarios ORDER BY ativo DESC, nome ASC"
    )
    return cur.fetchall()


def criar_usuario(nome, email, senha_plana, tipo):
    cur = get_db()
    cur.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (%s, %s, %s, %s)",
        (nome, email, generate_password_hash(senha_plana), tipo),
    )
    commit()
    return cur.lastrowid


def atualizar_usuario(id_usuario, nome, email, tipo, senha_plana=None):
    cur = get_db()
    if senha_plana:
        cur.execute(
            "UPDATE usuarios SET nome=%s, email=%s, tipo=%s, senha=%s WHERE id=%s",
            (nome, email, tipo, generate_password_hash(senha_plana), id_usuario),
        )
    else:
        cur.execute(
            "UPDATE usuarios SET nome=%s, email=%s, tipo=%s WHERE id=%s",
            (nome, email, tipo, id_usuario),
        )
    commit()


def desativar_usuario(id_usuario: int):
    """Soft delete - apenas marca ativo=0."""
    cur = get_db()
    cur.execute("UPDATE usuarios SET ativo=0 WHERE id=%s", (id_usuario,))
    commit()


# ------- NOTÍCIAS -------
def listar_noticias(apenas_ativas: bool = False):
    cur = get_db()
    sql = (
        "SELECT n.id, n.titulo, n.data_noticia, n.texto, n.imagem, n.ativo, "
        "       u.nome AS autor_nome "
        "FROM noticias n LEFT JOIN usuarios u ON u.id = n.autor_id "
    )
    if apenas_ativas:
        sql += "WHERE n.ativo = 1 "
    sql += "ORDER BY n.data_noticia DESC, n.id DESC"
    cur.execute(sql)
    return cur.fetchall()


def buscar_noticia(id_noticia: int):
    cur = get_db()
    cur.execute(
        "SELECT id, titulo, data_noticia, texto, imagem, ativo, autor_id "
        "FROM noticias WHERE id=%s",
        (id_noticia,),
    )
    return cur.fetchone()


def criar_noticia(titulo, data_noticia, texto, imagem, autor_id):
    cur = get_db()
    cur.execute(
        "INSERT INTO noticias (titulo, data_noticia, texto, imagem, autor_id) "
        "VALUES (%s, %s, %s, %s, %s)",
        (titulo, data_noticia, texto, imagem, autor_id),
    )
    commit()
    return cur.lastrowid


def atualizar_noticia(id_noticia, titulo, data_noticia, texto, imagem=None):
    cur = get_db()
    if imagem is not None:
        cur.execute(
            "UPDATE noticias SET titulo=%s, data_noticia=%s, texto=%s, imagem=%s WHERE id=%s",
            (titulo, data_noticia, texto, imagem, id_noticia),
        )
    else:
        cur.execute(
            "UPDATE noticias SET titulo=%s, data_noticia=%s, texto=%s WHERE id=%s",
            (titulo, data_noticia, texto, id_noticia),
        )
    commit()


def desativar_noticia(id_noticia: int):
    """Soft delete: marca ativo=0. NUNCA apaga do banco."""
    cur = get_db()
    cur.execute("UPDATE noticias SET ativo=0 WHERE id=%s", (id_noticia,))
    commit()
