
from pathlib import Path
from datetime import datetime, date

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk

HOJE = datetime.today()

from view import *

# ====== Cores ======
c01 = "#2e2d2b" 
c02 = "#feffff"  
c03 = "#BCAAA4" 
c04 = "#8D6E63" 
c05 = "#e06336"  
c06 = "#D7CCC8"  

ASSETS_DIR = Path("imagem")

# ====== Utilidades de UI ======
def load_image(path: Path, size=None):
    if not path.exists():
        return None
    try:
        img = Image.open(path)
        if size:
            img = img.resize(size, Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None

def ask_yesno(title, msg):
    return messagebox.askyesno(title, msg)

def info(msg, title="Sucesso"):
    messagebox.showinfo(title, msg)

def error(msg, title="Erro"):
    messagebox.showerror(title, msg)

def warn(msg, title="Atenção"):
    messagebox.showwarning(title, msg)

def email_valido(s: str) -> bool:
    s = (s or "").strip()
    return "@" in s and "." in s.split("@")[-1]

def tel_limpo(s: str) -> str:
    return "".join(ch for ch in (s or "") if ch.isdigit())

# ====== App ======
class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # Janela
        self.title("Sistema de Gerenciamento de Livros")
        self.geometry("980x560")
        self.configure(background=c02)
        self.resizable(False, False)

        style = ttk.Style(self)
        style.theme_use("clam")

        # Grid base
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.frame_top = tk.Frame(self, height=60, bg=c06, relief="flat")
        self.frame_top.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self._build_header()

        # Menu lateral
        self.frame_left = tk.Frame(self, width=200, bg=c04, relief="solid", bd=1)
        self.frame_left.grid(row=1, column=0, sticky="nsew")
        self._build_sidebar()

        # Área de conteúdo
        self.frame_right = tk.Frame(self, bg=c02, relief="flat")
        self.frame_right.grid(row=1, column=1, sticky="nsew")

        # Páginas
        self.pages = {}
        self._create_pages()

        # Página inicial
        self.show_page("UsuariosPage")

    # ====== Header ======
    def _build_header(self):
        logo = load_image(ASSETS_DIR / "logo.png", (46, 46))
        lbl_logo = tk.Label(
            self.frame_top, image=logo, bg=c06, fg=c06, width=60, anchor="w"
        )
        if logo:
            lbl_logo.image = logo
        lbl_logo.place(x=8, y=6)

        lbl_title = tk.Label(
            self.frame_top,
            text="Sistema de Gerenciamento de Livros",
            font=("Verdana", 15, "bold"),
            bg=c06,
            fg=c04,
            anchor="w",
        )
        lbl_title.place(x=70, y=14)

        sep = tk.Label(self.frame_top, bg=c03, height=1)
        sep.place(x=0, y=58, width=9999, height=2)

    # ====== Sidebar ======
    def _build_sidebar(self):
        def make_btn(text, cmd, y):
            btn = tk.Button(
                self.frame_left,
                text=text,
                font=("Ivy", 12, "bold"),
                bg=c04,
                fg=c06,
                activebackground=c03,
                activeforeground=c01,
                relief="ridge",
                bd=2,
                command=cmd,
                pady=6,
            )
            btn.place(x=12, y=y, width=176, height=42)
            return btn

        make_btn("Usuários", lambda: self.show_page("UsuariosPage"), 20)
        make_btn("Livros", lambda: self.show_page("LivrosPage"), 74)
        make_btn("Empréstimos", lambda: self.show_page("EmprestimosPage"), 128)
        make_btn("Devoluções", lambda: self.show_page("DevolucoesPage"), 182)

        # rodapé lateral
        lbl_version = tk.Label(
            self.frame_left,
            text=f"Hoje: {HOJE.strftime('%d/%m/%Y')}",
            font=("Ivy", 10),
            bg=c04,
            fg=c02,
        )
        lbl_version.place(x=10, y=510)

    # ====== Páginas ======
    def _create_pages(self):
        self.pages["UsuariosPage"] = UsuariosPage(self.frame_right)
        self.pages["LivrosPage"] = LivrosPage(self.frame_right)
        self.pages["EmprestimosPage"] = EmprestimosPage(self.frame_right)
        self.pages["DevolucoesPage"] = DevolucoesPage(self.frame_right)

    def show_page(self, name: str):
        for page_name, page_obj in self.pages.items():
            page_obj.place_forget()
        page = self.pages[name]
        page.place(x=0, y=0, relwidth=1, relheight=1)
        page.on_show()  # atualiza listagens quando abre

# ====== Página: Usuários ======
class UsuariosPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=c02)
        self._build()

    def _build(self):
        # Título
        tk.Label(
            self, text="Cadastro de Usuários", font=("Verdana", 14, "bold"), bg=c02, fg=c04
        ).grid(row=0, column=0, columnspan=6, sticky="w", padx=12, pady=(12, 2))

        ttk.Separator(self, orient="horizontal").grid(
            row=1, column=0, columnspan=6, sticky="ew", padx=12, pady=(0, 10)
        )

        # Form
        self.var_id = tk.StringVar()

        self.var_first = tk.StringVar()
        self.var_last = tk.StringVar()
        self.var_address = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_phone = tk.StringVar()

        def mk_lbl(text, r, c):
            tk.Label(self, text=text, bg=c02, fg=c04, font=("Ivy", 10)).grid(
                row=r, column=c, sticky="w", padx=12, pady=4
            )

        def mk_ent(var, r, c, w=28):
            e = tk.Entry(self, textvariable=var, width=w, relief="solid", justify="left")
            e.grid(row=r, column=c, sticky="w", padx=12, pady=4)
            return e

        mk_lbl("Primeiro nome", 2, 0)
        mk_ent(self.var_first, 2, 1)

        mk_lbl("Sobrenome", 2, 2)
        mk_ent(self.var_last, 2, 3)

        mk_lbl("Endereço", 3, 0)
        mk_ent(self.var_address, 3, 1, 46)

        mk_lbl("E-mail", 3, 2)
        mk_ent(self.var_email, 3, 3)

        mk_lbl("Telefone", 4, 0)
        mk_ent(self.var_phone, 4, 1)

        # Botões
        icon_save = load_image(ASSETS_DIR / "add_usuario.png", (18, 18))
        icon_delete = load_image(ASSETS_DIR / "lixeira.png", (18, 18))
        icon_clean = load_image(ASSETS_DIR / "limpar.png", (18, 18))

        tk.Button(
            self, image=icon_save, text="  Salvar", compound="left",
            font=("Ivy", 11), bg=c04, fg=c06, relief="ridge", bd=2,
            command=self._on_save, padx=8, pady=2
        ).grid(row=5, column=1, sticky="w", padx=12, pady=(8, 10))
        if icon_save: self.children[list(self.children)[-1]].image = icon_save

        tk.Button(
            self, image=icon_delete, text="  Excluir", compound="left",
            font=("Ivy", 11), bg=c05, fg=c02, relief="ridge", bd=2,
            command=self._on_delete, padx=8, pady=2
        ).grid(row=5, column=2, sticky="w", padx=12, pady=(8, 10))
        if icon_delete: self.children[list(self.children)[-1]].image = icon_delete

        tk.Button(
            self, image=icon_clean, text="  Limpar", compound="left",
            font=("Ivy", 11), bg=c06, fg=c04, relief="ridge", bd=2,
            command=self._on_clear, padx=8, pady=2
        ).grid(row=5, column=3, sticky="w", padx=12, pady=(8, 10))
        if icon_clean: self.children[list(self.children)[-1]].image = icon_clean

        # Lista
        cols = ("id", "first", "last", "address", "email", "phone")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        self.tree.grid(row=6, column=0, columnspan=6, sticky="nsew", padx=12, pady=(4, 12))

        self.tree.heading("id", text="ID")
        self.tree.heading("first", text="Primeiro")
        self.tree.heading("last", text="Sobrenome")
        self.tree.heading("address", text="Endereço")
        self.tree.heading("email", text="E-mail")
        self.tree.heading("phone", text="Telefone")

        self.tree.column("id", width=20, anchor="center")
        self.tree.column("first", width=80)
        self.tree.column("last", width=80)
        self.tree.column("address", width=270)
        self.tree.column("email", width=190)
        self.tree.column("phone", width=100, anchor="center")

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Scroll
        yscroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=yscroll.set)
        yscroll.grid(row=6, column=6, sticky="ns", pady=(4, 12))

        # Pesos
        for i in range(6):
            self.grid_columnconfigure(i, weight=1)

    def on_show(self):
        self._refresh_list()

    # ====== Handlers ======
    def _on_save(self):
        first = self.var_first.get().strip()
        last = self.var_last.get().strip()
        address = self.var_address.get().strip()
        email = self.var_email.get().strip()
        phone_raw = self.var_phone.get().strip()
        phone = tel_limpo(phone_raw)

        if not all([first, last, address, email, phone_raw]):
            return error("Preencha todos os campos")

        if not email_valido(email):
            return error("E-mail inválido")

        if len(phone) < 8:
            return error("Telefone inválido")

        user_id = self.var_id.get().strip()
        try:
            if user_id:
                update_user(int(user_id), first, last, address, email, phone)
                info("Usuário atualizado")
            else:
                insert_user(first, last, address, email, phone)
                info("Usuário inserido")
        except Exception as e:
            return error(f"Erro ao salvar usuário: {e}")

        self._on_clear()
        self._refresh_list()

    def _on_delete(self):
        user_id = self.var_id.get().strip()
        if not user_id:
            return warn("Selecione um usuário para excluir")
        if not ask_yesno("Confirmação", "Deseja excluir este usuário?"):
            return
        try:
            delete_user(int(user_id))
            info("Usuário excluído")
            self._on_clear()
            self._refresh_list()
        except Exception as e:
            error(f"Erro ao excluir: {e}")

    def _on_clear(self):
        self.var_id.set("")
        self.var_first.set("")
        self.var_last.set("")
        self.var_address.set("")
        self.var_email.set("")
        self.var_phone.set("")

    def _on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        # valores na ordem das colunas
        self.var_id.set(vals[0])
        self.var_first.set(vals[1])
        self.var_last.set(vals[2])
        self.var_address.set(vals[3])
        self.var_email.set(vals[4])
        self.var_phone.set(vals[5])

    def _refresh_list(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        try:
            data = list_users() or []
        except Exception as e:
            return warn(f"Não foi possível carregar usuários: {e}")

        # Aceita tupla ou dict
        for row in data:
            if isinstance(row, dict):
                rid = row.get("id", "")
                first = row.get("first_name", "")
                last = row.get("last_name", "")
                address = row.get("address", "")
                email = row.get("email", "")
                phone = row.get("phone", "")
            else:
                # id, first_name, last_name, address, email, phone, ...
                rid, first, last, address, email, phone = row[:6]
            self.tree.insert("", "end", values=(rid, first, last, address, email, phone))

# ====== Página: Livros ======
class LivrosPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=c02)
        self._build()

    def _build(self):
        tk.Label(
            self, text="Cadastro de Livros", font=("Verdana", 14, "bold"), bg=c02, fg=c04
        ).grid(row=0, column=0, columnspan=8, sticky="w", padx=12, pady=(12, 2))

        ttk.Separator(self, orient="horizontal").grid(
            row=1, column=0, columnspan=8, sticky="ew", padx=12, pady=(0, 10)
        )

        self.var_id = tk.StringVar()
        self.var_title = tk.StringVar()
        self.var_author = tk.StringVar()
        self.var_publisher = tk.StringVar()
        self.var_year = tk.StringVar()
        self.var_isbn = tk.StringVar()
        self.var_qty = tk.StringVar()

        def mk_lbl(text, r, c):
            tk.Label(self, text=text, bg=c02, fg=c04, font=("Ivy", 10)).grid(
                row=r, column=c, sticky="w", padx=12, pady=4
            )

        def mk_ent(var, r, c, w=28):
            e = tk.Entry(self, textvariable=var, width=w, relief="solid", justify="left")
            e.grid(row=r, column=c, sticky="w", padx=12, pady=4)
            return e

        mk_lbl("Título", 2, 0)
        mk_ent(self.var_title, 2, 1, 46)

        mk_lbl("Autor", 2, 2)
        mk_ent(self.var_author, 2, 3, 28)

        mk_lbl("Editora", 3, 0)
        mk_ent(self.var_publisher, 3, 1, 28)

        mk_lbl("Ano", 3, 2)
        mk_ent(self.var_year, 3, 3, 12)

        mk_lbl("ISBN", 4, 0)
        mk_ent(self.var_isbn, 4, 1, 20)

        mk_lbl("Quantidade", 4, 2)
        mk_ent(self.var_qty, 4, 3, 12)

        # Botões
        icon_save = load_image(ASSETS_DIR / "add_livro.png", (18, 18))
        icon_delete = load_image(ASSETS_DIR / "lixeira.png", (18, 18))
        icon_clean = load_image(ASSETS_DIR / "limpar.png", (18, 18))

        tk.Button(
            self, image=icon_save, text="  Salvar", compound="left",
            font=("Ivy", 11), bg=c04, fg=c06, relief="ridge", bd=2,
            command=self._on_save, padx=8, pady=2
        ).grid(row=5, column=1, sticky="w", padx=12, pady=(8, 10))
        if icon_save: self.children[list(self.children)[-1]].image = icon_save

        tk.Button(
            self, image=icon_delete, text="  Excluir", compound="left",
            font=("Ivy", 11), bg=c05, fg=c02, relief="ridge", bd=2,
            command=self._on_delete, padx=8, pady=2
        ).grid(row=5, column=2, sticky="w", padx=12, pady=(8, 10))
        if icon_delete: self.children[list(self.children)[-1]].image = icon_delete

        tk.Button(
            self, image=icon_clean, text="  Limpar", compound="left",
            font=("Ivy", 11), bg=c06, fg=c04, relief="ridge", bd=2,
            command=self._on_clear, padx=8, pady=2
        ).grid(row=5, column=3, sticky="w", padx=12, pady=(8, 10))
        if icon_clean: self.children[list(self.children)[-1]].image = icon_clean

        # Lista
        cols = ("id", "title", "author", "publisher", "year", "isbn", "qty")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=10)
        self.tree.grid(row=6, column=0, columnspan=8, sticky="nsew", padx=12, pady=(4, 12))

        for k, t in zip(cols, ["ID", "Título", "Autor", "Editora", "Ano", "ISBN", "Qtd."]):
            self.tree.heading(k, text=t)

        self.tree.column("id", width=20, anchor="center")
        self.tree.column("title", width=180)
        self.tree.column("author", width=160)
        self.tree.column("publisher", width=140)
        self.tree.column("year", width=60, anchor="center")
        self.tree.column("isbn", width=120)
        self.tree.column("qty", width=60, anchor="center")

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        yscroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=yscroll.set)
        yscroll.grid(row=6, column=8, sticky="ns", pady=(4, 12))

        for i in range(8):
            self.grid_columnconfigure(i, weight=1)

    def on_show(self):
        self._refresh_list()

    # ====== Handlers ======
    def _on_save(self):
        title = self.var_title.get().strip()
        author = self.var_author.get().strip()
        publisher = self.var_publisher.get().strip()
        year = self.var_year.get().strip()
        isbn = self.var_isbn.get().strip()
        qty = self.var_qty.get().strip()

        if not all([title, author, publisher, year, isbn, qty]):
            return error("Preencha todos os campos")

        if not year.isdigit() or len(year) not in (2, 4):
            return error("Ano inválido")

        if not qty.isdigit():
            return error("Quantidade inválida")

        bid = self.var_id.get().strip()
        try:
            if bid:
                update_book(int(bid), title, author, publisher, int(year), isbn, int(qty))
                info("Livro atualizado")
            else:
                insert_book(title, author, publisher, int(year), isbn, int(qty))
                info("Livro inserido")
        except Exception as e:
            return error(f"Erro ao salvar livro: {e}")

        self._on_clear()
        self._refresh_list()

    def _on_delete(self):
        bid = self.var_id.get().strip()
        if not bid:
            return warn("Selecione um livro para excluir")
        if not ask_yesno("Confirmação", "Deseja excluir este livro?"):
            return
        try:
            delete_book(int(bid))
            info("Livro excluído")
            self._on_clear()
            self._refresh_list()
        except Exception as e:
            error(f"Erro ao excluir: {e}")

    def _on_clear(self):
        self.var_id.set("")
        self.var_title.set("")
        self.var_author.set("")
        self.var_publisher.set("")
        self.var_year.set("")
        self.var_isbn.set("")
        self.var_qty.set("")

    def _on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        # id, title, author, publisher, year, isbn, qty
        self.var_id.set(vals[0])
        self.var_title.set(vals[1])
        self.var_author.set(vals[2])
        self.var_publisher.set(vals[3])
        self.var_year.set(vals[4])
        self.var_isbn.set(vals[5])
        self.var_qty.set(vals[6])

    def _refresh_list(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            data = list_books() or []
        except Exception as e:
            return warn(f"Não foi possível carregar livros: {e}")

        for row in data:
            if isinstance(row, dict):
                rid = row.get("id", "")
                title = row.get("title", "")
                author = row.get("author", "")
                publisher = row.get("publisher", "")
                year = row.get("year", "")
                isbn = row.get("isbn", "")
                qty = row.get("quantity", "")
            else:
                rid, title, author, publisher, year, isbn, qty = row[:7]
            self.tree.insert("", "end", values=(rid, title, author, publisher, year, isbn, qty))


# ====== Página: Empréstimos ======
class EmprestimosPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=c02)
        self._build()

    def _build(self):
        tk.Label(
            self, text="Empréstimos", font=("Verdana", 14, "bold"), bg=c02, fg=c04
        ).grid(row=0, column=0, columnspan=6, sticky="w", padx=12, pady=(12, 2))

        ttk.Separator(self, orient="horizontal").grid(
            row=1, column=0, columnspan=6, sticky="ew", padx=12, pady=(0, 10)
        )

        self.var_user_id = tk.StringVar()
        self.var_book_id = tk.StringVar()
        self.var_loan_date = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))

        def mk_lbl(text, r, c):
            tk.Label(self, text=text, bg=c02, fg=c04, font=("Ivy", 10)).grid(
                row=r, column=c, sticky="w", padx=12, pady=4
            )

        def mk_ent(var, r, c, w=22):
            e = tk.Entry(self, textvariable=var, width=w, relief="solid", justify="left")
            e.grid(row=r, column=c, sticky="w", padx=12, pady=4)
            return e

        mk_lbl("ID Usuário", 2, 0)
        mk_ent(self.var_user_id, 2, 1)

        mk_lbl("ID Livro", 2, 2)
        mk_ent(self.var_book_id, 2, 3)

        mk_lbl("Data Empréstimo (YYYY-MM-DD)", 3, 0)
        mk_ent(self.var_loan_date, 3, 1)

        icon_save = load_image(ASSETS_DIR / "emprestimo.png", (20, 20))
        tk.Button(
            self, image=icon_save, text="  Registrar Empréstimo", compound="left",
            font=("Ivy", 11), bg=c04, fg=c06, relief="ridge", bd=2,
            command=self._on_save, padx=8, pady=4
        ).grid(row=4, column=1, sticky="w", padx=12, pady=(8, 10))
        if icon_save: self.children[list(self.children)[-1]].image = icon_save

        # Lista
        cols = ("id", "user", "book", "loan_date", "expected", "status")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=12)
        self.tree.grid(row=6, column=0, columnspan=6, sticky="nsew", padx=12, pady=(6, 12))

        self.tree.heading("id", text="ID")
        self.tree.heading("user", text="Usuário")
        self.tree.heading("book", text="Livro")
        self.tree.heading("loan_date", text="Data Empréstimo")
        self.tree.heading("expected", text="Previsto")
        self.tree.heading("status", text="Status")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("user", width=160)
        self.tree.column("book", width=200)
        self.tree.column("loan_date", width=120, anchor="center")
        self.tree.column("expected", width=120, anchor="center")
        self.tree.column("status", width=80, anchor="center")

        yscroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=yscroll.set)
        yscroll.grid(row=6, column=6, sticky="ns", pady=(6, 12))

        for i in range(6):
            self.grid_columnconfigure(i, weight=1)

    def on_show(self):
        self._refresh_list()

    def _on_save(self):
        user_id = self.var_user_id.get().strip()
        book_id = self.var_book_id.get().strip()
        loan_date = self.var_loan_date.get().strip()

        if not all([user_id, book_id, loan_date]):
            return error("Preencha todos os campos")

        try:
            insert_loan(int(user_id), int(book_id), loan_date, None)
            info("Empréstimo registrado")
            self.var_user_id.set("")
            self.var_book_id.set("")
            self.var_loan_date.set(date.today().strftime("%Y-%m-%d"))
            self._refresh_list()
        except Exception as e:
            error(f"Erro ao registrar empréstimo: {e}")

    def _refresh_list(self):
        # Lista por padrão apenas abertos
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            data = list_loans(open_only=False) or []
        except Exception as e:
            return warn(f"Não foi possível carregar empréstimos: {e}")

        for row in data:
            if isinstance(row, dict):
                rid = row.get("id", "")
                user = row.get("user_name", row.get("user_id", ""))
                book = row.get("book_title", row.get("book_id", ""))
                loan_d = row.get("loan_date", "")
                expected = row.get("expected_date", "")
                status = row.get("status", "")
            else:
                rid, _uid, user, _bid, book, loan_d, expected, _ret, status = row[:9]
            self.tree.insert("", "end", values=(rid, user, book, loan_d, expected, status))


# ====== Página: Devoluções ======
class DevolucoesPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=c02)
        self._build()

    def _build(self):
        tk.Label(
            self, text="Devoluções", font=("Verdana", 14, "bold"), bg=c02, fg=c04
        ).grid(row=0, column=0, columnspan=6, sticky="w", padx=12, pady=(12, 2))

        ttk.Separator(self, orient="horizontal").grid(
            row=1, column=0, columnspan=6, sticky="ew", padx=12, pady=(0, 10)
        )

        self.var_loan_id = tk.StringVar()
        self.var_return_date = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))

        tk.Label(self, text="ID Empréstimo", bg=c02, fg=c04, font=("Ivy", 10)).grid(
            row=2, column=0, sticky="w", padx=12, pady=4
        )
        tk.Entry(self, textvariable=self.var_loan_id, width=20, relief="solid").grid(
            row=2, column=1, sticky="w", padx=12, pady=4
        )

        tk.Label(self, text="Data Devolução (YYYY-MM-DD)", bg=c02, fg=c04, font=("Ivy", 10)).grid(
            row=2, column=2, sticky="w", padx=12, pady=4
        )
        tk.Entry(self, textvariable=self.var_return_date, width=20, relief="solid").grid(
            row=2, column=3, sticky="w", padx=12, pady=4
        )

        icon_save = load_image(ASSETS_DIR / "devolucao.png", (20, 20))
        tk.Button(
            self, image=icon_save, text="  Registrar Devolução", compound="left",
            font=("Ivy", 11), bg=c04, fg=c06, relief="ridge", bd=2,
            command=self._on_close, padx=8, pady=4
        ).grid(row=3, column=1, sticky="w", padx=12, pady=(8, 10))
        if icon_save: self.children[list(self.children)[-1]].image = icon_save

        # Lista de empréstimos abertos para facilitar seleção
        cols = ("id", "user", "book", "loan_date", "expected")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=12)
        self.tree.grid(row=5, column=0, columnspan=6, sticky="nsew", padx=12, pady=(6, 12))

        self.tree.heading("id", text="ID")
        self.tree.heading("user", text="Usuário")
        self.tree.heading("book", text="Livro")
        self.tree.heading("loan_date", text="Data Empréstimo")
        self.tree.heading("expected", text="Previsto")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("user", width=200)
        self.tree.column("book", width=240)
        self.tree.column("loan_date", width=120, anchor="center")
        self.tree.column("expected", width=120, anchor="center")

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        yscroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=yscroll.set)
        yscroll.grid(row=5, column=6, sticky="ns", pady=(6, 12))

        for i in range(6):
            self.grid_columnconfigure(i, weight=1)

    def on_show(self):
        self._refresh_list()

    def _on_close(self):
        loan_id = self.var_loan_id.get().strip()
        ret_date = self.var_return_date.get().strip()
        if not all([loan_id, ret_date]):
            return error("Informe o ID do empréstimo e a data de devolução")
        try:
            close_loan(int(loan_id), ret_date)
            info("Devolução registrada")
            self.var_loan_id.set("")
            self.var_return_date.set(date.today().strftime("%Y-%m-%d"))
            self._refresh_list()
        except Exception as e:
            error(f"Erro ao registrar devolução: {e}")

    def _on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        self.var_loan_id.set(vals[0])

    def _refresh_list(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            data = list_loans(open_only=True) or []
        except Exception as e:
            return warn(f"Não foi possível carregar empréstimos abertos: {e}")

        for row in data:
            if isinstance(row, dict):
                rid = row.get("id", "")
                user = row.get("user_name", row.get("user_id", ""))
                book = row.get("book_title", row.get("book_id", ""))
                loan_d = row.get("loan_date", "")
                expected = row.get("expected_date", "")
            else:
                rid, _uid, user, _bid, book, loan_d, expected, _ret, _status = row[:9]
            self.tree.insert("", "end", values=(rid, user, book, loan_d, expected))


# ====== Execução ======
if __name__ == "__main__":
    app = App()
    app.mainloop()
