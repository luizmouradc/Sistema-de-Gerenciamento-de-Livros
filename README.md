# Sistema de Gerenciamento de Livros

Aplicação desktop em **Python/Tkinter** para gerenciar **usuários, livros, empréstimos e devoluções**.  
Interface em abas (menu lateral), banco local **SQLite** com migrações automáticas e validações de regras de negócio.

---

## Funcionalidades 

### Usuários
- Cadastrar, listar, atualizar e excluir usuários.
- Bloqueio de exclusão se houver empréstimos em aberto.
- Validação de e-mail e telefone.

### Livros
- Cadastrar, listar, atualizar e excluir livros.
- Controle de **quantidade total** e **disponibilidade** automática.
- Validação de ano de publicação e ISBN.

### Empréstimos
- Registrar empréstimos vinculando usuário + livro.
- Verificação de disponibilidade do livro.
- Cálculo automático da **data prevista de devolução** (7 dias após empréstimo).

### Devoluções
- Registrar devolução e atualizar disponibilidade do livro.
- Exibição de todos os empréstimos em aberto para facilitar a seleção.

---

## Screenshots / Visualização

Abaixo alguns exemplos de telas do sistema em execução:

| Usuários | Livros |
|---|---|
| <img width="400" alt="Usuários" src="https://github.com/user-attachments/assets/0fff659e-fd0f-41c4-8362-8a87d0353020" /> | <img width="400" alt="Livros" src="https://github.com/user-attachments/assets/d12a0e25-f42c-46a0-8198-f61784aeef3b" /> |

| Empréstimos |  Devoluções |
|---|---|
| <img width="400" alt="Empréstimos" src="https://github.com/user-attachments/assets/5c104284-a53c-426a-bc12-ed541c6e86c8" /> | <img width="400" alt="Devoluções" src="https://github.com/user-attachments/assets/0e194444-c9a5-4760-b4bc-7a51c26d610f" /> |

---

## Instalação & Execução

### Pré-requisitos
- **Python 3.10+** instalado no sistema.
- No Linux, pode ser necessário instalar:
  ```bash
  sudo apt install python3-tk

---

## Arquitetura e Fluxo

A aplicação segue uma arquitetura simples em **camadas**:

- **Interface Gráfica (`tela.py`)**
  - Construída com **Tkinter**.
  - Organizada em páginas: `UsuariosPage`, `LivrosPage`, `EmprestimosPage`, `DevolucoesPage`.
  - Cada página contém:
    - Formulários para cadastro/edição.
    - Botões de ação (Salvar, Excluir, Limpar).
    - Listagens em `Treeview` com rolagem.
  - O **menu lateral** permite navegar entre as páginas.

- **Camada de Dados (`view.py`)**
  - Responsável por acessar e manipular o **SQLite**.
  - Inclui **migrações automáticas**:
    - `livros`: adiciona colunas `quantidade` e `disponivel`.
    - `emprestimos`: adiciona colunas `data_prevista` e `status`.
  - Expõe funções CRUD (`insert_user`, `list_books`, `insert_loan`, etc.) utilizadas pela interface.

- **Banco (`dados.db`)**
  - Arquivo SQLite local criado automaticamente.
  - Estrutura compatível com `dados.py` (definição inicial das tabelas).
  - Evoluído por `view.py` quando necessário.

---

## Modelo de Dados

### Tabelas Base

**usuarios**  
- id, nome, sobrenome, endereco, email, telefone  

**livros**  
- id, titulo, autor, editora, ano_publicacao, isbn, quantidade, disponivel  

**emprestimos**  
- id, id_livro, id_usuario, data_emprestimo, data_devolucao, data_prevista, status  

---

## Regras de Negócio & Validações

### Usuários
- **Obrigatório** preencher todos os campos.
- **E-mail** precisa ter formato válido (`@` e domínio).
- **Telefone** aceita apenas números (mínimo de 8 dígitos).
- Não é permitido excluir usuários que possuam **empréstimos em aberto**.

### Livros
- **Título, autor, editora, ano, ISBN e quantidade** são obrigatórios.
- **Ano de publicação** deve ser numérico (formato 2 ou 4 dígitos).
- **Quantidade** deve ser número inteiro ≥ 0.
- Alterar quantidade ajusta automaticamente a coluna `disponivel`.
- Não é permitido excluir livros com **empréstimos em aberto**.

### Empréstimos
- Só é possível registrar empréstimo se `disponivel > 0`.
- A **data prevista de devolução** é definida automaticamente (`data_emprestimo + 7 dias`).
- Campos obrigatórios: **ID do usuário, ID do livro, data de empréstimo**.

### Devoluções
- É necessário informar o **ID do empréstimo** e a **data de devolução**.
- Ao devolver:
  - O status do empréstimo é atualizado para **`closed`**.
  - O campo `data_devolucao` é preenchido.
  - O campo `disponivel` em `livros` é incrementado.
    
---

## Ferramentas Utilizadas

Para o desenvolvimento do **Sistema de Gerenciamento de Livros**, foram utilizadas as seguintes tecnologias:

- **Python 3** → Linguagem principal.
- **Tkinter** → Interface gráfica desktop (nativa do Python).
- **SQLite3** → Banco de dados local, simples e leve.
- **Pillow (PIL)** → Manipulação e redimensionamento de imagens.
- **ttk (Themed Tkinter Widgets)** → Widgets estilizados para a interface.
- **datetime** → Manipulação de datas (empréstimos e devoluções).
- **Pathlib** → Organização de diretórios e manipulação de arquivos.
- **Git & GitHub** → Controle de versão e hospedagem do código.
- **VSCode** → Editor de código utilizado no desenvolvimento.
