import tkinter as tk
from tkinter import messagebox
import re
import ctypes
from ctypes import c_char_p, c_float, c_int
#versao 0.1.0
# criador: iurie
# Carregar DLL / O codigo c
logic = ctypes.CDLL("./logic1.dll")

# Definir argumentos da função do C
logic.salvar_produto.argtypes = [c_char_p, c_float, c_int, c_char_p]
logic.salvar_produto.restype = None

root = tk.Tk()
root.title("GETSTRINGDAMIAO app")
root.geometry("400x450")
root.resizable(False, False)
def salvar_produto_txt(nome, preco, quantidade, descricao):
    with open("produto.txt", "a") as f:  # <-- 'a' = append mode ou seja, nao vai apagar o que ja existe 'w' = write/overwrite mode
        f.write(f"{nome}\n{preco}\n{quantidade}\n{descricao}\n---\n")


#def data_valida(data):
 #   return bool(re.match(r"\d{2}/\d{2}/\d{4}$", data))

def financas():
    def calcular_valores():
        try:
            with open("vendas.txt", "r", encoding="utf-8") as f:
                vendas_raw = f.read().strip().split('---\n')
        except FileNotFoundError:
            vendas_raw = []

        lucro_total = 0.0
        custo_total = 0.0
        num_vendas = 0

        for item in vendas_raw:
            lines = item.strip().split('\n')
            if len(lines) >= 6:
                try:
                    nome_produto = lines[2].split(":", 1)[1].strip()
                    quantidade = int(lines[3].split(":", 1)[1].strip())
                    preco_unitario = float(lines[4].split(":", 1)[1].strip())
                    total_venda = float(lines[5].split(":", 1)[1].strip())
                except (ValueError, IndexError):
                    continue

                preco_custo = encontrar_preco_custo(nome_produto)
                if preco_custo is not None:
                    custo_total += preco_custo * quantidade
                    lucro_total += (preco_unitario - preco_custo) * quantidade
                else:
                    lucro_total += total_venda

                num_vendas += 1

        return custo_total, lucro_total, num_vendas

    def encontrar_preco_custo(produto_nome):
        try:
            with open("produto.txt", "r", encoding="utf-8") as f:
                produtos_raw = f.read().strip().split('---\n')
                for item in produtos_raw:
                    lines = item.strip().split('\n')
                    if len(lines) >= 2:
                        nome = lines[0].strip()
                        preco = float(lines[1].strip())
                        if nome.lower() == produto_nome.lower():
                            return preco
        except:
            return None
        return None

    def ler_caixa_manual():
        try:
            with open("caixa.txt", "r", encoding="utf-8") as f:
                linhas = f.readlines()
                return sum(float(linha.strip()) for linha in linhas)
        except:
            return 0.0

    def adicionar_valor(entrada=True):
        valor_str = entry_valor.get()
        try:
            valor = float(valor_str)
            if not entrada:
                valor = -valor
            with open("caixa.txt", "a", encoding="utf-8") as f:
                f.write(f"{valor}\n")
            win.destroy()
            financas()
        except ValueError:
            messagebox.showerror("Erro", "Digite um valor válido.")

    custo_total, lucro_total, num_vendas = calcular_valores()
    valor_manual = ler_caixa_manual()
    valor_em_caixa = lucro_total + valor_manual

    try:
        with open("produto.txt", "r", encoding="utf-8") as f:
            produtos_raw = f.read().strip().split('---\n')
            num_compras = len(produtos_raw)
    except:
        num_compras = 0

    # Interface
    win = tk.Toplevel(root)
    win.title("Finanças da Papelaria")
    win.geometry("400x340")

    tk.Label(win, text="Relatório Financeiro", font=("Arial", 14)).pack(pady=10)
    tk.Label(win, text=f" Despesas com produtos: € {custo_total:.2f}").pack()
    tk.Label(win, text=f" Lucro obtido:  € {lucro_total:.2f}").pack()
    tk.Label(win, text=f" Valor atual em caixa:  € {valor_em_caixa:.2f}").pack(pady=10)
    tk.Label(win, text=f" Compras registradas: {num_compras}").pack()
    tk.Label(win, text=f" Vendas registradas: {num_vendas}").pack(pady=10)

    tk.Label(win, text="Alterar caixa manualmente:").pack(pady=5)
    entry_valor = tk.Entry(win)
    entry_valor.pack()

    tk.Button(win, text="Adicionar valor", command=lambda: adicionar_valor(True)).pack(pady=5)
    tk.Button(win, text="Retirar valor", command=lambda: adicionar_valor(False)).pack(pady=5)


def registar_venda():
    def carregar_estoque():
        try:
            with open("produto.txt", "r") as f:
                data = f.read()
                produtos_raw = data.strip().split('---\n')
                estoque = []

                for item in produtos_raw:
                    lines = item.strip().split('\n')
                    if len(lines) >= 4:
                        nome, preco, quantidade, descricao = lines[:4]
                        estoque.append({
                            "nome": nome,
                            "preco": float(preco),
                            "quantidade": int(quantidade),
                            "descricao": descricao
                        })
                return estoque
        except FileNotFoundError:
            return []

    def salvar_estoque(estoque):
        with open("produto.txt", "a") as f:
            for produto in estoque:
                f.write(f"{produto['nome']}\n{produto['preco']}\n{produto['quantidade']}\n{produto['descricao']}\n---\n")

    def registrar():
        nome_cliente = entry_cliente.get()
        nome_produto = entry_produto.get()
        data_venda = entry_data.get()

        produto_encontrado = next((p for p in estoque if p["nome"].lower() == nome_produto.lower()), None)

        if not produto_encontrado:
            messagebox.showerror("Erro", "Produto não encontrado em estoque.")
            return

        quantidade_em_estoque = produto_encontrado["quantidade"]
        preco_custo = produto_encontrado["preco"]

        try:
            quantidade_vender = int(entry_qtd.get())
            preco_venda_unitario = float(entry_preco_venda.get())
        except ValueError:
            messagebox.showerror("Erro", "Quantidade ou preço inválido.")
            return

        if quantidade_vender > quantidade_em_estoque:
            messagebox.showerror("Erro", f"Quantidade indisponível. Estoque atual: {quantidade_em_estoque}")
            return

        total = quantidade_vender * preco_venda_unitario

        produto_encontrado["quantidade"] -= quantidade_vender
        salvar_estoque(estoque)

        # salvar a venda
        with open("vendas.txt", "a", encoding="utf-8") as f:
            f.write(f"Data: {data_venda}\n")
            f.write(f"Cliente: {nome_cliente}\n")
            f.write(f"Produto: {nome_produto}\n")
            f.write(f"Quantidade: {quantidade_vender}\n")
            f.write(f"Preço unitário: {preco_venda_unitario:.2f}\n")
            f.write(f"Preço total: {total:.2f}\n")
            f.write("---\n")
        messagebox.showinfo("Venda Salva", f"Venda foi vendida!")
        venda_win.destroy()

    estoque = carregar_estoque()

    venda_win = tk.Toplevel(root)
    venda_win.title("Registrar Venda")
    venda_win.geometry("400x400")

    tk.Label(venda_win, text="Data da venda:").pack()
    entry_data = tk.Entry(venda_win)
    entry_data.pack(pady=5)

    tk.Label(venda_win, text="Nome do cliente:").pack()
    entry_cliente = tk.Entry(venda_win)
    entry_cliente.pack(pady=5)

    tk.Label(venda_win, text="Nome do produto:").pack()
    entry_produto = tk.Entry(venda_win)
    entry_produto.pack(pady=5)

    tk.Label(venda_win, text="Quantidade a vender:").pack()
    entry_qtd = tk.Entry(venda_win)
    entry_qtd.pack(pady=5)

    tk.Label(venda_win, text="Preço de venda por unidade:").pack()
    entry_preco_venda = tk.Entry(venda_win)
    entry_preco_venda.pack(pady=5)

    tk.Button(venda_win, text="Confirmar venda", command=registrar, width=40, height=2).pack(pady=20)
    tk.Button(venda_win, text="Sair", command=venda_win.destroy, width=40, height=2).pack(pady=10)
def listar_vendas():
    try:
        with open("vendas.txt", "r", encoding="utf-8") as f:
            conteudo = f.read()
    except FileNotFoundError:
        conteudo = "Nenhuma venda registrada ainda."

    janela_vendas = tk.Toplevel(root)
    janela_vendas.title("Lista de Vendas")
    janela_vendas.geometry("400x400")

    texto = tk.Text(janela_vendas, wrap="word")
    texto.insert("1.0", conteudo)
    texto.configure(state="disabled") 
    texto.pack(expand=True, fill="both", padx=10, pady=10)


def listar_produtos():
    try:
        with open("produto.txt", "r") as f:
            data = f.read()
            produtos_raw = data.strip().split('---\n')
            produtos = []

            for item in produtos_raw:
                lines = item.strip().split('\n')
                if len(lines) >= 4:
                    nome, preco, quantidade, descricao = lines[:4]
                    produtos.append((nome, preco, quantidade, descricao))
    except FileNotFoundError:
        messagebox.showerror("Erro", "Nenhum produto foi encontrado.")
        return

    # Criar nova janela para mostrar os produtos
    list_win = tk.Toplevel(root)
    list_win.title("Lista de Produtos")
    list_win.geometry("400x450")
    list_win.resizable(False, False)

    tk.Label(list_win, text="Produtos Salvos:", font=("Arial", 14)).pack(pady=10)

    text_box = tk.Text(list_win, width=45, height=30)
    text_box.pack(pady=10)

    for i, (nome, preco, quantidade, descricao) in enumerate(produtos, start=1):
        text_box.insert(tk.END, f"Produto {i}:\n")
        text_box.insert(tk.END, f"  Nome: {nome}\n")
        text_box.insert(tk.END, f"  Preço: {preco}\n")
        text_box.insert(tk.END, f"  Quantidade: {quantidade}\n")
        text_box.insert(tk.END, f"  Descrição: {descricao}\n")
        text_box.insert(tk.END, "------------------------\n")

    text_box.config(state=tk.DISABLED)

def open_new_window(): # janela pra inserir produto
    def save_product():
        nome = entry1.get()
        try:
            preco = float(entry2.get())
            quantidade = int(entry3.get())
        except ValueError:
            messagebox.showerror("Erro", "Preço deve ser número e quantidade um inteiro.")
            return
        descricao = entry4.get("1.0", tk.END).strip()

        # Chamar a função do C
        logic.salvar_produto(nome.encode(), preco, quantidade, descricao.encode())

        messagebox.showinfo("Produto Salvo", f"Produto {nome} foi salvo!")
        new_win.destroy()

    new_win = tk.Toplevel(root)
    new_win.title("Inserir produto")
    new_win.geometry("400x530")
    new_win.resizable(False, False)

    tk.Label(new_win, text="Insira os detalhes do produto:").pack(pady=20)
    
    tk.Label(new_win, text="Nome do produto:").pack()
    entry1 = tk.Entry(new_win, width=30)
    entry1.pack(pady=5)

    tk.Label(new_win, text="Preço do produto:").pack()
    entry2 = tk.Entry(new_win, width=30)
    entry2.pack(pady=5)

    tk.Label(new_win, text="Quantidade do produto:").pack()
    entry3 = tk.Entry(new_win, width=30)
    entry3.pack(pady=5)

    tk.Label(new_win, text="Descrição do produto:").pack()
    entry4 = tk.Text(new_win, width=40, height=10, wrap="word")
    entry4.pack(pady=5)

    tk.Button(new_win, text="Salvar Produto", command=save_product).pack(pady=20)
    botton = tk.Button(new_win, text="sair", command=new_win.destroy).pack(pady=10)
    

def exit_program():
    root.destroy()

def on_button_click():
    messagebox.showinfo("Info", "Função ainda não implementada!")

def create_title_label():
    label = tk.Label(root, text="------ PAPELARIA GETSTRINGDAMIAO ------", font=("Arial", 15))
    label.pack(pady=20)

create_title_label()

btn_texts = [
    ("Inserir produto", open_new_window),
    ("Listar produto", listar_produtos),
    ("Registar venda", registar_venda), 
    ("Listar vendas", listar_vendas),
    ("Finanças", financas),
    ("Terminar", exit_program)
]

for text, command in btn_texts:
    button = tk.Button(root, text=text, command=command, width=50, height=2)
    button.pack(pady=10, padx=20)

root.mainloop()