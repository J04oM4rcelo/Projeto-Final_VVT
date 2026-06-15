"""
setup_db.py — Configuração automática do banco de dados
========================================================
Rode este script UMA VEZ após clonar o repositório.
Ele cria o banco, as tabelas e o usuário admin inicial.

Uso:
    cd backend
    python setup_db.py

Pré-requisitos:
    - MySQL rodando
    - Arquivo .env preenchido (copie de .env.example)
    - pip install mysqlclient python-dotenv werkzeug
"""

import os
import sys
from pathlib import Path

# Garante que o .env seja encontrado mesmo rodando de outra pasta
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")

# =============================================
# mysqlclient fornece o módulo "MySQLdb"
# (é o que Flask-MySQLdb usa por baixo)
# =============================================
import MySQLdb
from werkzeug.security import generate_password_hash


def main():
    print("=" * 55)
    print("  SETUP DO BANCO DE DADOS — Projeto VV&T")
    print("=" * 55)
    print()

    # --- 1. Lê configurações do .env ---
    host = os.getenv("MYSQL_HOST", "localhost")
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")
    db_name = os.getenv("MYSQL_DB", "vvt_news")
    port = int(os.getenv("MYSQL_PORT", "3306"))

    if not password:
        print("[ERRO] MYSQL_PASSWORD está vazio no .env!")
        print("       Copie .env.example para .env e preencha.")
        sys.exit(1)

    print(f"  Host:    {host}:{port}")
    print(f"  User:    {user}")
    print(f"  Banco:   {db_name}")
    print()

    # --- 2. Conecta no MySQL (sem banco específico) ---
    try:
        conn = MySQLdb.connect(
            host=host,
            user=user,
            passwd=password,
            port=port,
        )
        cur = conn.cursor()
        print("[OK] Conectado ao MySQL")
    except MySQLdb.Error as e:
        print(f"[ERRO] Não conseguiu conectar ao MySQL: {e}")
        print()
        print("Verifique se:")
        print("  - O MySQL está rodando")
        print("  - O usuário e senha no .env estão corretos")
        print("  - A porta está correta")
        sys.exit(1)

    # --- 3. Cria o banco ---
    cur.execute(
        f"CREATE DATABASE IF NOT EXISTS {db_name} "
        f"DEFAULT CHARACTER SET utf8mb4 "
        f"DEFAULT COLLATE utf8mb4_unicode_ci"
    )
    conn.commit()
    print(f"[OK] Banco '{db_name}' criado (ou já existia)")

    # --- 4. Usa o banco e cria as tabelas ---
    cur.execute(f"USE {db_name}")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            nome       VARCHAR(100) NOT NULL,
            email      VARCHAR(150) NOT NULL UNIQUE,
            senha      VARCHAR(255) NOT NULL,
            tipo       ENUM('admin', 'comum') NOT NULL DEFAULT 'comum',
            ativo      TINYINT(1) NOT NULL DEFAULT 1,
            criado_em  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            editado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                                  ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_email (email),
            INDEX idx_ativo (ativo)
        ) ENGINE=InnoDB
    """)
    print("[OK] Tabela 'usuarios' criada (ou já existia)")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS noticias (
            id         INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            titulo     VARCHAR(200) NOT NULL,
            data_noticia DATE NOT NULL,
            texto      TEXT NOT NULL,
            imagem     VARCHAR(255) NULL,
            autor_id   INT UNSIGNED NULL,
            ativo      TINYINT(1) NOT NULL DEFAULT 1,
            criado_em  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            editado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                                  ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_data_noticia (data_noticia),
            INDEX idx_ativo (ativo),
            CONSTRAINT fk_noticias_autor FOREIGN KEY (autor_id)
                REFERENCES usuarios(id) ON DELETE SET NULL
        ) ENGINE=InnoDB
    """)
    print("[OK] Tabela 'noticias' criada (ou já existia)")
    conn.commit()

    # --- 5. Cria o admin inicial (se não existir) ---
    cur.execute(
        "SELECT id FROM usuarios WHERE email = %s",
        ("admin@exemplo.com",),
    )
    admin_existe = cur.fetchone()

    if admin_existe:
        print("[OK] Admin 'admin@exemplo.com' já existe (pulando)")
    else:
        senha_hash = generate_password_hash("admin123")
        cur.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo, ativo) "
            "VALUES (%s, %s, %s, %s, %s)",
            ("Administrador", "admin@exemplo.com", senha_hash, "admin", 1),
        )
        conn.commit()
        print("[OK] Admin criado:")
        print("     Email: admin@exemplo.com")
        print("     Senha: admin123")
        print("     (hash gerado automaticamente)")

    # --- 6. Resumo ---
    cur.execute("SELECT COUNT(*) FROM usuarios")
    total_users = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM noticias")
    total_news = cur.fetchone()[0]

    cur.close()
    conn.close()

    print()
    print("=" * 55)
    print("  SETUP CONCLUÍDO COM SUCESSO!")
    print("=" * 55)
    print(f"  Usuários no banco: {total_users}")
    print(f"  Notícias no banco: {total_news}")
    print()
    print("  Próximo passo: python app.py")
    print("=" * 55)


if __name__ == "__main__":
    main()
