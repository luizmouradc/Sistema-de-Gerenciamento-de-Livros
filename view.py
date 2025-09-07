# -*- coding: utf-8 -*-
"""
view.py — Camada de dados (SQLite) compatível com o banco 'dados.db' que você já criou.

- Usa as tabelas existentes:
  livros(id, titulo, autor, editora, ano_publicacao, isbn)
  usuarios(id, nome, sobrenome, endereco, email, telefone)
  emprestimos(id, id_livro, id_usuario, data_emprestimo, data_devolucao)

- Na importação, roda migrações para adicionar colunas que o app usa:
  livros:     quantidade INTEGER DEFAULT 1, disponivel INTEGER DEFAULT 1
  emprestimos: data_prevista TEXT, status TEXT DEFAULT 'open'

- Expõe as funções no formato esperado pelo app (tuplas na ordem certa).

Assinaturas:
USUÁRIOS
- insert_user(first_name, last_name, address, email, phone) -> None
- list_users() -> list[tuple]  (id, first_name, last_name, address, email, phone, created_at)
- update_user(user_id, first_name, last_name, address, email, phone) -> None
- delete_user(user_id) -> None

LIVROS
- insert_book(title, author, publisher, year, isbn, quantity) -> None
- list_books() -> list[tuple]  (id, title, author, publisher, year, isbn, quantity, available, created_at)
- update_book(book_id, title, author, publisher, year, isbn, quantity) -> None
- delete_book(book_id) -> None

EMPRÉSTIMOS
- insert_loan(user_id, book_id, loan_date, return_date) -> None
- list_loans(open_only=False) -> list[tuple]
  (id, user_id, user_name, book_id, book_title, loan_date, expected_date, return_date, status)
- close_loan(loan_id, return_date) -> None
"""

from __future__ import annotations
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from datetime import date, datetime, timedelta
from typing import Iterable, List, Dict, Any, Optional

DB_PATH = Path(__file__).with_name("dados.db")

# =========================
# Infra básica do SQLite
# =========================
@contextmanager
def _conn():
    con = sqlite3.connect(DB_PATH)
    try:
        con.row_factory = sqlite3.Row
        # Importante no SQLite para chaves estrangeiras (se usar futuramente com ON DELETE CASCADE):
        con.execute("PRAGMA foreign_keys = ON;")
        yield con
        con.commit()
    finally:
        con.close()

def _colunas_da_tabela(con: sqlite3.Connection, tabela: str) -> List[str]:
    cols = con.execute(f"PRAGMA table_info({tabela});").fetchall()
    return [c["name"] for c in cols]

def _add_coluna_se_nao_existir(con: sqlite3.Connection, tabela: str, coluna: str, ddl: str):
    # ddl = tipo + default, ex.: "INTEGER DEFAULT 1"
    cols = _colunas_da_tabela(con, tabela)
    if coluna not in cols:
        sql = f"ALTER TABLE {tabela} ADD COLUMN {coluna} {ddl};"
        con.execute(sql)

def _init_and_migrate():
    # Garante tabelas base (caso rode esse arquivo sem ter criado as tabelas)
    with _conn() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS livros (
                id INTEGER PRIMARY KEY,
                titulo TEXT,
                autor TEXT,
                editora TEXT,
                ano_publicacao INTEGER,
                isbn TEXT
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY,
                nome TEXT,
                sobrenome TEXT,
                endereco TEXT,
                email TEXT,
                telefone TEXT
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS emprestimos (
                id INTEGER PRIMARY KEY,
                id_livro INTEGER,
                id_usuario INTEGER,
                data_emprestimo TEXT,
                data_devolucao TEXT,
                FOREIGN KEY(id_livro) REFERENCES livros(id),
                FOREIGN KEY(id_usuario) REFERENCES usuarios(id)
            )
        """)

        # Migrações necessárias pro app
        # livros: quantidade, disponivel
        _add_coluna_se_nao_existir(con, "livros", "quantidade", "INTEGER DEFAULT 1")
        _add_coluna_se_nao_existir(con, "livros", "disponivel", "INTEGER DEFAULT 1")

        # emprestimos: data_prevista, status
        _add_coluna_se_nao_existir(con, "emprestimos", "data_prevista", "TEXT")
        _add_coluna_se_nao_existir(con, "emprestimos", "status", "TEXT DEFAULT 'open'")

_init_and_migrate()

# =========================
# Helpers
# =========================
def _today_str() -> str:
    return date.today().isoformat()

def _expected_from(loan_date: str, days: int = 7) -> str:
    try:
        d = datetime.strptime(loan_date, "%Y-%m-%d").date()
    except Exception:
        d = date.today()
    return (d + timedelta(days=days)).isoformat()

# =========================
# USUÁRIOS
# =========================
def insert_user(first_name: str, last_name: str, address: str, email: str, phone: str) -> None:
    with _conn() as con:
        con.execute("""
            INSERT INTO usuarios (nome, sobrenome, endereco, email, telefone)
            VALUES (?, ?, ?, ?, ?)
        """, (first_name, last_name, address, email, phone))

def list_users() -> List[tuple]:
    with _conn() as con:
        rows = con.execute("""
            SELECT id, nome, sobrenome, endereco, email, telefone
            FROM usuarios
            ORDER BY id DESC
        """).fetchall()
        # Tuplas na ordem esperada pelo app:
        # (id, first_name, last_name, address, email, phone, created_at)
        return [(r["id"], r["nome"], r["sobrenome"], r["endereco"], r["email"], r["telefone"], None) for r in rows]

def update_user(user_id: int, first_name: str, last_name: str, address: str, email: str, phone: str) -> None:
    with _conn() as con:
        con.execute("""
            UPDATE usuarios
               SET nome=?, sobrenome=?, endereco=?, email=?, telefone=?
             WHERE id=?
        """, (first_name, last_name, address, email, phone, user_id))

def delete_user(user_id: int) -> None:
    with _conn() as con:
        # se houver empréstimo em aberto, bloqueia
        aberto = con.execute(
            "SELECT 1 FROM emprestimos WHERE id_usuario=? AND (status IS NULL OR status!='closed') LIMIT 1",
            (user_id,)
        ).fetchone()
        if aberto:
            raise ValueError("Não é possível excluir: o usuário possui empréstimo em aberto.")

        # apaga histórico (fechados) e depois o usuário
        con.execute("DELETE FROM emprestimos WHERE id_usuario=?", (user_id,))
        con.execute("DELETE FROM usuarios WHERE id=?", (user_id,))

# =========================
# LIVROS
# =========================
def insert_book(title: str, author: str, publisher: str, year: int, isbn: str, quantity: int) -> None:
    qtd = int(quantity)
    with _conn() as con:
        con.execute("""
            INSERT INTO livros (titulo, autor, editora, ano_publicacao, isbn, quantidade, disponivel)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (title, author, publisher, int(year), isbn, qtd, qtd))

def list_books() -> List[tuple]:
    with _conn() as con:
        rows = con.execute("""
            SELECT id, titulo, autor, editora, ano_publicacao, isbn, quantidade, disponivel
            FROM livros
            ORDER BY id DESC
        """).fetchall()
        # Tuplas na ordem esperada:
        # (id, title, author, publisher, year, isbn, quantity, available, created_at)
        return [(r["id"], r["titulo"], r["autor"], r["editora"], r["ano_publicacao"], r["isbn"], r["quantidade"], r["disponivel"], None)
                for r in rows]

def update_book(book_id: int, title: str, author: str, publisher: str, year: int, isbn: str, quantity: int) -> None:
    with _conn() as con:
        cur = con.execute("SELECT quantidade, disponivel FROM livros WHERE id=?", (book_id,))
        row = cur.fetchone()
        if row is None:
            return
        old_qtd, old_avail = int(row["quantidade"]), int(row["disponivel"])
        new_qtd = int(quantity)
        delta = new_qtd - old_qtd
        new_avail = max(0, old_avail + delta)  # tenta manter consistência
        con.execute("""
            UPDATE livros
               SET titulo=?, autor=?, editora=?, ano_publicacao=?, isbn=?, quantidade=?, disponivel=?
             WHERE id=?
        """, (title, author, publisher, int(year), isbn, new_qtd, new_avail, book_id))


def delete_book(book_id: int) -> None:
    with _conn() as con:
        # se houver empréstimo em aberto, bloqueia
        aberto = con.execute(
            "SELECT 1 FROM emprestimos WHERE id_livro=? AND (status IS NULL OR status!='closed') LIMIT 1",
            (book_id,)
        ).fetchone()
        if aberto:
            raise ValueError("Não é possível excluir: o livro possui empréstimo em aberto.")

        # apaga histórico (fechados) e depois o livro
        con.execute("DELETE FROM emprestimos WHERE id_livro=?", (book_id,))
        con.execute("DELETE FROM livros WHERE id=?", (book_id,))

# =========================
# EMPRÉSTIMOS
# =========================
def _book_is_available(con: sqlite3.Connection, book_id: int) -> bool:
    row = con.execute("SELECT disponivel FROM livros WHERE id=?", (book_id,)).fetchone()
    return row is not None and int(row["disponivel"]) > 0

def insert_loan(user_id: int, book_id: int, loan_date: Optional[str], return_date: Optional[str]) -> None:
    ld = (loan_date or _today_str())
    expected = _expected_from(ld, days=7)
    rd = return_date  # normalmente None ao emprestar

    with _conn() as con:
        # valida usuário/livro
        u = con.execute("SELECT id FROM usuarios WHERE id=?", (user_id,)).fetchone()
        if u is None:
            raise ValueError("Usuário inexistente")
        b = con.execute("SELECT id FROM livros WHERE id=?", (book_id,)).fetchone()
        if b is None:
            raise ValueError("Livro inexistente")
        if not _book_is_available(con, book_id):
            raise ValueError("Livro indisponível para empréstimo")

        con.execute("""
            INSERT INTO emprestimos (id_livro, id_usuario, data_emprestimo, data_devolucao, data_prevista, status)
            VALUES (?, ?, ?, ?, ?, 'open')
        """, (book_id, user_id, ld, rd, expected))

        # decrementa disponibilidade
        con.execute("UPDATE livros SET disponivel = disponivel - 1 WHERE id=? AND disponivel > 0", (book_id,))

def list_loans(open_only: bool = False) -> List[tuple]:
    with _conn() as con:
        where = "WHERE e.status='open'" if open_only else ""
        rows = con.execute(f"""
            SELECT
                e.id                               AS id,
                u.id                               AS user_id,
                (u.nome || ' ' || u.sobrenome)     AS user_name,
                l.id                               AS book_id,
                l.titulo                           AS book_title,
                e.data_emprestimo                  AS loan_date,
                e.data_prevista                    AS expected_date,
                e.data_devolucao                   AS return_date,
                e.status                           AS status
            FROM emprestimos e
            JOIN usuarios u ON u.id = e.id_usuario
            JOIN livros    l ON l.id = e.id_livro
            {where}
            ORDER BY e.id DESC
        """).fetchall()

        # tuplas na ordem esperada
        out = []
        for r in rows:
            out.append((
                r["id"],
                r["user_id"],
                r["user_name"],
                r["book_id"],
                r["book_title"],
                r["loan_date"],
                r["expected_date"],
                r["return_date"],
                r["status"],
            ))
        return out

def close_loan(loan_id: int, return_date: Optional[str]) -> None:
    rd = (return_date or _today_str())
    with _conn() as con:
        loan = con.execute("SELECT id, id_livro, status FROM emprestimos WHERE id=?", (loan_id,)).fetchone()
        if loan is None:
            raise ValueError("Empréstimo inexistente")
        if loan["status"] == "closed":
            return  # idempotente

        con.execute("""
            UPDATE emprestimos
               SET data_devolucao=?, status='closed'
             WHERE id=?
        """, (rd, loan_id))

        con.execute("UPDATE livros SET disponivel = disponivel + 1 WHERE id=?", (loan["id_livro"],))
