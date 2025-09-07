import sqlite3

# conectar ao banco de dados ou criar um novo banco de dados caso nao existe
con = sqlite3.connect('dados.db')

# criar tabela de livros
con.execute('''
    CREATE TABLE IF NOT EXISTS livros(
        id INTEGER PRIMARY KEY,
        titulo TEXT,
        autor TEXT,
        editora TEXT,
        ano_publicacao INTEGER,
        isbn TEXT
    )
''')

# criar tabela de usuarios
con.execute('''
    CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY,
        nome TEXT,
        sobrenome TEXT,
        endereco TEXT,
        email TEXT,
        telefone TEXT
    )
''')

# criar tabela de emprestimos
con.execute('''
    CREATE TABLE IF NOT EXISTS emprestimos(
        id INTEGER PRIMARY KEY,
        id_livro INTEGER,
        id_usuario INTEGER,
        data_emprestimo TEXT,
        data_devolucao TEXT,
        FOREIGN KEY(id_livro) REFERENCES livros(id),
        FOREIGN KEY(id_usuario) REFERENCES usuarios(id)
    )
''')
