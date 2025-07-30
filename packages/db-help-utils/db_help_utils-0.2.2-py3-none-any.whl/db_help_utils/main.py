import sqlite3
import psycopg2
from tkinter import ttk, Frame, Toplevel
from tkinter.messagebox import askyesno, showerror
# Database Connection Class
class DBConnector:
    def __init__(self, db_type, **kwargs):
        self.db_type = db_type
        self.connection = self.connect_to_db(**kwargs)

    def connect_to_db(self, **kwargs):
        if self.db_type == 'sqlite':
            return sqlite3.connect(kwargs['database'])
        elif self.db_type == 'postgresql':
            return psycopg2.connect(**kwargs)

        else:
            raise ValueError("Unsupported database type!")

    def close_connection(self):
        if self.connection:
            self.connection.close()

# Query Execution Class
class QueryExecutor:
    def __init__(self, connection):
        self.connection = connection

    def execute_query(self, query, params=None):
        cursor = self.connection.cursor()
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        cursor.close()
        return rows

    def execute_non_query(self, query, params=None):
        cursor = self.connection.cursor()
        cursor.execute(query, params or ())
        self.connection.commit()
        cursor.close()

# UI Utility Functions
def create_buttons_from_data(frame, data, column_names, command_func):
    for row in data:
        button_text = "\n".join(f"{col}: {row[idx]}" for idx, col in enumerate(column_names))
        btn = ttk.Button(frame, text=button_text, command=lambda r=row: command_func(r))
        btn.pack(pady=5, anchor='n')

def show_table_in_window(data, headers, title="Table View"):
    win = Toplevel()
    win.title(title)
    frame = Frame(win)
    frame.pack(fill='both', expand=True)
    tree = ttk.Treeview(frame, columns=headers, show='headings')

    for header in headers:
        tree.heading(header, text=header)
        tree.column(header, width=150, anchor="center")

    for row in data:
        tree.insert('', 'end', values=row)

    tree.pack(fill='both', expand=True)

def show_details_in_window(row_data, detail_query_func):
    """Opens a new window and displays details based on the given row data."""
    detail_data = detail_query_func(row_data)
    if not detail_data:
        detail_data = [["No details available"]]
        headers = ["Message"]
    else:
        headers = [f"Column {i+1}" for i in range(len(detail_data[0]))]

    show_table_in_window(detail_data, headers, title="Details View")


def create_add_record_form(frame, headers, submit_func):
    """Generates a form for adding records to the database."""
    entries = {}
    for idx, header in enumerate(headers):
        lbl = ttk.Label(frame, text=f"{header}:")
        lbl.grid(row=idx, column=0, padx=5, pady=5, sticky='e')
        entry = ttk.Entry(frame)
        entry.grid(row=idx, column=1, padx=5, pady=5, sticky='w')
        entries[header] = entry

    def submit():
        record = {key: entry.get() for key, entry in entries.items()}
        submit_func(record)

    submit_btn = ttk.Button(frame, text="Submit", command=submit)
    submit_btn.grid(row=len(headers), columnspan=2, pady=10)

def delete_record(confirm_message, delete_func):
    """Asks for confirmation and deletes a record."""
    if askyesno("Confirm Deletion", confirm_message):
        delete_func()















# Логика для создания вкладки
"""
root = Tk()

root.geometry("600x500")

root.title("Рбаота с бд")

notebook = ttk.Notebook(root)
notebook.pack(fill=BOTH, expand=True)


tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="Партнеры")

# Вторая вкладка (Другая информация)
tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="Другая информация")
"""

#clear tkinter + psycopg2 Илья Харьковец
"""
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo
import psycopg2

# Подключение к базе данных
conn = psycopg2.connect(
    user="postgres",
    password="1234",
    host="localhost",
    port="5432",
    database="main_prac"
)
cursor = conn.cursor()

# Запросы к базе данных
partner_query = '''
SELECT p.Тип_партнера, p.Наименование_партнера, p.Директор, p.Телефон_партнера, p.Рейтинг,
    CASE 
        WHEN COALESCE(SUM(pp."Количество_продукции"), 0) <= 10000 THEN '0%'
        WHEN COALESCE(SUM(pp."Количество_продукции"), 0) <= 50000 THEN '5%'
        WHEN COALESCE(SUM(pp."Количество_продукции"), 0) <= 300000 THEN '10%'
        WHEN COALESCE(SUM(pp."Количество_продукции"), 0) > 300000 THEN '15%'
        ELSE '0%'
    END AS Скидка
FROM partners_import p
LEFT JOIN partner_products_import pp ON p.Наименование_партнера = pp.Наименование_партнера
GROUP BY p.Тип_партнера, p.Наименование_партнера, p.Директор, p.Телефон_партнера, p.Рейтинг
'''

# Функция для обновления списка партнеров и кнопок
def refresh_partners():
    global partner_data
    for widget in content_frame.winfo_children():
        widget.destroy()

    cursor.execute(partner_query)
    partner_data = cursor.fetchall()

    for i, partner in enumerate(partner_data):
        create_button(i)

    create_two_bnt()

# Функция для вывода покупок по партнеру
def show_purchases(partner_name):
    sales_query = '''SELECT Продукция FROM buys WHERE Наименование_партнера = %s'''
    cursor.execute(sales_query, (partner_name,))
    purchases = cursor.fetchall()
    purchases_list = "\n".join(row[0] for row in purchases) if purchases else "Нет данных о покупках"
    showinfo(title="Покупки", message=f"Покупки партнера {partner_name}:\n{purchases_list}")

# Создание кнопок
def create_button(partner_index):
    partner = partner_data[partner_index]
    partner_info = (
        f"{partner[0]} | {partner[1]}\n"
        f"Директор: {partner[2]}\n"
        f"Телефон: {partner[3]}\n"
        f"Рейтинг: {partner[4]}\n"
        f"Скидка: {partner[5]}"
    )
    btn = ttk.Button(
        content_frame,
        text=partner_info,
        width=50,
        command=lambda: show_purchases(partner[1])
    )
    btn.pack(pady=5, anchor=N)

# Окно добавления партнера
def add_partner_win():
    def add_partner():
        new_type = part_type_field.get()
        new_name = part_name_field.get()
        new_dir = der_name_field.get()
        new_phone = phone_num_field.get()
        new_rate = rate_field.get()

        if new_name:
            cursor.execute(
                '''INSERT INTO partners_import (Тип_партнера, Наименование_партнера, Директор, Телефон_партнера, Рейтинг)
                   VALUES (%s, %s, %s, %s, %s)''',
                (new_type, new_name, new_dir, new_phone, new_rate)
            )
            conn.commit()
            second_win.destroy()
            refresh_partners()
        else:
            showinfo(title="Ошибка", message="Наименование партнера обязательно для заполнения.")

    second_win = Toplevel(root)
    second_win.title("Добавление партнера")
    second_win.geometry("300x200")

    Label(second_win, text="Тип партнера: ").grid(row=0, column=0, pady=5)
    part_type_field = Entry(second_win)
    part_type_field.grid(row=0, column=1, pady=5)

    Label(second_win, text="Наименование партнера: ").grid(row=1, column=0, pady=5)
    part_name_field = Entry(second_win)
    part_name_field.grid(row=1, column=1, pady=5)

    Label(second_win, text="Директор: ").grid(row=2, column=0, pady=5)
    der_name_field = Entry(second_win)
    der_name_field.grid(row=2, column=1, pady=5)

    Label(second_win, text="Телефон: ").grid(row=3, column=0, pady=5)
    phone_num_field = Entry(second_win)
    phone_num_field.grid(row=3, column=1, pady=5)

    Label(second_win, text="Рейтинг: ").grid(row=4, column=0, pady=5)
    rate_field = Entry(second_win)
    rate_field.grid(row=4, column=1, pady=5)

    ttk.Button(second_win, text="Добавить", command=add_partner).grid(row=5, columnspan=2, pady=10)

# Окно удаления партнера
def del_partner_win():
    def del_partner():
        del_name = part_name_field.get()

        if del_name:
            cursor.execute('''DELETE FROM partners_import WHERE Наименование_партнера = %s''', (del_name,))
            conn.commit()
            third_win.destroy()
            refresh_partners()
        else:
            showinfo(title="Ошибка", message="Введите наименование партнера для удаления.")

    third_win = Toplevel(root)
    third_win.title("Удаление партнера")
    third_win.geometry("300x100")

    Label(third_win, text="Наименование партнера для удаления: ").grid(row=0, column=0, pady=5)
    part_name_field = Entry(third_win)
    part_name_field.grid(row=1, column=0, pady=5)

    ttk.Button(third_win, text="Удалить", command=del_partner).grid(row=2, column=0, pady=10)

# Создание кнопок для добавления и удаления
def create_two_bnt():
    del_btn = ttk.Button(
        content_frame,
        text="Удалить партнера",
        width=50,
        command=del_partner_win
    )
    del_btn.pack(anchor=S)

    add_btn = ttk.Button(
        content_frame,
        text="Добавить партнера",
        width=50,
        command=add_partner_win
    )
    add_btn.pack(anchor=S)

    partenr_win = ttk.Button(
        content_frame,
        text="Открыть таблицу парнеров",
        width=50,
        
    )

# Настройка окна
root = Tk()
root.geometry("800x600")
root.title("Практика 2024")

# Основной фрейм для контента
content_frame = Frame(root)
content_frame.pack(side=RIGHT, fill=BOTH, expand=True)

# Логотип (при наличии)
try:
    img = PhotoImage(file="logo.png")
    img = img.subsample(10, 10)  # Уменьшение размера изображения
    logo_label = Label(root, image=img)
    logo_label.pack(side=TOP, fill=Y)
    root.iconphoto(True, img)
except Exception:
    pass

# Инициализация списка партнеров и создание кнопок
partner_data = []
refresh_partners()

root.mainloop()

# Закрытие соединения с базой данных
cursor.close()
conn.close()
"""

#Харьковец 2
"""
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo
import psycopg2

# Подключение к базе данных
conn = psycopg2.connect(
    user="postgres",
    password="1234",
    host="localhost",
    port="5432",
    database="main_prac"
)
cursor = conn.cursor()

# Запросы к базе данных
partner_query = '''
SELECT p.Тип_партнера, p.Наименование_партнера, p.Директор, p.Телефон_партнера, p.Рейтинг,
    CASE 
        WHEN COALESCE(SUM(pp."Количество_продукции"), 0) <= 10000 THEN '0%'
        WHEN COALESCE(SUM(pp."Количество_продукции"), 0) <= 50000 THEN '5%'
        WHEN COALESCE(SUM(pp."Количество_продукции"), 0) <= 300000 THEN '10%'
        WHEN COALESCE(SUM(pp."Количество_продукции"), 0) > 300000 THEN '15%'
        ELSE '0%'
    END AS Скидка
FROM partners_import p
LEFT JOIN partner_products_import pp ON p.Наименование_партнера = pp.Наименование_партнера
GROUP BY p.Тип_партнера, p.Наименование_партнера, p.Директор, p.Телефон_партнера, p.Рейтинг
'''

product_query = '''
SELECT * FROM product_details_view
'''

def refresh_partners():
    global partner_data
    for widget in content_frame.winfo_children():
        widget.destroy()

    cursor.execute(partner_query)
    partner_data = cursor.fetchall()

    for i, partner in enumerate(partner_data):
        create_button(i)

    create_two_bnt()

def show_purchases(partner_name):
    sales_query = '''SELECT Продукция FROM buys WHERE Наименование_партнера = %s'''
    cursor.execute(sales_query, (partner_name,))
    purchases = cursor.fetchall()
    purchases_list = "\n".join(row[0] for row in purchases) if purchases else "Нет данных о покупках"
    showinfo(title="Покупки", message=f"Покупки партнера {partner_name}:\n{purchases_list}")

def create_button(partner_index):
    partner = partner_data[partner_index]
    partner_info = (
        f"{partner[0]} | {partner[1]}\n"
        f"Директор: {partner[2]}\n"
        f"Телефон: {partner[3]}\n"
        f"Рейтинг: {partner[4]}\n"
        f"Скидка: {partner[5]}"
    )
    btn = ttk.Button(
        content_frame,
        text=partner_info,
        width=50,
        command=lambda: show_purchases(partner[1])
    )
    btn.pack(pady=5, anchor=N)

    
def create_product_buttons():
    cursor.execute(product_query)
    products = cursor.fetchall()

    for product in products:
        product_info = (
            f"{product[1]} (Тип: {product[2]})\n"
            f"Цена: {product[3]} | Коэффициент: {product[4]}"
        )
        btn = ttk.Button(
            content_frame,
            text=product_info,
            width=50,
            command=lambda p=product: showinfo(title="Информация о продукте", message=str(p))
        )
        btn.pack(pady=5, anchor=N)
def window_with_products():
    cursor.execute('''
        SELECT 
            pi.Артикул, 
            pi.Наименование_продукции, 
            pi.Тип_продукции, 
            pi.Минимальная_стоимость_для_партнеров, 
            pt.Коэффициент_типа_продукции
        FROM products_import pi
        LEFT JOIN product_type_import pt ON pi.Тип_продукции = pt.Тип_продукции
    ''')
    products = cursor.fetchall()

    product_win = Toplevel(root)
    product_win.title("Продукция")
    product_win.geometry("800x600")

    product_frame = Frame(product_win)
    product_frame.pack(fill=BOTH, expand=True)

    for product in products:
        product_info = (
            f"Артикул: {product[0]}\n"
            f"Название: {product[1]}\n"
            f"Тип: {product[2]}\n"
            f"Цена: {product[3]} руб.\n"
            f"Коэффициент: {product[4]}"
        )
        btn = ttk.Button(
            product_frame,
            text=product_info,
            width=100,
            command=lambda p=product: show_buyers(p[1])
        )
        btn.pack(pady=5, anchor=N)

def show_buyers(product_name):
    buyers_query = '''
        SELECT p.Наименование_партнера, Директор 
        FROM partners_import p
        JOIN partner_products_import pp ON p.Наименование_партнера = pp.Наименование_партнера
        WHERE pp.Продукция = %s
    '''
    cursor.execute(buyers_query, (product_name,))
    buyers = cursor.fetchall()

    if buyers:
        buyers_list = "\n".join(f"{row[0]} (Директор: {row[1]})" for row in buyers)
    else:
        buyers_list = "Нет данных о покупателях"

    showinfo(
        title="Покупатели продукта",
        message=f"Покупатели продукта {product_name}:\n{buyers_list}"
    )



def add_partner_win():
    def add_partner():
        new_type = part_type_field.get()
        new_name = part_name_field.get()
        new_dir = der_name_field.get()
        new_phone = phone_num_field.get()
        new_rate = rate_field.get()

        if new_name:
            cursor.execute(
                '''INSERT INTO partners_import (Тип_партнера, Наименование_партнера, Директор, Телефон_партнера, Рейтинг)
                   VALUES (%s, %s, %s, %s, %s)''',
                (new_type, new_name, new_dir, new_phone, new_rate)
            )
            conn.commit()
            second_win.destroy()
            refresh_partners()
        else:
            showinfo(title="Ошибка", message="Наименование партнера обязательно для заполнения.")

    second_win = Toplevel(root)
    second_win.title("Добавление партнера")
    second_win.geometry("300x200")

    Label(second_win, text="Тип партнера: ").grid(row=0, column=0, pady=5)
    part_type_field = Entry(second_win)
    part_type_field.grid(row=0, column=1, pady=5)

    Label(second_win, text="Наименование партнера: ").grid(row=1, column=0, pady=5)
    part_name_field = Entry(second_win)
    part_name_field.grid(row=1, column=1, pady=5)

    Label(second_win, text="Директор: ").grid(row=2, column=0, pady=5)
    der_name_field = Entry(second_win)
    der_name_field.grid(row=2, column=1, pady=5)

    Label(second_win, text="Телефон: ").grid(row=3, column=0, pady=5)
    phone_num_field = Entry(second_win)
    phone_num_field.grid(row=3, column=1, pady=5)

    Label(second_win, text="Рейтинг: ").grid(row=4, column=0, pady=5)
    rate_field = Entry(second_win)
    rate_field.grid(row=4, column=1, pady=5)

    ttk.Button(second_win, text="Добавить", command=add_partner).grid(row=5, columnspan=2, pady=10)

# Окно удаления партнера
def del_partner_win():
    def del_partner():
        del_name = part_name_field.get()

        if del_name:
            cursor.execute('''DELETE FROM partners_import WHERE Наименование_партнера = %s''', (del_name,))
            conn.commit()
            third_win.destroy()
            refresh_partners()
        else:
            showinfo(title="Ошибка", message="Введите наименование партнера для удаления.")

    third_win = Toplevel(root)
    third_win.title("Удаление партнера")
    third_win.geometry("300x100")

    Label(third_win, text="Наименование партнера для удаления: ").grid(row=0, column=0, pady=5)
    part_name_field = Entry(third_win)
    part_name_field.grid(row=1, column=0, pady=5)

    ttk.Button(third_win, text="Удалить", command=del_partner).grid(row=2, column=0, pady=10)

def partner_win_open():
    query1 = '''SELECT * FROM partners_import'''
    cursor.execute(query1)
    rows = cursor.fetchall()

    cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = 'partners_import';")
    headers = [row[0] for row in cursor.fetchall()]

    fourth_win = Toplevel(root)
    fourth_win.title("Просмотр партнеров")
    fourth_win.geometry("1200x400")

    frame = ttk.Frame(fourth_win)
    frame.pack(fill='both', expand=True)

    tree = ttk.Treeview(frame, columns=headers, show='headings', height=20)

    for header in headers:
        tree.heading(header, text=header)
        tree.column(header, width=150, anchor="center")  # Увеличиваем ширину столбцов для крупных данных

    for row in rows:
        tree.insert("", "end", values=row)

    h_scrollbar = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(xscrollcommand=h_scrollbar.set)
    h_scrollbar.pack(side="bottom", fill="x")

    v_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=v_scrollbar.set)
    v_scrollbar.pack(side="right", fill="y")

    tree.pack(fill='both', expand=True)

def buys_win_open():
    query1 = '''SELECT * FROM buys'''
    cursor.execute(query1)
    rows = cursor.fetchall()

    cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = 'buys';")
    headers = [row[0] for row in cursor.fetchall()]

    fifth_win = Toplevel(root)
    fifth_win.title("Просмотр покупок")
    fifth_win.geometry("1200x400")

    frame = ttk.Frame(fifth_win)
    frame.pack(fill='both', expand=True)

    tree = ttk.Treeview(frame, columns=headers, show='headings', height=20)

    for header in headers:
        tree.heading(header, text=header)
        tree.column(header, width=150, anchor="center")  # Увеличиваем ширину столбцов для крупных данных

    for row in rows:
        tree.insert("", "end", values=row)

    h_scrollbar = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(xscrollcommand=h_scrollbar.set)
    h_scrollbar.pack(side="bottom", fill="x")

    v_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=v_scrollbar.set)
    v_scrollbar.pack(side="right", fill="y")

    tree.pack(fill='both', expand=True)

def mat_and_part():
    query1 = '''SELECT * FROM partner_material_prices'''
    cursor.execute(query1)
    rows = cursor.fetchall()

    cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = 'partner_material_prices';")
    headers = [row[0] for row in cursor.fetchall()]

    fifth_win = Toplevel(root)
    fifth_win.title("Просмотр материалов и цен")
    fifth_win.geometry("1200x400")

    frame = ttk.Frame(fifth_win)
    frame.pack(fill='both', expand=True)

    tree = ttk.Treeview(frame, columns=headers, show='headings', height=20)

    for header in headers:
        tree.heading(header, text=header)
        tree.column(header, width=150, anchor="center")  # Увеличиваем ширину столбцов для крупных данных

    for row in rows:
        tree.insert("", "end", values=row)

    h_scrollbar = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(xscrollcommand=h_scrollbar.set)
    h_scrollbar.pack(side="bottom", fill="x")

    v_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=v_scrollbar.set)
    v_scrollbar.pack(side="right", fill="y")

    tree.pack(fill='both', expand=True)

def create_two_bnt():
    del_btn = ttk.Button(
        content_frame,
        text="Удалить партнера",
        width=50,
        command=del_partner_win
    )
    del_btn.pack(anchor=S)

    add_btn = ttk.Button(
        content_frame,
        text="Добавить партнера",
        width=50,
        command=add_partner_win
    )
    add_btn.pack(anchor=S)

    partenr_win = ttk.Button(
        content_frame,
        text="Открыть таблицу партнеров",
        width=50,
        command=partner_win_open
    )
    partenr_win.pack(anchor=S)

    buys_win = ttk.Button(
        content_frame,
        text="Открыть все покупки",
        width=50,
        command=buys_win_open
    )
    buys_win.pack(anchor=S)

    prices_part = ttk.Button(
        content_frame,
        text="Открыть все цены для парнеров",
        width=50,
        command=mat_and_part
    )
    prices_part.pack(anchor=S)

    win_with_products = ttk.Button(
        content_frame,
        text="Открыть окно со всей продукцией",
        width=50,
        command=window_with_products
    )
    win_with_products.pack(anchor=S)

# Настройка окна
root = Tk()
root.geometry("1000x650")
root.title("Практика 2024")

content_frame = Frame(root)
content_frame.pack(side=RIGHT, fill=BOTH, expand=True)

try:
    img = PhotoImage(file="logo.png")
    img = img.subsample(10, 10)
    logo_label = Label(root, image=img)
    logo_label.pack(side=TOP, fill=Y)
    root.iconphoto(True, img)
except Exception:
    pass

partner_data = []
refresh_partners()

root.mainloop()

cursor.close()
conn.close()


"""


#Щерба

"""
import tkinter as tk
from tkinter import ttk
import psycopg2

class PostgresApp:
    def init(self, root):  # Исправлено: двойное подчеркивание
        self.root = root
        self.root.title("PostgreSQL Viewer")
        
        # Параметры подключения
        self.conn = psycopg2.connect(
            host='localhost',
            dbname='teh2',
            user='postgres',
            password='1488',
            port='5432'
        )
        self.cur = self.conn.cursor()
        
        # Создание интерфейса
        frame = ttk.Frame(root)
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frame, text="Table:").pack(side=tk.LEFT)
        self.table = ttk.Combobox(frame, state='readonly')
        self.table.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.table.bind('<<ComboboxSelected>>', self.load_data)
        
        self.tree = ttk.Treeview(root, show='headings')
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Загрузка списка таблиц
        self.cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        self.table['values'] = [t[0] for t in self.cur.fetchall()]
        if self.table['values']:  # Проверка наличия таблиц
            self.table.current(0)
            self.load_data()

    def load_data(self, event=None):
        t = self.table.get()
        self.tree.delete(*self.tree.get_children())
        self.cur.execute(f"SELECT * FROM {t} LIMIT 100")
        
        # Настройка колонок
        self.tree['columns'] = [desc[0] for desc in self.cur.description]
        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Загрузка данных
        for row in self.cur.fetchall():
            self.tree.insert('', tk.END, values=row)

    def del(self):  # Исправлено: двойное подчеркивание
        self.conn.close()

if name == "main":  # Исправлено: правильное условие
    root = tk.Tk()
    app = PostgresApp(root)
    root.mainloop()
"""

#Павлов
"""
import tkinter as tk
from tkinter import messagebox, simpledialog
import psycopg2
from psycopg2 import Error

# --- Новые настройки подключения к БД ---
DB_NAME = "Database1"
DB_USER = "postgres"
DB_PASSWORD = "1111"
DB_HOST = "localhost"
DB_PORT = "5432"

class NewNamesDBApp:
    def __init__(self, master):
        self.master = master
        master.title("Управление Пользователями и Заказами")
        master.geometry("450x400") # Немного увеличим окно

        self.conn = None
        self.cursor = None
        self.connect_db()

        # Кнопки для Пользователей
        tk.Label(master, text="Управление Пользователями", font=("Arial", 12, "bold")).pack(pady=5)
        tk.Button(master, text="Добавить Пользователя", command=self.add_user).pack(pady=2)
        tk.Button(master, text="Показать Пользователей", command=self.view_users).pack(pady=2)
        tk.Button(master, text="Удалить Пользователя", command=self.delete_user).pack(pady=2)

        tk.Frame(master, height=2, bd=1, relief="sunken").pack(fill="x", padx=10, pady=10)

        # Кнопки для Заказов
        tk.Label(master, text="Управление Заказами", font=("Arial", 12, "bold")).pack(pady=5)
        tk.Button(master, text="Добавить Заказ", command=self.add_order).pack(pady=2)
        tk.Button(master, text="Показать Заказы", command=self.view_orders).pack(pady=2)
        tk.Button(master, text="Удалить Заказ", command=self.delete_order).pack(pady=2)
        tk.Button(master, text="Показать Заказы Пользователя", command=self.view_user_orders).pack(pady=2)


        tk.Button(master, text="Выйти", command=self.on_closing).pack(pady=10)
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def connect_db(self):
        try:
            self.conn = psycopg2.connect(
                dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
            )
            self.cursor = self.conn.cursor()
            messagebox.showinfo("Подключение", f"Успешное подключение к БД '{DB_NAME}'!")
        except Error as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться: {e}\nЗапустите PostgreSQL и проверьте настройки.")
            self.master.destroy()

    def close_db(self):
        if self.cursor: self.cursor.close()
        if self.conn: self.conn.close()
        messagebox.showinfo("Отключение", "Соединение с БД закрыто.")

    def on_closing(self):
        if messagebox.askokcancel("Выход", "Выйти из приложения?"):
            self.close_db()
            self.master.destroy()

    # --- Методы для Пользователей (таблица AppUsers) ---
    def add_user(self):
        username = simpledialog.askstring("Добавить Пользователя", "Введите имя пользователя:")
        if not username: return
        email = simpledialog.askstring("Добавить Пользователя", "Введите email пользователя:")
        if not email: return
        try:
            self.cursor.execute(
                "INSERT INTO AppUsers (username, email) VALUES (%s, %s)",
                (username, email)
            )
            self.conn.commit()
            messagebox.showinfo("Успех", f"Пользователь '{username}' добавлен.")
        except Error as e:
            self.conn.rollback()
            messagebox.showerror("Ошибка", f"Не удалось добавить пользователя: {e}\n(Имя пользователя может быть занято)")

    def view_users(self):
        try:
            self.cursor.execute("SELECT user_id, username, email FROM AppUsers ORDER BY user_id")
            users = self.cursor.fetchall()
            if not users:
                messagebox.showinfo("Пользователи", "В базе данных нет пользователей.")
                return
            info = "Пользователи:\n" + "\n".join([f"ID: {u[0]}, Имя: {u[1]}, Email: {u[2]}" for u in users])
            messagebox.showinfo("Список Пользователей", info)
        except Error as e:
            messagebox.showerror("Ошибка", f"Не удалось получить список пользователей: {e}")

    def delete_user(self):
        user_id_str = simpledialog.askstring("Удалить Пользователя", "Введите ID пользователя для удаления:")
        if not user_id_str: return
        try:
            user_id = int(user_id_str)
        except ValueError:
            messagebox.showerror("Ошибка ввода", "ID должен быть числом.")
            return

        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить пользователя с ID {user_id}?"):
            try:
                self.cursor.execute("DELETE FROM AppUsers WHERE user_id = %s", (user_id,))
                self.conn.commit()
                if self.cursor.rowcount > 0:
                    messagebox.showinfo("Успех", f"Пользователь с ID {user_id} удален.")
                else:
                    messagebox.showwarning("Не найдено", f"Пользователь с ID {user_id} не найден.")
            except Error as e:
                self.conn.rollback()
                messagebox.showerror("Ошибка", f"Не удалось удалить пользователя. Возможно, у него есть заказы (FOREIGN KEY): {e}")

    # --- Методы для Заказов (таблица CustomerOrders) ---
    def add_order(self):
        order_desc = simpledialog.askstring("Добавить Заказ", "Введите описание заказа:")
        if not order_desc: return
        user_id_str = simpledialog.askstring("Добавить Заказ", "Введите ID пользователя для заказа (ОБЯЗАТЕЛЬНО!):")
        if not user_id_str: return
        order_amount_str = simpledialog.askstring("Добавить Заказ", "Введите сумму заказа (например, 123.45):")
        if not order_amount_str: return

        try:
            user_id = int(user_id_str)
            order_amount = float(order_amount_str) # Сумма может быть дробной
        except ValueError:
            messagebox.showerror("Ошибка ввода", "ID пользователя должен быть числом, сумма - числом (например, 123.45).")
            return

        try:
            self.cursor.execute(
                "INSERT INTO CustomerOrders (order_description, user_id, order_amount) VALUES (%s, %s, %s)",
                (order_desc, user_id, order_amount)
            )
            self.conn.commit()
            messagebox.showinfo("Успех", f"Заказ '{order_desc}' добавлен.")
        except Error as e:
            self.conn.rollback()
            messagebox.showerror("Ошибка", f"Не удалось добавить заказ: {e}\n(Проверьте, существует ли ID пользователя)")

    def view_orders(self):
        try:
            self.cursor.execute('''
                SELECT co.order_id, co.order_description, co.order_amount, au.username
                FROM CustomerOrders AS co
                JOIN AppUsers AS au ON co.user_id = au.user_id
                ORDER BY co.order_id
            ''')
            orders = self.cursor.fetchall()
            if not orders:
                messagebox.showinfo("Заказы", "В базе данных нет заказов.")
                return
            info = "Заказы:\n" + "\n".join([f"ID: {o[0]}, '{o[1]}' (Сумма: {o[2]:.2f}, Пользователь: {o[3]})" for o in orders])
            messagebox.showinfo("Список Заказов", info)
        except Error as e:
            messagebox.showerror("Ошибка", f"Не удалось получить список заказов: {e}")

    def delete_order(self):
        order_id_str = simpledialog.askstring("Удалить Заказ", "Введите ID заказа для удаления:")
        if not order_id_str: return
        try:
            order_id = int(order_id_str)
        except ValueError:
            messagebox.showerror("Ошибка ввода", "ID должен быть числом.")
            return

        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить заказ с ID {order_id}?"):
            try:
                self.cursor.execute("DELETE FROM CustomerOrders WHERE order_id = %s", (order_id,))
                self.conn.commit()
                if self.cursor.rowcount > 0:
                    messagebox.showinfo("Успех", f"Заказ с ID {order_id} удален.")
                else:
                    messagebox.showwarning("Не найдено", f"Заказ с ID {order_id} не найден.")
            except Error as e:
                self.conn.rollback()
                messagebox.showerror("Ошибка", f"Не удалось удалить заказ: {e}")

    def view_user_orders(self):
        user_id_str = simpledialog.askstring("Заказы Пользователя", "Введите ID пользователя, чьи заказы хотите посмотреть:")
        if not user_id_str: return
        try:
            user_id = int(user_id_str)
        except ValueError:
            messagebox.showerror("Ошибка ввода", "ID должен быть числом.")
            return

        try:
            # Сначала проверяем, существует ли пользователь
            self.cursor.execute("SELECT username FROM AppUsers WHERE user_id = %s", (user_id,))
            user_name = self.cursor.fetchone()
            if not user_name:
                messagebox.showwarning("Пользователь не найден", f"Пользователь с ID {user_id} не найден.")
                return

            self.cursor.execute('''
                SELECT order_id, order_description, order_amount
                FROM CustomerOrders
                WHERE user_id = %s
                ORDER BY order_id
            ''', (user_id,))
            orders = self.cursor.fetchall()

            if not orders:
                messagebox.showinfo("Заказы Пользователя", f"У пользователя '{user_name[0]}' нет заказов.")
                return

            info = f"Заказы пользователя '{user_name[0]}':\n" + "\n".join([f"ID: {o[0]}, '{o[1]}' (Сумма: {o[2]:.2f})" for o in orders])
            messagebox.showinfo("Заказы Пользователя", info)

        except Error as e:
            messagebox.showerror("Ошибка", f"Не удалось получить заказы пользователя: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NewNamesDBApp(root)
    root.mainloop()

   
import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3 # Built-in Python library for SQLite

# --- 1. Database File Configuration ---
DB_FILE = "my_company_sqlite.db" # The SQLite database will be stored in this file

class SQLiteUsersOrdersApp:
    def __init__(self, master):
        self.master = master
        master.title("Управление Пользователями и Заказами (SQLite)")
        master.geometry("450x400")

        self.conn = None
        self.cursor = None

        self.connect_db() # Connect to DB and create tables if they don't exist

        # --- 2. Create Interaction Buttons ---
        # Buttons for Users
        tk.Label(master, text="Управление Пользователями", font=("Arial", 12, "bold")).pack(pady=5)
        tk.Button(master, text="Добавить Пользователя", command=self.add_user).pack(pady=2)
        tk.Button(master, text="Показать Пользователей", command=self.view_users).pack(pady=2)
        tk.Button(master, text="Удалить Пользователя", command=self.delete_user).pack(pady=2)

        tk.Frame(master, height=2, bd=1, relief="sunken").pack(fill="x", padx=10, pady=10)

        # Buttons for Orders
        tk.Label(master, text="Управление Заказами", font=("Arial", 12, "bold")).pack(pady=5)
        tk.Button(master, text="Добавить Заказ", command=self.add_order).pack(pady=2)
        tk.Button(master, text="Показать Все Заказы", command=self.view_all_orders).pack(pady=2)
        tk.Button(master, text="Показать Заказы Пользователя", command=self.view_user_orders).pack(pady=2)
        tk.Button(master, text="Удалить Заказ", command=self.delete_order).pack(pady=2)


        tk.Button(master, text="Выйти", command=self.on_closing).pack(pady=10)

        # --- 3. Handle Window Closing Event ---
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    # --- Database Connection and Setup Functions ---
    def connect_db(self):
        try:
            # Connect to the DB file. If the file doesn't exist, it will be created.
            self.conn = sqlite3.connect(DB_FILE)
            self.cursor = self.conn.cursor()

            # IMPORTANT: Enable foreign key support for SQLite
            # This must be done for each connection.
            self.cursor.execute("PRAGMA foreign_keys = ON;")

            # Create tables if they don't exist
            # AppUsers table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS AppUsers (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL
                );
            ''')
            # CustomerOrders table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS CustomerOrders (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_description TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    order_amount REAL NOT NULL, -- REAL for floating point numbers (decimals)
                    FOREIGN KEY (user_id) REFERENCES AppUsers (user_id) ON DELETE RESTRICT
                );
            ''')
            self.conn.commit() # Save the table creation
            messagebox.showinfo("Успех", f"Подключение к БД SQLite '{DB_FILE}' успешно!\nТаблицы созданы/проверены.")
        except sqlite3.Error as e: # Catch SQLite specific errors
            messagebox.showerror("Ошибка", f"Не удалось подключиться к БД SQLite: {e}")
            self.master.destroy()

    def close_db(self):

        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        messagebox.showinfo("Готово", "Соединение с БД закрыто.")

    def on_closing(self):
        if messagebox.askokcancel("Выход", "Выйти из приложения?"):
            self.close_db()
            self.master.destroy()

    # --- Methods for Users (AppUsers table) ---
    def add_user(self):
        username = simpledialog.askstring("Добавить Пользователя", "Введите имя пользователя:")
        if not username: return
        email = simpledialog.askstring("Добавить Пользователя", "Введите email пользователя:")
        if not email: return
        try:
            self.cursor.execute(
                "INSERT INTO AppUsers (username, email) VALUES (?, ?)", # Use '?' for placeholders in SQLite
                (username, email)
            )
            self.conn.commit()
            messagebox.showinfo("Успех", f"Пользователь '{username}' добавлен.")
        except sqlite3.IntegrityError as e: # Catch specific error for UNIQUE constraint
            self.conn.rollback()
            messagebox.showerror("Ошибка", f"Не удалось добавить пользователя: Имя пользователя '{username}' уже занято.")
        except sqlite3.Error as e:
            self.conn.rollback()
            messagebox.showerror("Ошибка", f"Не удалось добавить пользователя: {e}")

    def view_users(self):
        try:
            self.cursor.execute("SELECT user_id, username, email FROM AppUsers ORDER BY user_id")
            users = self.cursor.fetchall()
            if not users:
                messagebox.showinfo("Пользователи", "В базе данных нет пользователей.")
                return
            info = "Пользователи:\n" + "\n".join([f"ID: {u[0]}, Имя: {u[1]}, Email: {u[2]}" for u in users])
            messagebox.showinfo("Список Пользователей", info)
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось получить список пользователей: {e}")

    def delete_user(self):
        user_id_str = simpledialog.askstring("Удалить Пользователя", "Введите ID пользователя для удаления:")
        if not user_id_str: return
        try:
            user_id = int(user_id_str)
        except ValueError:
            messagebox.showerror("Ошибка ввода", "ID должен быть числом.")
            return

        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить пользователя с ID {user_id}?"):
            try:
                self.cursor.execute("DELETE FROM AppUsers WHERE user_id = ?", (user_id,))
                self.conn.commit()
                if self.cursor.rowcount > 0:
                    messagebox.showinfo("Успех", f"Пользователь с ID {user_id} удален.")
                else:
                    messagebox.showwarning("Не найдено", f"Пользователь с ID {user_id} не найден.")
            except sqlite3.IntegrityError as e: # Catch specific error for FOREIGN KEY constraint
                self.conn.rollback()
                messagebox.showerror("Ошибка", f"Не удалось удалить пользователя: У него есть заказы, связанные с ним. {e}")
            except sqlite3.Error as e:
                self.conn.rollback()
                messagebox.showerror("Ошибка", f"Не удалось удалить пользователя: {e}")

    # --- Methods for Orders (CustomerOrders table) ---
    def add_order(self):
        order_desc = simpledialog.askstring("Добавить Заказ", "Введите описание заказа:")
        if not order_desc: return
        user_id_str = simpledialog.askstring("Добавить Заказ", "Введите ID пользователя для заказа (ОБЯЗАТЕЛЬНО!):")
        if not user_id_str: return
        order_amount_str = simpledialog.askstring("Добавить Заказ", "Введите сумму заказа (например, 123.45):")
        if not order_amount_str: return

        try:
            user_id = int(user_id_str)
            order_amount = float(order_amount_str) # REAL in SQLite stores floats
        except ValueError:
            messagebox.showerror("Ошибка ввода", "ID пользователя должен быть целым числом, сумма - числом (например, 123.45).")
            return

        try:
            self.cursor.execute(
                "INSERT INTO CustomerOrders (order_description, user_id, order_amount) VALUES (?, ?, ?)",
                (order_desc, user_id, order_amount)
            )
            self.conn.commit()
            messagebox.showinfo("Успех", f"Заказ '{order_desc}' добавлен.")
        except sqlite3.IntegrityError as e: # Catch specific error for FOREIGN KEY (user_id not found)
            self.conn.rollback()
            messagebox.showerror("Ошибка", f"Не удалось добавить заказ: Пользователь с ID {user_id} не найден.")
        except sqlite3.Error as e:
            self.conn.rollback()
            messagebox.showerror("Ошибка", f"Не удалось добавить заказ: {e}")

    def view_all_orders(self):
        try:
            self.cursor.execute('''
                SELECT co.order_id, co.order_description, co.order_amount, au.username
                FROM CustomerOrders AS co
                JOIN AppUsers AS au ON co.user_id = au.user_id
                ORDER BY co.order_id
            ''')
            orders = self.cursor.fetchall()
            if not orders:
                messagebox.showinfo("Заказы", "В базе данных нет заказов.")
                return
            info = "Заказы:\n" + "\n".join([f"ID: {o[0]}, '{o[1]}' (Сумма: {o[2]:.2f}, Пользователь: {o[3]})" for o in orders])
            messagebox.showinfo("Список Всех Заказов", info)
        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось получить список заказов: {e}")

    def view_user_orders(self):
        user_id_str = simpledialog.askstring("Заказы Пользователя", "Введите ID пользователя, чьи заказы хотите посмотреть:")
        if not user_id_str: return
        try:
            user_id = int(user_id_str)
        except ValueError:
            messagebox.showerror("Ошибка ввода", "ID должен быть числом.")
            return

        try:
            # First, check if the user exists
            self.cursor.execute("SELECT username FROM AppUsers WHERE user_id = ?", (user_id,))
            user_name = self.cursor.fetchone()
            if not user_name:
                messagebox.showwarning("Пользователь не найден", f"Пользователь с ID {user_id} не найден.")
                return

            self.cursor.execute('''
                SELECT order_id, order_description, order_amount
                FROM CustomerOrders
                WHERE user_id = ?
                ORDER BY order_id
            ''', (user_id,))
            orders = self.cursor.fetchall()

            if not orders:
                messagebox.showinfo("Заказы Пользователя", f"У пользователя '{user_name[0]}' нет заказов.")
                return

            info = f"Заказы пользователя '{user_name[0]}':\n" + "\n".join([f"ID: {o[0]}, '{o[1]}' (Сумма: {o[2]:.2f})" for o in orders])
            messagebox.showinfo("Заказы Пользователя", info)

        except sqlite3.Error as e:
            messagebox.showerror("Ошибка", f"Не удалось получить заказы пользователя: {e}")

    def delete_order(self):
        order_id_str = simpledialog.askstring("Удалить Заказ", "Введите ID заказа для удаления:")
        if not order_id_str: return
        try:
            order_id = int(order_id_str)
        except ValueError:
            messagebox.showerror("Ошибка ввода", "ID должен быть числом.")
            return

        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить заказ с ID {order_id}?"):
            try:
                self.cursor.execute("DELETE FROM CustomerOrders WHERE order_id = ?", (order_id,))
                self.conn.commit()
                if self.cursor.rowcount > 0:
                    messagebox.showinfo("Успех", f"Заказ с ID {order_id} удален.")
                else:
                    messagebox.showwarning("Не найдено", f"Заказ с ID {order_id} не найден.")
            except sqlite3.Error as e:
                self.conn.rollback()
                messagebox.showerror("Ошибка", f"Не удалось удалить заказ: {e}")

# --- 4. Run the Application ---
if __name__ == "__main__":
    root = tk.Tk()
    app = SQLiteUsersOrdersApp(root)
    root.mainloop()
"""

#Радзивилов
"""
Turron
using Npgsql;
using System.Data;
namespace Partners_program_1
{
    public partial class Form1 : Form
    {
        static string connString = "Host=localhost;Username=postgres;Password=postgres;Database=Partners";
        public NpgsqlConnection nc = new NpgsqlConnection(connString);

        List<Button> PartnersButtonsList = new List<Button>();
        List<Button> ProductionButtonsList = new List<Button>();

        public Form1()
        {
            InitializeComponent();
        }

        public void UpdateData()
        {
            try
            {
                // Партнёры
                foreach (var button in PartnersButtonsList)
                {
                    tabPage1.Controls.Remove(button);
                }
                PartnersButtonsList.Clear();

                NpgsqlCommand npgc = new NpgsqlCommand("select partners.id, partners_types.type, name, director, phone, rating, coalesce(sum(amount), 0) as sum from partners join partners_types on (partners.type = partners_types.id) left join sales on (partners.id = sales.partner_id)group by partners.id, partners_types.type, name, director, phone, rating order by partners.id", nc);
                NpgsqlDataReader reader = npgc.ExecuteReader();

                DataTable dtPartners = new DataTable();
                dtPartners.Load(reader);

                int top = 10;
                int left = 10;

                DataRow partnersRow;

                for (int i = 0; i < dtPartners.Rows.Count; i++)
                {
                    partnersRow = dtPartners.Rows[i];

                    Button buttonPartner = new Button();
                    buttonPartner.Left = left;
                    buttonPartner.Top = top;
                    buttonPartner.Width = 600;
                    buttonPartner.Height = 110;
                    buttonPartner.Padding = new Padding(10);
                    buttonPartner.TextAlign = ContentAlignment.TopLeft;
                    buttonPartner.Name = $"partnerButton{i}";

                    int discount = 0;
                    int salesSum = Convert.ToInt32(partnersRow[6]);
                    if (salesSum < 10000)
                        discount = 0;
                    else if (salesSum > 10000 && salesSum < 50000)
                        discount = 5;
                    else if (salesSum > 50000 && salesSum < 300000)
                        discount = 10;
                    else if (salesSum > 300000)
                        discount = 15;

                    buttonPartner.Text = $"{partnersRow[1]} | {partnersRow[2]}         {discount}%\r\n" +
                        $"{partnersRow[3]}\r\n" +
                        $"{partnersRow[4]}\r\n" +
                        $"Рейтинг: {partnersRow[5]}\r\n";

                    tabPage1.Controls.Add(buttonPartner);
                    top += buttonPartner.Height + 20;

                    PartnersButtonsList.Add(buttonPartner);
                }
                //Продукция
                foreach (var button in ProductionButtonsList)
                {
                    tabPage2.Controls.Remove(button);
                }
                ProductionButtonsList.Clear();

                npgc = npgc = new NpgsqlCommand("select name, min_price, article, production_types.type, coefficient from production join production_types on (production_types.id = production.type) order by production.id", nc);
                reader = npgc.ExecuteReader();

                DataTable dtProduction = new DataTable();
                dtProduction.Load(reader);

                DataRow productionRow;

                top = 10;

                for (int i = 0; i < dtProduction.Rows.Count; i++)
                {
                    productionRow = dtProduction.Rows[i];

                    Button buttonProduction = new Button();
                    buttonProduction.Left = left;
                    buttonProduction.Top = top;
                    buttonProduction.Width = 600;
                    buttonProduction.Height = 135;
                    buttonProduction.Padding = new Padding(10);
                    buttonProduction.TextAlign = ContentAlignment.TopLeft;
                    buttonProduction.Name = $"productionButton{i}";

                    buttonProduction.Text = $"{productionRow[0]}\r\n" +
                        $"Минимальная цена: {productionRow[1]}\r\n" +
                        $"{productionRow[2]}\r\n" +
                        $"{productionRow[3]}\r\n" +
                        $"Коэффициент: {productionRow[4]}";

                    tabPage2.Controls.Add(buttonProduction);
                    top += buttonProduction.Height + 20;

                    ProductionButtonsList.Add(buttonProduction);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            nc.Open();
            UpdateData();
        }

        private void button1_Click(object sender, EventArgs e)
        {
            var f = new FormAddPartner();
            f.Show();
        }

        private void Form1_Activated(object sender, EventArgs e)
        {
            UpdateData();
        }

        private void Form1_Enter(object sender, EventArgs e)
        {
            UpdateData();
        }

        private void buttonChaneProducion_Click(object sender, EventArgs e)
        {
            var f = new FormAddProduction();
            f.Show();
        }
    }
}
using Npgsql;
using System.Data;
namespace Partners_program_1
{
    public partial class FormAddPartner : Form
    {
        static string connString = "Host=localhost;Username=postgres;Password=postgres;Database=Partners";
        NpgsqlConnection nc = new NpgsqlConnection(connString);

        private int selectedRowId;

        public FormAddPartner()
        {
            InitializeComponent();
        }

        private void UpdateTable()
        {
            try
            {
                dataGridView1.Columns.Clear();
                dataGridView1.Rows.Clear();
                NpgsqlDataAdapter adapter = new NpgsqlDataAdapter("select partners.id, partners_types.type, name, director, email, phone, address, inn, rating from partners join partners_types on (partners.type = partners_types.id) \r\norder by partners.id", nc);
                DataSet dsPartnres = new DataSet();
                adapter.Fill(dsPartnres);
                DataTable dtPartners = dsPartnres.Tables[0];
                foreach (DataColumn column in dtPartners.Columns)
                {
                    dataGridView1.Columns.Add(column.ColumnName, column.ColumnName);
                }
                foreach (DataRow row in dtPartners.Rows)
                {
                    var rowAsArray = row.ItemArray;
                    dataGridView1.Rows.Add(rowAsArray);
                }
                dataGridView1.Columns[0].Width = 50;
                dataGridView1.Columns[6].Width = 250;

                comboBox1.Items.Clear();
                adapter = new NpgsqlDataAdapter("select * from partners_types", nc);
                DataSet dsPartnresTypes = new DataSet();
                adapter.Fill(dsPartnresTypes);
                DataTable dtPartnersTypes = dsPartnresTypes.Tables[0];

                foreach (DataRow row in dtPartnersTypes.Rows)
                {
                    var rowAsArray = row.ItemArray;
                    comboBox1.Items.Add(rowAsArray[1]);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }

        private void FormAddPartner_Load(object sender, EventArgs e)
        {
            nc.Open();
            UpdateTable();
        }

        private void buttonAdd_Click(object sender, EventArgs e)
        {
            string[] rowToInsert = { textBoxId.Text, comboBox1.Text, textBoxName.Text,
                textBoxDirector.Text, textBoxEmail.Text, textBoxPhone.Text, textBoxAddress.Text,
                textBoxInn.Text, numericRating.Text};

            try
            {
                for (int i = 0; i < rowToInsert.Length; i++)
                {
                    var value = rowToInsert[i];
                    if (value == "" && i != 0)
                    {
                        throw new Exception("Не все данные введены.\r\nЗаполните все поля и повторите попытку.");
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message, "Ошибка");
            }

            NpgsqlDataAdapter adapter = new NpgsqlDataAdapter("select * from partners_types", nc);
            DataSet dsPartnresTypes = new DataSet();
            adapter.Fill(dsPartnresTypes);
            DataTable dtPartnersTypes = dsPartnresTypes.Tables[0];

            foreach (DataRow row in dtPartnersTypes.Rows)
            {
                if (row[1].ToString() == rowToInsert[1])
                    rowToInsert[1] = row[0].ToString();
            }

            NpgsqlCommand npgc;

            if (rowToInsert[0] == "")
            {
                npgc = new NpgsqlCommand($"insert into partners values (default, {rowToInsert[1]}, '{rowToInsert[2]}', '{rowToInsert[3]}', '{rowToInsert[4]}', '{rowToInsert[5]}', '{rowToInsert[6]}', '{rowToInsert[7]}', {rowToInsert[8]})", nc);
                // insert into partners (type, name, director, email, phone, address, inn, rating) values ({rowToInsert[1]}, '{rowToInsert[2]}', '{rowToInsert[3]}', '{rowToInsert[4]}', '{rowToInsert[5]}', '{rowToInsert[6]}', '{rowToInsert[7]}', {rowToInsert[8]})
            }
            else
            {
                npgc = new NpgsqlCommand($"insert into partners values ({rowToInsert[0]}, {rowToInsert[1]}, '{rowToInsert[2]}', '{rowToInsert[3]}', '{rowToInsert[4]}', '{rowToInsert[5]}', '{rowToInsert[6]}', '{rowToInsert[7]}', {rowToInsert[8]})", nc);
            }
            try
            {
                npgc.ExecuteNonQuery();
                UpdateTable();
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message, "Ошибка");
            }
        }

        private void dataGridView1_RowHeaderMouseClick(object sender, DataGridViewCellMouseEventArgs e)
        {
            var selectedRow = dataGridView1.Rows[e.RowIndex];
            string[] selectedData = new string[dataGridView1.Columns.Count];
            for (int i = 0; i < dataGridView1.Columns.Count; i++)
            {
                selectedData[i] = selectedRow.Cells[i].Value.ToString();
            }
            textBoxId.Text = selectedData[0];
            comboBox1.Text = selectedData[1];
            textBoxName.Text = selectedData[2];
            textBoxDirector.Text = selectedData[3];
            textBoxEmail.Text = selectedData[4];
            textBoxPhone.Text = selectedData[5];
            textBoxAddress.Text = selectedData[6];
            textBoxInn.Text = selectedData[7];
            numericRating.Text = selectedData[8];
        }

        private void buttonChange_Click(object sender, EventArgs e)
        {
            if (dataGridView1.SelectedRows.Count != 0)
            {
                string[] rowToUpdate = { textBoxId.Text, comboBox1.Text, textBoxName.Text,
                textBoxDirector.Text, textBoxEmail.Text, textBoxPhone.Text, textBoxAddress.Text,
                textBoxInn.Text, numericRating.Text};

                try
                {
                    for (int i = 0; i < rowToUpdate.Length; i++)
                    {
                        var value = rowToUpdate[i];
                        if (value == "")
                        {
                            throw new Exception("Не все данные введены.\r\nЗаполните все поля и повторите попытку.");
                        }
                    }
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message, "Ошибка");
                }

                NpgsqlDataAdapter adapter = new NpgsqlDataAdapter("select * from partners_types", nc);
                DataSet dsPartnresTypes = new DataSet();
                adapter.Fill(dsPartnresTypes);
                DataTable dtPartnersTypes = dsPartnresTypes.Tables[0];

                foreach (DataRow row in dtPartnersTypes.Rows)
                {
                    if (row[1].ToString() == rowToUpdate[1])
                        rowToUpdate[1] = row[0].ToString();
                }

                NpgsqlCommand npgc = new NpgsqlCommand($"update partners set type = {rowToUpdate[1]}, name = '{rowToUpdate[2]}', director = '{rowToUpdate[3]}', email = '{rowToUpdate[4]}', phone = '{rowToUpdate[5]}', address = '{rowToUpdate[6]}', inn = '{rowToUpdate[7]}', rating = {rowToUpdate[8]} where id = {rowToUpdate[0]}", nc);
                try
                {
                    npgc.ExecuteNonQuery();
                    UpdateTable();
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message, "Ошибка");
                }
            }
            else
                MessageBox.Show("Выберите строку для изменения", "Ошибка");
        }

        private void buttonDelete_Click(object sender, EventArgs e)
        {
            if (dataGridView1.SelectedRows.Count != 0)
            {
                int selectedId = int.Parse(textBoxId.Text);
                NpgsqlCommand npgc = new NpgsqlCommand($"delete from partners where id = {selectedId}", nc);
                if (MessageBox.Show("Вы действительно хотите удалить запись?", "Подтверждение", MessageBoxButtons.YesNo) == DialogResult.Yes)
                {
                    try
                    {
                        npgc.ExecuteNonQuery();
                        UpdateTable();
                    }
                    catch (Exception ex)
                    {
                        MessageBox.Show(ex.Message, "Ошибка");
                    }
                }
            }
            else
                MessageBox.Show("Выберите строку для удаления", "Ошибка");
        }
    }
}
using Npgsql;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Partners_program_1
{
    public partial class FormAddProduction : Form
    {
        static string connString = "Host=localhost;Username=postgres;Password=postgres;Database=Partners";
        NpgsqlConnection nc = new NpgsqlConnection(connString);

        private int selectedRowId;

        public FormAddProduction()
        {
            InitializeComponent();
        }

        private void UpdateTable()
        {
            try
            {
                dataGridView1.Columns.Clear();
                dataGridView1.Rows.Clear();
                NpgsqlDataAdapter adapter = new NpgsqlDataAdapter("select production.id, name, production_types.type, article, min_price from production join production_types on (production_types.id = production.type) order by production.id", nc);
                DataSet dsProduction = new DataSet();
                adapter.Fill(dsProduction);
                DataTable dtProduction = dsProduction.Tables[0];
                foreach (DataColumn column in dtProduction.Columns)
                {
                    dataGridView1.Columns.Add(column.ColumnName, column.ColumnName);
                }
                foreach (DataRow row in dtProduction.Rows)
                {
                    var rowAsArray = row.ItemArray;
                    dataGridView1.Rows.Add(rowAsArray);
                }
                dataGridView1.Columns[0].Width = 50;
                dataGridView1.Columns[1].Width = 250;

                comboBox1.Items.Clear();
                adapter = new NpgsqlDataAdapter("select * from production_types", nc);
                DataSet dsProductionTypes = new DataSet();
                adapter.Fill(dsProductionTypes);
                DataTable dtProductionTypes = dsProductionTypes.Tables[0];

                foreach (DataRow row in dtProductionTypes.Rows)
                {
                    var rowAsArray = row.ItemArray;
                    comboBox1.Items.Add(rowAsArray[1]);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
        }

        private void FormAddProduction_Load(object sender, EventArgs e)
        {
            nc.Open();
            UpdateTable();
        }

        private void buttonAdd_Click(object sender, EventArgs e)
        {
            string[] rowToInsert = { textBoxId.Text, textBoxName.Text, comboBox1.Text,
                textBoxArticle.Text, numericPrice.Text};

            try
            {
                for (int i = 0; i < rowToInsert.Length; i++)
                {
                    var value = rowToInsert[i];
                    if (value == "" && i != 0)
                    {
                        throw new Exception("Не все данные введены.\r\nЗаполните все поля и повторите попытку.");
                    }
                }
                NpgsqlDataAdapter adapter = new NpgsqlDataAdapter("select * from production_types", nc);
                DataSet dsPartnresTypes = new DataSet();
                adapter.Fill(dsPartnresTypes);
                DataTable dtPartnersTypes = dsPartnresTypes.Tables[0];

                foreach (DataRow row in dtPartnersTypes.Rows)
                {
                    if (row[1].ToString() == rowToInsert[2])
                        rowToInsert[2] = row[0].ToString();
                }

                NpgsqlCommand npgc;

                if (rowToInsert[0] == "")
                {
                    npgc = new NpgsqlCommand($"insert into production values (default, '{rowToInsert[1]}', {rowToInsert[2]}, '{rowToInsert[3]}', '{rowToInsert[4]}')", nc);
                }
                else
                {
                    npgc = new NpgsqlCommand($"insert into production values ({rowToInsert[0]}, '{rowToInsert[1]}', {rowToInsert[2]}, '{rowToInsert[3]}', '{rowToInsert[4]}')", nc);
                }
                npgc.ExecuteNonQuery();
                UpdateTable();
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message, "Ошибка");
            }
        }

        private void dataGridView1_RowHeaderMouseClick(object sender, DataGridViewCellMouseEventArgs e)
        {
            var selectedRow = dataGridView1.Rows[e.RowIndex];
            string[] selectedData = new string[dataGridView1.Columns.Count];
            for (int i = 0; i < dataGridView1.Columns.Count; i++)
            {
                selectedData[i] = selectedRow.Cells[i].Value.ToString();
            }
            textBoxId.Text = selectedData[0];
            textBoxName.Text = selectedData[1];
            comboBox1.Text = selectedData[2];
            textBoxArticle.Text = selectedData[3];
            numericPrice.Text = selectedData[4];
        }

        private void buttonChange_Click(object sender, EventArgs e)
        {
            if (dataGridView1.SelectedRows.Count != 0)
            {
                string[] rowToUpdate = { textBoxId.Text, textBoxName.Text, comboBox1.Text,
                textBoxArticle.Text, numericPrice.Text};

                try
                {
                    for (int i = 0; i < rowToUpdate.Length; i++)
                    {
                        var value = rowToUpdate[i];
                        if (value == "")
                        {
                            throw new Exception("Не все данные введены.\r\nЗаполните все поля и повторите попытку.");
                        }
                    }
                    NpgsqlDataAdapter adapter = new NpgsqlDataAdapter("select * from production_types", nc);
                    DataSet dsPartnresTypes = new DataSet();
                    adapter.Fill(dsPartnresTypes);
                    DataTable dtProductionTypes = dsPartnresTypes.Tables[0];

                    foreach (DataRow row in dtProductionTypes.Rows)
                    {
                        if (row[1].ToString() == rowToUpdate[2])
                            rowToUpdate[2] = row[0].ToString();
                    }

                    NpgsqlCommand npgc = new NpgsqlCommand($"update production set name = '{rowToUpdate[1]}', type = {rowToUpdate[2]}, article = '{rowToUpdate[3]}', min_price = '{rowToUpdate[4]}' where id = {rowToUpdate[0]}", nc);

                    npgc.ExecuteNonQuery();
                    UpdateTable();
                }
                catch (Exception ex)
                {
                    MessageBox.Show(ex.Message, "Ошибка");
                }
            }
            else
                MessageBox.Show("Выберите строку для изменения", "Ошибка");
        }

        private void buttonDelete_Click(object sender, EventArgs e)
        {
            if (dataGridView1.SelectedRows.Count != 0)
            {
                int selectedId = int.Parse(textBoxId.Text);
                NpgsqlCommand npgc = new NpgsqlCommand($"delete from production where id = {selectedId}", nc);
                if (MessageBox.Show("Вы действительно хотите удалить запись?", "Подтверждение", MessageBoxButtons.YesNo) == DialogResult.Yes)
                {
                    try
                    {
                        npgc.ExecuteNonQuery();
                        UpdateTable();
                    }
                    catch (Exception ex)
                    {
                        MessageBox.Show(ex.Message, "Ошибка");
                    }
                }
            }
            else
                MessageBox.Show("Выберите строку для удаления", "Ошибка");
        }
    }
}



"""

#Юрченко
"""
import pyodbc
import tkinter as tk
from tkinter import ttk, messagebox

# Цветовая палитра
BG_COLOR = "#efdecd"  # Бежевый фон
BTN_COLOR = "#8b4513"  # Коричневый цвет кнопок
BTN_ACTIVE_COLOR = "#a0522d"  # Темно-коричневый цвет кнопок при наведении
TEXT_COLOR = "#4b2e1a"  # Цвет текста

# Функция для подключения к базе данных и загрузки данных о партнёрах
def fetch_partners():
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=SOFYA\\MSSQLSERVER02;"
            "DATABASE=Мастер_пол;"
            "Trusted_Connection=yes;"
        )
        cursor = conn.cursor()
        query = '''
        SELECT 
            Идентификатор_партнера,
            Тип_партнера,
            Наименование_партнера,
            Директор,
            Телефон_партнера,
            Рейтинг
        FROM Партнеры
        '''
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return rows
    except pyodbc.Error as e:
        messagebox.showerror("Ошибка подключения", f"Ошибка подключения к базе данных:\n{e}")
        return []

# Функция для расчёта скидки
def calculate_discount(partner_id):
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=SOFYA\\MSSQLSERVER02;"
            "DATABASE=Мастер_пол;"
            "Trusted_Connection=yes;"
        )
        cursor = conn.cursor()
        query = '''
        SELECT SUM(Количество) FROM Реализованная_продукция
        WHERE Идентификатор_партнера = ?
        '''
        cursor.execute(query, (partner_id,))
        total_sales = cursor.fetchone()[0]
        conn.close()

        if total_sales is None:
            return 0  # Если данных о продажах нет, скидка 0%

        # Расчёт скидки в зависимости от объема продаж
        if total_sales <= 10000:
            return 0
        elif 10000 < total_sales <= 50000:
            return 5
        elif 50000 < total_sales <= 300000:
            return 10
        else:
            return 15
    except pyodbc.Error as e:
        messagebox.showerror("Ошибка расчёта скидки", f"Ошибка при расчёте скидки:\n{e}")
        return 0

# Открытие окна для добавления партнёра
def open_add_partner_window():
    add_window = tk.Toplevel()
    add_window.title("Добавить партнёра")
    add_window.geometry("400x650")

    # Пытаемся установить иконку для окна, если не получается - выводим ошибку
    try:
        add_window.iconbitmap('Мастер пол.ico')  # Устанавливаем иконку для этого окна
    except Exception as e:
        messagebox.showwarning("Предупреждение", f"Не удалось установить иконку: {e}")

    labels = [
        "Идентификатор_партнера", "Тип_партнера", "Наименование_партнера",
        "Директор", "Электронная_почта", "Телефон_партнера",
        "Юридический_адрес", "ИНН", "Рейтинг"
    ]

    entries = {}
    for label in labels:
        ttk.Label(add_window, text=label).pack(pady=5)
        entry = ttk.Entry(add_window)
        entry.pack(pady=5)
        entries[label] = entry

    # Сохранение нового партнёра
    def save_partner():
        try:
            values = [entries[label].get() for label in labels]
            if all(values):
                conn = pyodbc.connect(
                    "DRIVER={ODBC Driver 17 for SQL Server};"
                    "SERVER=SOFYA\\MSSQLSERVER02;"
                    "DATABASE=Мастер_пол;"
                    "Trusted_Connection=yes;"
                )
                cursor = conn.cursor()
                query = '''
                INSERT INTO Партнеры 
                (Идентификатор_партнера, Тип_партнера, Наименование_партнера, Директор, 
                Электронная_почта, Телефон_партнера, Юридический_адрес, ИНН, Рейтинг)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
                cursor.execute(query, values)
                conn.commit()
                conn.close()
                messagebox.showinfo("Успех", "Партнёр успешно добавлен!")
                add_window.destroy()
            else:
                messagebox.showerror("Ошибка", "Заполните все поля!")
        except pyodbc.Error as e:
            messagebox.showerror("Ошибка добавления", f"Ошибка при добавлении партнёра:\n{e}")

    ttk.Button(add_window, text="Сохранить", command=save_partner).pack(pady=20)

# Открытие окна для редактирования партнёра
def open_edit_partner_window(partner_id):
    edit_window = tk.Toplevel()
    edit_window.title("Редактировать партнёра")
    edit_window.geometry("400x650")

    # Пытаемся установить иконку для окна, если не получается - выводим ошибку
    try:
        edit_window.iconbitmap('Мастер пол.ico')  # Устанавливаем иконку для этого окна
    except Exception as e:
        messagebox.showwarning("Предупреждение", f"Не удалось установить иконку: {e}")

    labels = [
        "Идентификатор_партнера", "Тип_партнера", "Наименование_партнера",
        "Директор", "Электронная_почта", "Телефон_партнера",
        "Юридический_адрес", "ИНН", "Рейтинг"
    ]

    entries = {}
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=SOFYA\\MSSQLSERVER02;"
        "DATABASE=Мастер_пол;"
        "Trusted_Connection=yes;"
    )
    cursor = conn.cursor()
    query = '''
    SELECT * FROM Партнеры WHERE Идентификатор_партнера = ?
    '''
    cursor.execute(query, (partner_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        messagebox.showerror("Ошибка", "Партнёр не найден!")
        return

    for i, label in enumerate(labels):
        ttk.Label(edit_window, text=label).pack(pady=5)
        entry = ttk.Entry(edit_window)
        entry.pack(pady=5)
        entries[label] = entry
        entries[label].insert(0, row[i])  # Заполняем поле данными из базы

    def save_changes():
        try:
            # Считываем все значения из полей
            values = {label: entries[label].get() for label in labels}
            # Убираем пустые значения
            updated_values = {key: value for key, value in values.items() if value}

            if updated_values:
                # Создание части запроса для обновленных полей
                set_clause = ", ".join([f"{key} = ?" for key in updated_values.keys()])
                query = f'''
                UPDATE Партнеры
                SET {set_clause}
                WHERE Идентификатор_партнера = ?
                '''

                # Передаем параметры: значения обновленных полей + идентификатор партнера
                params = list(updated_values.values()) + [partner_id]

                conn = pyodbc.connect(
                    "DRIVER={ODBC Driver 17 for SQL Server};"
                    "SERVER=SOFYA\\MSSQLSERVER02;"
                    "DATABASE=Мастер_пол;"
                    "Trusted_Connection=yes;"
                )
                cursor = conn.cursor()
                cursor.execute(query, tuple(params))
                conn.commit()
                conn.close()
                messagebox.showinfo("Успех", "Данные партнёра успешно обновлены!")
                edit_window.destroy()
            else:
                messagebox.showerror("Ошибка", "Заполните хотя бы одно поле!")
        except pyodbc.Error as e:
            messagebox.showerror("Ошибка редактирования", f"Ошибка при редактировании партнёра:\n{e}")

    ttk.Button(edit_window, text="Сохранить изменения", command=save_changes).pack(pady=20)

def open_purchases_window():
    purchases_window = tk.Toplevel(root)
    purchases_window.title("Покупки партнёров")
    purchases_window.geometry("900x600")

    try:
        purchases_window.iconbitmap('Мастер пол.ico')
    except Exception as e:
        messagebox.showwarning("Предупреждение", f"Не удалось установить иконку: {e}")

    ttk.Label(purchases_window, text="Список покупок", font=("Arial", 16, "bold")).pack(pady=10)

    # Fetch purchases data
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=SOFYA\\MSSQLSERVER02;"
            "DATABASE=Мастер_пол;"
            "Trusted_Connection=yes;"
        )
        cursor = conn.cursor()
        query = '''
            SELECT 
                Партнеры.Идентификатор_партнера,
                Партнеры.Наименование_партнера,
                Партнеры.Директор,
                Продукция.Наименование_продукции,
                Описание_продукции.Размер_упаковки,
                Реализованная_продукция.Количество,
                Реализованная_продукция.Дата_реализации
            FROM Реализованная_продукция
            JOIN Партнеры ON Реализованная_продукция.Идентификатор_партнера = Партнеры.Идентификатор_партнера
            JOIN Продукция ON Реализованная_продукция.Идентификатор_продукции = Продукция.Идентификатор_продукции
            JOIN Описание_продукции ON Продукция.Наименование_продукции = Описание_продукции.Наименование_продукции
        '''
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
    except pyodbc.Error as e:
        messagebox.showerror("Ошибка загрузки", f"Ошибка при загрузке данных о покупках:\n{e}")
        return

    # Canvas для прокрутки
    canvas = tk.Canvas(purchases_window)
    scrollbar = ttk.Scrollbar(purchases_window, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Используем grid для создания двух карточек в строке
    row = 0
    column = 0

    for idx, row_data in enumerate(rows):
        frame = ttk.Frame(scrollable_frame, borderwidth=2, relief="solid", padding=10)
        frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")

        labels = [
            f"Идентификатор партнёра: {row_data[0]}",
            f"Наименование партнёра: {row_data[1]}",
            f"Директор: {row_data[2]}",
            f"Продукция: {row_data[3]}",
            f"Размер упаковки: {row_data[4]}",
            f"Количество: {row_data[5]}",
            f"Дата реализации: {row_data[6]}"
        ]

        # Вывод меток в карточке
        for text in labels:
            ttk.Label(frame, text=text, font=("Arial", 10), anchor="w").pack(anchor="w", pady=2)

        # Если два элемента в строке, переходим ко второму столбцу
        column += 1
        if column == 2:  # После двух карточек переходим на новую строку
            column = 0
            row += 1

    # Обновление прокрутки
    scrollable_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

# Открытие окна с партнёрами
def open_partners_window():
    partners_window = tk.Toplevel(root)
    partners_window.title("Партнеры")
    partners_window.geometry("800x600")

    # Пытаемся установить иконку для окна, если не получается - выводим ошибку
    try:
        partners_window.iconbitmap('Мастер пол.ico')  # Устанавливаем иконку для этого окна
    except Exception as e:
        messagebox.showwarning("Предупреждение", f"Не удалось установить иконку: {e}")

    ttk.Label(partners_window, text="Список партнёров", font=("Arial", 16)).pack(pady=10)
    # Фрейм для кнопок
    button_frame = ttk.Frame(partners_window)
    button_frame.pack(pady=10, fill='x')
    # Кнопки на одной строке
    ttk.Button(button_frame, text="Назад", command=partners_window.destroy).pack(side="left", padx=10)
    ttk.Button(button_frame, text="Добавить партнёра", command=open_add_partner_window).pack(side="left", padx=10)
    ttk.Button(button_frame, text="Покупки", command=open_purchases_window).pack(side="left", padx=10)

    # Canvas для прокрутки списка партнёров
    canvas = tk.Canvas(partners_window)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(partners_window, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)
    frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor="nw")

    rows = fetch_partners()

    if not rows:
        ttk.Label(frame, text="Нет данных о партнёрах или ошибка подключения.", font=("Arial", 12)).pack(pady=20)
        return

    # Создание карточек партнёров
    row = 0  # Для отслеживания текущей строки в сетке
    column = 0  # Для отслеживания текущего столбца в сетке

    for row_data in rows:
        partner_id, partner_type, name, director, phone, rating = row_data
        discount = calculate_discount(partner_id)  # Расчет скидки для партнера

        partner_frame = ttk.Frame(frame, borderwidth=2, relief="solid", padding=10)
        partner_frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")

        ttk.Label(partner_frame, text=f"{partner_type} | {name}", font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(partner_frame, text=f"Директор: {director}", font=("Arial", 10)).grid(row=1, column=0, sticky="w")
        ttk.Label(partner_frame, text=f"Телефон: {phone}", font=("Arial", 10)).grid(row=2, column=0, sticky="w")
        ttk.Label(partner_frame, text=f"Рейтинг: {rating}", font=("Arial", 10)).grid(row=3, column=0, sticky="w")
        ttk.Label(partner_frame, text=f"Скидка: {discount}%",
                  font=("Arial", 10, "italic"),  # Курсив
                  foreground="#ff0066"  # Розовый цвет
                  ).grid(row=4, column=0, sticky="w")

        # Кнопка редактирования
        ttk.Button(partner_frame, text="Редактировать", command=lambda partner_id=partner_id: open_edit_partner_window(partner_id)).grid(row=5, column=0, pady=10, sticky="w")

        # После каждой второй карточки, переходим на новую строку
        column += 1
        if column == 2:  # После двух карточек переходим на новую строку
            column = 0
            row += 1

    # Обновление прокрутки
    frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

def open_add_product_window(products_window):
    add_product_window = tk.Toplevel(products_window)
    add_product_window.title("Добавить продукцию")
    add_product_window.geometry("400x400")

    ttk.Label(add_product_window, text="Идентификатор продукции:").pack(pady=5)
    entry_id = ttk.Entry(add_product_window)
    entry_id.pack(pady=5)

    ttk.Label(add_product_window, text="Тип продукции:").pack(pady=5)
    entry_type = ttk.Entry(add_product_window)
    entry_type.pack(pady=5)

    ttk.Label(add_product_window, text="Наименование продукции:").pack(pady=5)
    entry_name = ttk.Entry(add_product_window)
    entry_name.pack(pady=5)

    ttk.Label(add_product_window, text="Артикул:").pack(pady=5)
    entry_article = ttk.Entry(add_product_window)
    entry_article.pack(pady=5)

    ttk.Label(add_product_window, text="Минимальная стоимость:").pack(pady=5)
    entry_price = ttk.Entry(add_product_window)
    entry_price.pack(pady=5)

    def save_product():
        product_id = entry_id.get()
        product_type = entry_type.get()
        product_name = entry_name.get()
        product_article = entry_article.get()
        product_price = entry_price.get()

        if not all([product_id, product_type, product_name, product_article, product_price]):
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены.")
            return

        try:
            conn = pyodbc.connect(
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=SOFYA\\MSSQLSERVER02;"
                "DATABASE=Мастер_пол;"
                "Trusted_Connection=yes;"
            )
            cursor = conn.cursor()
            query = '''
                INSERT INTO Продукция (Идентификатор_продукции, Тип_продукции, Наименование_продукции, Артикул, Минимальная_стоимость)
                VALUES (?, ?, ?, ?, ?)
            '''
            cursor.execute(query, (product_id, product_type, product_name, product_article, product_price))
            conn.commit()
            conn.close()

            messagebox.showinfo("Успех", "Продукция успешно добавлена.")
            add_product_window.destroy()

            # Закрываем и обновляем окно продукции
            products_window.destroy()
            open_products_window()  # Открыть заново окно продукции с обновленными данными

        except pyodbc.Error as e:
            messagebox.showerror("Ошибка добавления", f"Ошибка при добавлении продукции:\n{e}")

    ttk.Button(add_product_window, text="Сохранить", command=save_product).pack(pady=20)

def open_products_window():
    products_window = tk.Toplevel(root)
    products_window.title("Продукция")
    products_window.geometry("900x600")

    try:
        products_window.iconbitmap('Мастер пол.ico')
    except Exception as e:
        messagebox.showwarning("Предупреждение", f"Не удалось установить иконку: {e}")

    ttk.Label(products_window, text="Список продукции", font=("Arial", 16, "bold")).pack(pady=10)

    # Создаём контейнер для кнопок "Добавить продукцию" и "Назад"
    button_frame = ttk.Frame(products_window)
    button_frame.pack(pady=10)

    # Кнопка "Добавить продукцию"
    add_button = ttk.Button(button_frame, text="Добавить продукцию", command=lambda: open_add_product_window(products_window))
    add_button.grid(row=0, column=0, padx=10)

    # Кнопка "Назад"
    back_button = ttk.Button(button_frame, text="Назад", command=products_window.destroy)
    back_button.grid(row=0, column=1, padx=10)

    # Fetch product data from the database
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=SOFYA\\MSSQLSERVER02;"
            "DATABASE=Мастер_пол;"
            "Trusted_Connection=yes;"
        )
        cursor = conn.cursor()
        query = '''
            SELECT 
                Идентификатор_продукции,
                Тип_продукции,
                Наименование_продукции,
                Артикул,
                Минимальная_стоимость
            FROM Продукция
        '''
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
    except pyodbc.Error as e:
        messagebox.showerror("Ошибка загрузки", f"Ошибка при загрузке данных о продукции:\n{e}")
        return

    # Canvas для прокрутки
    canvas = tk.Canvas(products_window)
    scrollbar = ttk.Scrollbar(products_window, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Используем grid для создания двух карточек в строке
    row = 0
    column = 0

    for idx, row_data in enumerate(rows):
        frame = ttk.Frame(scrollable_frame, borderwidth=2, relief="solid", padding=10)
        frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")

        labels = [
            f"Идентификатор продукции: {row_data[0]}",
            f"Тип продукции: {row_data[1]}",
            f"Наименование продукции: {row_data[2]}",
            f"Артикул: {row_data[3]}",
            f"Минимальная стоимость: {row_data[4]} руб"
        ]

        for text in labels:
            ttk.Label(frame, text=text, font=("Arial", 10), anchor="w").pack(anchor="w", pady=2)

        # Кнопка редактирования
        ttk.Button(frame, text="Редактировать",
                   command=lambda r=row_data: open_edit_product_window(products_window, r)).pack(pady=5)

        # Перемещение по столбцам и строкам
        column += 1
        if column == 2:
            column = 0
            row += 1

    # Обновление прокрутки
    scrollable_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Используем grid для создания двух карточек в строке
    row = 0
    column = 0

    # В цикле, где создаются карточки продукции
    for idx, row_data in enumerate(rows):
        frame = ttk.Frame(scrollable_frame, borderwidth=2, relief="solid", padding=10)
        frame.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")

        labels = [
            f"Идентификатор продукции: {row_data[0]}",
            f"Тип продукции: {row_data[1]}",
            f"Наименование продукции: {row_data[2]}",
            f"Артикул: {row_data[3]}",
            f"Минимальная стоимость: {row_data[4]} руб"
        ]

        for text in labels:
            ttk.Label(frame, text=text, font=("Arial", 10), anchor="w").pack(anchor="w", pady=2)

        # Кнопка редактирования
        ttk.Button(frame, text="Редактировать",
                   command=lambda r=row_data: open_edit_product_window(products_window, r)).pack(pady=5)

        # Перемещение по столбцам и строкам
        column += 1
        if column == 2:
            column = 0
            row += 1

    # Обновление прокрутки
    scrollable_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

def open_edit_product_window(products_window, product_data):
    edit_product_window = tk.Toplevel(products_window)
    edit_product_window.title("Редактировать продукцию")
    edit_product_window.geometry("400x350")

    # Поля для редактирования
    ttk.Label(edit_product_window, text="Тип продукции:").pack(pady=5)
    entry_type = ttk.Entry(edit_product_window)
    entry_type.insert(0, product_data[1])  # Предзаполнение текущим значением
    entry_type.pack(pady=5)

    ttk.Label(edit_product_window, text="Наименование продукции:").pack(pady=5)
    entry_name = ttk.Entry(edit_product_window)
    entry_name.insert(0, product_data[2])
    entry_name.pack(pady=5)

    ttk.Label(edit_product_window, text="Артикул:").pack(pady=5)
    entry_article = ttk.Entry(edit_product_window)
    entry_article.insert(0, product_data[3])
    entry_article.pack(pady=5)

    ttk.Label(edit_product_window, text="Минимальная стоимость:").pack(pady=5)
    entry_price = ttk.Entry(edit_product_window)
    entry_price.insert(0, product_data[4])
    entry_price.pack(pady=5)

    def save_changes():
        new_type = entry_type.get()
        new_name = entry_name.get()
        new_article = entry_article.get()
        new_price = entry_price.get()

        try:
            conn = pyodbc.connect(
                "DRIVER={ODBC Driver 17 for SQL Server};"
                "SERVER=SOFYA\\MSSQLSERVER02;"
                "DATABASE=Мастер_пол;"
                "Trusted_Connection=yes;"
            )
            cursor = conn.cursor()
            query = '''
                UPDATE Продукция
                SET Тип_продукции = ?, Наименование_продукции = ?, Артикул = ?, Минимальная_стоимость = ?
                WHERE Идентификатор_продукции = ?
            '''
            cursor.execute(query, (new_type, new_name, new_article, new_price, product_data[0]))
            conn.commit()
            conn.close()

            messagebox.showinfo("Успех", "Продукция успешно обновлена.")
            edit_product_window.destroy()

            # Закрываем и обновляем окно продукции
            products_window.destroy()
            open_products_window()

        except pyodbc.Error as e:
            messagebox.showerror("Ошибка редактирования", f"Ошибка при обновлении продукции:\n{e}")

    ttk.Button(edit_product_window, text="Сохранить изменения", command=save_changes).pack(pady=20)

# Главное окно приложения
root = tk.Tk()
root.title("Главное меню")
root.geometry("680x400")
root.configure(bg=BG_COLOR)

# Установка иконки
try:
    root.iconbitmap('Мастер пол.ico') 
except Exception as e:
    messagebox.showwarning("Предупреждение", f"Не удалось установить иконку: {e}")

# Заголовок
title_label = tk.Label(root, text="Учет партнёров и продукции", font=("Arial", 22, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
title_label.pack(pady=30)

# Стилизация кнопок
style = ttk.Style()
style.theme_use("clam")

style.configure("TButton",
                font=("Arial", 14),
                padding=10,
                background=BTN_COLOR,
                foreground="white",
                borderwidth=0,
                relief="flat")
style.map("TButton",
          background=[("active", BTN_ACTIVE_COLOR)],
          foreground=[("active", "white")])

# Добавляем кнопки с отступами
button_frame = tk.Frame(root, bg=BG_COLOR)
button_frame.pack(pady=20)

btn_partners = ttk.Button(button_frame, text="Партнёры", command=lambda: open_partners_window())
btn_partners.grid(row=0, column=0, padx=20, pady=10, ipadx=20)

btn_products = ttk.Button(button_frame, text="Продукция", command=lambda: open_products_window())  # Кнопка "Продукция"
btn_products.grid(row=0, column=1, padx=20, pady=10, ipadx=20)

btn_exit = ttk.Button(button_frame, text="Выход", command=root.quit)
btn_exit.grid(row=0, column=2, padx=20, pady=10, ipadx=20)

root.mainloop()

"""

#чистый интерфейс
"""
from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showinfo

def refresh_partners():

    showinfo("Info", "Функция refresh_partners() будет здесь")

def show_purchases(partner_name):

    showinfo("Покупки", f"Покупки партнера {partner_name} будут здесь")

def create_button(partner_index):

    btn = ttk.Button(
        content_frame,
        text=f"Партнер {partner_index}\nИнформация о партнере...",
        width=50,
        command=lambda: show_purchases(f"Партнер {partner_index}")
    )
    btn.pack(pady=5, anchor=N)

def create_product_buttons():
    for i in range(3):
        btn = ttk.Button(
            content_frame,
            text=f"Продукт {i+1}\nОписание продукта...",
            width=50,
            command=lambda x=i: showinfo("Продукт", f"Информация о продукте {x+1}")
        )
        btn.pack(pady=5, anchor=N)

def window_with_products():

    win = Toplevel(root)
    win.title("Продукция (заглушка)")
    Label(win, text="Здесь будет список продуктов").pack()

def show_buyers(product_name):

    showinfo("Покупатели", f"Покупатели продукта {product_name} будут здесь")

def add_partner_win():
    win = Toplevel(root)
    win.title("Добавить партнера (заглушка)")
    Label(win, text="Форма добавления партнера будет здесь").pack()

def del_partner_win():
    
    win = Toplevel(root)
    win.title("Удалить партнера (заглушка)")
    Label(win, text="Форма удаления партнера будет здесь").pack()

def partner_win_open():
    
    win = Toplevel(root)
    win.title("Партнеры (заглушка)")
    Label(win, text="Таблица партнеров будет здесь").pack()

def buys_win_open():
    
    win = Toplevel(root)
    win.title("Покупки (заглушка)")
    Label(win, text="Таблица покупок будет здесь").pack()

def mat_and_part():
    win = Toplevel(root)
    win.title("Материалы и цены (заглушка)")
    Label(win, text="Таблица материалов и цен будет здесь").pack()

def create_two_bnt():
    
    buttons_info = [
        ("Удалить партнера", del_partner_win),
        ("Добавить партнера", add_partner_win),
        ("Открыть таблицу партнеров", partner_win_open),
        ("Открыть все покупки", buys_win_open),
        ("Открыть все цены для парнеров", mat_and_part),
        ("Открыть окно со всей продукцией", window_with_products)
    ]
    
    for text, command in buttons_info:
        btn = ttk.Button(
            content_frame,
            text=text,
            width=50,
            command=command
        )
        btn.pack(anchor=S)

# Настройка основного окна
root = Tk()
root.geometry("1000x650")
root.title("Шаблон интерфейса")

content_frame = Frame(root)
content_frame.pack(side=RIGHT, fill=BOTH, expand=True)


# Создаем 3 примерные кнопки партнеров
for i in range(3):
    create_button(i)

# Создаем все дополнительные кнопки
create_two_bnt()

root.mainloop()
"""

# Подоксенов
"""
import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


class DatabaseQueryApp:
    def __init__(self, master):
        self.master = master
        master.title("Программа для работы с SQLite")

        # Параметры подключения к БД
        self.db_path = tk.StringVar(value="база_данных.db")
        self.connected = False
        self.conn = None
        self.cursor = None

        # Элементы интерфейса
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill="both")

        # Вкладка подключения
        self.connection_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.connection_frame, text="Подключение")

        # Вкладка запросов
        self.query_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.query_frame, text="Запросы")

        # Вкладка о программе
        self.about_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.about_frame, text="О программе")

        self.create_connection_ui(self.connection_frame)
        self.create_query_ui(self.query_frame)
        self.create_about_ui(self.about_frame)

    def create_connection_ui(self, frame):

        # Поля для SQLite
        ttk.Label(frame, text="Путь к базе SQLite:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.sqlite_path_entry = ttk.Entry(frame, textvariable=self.db_path, width=40)
        self.sqlite_path_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Кнопка подключения
        ttk.Button(frame, text="Подключиться", command=self.connect_database).grid(row=1, column=0, columnspan=2,
                                                                                   pady=10)

        # Кнопка создания примерной БД
        ttk.Button(frame, text="Создать пример базы", command=self.create_example_database).grid(row=2, column=0,
                                                                                                 columnspan=2, pady=5)

        # Кнопка просмотра всей БД
        ttk.Button(frame, text="Показать всю базу", command=self.show_all_database).grid(row=3, column=0, columnspan=2,
                                                                                         pady=5)

        # Статус подключения
        self.status_label = ttk.Label(frame, text="Не подключено", foreground="red")
        self.status_label.grid(row=4, column=0, columnspan=2, pady=5)

        # Настройка сетки
        frame.grid_columnconfigure(1, weight=1)

    def create_query_ui(self, frame):

        # Поле для SQL-запроса
        ttk.Label(frame, text="SQL-запрос:").pack(anchor="w")
        self.query_text = tk.Text(frame, height=10, width=80)
        self.query_text.pack(fill="both", expand=True, pady=5)

        # Примеры запросов
        ttk.Label(frame, text="Примеры запросов:").pack(anchor="w")
        self.predefined_queries = ttk.Combobox(frame, values=[
            "SELECT * FROM сотрудники",
            "SELECT * FROM отделы",
            "SELECT имя, зарплата FROM сотрудники WHERE зарплата > 55000",
            "SELECT name FROM sqlite_master WHERE type='table'"
        ], width=80)
        self.predefined_queries.pack(fill="x", pady=5)
        self.predefined_queries.bind("<<ComboboxSelected>>", self.load_predefined_query)

        # Кнопка выполнения
        ttk.Button(frame, text="Выполнить запрос", command=self.execute_query).pack(pady=10)

        # Таблица результатов
        self.result_tree = ttk.Treeview(frame)
        self.result_tree.pack(fill="both", expand=True, pady=5)

    def create_about_ui(self, frame):

        about_text = "программа расписать о программе"
        ttk.Label(frame, text=about_text, justify="left", wraplength=500).pack(pady=20, padx=20)

    def connect_database(self):

        try:
            self.conn = sqlite3.connect(self.db_path.get())
            self.cursor = self.conn.cursor()
            self.connected = True
            self.status_label.config(text="Подключено", foreground="green")
            messagebox.showinfo("Успех", "Успешное подключение к базе данных.")
        except Exception as e:
            self.conn = None
            self.cursor = None
            self.connected = False
            self.status_label.config(text="Не подключено", foreground="red")
            messagebox.showerror("Ошибка подключения", str(e))

    def show_all_database(self):

        if not self.connected:
            messagebox.showerror("Ошибка", "Сначала подключитесь к базе данных!")
            return

        try:
            # Получаем список всех таблиц
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = self.cursor.fetchall()

            if not tables:
                messagebox.showinfo("Информация", "В базе данных нет таблиц.")
                return

            # Очищаем предыдущие результаты
            for item in self.result_tree.get_children():
                self.result_tree.delete(item)

            # Показываем содержимое всех таблиц
            for table in tables:
                table_name = table[0]
                self.cursor.execute(f"SELECT * FROM {table_name}")

                # Получаем названия столбцов
                column_names = [description[0] for description in self.cursor.description]

                # Настраиваем столбцы Treeview
                self.result_tree["columns"] = column_names
                for col in column_names:
                    self.result_tree.heading(col, text=col)
                    self.result_tree.column(col, width=100)

                # Добавляем данные
                for row in self.cursor.fetchall():
                    self.result_tree.insert("", tk.END, values=row)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать базу данных: {e}")

    def execute_query(self):

        if not self.connected:
            messagebox.showerror("Ошибка", "Нет подключения к базе данных.")
            return

        query = self.query_text.get("1.0", tk.END).strip()
        if not query:
            messagebox.showerror("Ошибка", "Пожалуйста, введите SQL-запрос.")
            return

        try:
            self.cursor.execute(query)

            # Для запросов, изменяющих данные
            if self.cursor.description is None:
                self.conn.commit()
                messagebox.showinfo("Успех", "Запрос выполнен успешно.")
                return

            results = self.cursor.fetchall()

            # Очистка предыдущих результатов
            for item in self.result_tree.get_children():
                self.result_tree.delete(item)

            # Динамическое создание столбцов
            column_names = [desc[0] for desc in self.cursor.description]
            self.result_tree["columns"] = column_names
            for col in column_names:
                self.result_tree.heading(col, text=col)
                self.result_tree.column(col, width=100)

            # Вставка данных
            for row in results:
                self.result_tree.insert("", tk.END, values=row)

        except Exception as e:
            messagebox.showerror("Ошибка запроса", str(e))

    def load_predefined_query(self, event=None):

        query = self.predefined_queries.get()
        self.query_text.delete("1.0", tk.END)
        self.query_text.insert("1.0", query)

    def create_example_database(self):

        try:
            conn = sqlite3.connect(self.db_path.get())
            cursor = conn.cursor()

            # Создаем таблицу сотрудников
            cursor.execute(# вставть тройные кавычки
                CREATE TABLE IF NOT EXISTS сотрудники (
                    id INTEGER PRIMARY KEY,
                    имя TEXT,
                    должность TEXT,
                    зарплата REAL,
                    дата_приема TEXT
                )
            # вставть тройные кавычки)

            # Добавляем тестовые данные
            employees = [
                (1, 'Иванов Иван', 'Менеджер', 75000.0, '2020-05-15'),
                (2, 'Петрова Анна', 'Разработчик', 90000.0, '2019-11-20'),
                (3, 'Сидоров Дмитрий', 'Аналитик', 85000.0, '2021-02-10'),
                (4, 'Кузнецова Елена', 'Дизайнер', 80000.0, '2020-08-03')
            ]

            cursor.executemany("INSERT INTO сотрудники VALUES (?, ?, ?, ?, ?)", employees)

            # Создаем вторую таблицу для демонстрации
            cursor.execute(# вставть тройные кавычки
                CREATE TABLE IF NOT EXISTS отделы (
                    id INTEGER PRIMARY KEY,
                    название TEXT,
                    руководитель TEXT,
                    кол_сотрудников INTEGER
                )
            # вставть тройные кавычки)

            departments = [
                (1, 'IT', 'Петрова Анна', 12),
                (2, 'Маркетинг', 'Иванов Иван', 8),
                (3, 'Финансы', 'Смирнова Ольга', 5)
            ]

            cursor.executemany("INSERT INTO отделы VALUES (?, ?, ?, ?)", departments)

            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", "Пример базы данных успешно создан.")
        except Exception as e:
            messagebox.showerror("Ошибка создания базы", str(e))

    def on_closing(self):

        if self.connected:
            try:
                self.conn.close()
                print("Подключение к базе закрыто.")
            except Exception as e:
                print(f"Ошибка при закрытии подключения: {e}")
        self.master.destroy()


root = tk.Tk()
app = DatabaseQueryApp(root)
root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.mainloop()

"""

# Девальд
"""
import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from psycopg2 import OperationalError

DB_CONFIG = {
    "host": "localhost",
    "database": "Servers",
    "user": "postgres",
    "password": "1234",
    "port": "5432"
}

def fetch_tables():
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        cursor.execute('''
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        ''')

        tables = [table[0] for table in cursor.fetchall()]
        return tables

    except OperationalError as e:
        messagebox.showerror("Ошибка подключения", f"Не удалось подключиться к БД:\n{e}")
        return []
    finally:
        if 'connection' in locals():
            cursor.close()
            connection.close()


def fetch_table_data(table_name):
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        cursor = connection.cursor()

        cursor.execute(f"SELECT * FROM {table_name} LIMIT 100")
        rows = cursor.fetchall()

        cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'")
        columns = [col[0] for col in cursor.fetchall()]

        return columns, rows

    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить данные:\n{e}")
        return [], []
    finally:
        if 'connection' in locals():
            cursor.close()
            connection.close()


def load_table_data(event=None):
    table_name = table_combobox.get()
    if not table_name:
        return

    for item in data_tree.get_children():
        data_tree.delete(item)

    columns, rows = fetch_table_data(table_name)

    if not columns:
        return

    data_tree["columns"] = columns
    data_tree["show"] = "headings"

    for col in columns:
        data_tree.heading(col, text=col)
        data_tree.column(col, width=100, anchor="center")

    # Вставляем данные
    for row in rows:
        data_tree.insert("", "end", values=row)


root = tk.Tk()
root.title("Просмотр таблиц PostgreSQL")

tk.Label(root, text="Выберите таблицу:").pack(pady=5)
table_combobox = ttk.Combobox(root, state="readonly")
table_combobox.pack(pady=5)
table_combobox.bind("<<ComboboxSelected>>", load_table_data)

def refresh_tables():
    tables = fetch_tables()
    table_combobox["values"] = tables
    if tables:
        table_combobox.current(0)
        load_table_data()


refresh_button = tk.Button(root, text="Обновить", command=refresh_tables)
refresh_button.pack(pady=5)

data_tree = ttk.Treeview(root)
data_tree.pack(fill="both", expand=True, padx=10, pady=10)

refresh_tables()

root.mainloop()
"""

# Харьковец 2025 вкладки 
"""
import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from tkinter import *
from PIL import Image, ImageTk
from art import text2art 

# Подключение к базе данных PostgreSQL
def connect_to_db(show_error=True):
    try:
        conn = psycopg2.connect(
            dbname="prac_2025",
            user="postgres",
            password="1234",
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        if show_error:
            messagebox.showerror("Ошибка подключения", f"Не удалось подключиться к базе данных: {e}")
        return None


def fetch_data(table_name, condition=None):
    if not table_name.isidentifier():  # Проверка, что имя таблицы безопасно
        messagebox.showerror("Ошибка", "Недопустимое имя таблицы")
        return [], []

    conn = connect_to_db()
    if conn:
        try:
            with conn.cursor() as cursor:
                if condition:
                    query = f"SELECT * FROM {table_name} WHERE {condition};"
                else:
                    query = f"SELECT * FROM {table_name};"
                cursor.execute(query)
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return columns, rows
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при получении данных: {e}")
            return [], []
        finally:
            conn.close()
    return [], []

def insert_data(table_name, data):
    if not data:
        messagebox.showwarning("Предупреждение", "Нет данных для вставки")
        return

    conn = connect_to_db()
    if conn:
        try:
            with conn.cursor() as cursor:
                columns = ", ".join(data.keys())
                values = ", ".join(["%s"] * len(data))
                query = f"INSERT INTO {table_name} ({columns}) VALUES ({values});"
                cursor.execute(query, list(data.values()))
                conn.commit()
                messagebox.showinfo("Успех", "Данные успешно добавлены!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при вставке данных: {e}")
        finally:
            conn.close()

def delete_data(table_name, id):
    conn = connect_to_db()
    if conn:
        try:
            with conn.cursor() as cursor:
                query = f"DELETE FROM {table_name} WHERE id = %s;"
                cursor.execute(query, (id,))
                conn.commit()
                messagebox.showinfo("Успех", "Данные успешно удалены!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении данных: {e}")
        finally:
            conn.close()

def fetch_query(query, parameters=()):
    conn = connect_to_db()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, parameters)
                result = cursor.fetchall()
                return result
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")
            return []
        finally:
            conn.close()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Управление базой данных")
        self.geometry("1024x450")
        try:
            header_frame = tk.Frame(self)
            header_frame.pack(pady=10)

            original_image = Image.open('logo2.jpg')
            resized_image = original_image.resize((100, 100), Image.Resampling.LANCZOS)
            logo_img = ImageTk.PhotoImage(resized_image)

            logo_label = tk.Label(header_frame, image=logo_img)
            logo_label.image = logo_img
            logo_label.grid(row=0, column=1, padx=10)

            ascii_art = text2art("Practice_2025", font="standard")
            label_title = tk.Label(header_frame, text=ascii_art, font='Courier 9')
            label_title.grid(row=0, column=0, sticky="nsew")
            header_frame.columnconfigure(1, weight=1)

        except Exception as e:
            messagebox.showwarning("Предупреждение", f"Не удалось загрузить логотип: {e}")

        self.tab_control = ttk.Notebook(self)
        self.tabs = {}
        for table in ["преподаватели", "кабинеты", "группы", "расписание"]:
            tab = ttk.Frame(self.tab_control)
            self.tabs[table] = tab
            self.tab_control.add(tab, text=table.capitalize())
            self.setup_tab(tab, table)
        self.tab_control.pack(expand=1, fill="both")

    def setup_tab(self, tab, table_name):
        frame = ttk.Frame(tab)
        frame.pack(fill="both", expand=True)

        columns, rows = fetch_data(table_name)
        if not columns:
            return

        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill="both", expand=True)

        tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        tree.grid(row=0, column=0, sticky="nsew")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor='center')

        for row in rows:
            tree.insert("", "end", values=row)

        x_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(xscrollcommand=x_scroll.set)
        x_scroll.grid(row=1, column=0, sticky="ew")

        frame_buttons = ttk.Frame(tab)
        frame_buttons.pack(pady=10)

        ttk.Button(frame_buttons, text="Добавить", command=lambda: self.show_insert_dialog(table_name, tree)).pack(side="left", padx=5)
        ttk.Button(frame_buttons, text="Удалить", command=lambda: self.show_delete_dialog(table_name, tree)).pack(side="left", padx=5)
        ttk.Button(frame_buttons, text="Вывести данные", command=lambda: self.show_related_data(tree, table_name)).pack(side="left", padx=5)

        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        tab.tree = tree

    def show_insert_dialog(self, table_name, tree):
        dialog = tk.Toplevel(self)
        dialog.title(f"Добавить данные в {table_name}")
        entries = {}

        columns, _ = fetch_data(table_name)
        for col in columns:
            ttk.Label(dialog, text=col).pack()
            entry = ttk.Entry(dialog)
            entry.pack()
            entries[col] = entry

        ttk.Button(dialog, text="Добавить", command=lambda: self.insert_and_refresh(dialog, table_name, entries, tree)).pack(pady=10)

    def show_delete_dialog(self, table_name, tree):
        dialog = tk.Toplevel(self)
        dialog.title(f"Удалить данные из {table_name}")

        ttk.Label(dialog, text="Введите ID для удаления:").pack()
        id_entry = ttk.Entry(dialog)
        id_entry.pack()

        ttk.Button(dialog, text="Удалить", command=lambda: self.delete_and_refresh(dialog, table_name, id_entry.get(), tree)).pack(pady=10)

    def insert_and_refresh(self, dialog, table_name, entries, tree):
        data = {col: entry.get() for col, entry in entries.items()}
        insert_data(table_name, data)
        self.refresh_table(tree, table_name)
        dialog.destroy()

    def show_related_data(self, tree, table_name):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Не выбрана запись для вывода данных.")
            return

        # Вместо ID получаем название дисциплины (например, из столбца с индексом 5)
        item_id = tree.item(selected_item)["values"][4]  # Замените 4 на индекс столбца с названием дисциплины

        if table_name == "преподаватели":
            query = '''
            SELECT преподаватели.фио, группы.название, кабинеты.номер
            FROM преподаватели
            JOIN группы ON преподаватели.группа_id = группы.id
            JOIN кабинеты ON преподаватели.кабинет_id = кабинеты.id
            WHERE преподаватели.id = %s;
            '''
            column_names = ["ФИО", "Группа", "Кабинет"]

        elif table_name == "группы":
            query = '''
            SELECT группы.название, преподаватели.фио, кабинеты.номер
            FROM группы
            JOIN преподаватели ON преподаватели.группа_id = группы.id
            JOIN кабинеты ON преподаватели.кабинет_id = кабинеты.id
            WHERE группы.id = %s;
            '''
            column_names = ["Группа", "Преподаватель", "Кабинет"]

        elif table_name == "расписание":
            query = '''
            SELECT 
                расписание.день, 
                расписание.пара, 
                группы.название AS группа, 
                группы.количество_студентов, 
                расписание.дисциплина, 
                преподаватели.фио AS преподаватель, 
                SUM(преподаватели.лекции_в_неделю + преподаватели.практики_в_неделю + преподаватели.лабораторные_в_неделю) AS сумма_пар, 
                кабинеты.номер AS аудитория, 
                кабинеты.описание, 
                кабинеты.вместимость, 
                кабинеты.примечания
            FROM расписание
            JOIN группы ON расписание.группа_id = группы.id
            JOIN преподаватели ON расписание.преподаватель_id = преподаватели.id
            JOIN кабинеты ON расписание.аудитория_id = кабинеты.id
            WHERE расписание.дисциплина = %s  -- Смотрим по дисциплине
            GROUP BY 
                расписание.день, 
                расписание.пара, 
                группы.название, 
                группы.количество_студентов, 
                расписание.дисциплина, 
                преподаватели.фио, 
                кабинеты.номер, 
                кабинеты.описание, 
                кабинеты.вместимость, 
                кабинеты.примечания;
            '''
            column_names = ["День", "Пара", "Группа", "Студенты", "Дисциплина", "Преподаватель", "Сумма_пар", "Аудитория", "Описание", "Вместимость", "Примечания"]
        else:
            messagebox.showerror("Ошибка", "Для этой таблицы запросы не поддерживаются.")
            return

        # Запрашиваем данные по выбранной дисциплине
        results = fetch_query(query, (item_id,))  # Передаем название дисциплины, а не ID
        if results:
            result_window = tk.Toplevel(self)
            result_window.title("Результаты запроса")
            result_window.geometry("1000x600")  # Увеличен размер окна для скроллов

            # Создаем Treeview
            result_tree = ttk.Treeview(result_window, columns=column_names, show="headings")
            result_tree.grid(row=0, column=0, sticky="nsew")

            # Горизонтальный скролл
            x_scroll = ttk.Scrollbar(result_window, orient="horizontal", command=result_tree.xview)
            x_scroll.grid(row=1, column=0, sticky="ew")

            # Вертикальный скролл
            y_scroll = ttk.Scrollbar(result_window, orient="vertical", command=result_tree.yview)
            y_scroll.grid(row=0, column=1, sticky="ns")

            # Настроим скроллы для Treeview
            result_tree.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)

            for col in column_names:
                result_tree.heading(col, text=col)
                result_tree.column(col, width=150)

            for result in results:
                result_tree.insert("", "end", values=result)

            # Кнопка "Закрыть", которая будет по центру
            close_button = tk.Button(result_window, text="Закрыть", command=result_window.destroy)
            close_button.grid(row=2, column=0, pady=10, sticky="nsew")

            # Разрешим растягивать строки и колонки
            result_window.grid_rowconfigure(0, weight=1)  # Растягиваем первую строку (Treeview)
            result_window.grid_columnconfigure(0, weight=1)  # Растягиваем первую колонку (Treeview)
            result_window.grid_columnconfigure(1, weight=0)  # Для вертикального скролла
            result_window.grid_rowconfigure(1, weight=0)  # Для горизонтального скролла

        else:
            messagebox.showinfo("Результаты запроса", "Данные не найдены.")


    def delete_and_refresh(self, dialog, table_name, id, tree):
        delete_data(table_name, id)
        self.refresh_table(tree, table_name)
        dialog.destroy()

    def refresh_table(self, tree, table_name, condition=None):
        tree.delete(*tree.get_children())
        _, rows = fetch_data(table_name, condition)
        for row in rows:
            tree.insert("", "end", values=row)

if __name__ == "__main__":
    app = App()
    app.mainloop()
"""


# Толстобров

"""
import tkinter as tk
from tkinter import messagebox
import psycopg2
from PIL import Image, ImageTk

# Строка подключения к базе данных
connection_string = "dbname='практика' user='postgres' host='localhost' password='1234' port='5432'"

# Загрузка партнёров
def load_partners():
    for widget in partners_frame.winfo_children():
        widget.destroy()

    query = '''
    SELECT p."Тип партнера", p."Наименование партнера", p."Директор", p."Телефон партнера", p."Рейтинг",
           CASE 
               WHEN SUM(pp."Количество продукции") <= 10000 THEN '0%'
               WHEN SUM(pp."Количество продукции") <= 50000 THEN '5%'
               WHEN SUM(pp."Количество продукции") <= 300000 THEN '10%'
               ELSE '15%'
           END AS "Скидка"
    FROM partners_import p
    LEFT JOIN partner_products_import pp ON p."Наименование партнера" = pp."Наименование партнера"
    GROUP BY p."Тип партнера", p."Наименование партнера", p."Директор", p."Телефон партнера", p."Рейтинг";
    '''
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()

    for index, row in enumerate(rows, start=1):
        create_partner_card(*row, index)

def create_partner_card(partner_type, name, director, phone, rating, discount, row_index):
    btn = tk.Button(
        partners_frame,
        text=f"Тип: {partner_type}\nНаименование: {name}\nДиректор: {director}\nТелефон: {phone}\nРейтинг: {rating}\nСкидка: {discount}",
        font=("Arial", 12),
        bg="#90EE90",
        bd=2,
        relief="solid",
        width=35,
        height=8,
        anchor="w",
        justify="left",
        command=lambda: show_partner_purchases(name)
    )
    btn.grid(row=row_index, column=0, padx=10, pady=10, sticky="w")

def show_partner_purchases(partner_name):
    query = '''
    SELECT pp."Продукция", pp."Количество продукции", pp."Дата продажи"
    FROM partner_products_import pp
    WHERE pp."Наименование партнера" = %s;
    '''
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor()
    cur.execute(query, (partner_name,))
    rows = cur.fetchall()
    conn.close()

    purchases = f"Покупки партнёра \"{partner_name}\":\n"
    for product, quantity, date in rows:
        purchases += f"- {product}, Количество: {quantity}, Дата: {date}\n"

    messagebox.showinfo("Список покупок", purchases)

def add_partner_window():
    def save_partner():
        values = [entry_type.get(), entry_name.get(), entry_director.get(), entry_phone.get(), entry_rating.get()]
        if not all(values):
            messagebox.showwarning("Ошибка", "Заполните все поля")
            return
        try:
            conn = psycopg2.connect(connection_string)
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO partners_import("Тип партнера", "Наименование партнера", "Директор", "Телефон партнера", "Рейтинг")
                VALUES (%s, %s, %s, %s, %s)
            ''', values)
            conn.commit()
            conn.close()
            top.destroy()
            load_partners()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить партнёра:\n{e}")

    top = tk.Toplevel(root)
    top.title("Добавить партнёра")
    top.geometry("300x300")

    tk.Label(top, text="Тип партнёра").pack()
    entry_type = tk.Entry(top)
    entry_type.pack()

    tk.Label(top, text="Наименование партнёра").pack()
    entry_name = tk.Entry(top)
    entry_name.pack()

    tk.Label(top, text="Директор").pack()
    entry_director = tk.Entry(top)
    entry_director.pack()

    tk.Label(top, text="Телефон").pack()
    entry_phone = tk.Entry(top)
    entry_phone.pack()

    tk.Label(top, text="Рейтинг").pack()
    entry_rating = tk.Entry(top)
    entry_rating.pack()

    tk.Button(top, text="Сохранить", command=save_partner).pack(pady=10)

def delete_partner():
    def confirm_delete():
        name = entry_name.get()
        if not name:
            messagebox.showwarning("Ошибка", "Введите наименование партнёра")
            return
        try:
            conn = psycopg2.connect(connection_string)
            cur = conn.cursor()
            cur.execute('DELETE FROM partners_import WHERE "Наименование партнера" = %s', (name,))
            conn.commit()
            conn.close()
            top.destroy()
            load_partners()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить партнёра:\n{e}")

    top = tk.Toplevel(root)
    top.title("Удалить партнёра")
    top.geometry("300x100")

    tk.Label(top, text="Наименование партнёра для удаления:").pack()
    entry_name = tk.Entry(top)
    entry_name.pack()
    tk.Button(top, text="Удалить", command=confirm_delete).pack(pady=5)

def edit_partner_window():
    def load_existing():
        name = entry_search_name.get()
        if not name:
            messagebox.showwarning("Ошибка", "Введите наименование партнёра")
            return
        try:
            conn = psycopg2.connect(connection_string)
            cur = conn.cursor()
            cur.execute('SELECT "Тип_партнера", "Директор", "Телефон_партнера", "Рейтинг" FROM partners_import WHERE "Наименование партнера" = %s', (name,))
            row = cur.fetchone()
            if not row:
                messagebox.showinfo("Нет данных", "Партнёр не найден")
                return
            entry_type.insert(0, row[0])
            entry_director.insert(0, row[1])
            entry_phone.insert(0, row[2])
            entry_rating.insert(0, row[3])
            conn.close()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные:\n{e}")

    def save_edit():
        name = entry_search_name.get()
        new_values = [entry_type.get(), entry_director.get(), entry_phone.get(), entry_rating.get(), name]
        try:
            conn = psycopg2.connect(connection_string)
            cur = conn.cursor()
            cur.execute('''
                UPDATE partners_import
                SET "Тип партнера" = %s, "Директор" = %s, "Телефон партнера" = %s, "Рейтинг" = %s
                WHERE "Наименованиепартнера" = %s
            ''', new_values)
            conn.commit()
            conn.close()
            top.destroy()
            load_partners()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить изменения:\n{e}")

    top = tk.Toplevel(root)
    top.title("Редактировать партнёра")
    top.geometry("300x350")

    tk.Label(top, text="Наименование партнёра").pack()
    entry_search_name = tk.Entry(top)
    entry_search_name.pack()

    tk.Button(top, text="Загрузить", command=load_existing).pack(pady=5)

    tk.Label(top, text="Тип партнёра").pack()
    entry_type = tk.Entry(top)
    entry_type.pack()

    tk.Label(top, text="Директор").pack()
    entry_director = tk.Entry(top)
    entry_director.pack()

    tk.Label(top, text="Телефон").pack()
    entry_phone = tk.Entry(top)
    entry_phone.pack()

    tk.Label(top, text="Рейтинг").pack()
    entry_rating = tk.Entry(top)
    entry_rating.pack()

    tk.Button(top, text="Сохранить изменения", command=save_edit).pack(pady=10)

# Основное окно
root = tk.Tk()
root.title("Список партнёров")
root.geometry("600x700")

scrollbar_frame = tk.Frame(root)
scrollbar_frame.grid(row=0, column=0, padx=20, pady=20)

scrollbar = tk.Scrollbar(scrollbar_frame, orient="vertical")
partners_canvas = tk.Canvas(scrollbar_frame, yscrollcommand=scrollbar.set, height=600, width=350)
scrollbar.config(command=partners_canvas.yview)
scrollbar.grid(row=0, column=1, sticky="ns")
partners_canvas.grid(row=0, column=0, padx=10, pady=10)

partners_frame = tk.Frame(partners_canvas)
partners_canvas.create_window((0, 0), window=partners_frame, anchor="nw")

def on_canvas_configure(event):
    partners_canvas.configure(scrollregion=partners_canvas.bbox("all"))

partners_frame.bind("<Configure>", on_canvas_configure)

logo_frame = tk.Frame(root)
logo_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nw")

logo_image = Image.open("C:\\Users\\dsawr\\Desktop\\Ресурсы7\\Мастер пол.png")
logo_image = logo_image.resize((100, 100))
logo_photo = ImageTk.PhotoImage(logo_image)
logo_label = tk.Label(logo_frame, image=logo_photo)
logo_label.grid(row=0, column=0)

button_add = tk.Button(logo_frame, text="Добавить", width=12, height=2, bg="#90EE90", command=add_partner_window)
button_add.grid(row=1, column=0, padx=10, pady=5)

button_delete = tk.Button(logo_frame, text="Удалить", width=12, height=2, bg="#FF0000", command=delete_partner)
button_delete.grid(row=2, column=0, padx=10, pady=5)

button_edit = tk.Button(logo_frame, text="Изменить", width=12, height=2, bg="#00BFFF", command=edit_partner_window)
button_edit.grid(row=3, column=0, padx=10, pady=5)

load_partners()
root.mainloop()

"""

# Зоря
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import psycopg2
from psycopg2 import sql, extras # extras для DictCursor
import hashlib
from datetime import datetime

DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "1111",
    "host": "localhost",
    "port": "5432"
}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class DBConnector:
    def __init__(self, db_config):
        self.db_config = db_config
        self.connection = self._connect()
        self.canvas = None

    def _connect(self):
        try:
            conn = psycopg2.connect(**self.db_config)
            print("Подключение к PostgreSQL успешно установлено.")
            return conn
        except psycopg2.OperationalError as e:
            messagebox.showerror("Ошибка подключения к БД", f"Не удалось подключиться к PostgreSQL: {e}")
            return None

    def get_connection(self):
        if not self.connection or self.connection.closed:
            print("Соединение потеряно, попытка переподключения...")
            self.connection = self._connect()
        return self.connection

    def close(self):
        if self.connection and not self.connection.closed:
            self.connection.close()
            print("Соединение с PostgreSQL закрыто.")

class QueryExecutor:
    def __init__(self, db_connector):
        self.db_connector = db_connector

    def execute_query(self, query, params=None, fetchone=False, fetchall=False, commit=False):
        conn = self.db_connector.get_connection()
        if not conn:
            return None
        
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        try:
            cur.execute(query, params)
            if commit:
                conn.commit()
            
            result = None
            if fetchone:
                result = cur.fetchone()
            elif fetchall:
                result = cur.fetchall()
            return result
        except Exception as e:
            conn.rollback()
            print(f"Ошибка выполнения запроса: {e}")
            try:
                query_str = cur.query.decode() if isinstance(cur.query, bytes) else str(cur.query)
                print(f"Запрос: {query_str}")
            except:
                 print(f"Запрос (не удалось декодировать полностью): {query}")
            messagebox.showerror("Ошибка БД", f"Произошла ошибка: {e}")
            return None
        finally:
            cur.close()

class SchoolApp:
    def __init__(self, root, db_executor):
        self.root = root
        self.db_executor = db_executor
        self.root.title("Система управления школой (Ученики)")
        self.root.geometry("700x550")

        self.logo_label = tk.Label(root, text="🎓 SchoolManager Lite", font=("Arial", 18, "bold"), pady=8, fg="navy")
        self.logo_label.pack(pady=3)
        
        self.main_frame = ttk.Frame(root, padding="8")
        self.main_frame.pack(expand=True, fill=tk.BOTH)
        
        self.selected_student_id = None
        self.student_cards = []
        self.canvas_widget = None

        self.show_main_student_view()

    def clear_main_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.selected_student_id = None
        self.student_cards = []

    def show_main_student_view(self):
        self.clear_main_frame()

        controls_frame = ttk.Frame(self.main_frame)
        controls_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        ttk.Button(controls_frame, text="Добавить", command=self.add_student_dialog, width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(controls_frame, text="Изменить", command=self.edit_student_dialog, width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(controls_frame, text="Удалить", command=self.delete_student, width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(controls_frame, text="Обновить", command=self.refresh_student_cards, width=12).pack(side=tk.LEFT, padx=3)

        self.canvas_widget = tk.Canvas(self.main_frame, borderwidth=0, background="#f0f0f0") # Цвет фона холста
        self.cards_frame = tk.Frame(self.canvas_widget, background="#f0f0f0")
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas_widget.yview)
        self.canvas_widget.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.canvas_widget.pack(side="left", fill="both", expand=True)
        self.canvas_window = self.canvas_widget.create_window((4, 4), window=self.cards_frame, anchor="nw")

        self.cards_frame.bind("<Configure>", lambda e: self.canvas_widget.configure(scrollregion=self.canvas_widget.bbox("all")))
        self.canvas_widget.bind('<Configure>', self.on_canvas_configure)

        self.canvas_widget.bind_all("<MouseWheel>", lambda event: self.canvas_widget.yview_scroll(int(-1*(event.delta/120)), "units"))
        self.canvas_widget.bind_all("<Button-4>", lambda event: self.canvas_widget.yview_scroll(-1, "units"))
        self.canvas_widget.bind_all("<Button-5>", lambda event: self.canvas_widget.yview_scroll(1, "units"))

        self.refresh_student_cards()
    
    def on_canvas_configure(self, event):
        canvas_width = event.width
        if self.canvas_widget: # Убедимся, что canvas_widget уже создан
            self.canvas_widget.itemconfig(self.canvas_window, width=canvas_width)

    def refresh_student_cards(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        self.student_cards = []
        self.selected_student_id = None

        query = '''
            SELECT s.student_id, s.first_name, s.last_name, c.class_name, s.email 
            FROM Students s
            LEFT JOIN Classes c ON s.class_id = c.class_id
            ORDER BY s.last_name, s.first_name;
            '''
        students_data = self.db_executor.execute_query(query, fetchall=True)

        if students_data:
            for student in students_data:
                card_bg = "#e0ffe0"
                card = tk.Frame(self.cards_frame, relief=tk.SOLID, borderwidth=1, padx=6, pady=4, bg=card_bg)
                card.pack(pady=4, padx=8, fill=tk.X)
                
                info_text = (f"ID: {student['student_id']} :: {student['last_name']} {student['first_name']}\n"
                             f"Класс: {student['class_name'] or 'N/A'}\n"
                             f"Email: {student['email'] or 'N/A'}")
                
                lbl = tk.Label(card, text=info_text, justify=tk.LEFT, anchor="w", bg=card_bg, font=("Arial", 9))
                lbl.pack(fill=tk.X)
                
                card.student_id_ref = student['student_id'] 
                lbl.student_id_ref = student['student_id']

                card.bind("<Button-1>", self.on_card_select)
                lbl.bind("<Button-1>", self.on_card_select)
                self.student_cards.append(card)
        else:
            tk.Label(self.cards_frame, text="Нет данных об учениках.", bg="#f0f0f0", font=("Arial", 10)).pack(pady=20)
        
        self.cards_frame.update_idletasks()
        if self.canvas_widget:
             self.canvas_widget.config(scrollregion=self.canvas_widget.bbox("all"))

    def on_card_select(self, event):
        widget = event.widget
        card_frame = widget.master if isinstance(widget, tk.Label) else widget
        clicked_student_id = card_frame.student_id_ref
        
        default_bg = "#e0ffe0"
        selected_bg = "#b3e0ff"

        for card in self.student_cards:
            is_selected_card = (card.student_id_ref == clicked_student_id)
            current_bg = selected_bg if is_selected_card and self.selected_student_id != clicked_student_id else default_bg
            
            if card.student_id_ref == self.selected_student_id and card.student_id_ref != clicked_student_id:
                 card.config(bg=default_bg)
                 for child in card.winfo_children(): child.config(bg=default_bg)

        if self.selected_student_id == clicked_student_id:
            self.selected_student_id = None
            card_frame.config(bg=default_bg)
            for child in card_frame.winfo_children(): child.config(bg=default_bg)
        else:
            self.selected_student_id = clicked_student_id
            card_frame.config(bg=selected_bg)
            for child in card_frame.winfo_children(): child.config(bg=selected_bg)

    def _get_student_form_data(self, title, student_data=None):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.transient(self.root); dialog.grab_set(); dialog.resizable(False, False)
        
        entries = {}
        form_frame = ttk.Frame(dialog, padding="10")
        form_frame.pack(expand=True, fill="both")

        fields_config = [
            ("first_name", "Имя*", ""), ("last_name", "Фамилия*", ""),
            ("email", "Email", ""), ("phone", "Телефон", ""),
            ("date_of_birth", "Дата рожд. (ГГГГ-ММ-ДД)", ""),
            ("class_id", "ID Класса (число)", "") 
        ]
        
        if not student_data:
            fields_config.insert(0, ("password", "Пароль (для нов. пользователя)*", ""))
            fields_config.insert(0, ("username", "Логин (для нов. пользователя)*", ""))

        for i, (key, label, _) in enumerate(fields_config):
            ttk.Label(form_frame, text=label + ":").grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry_widget = ttk.Entry(form_frame, width=30, show="*" if key == "password" else "")
            
            if student_data and key in student_data:
                entry_widget.insert(0, str(student_data.get(key) or ""))
            entry_widget.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
            entries[key] = entry_widget
        
        result_data = {}
        def on_submit():
            for key, entry_widget in entries.items():
                result_data[key] = entry_widget.get().strip() or None

            if not student_data:
                if not result_data.get("username") or not result_data.get("password"):
                    messagebox.showerror("Ошибка", "Логин и пароль обязательны для нового пользователя.", parent=dialog)
                    result_data.clear(); return
            if not result_data.get("first_name") or not result_data.get("last_name"):
                messagebox.showerror("Ошибка", "Имя и фамилия ученика обязательны.", parent=dialog)
                result_data.clear(); return
            if result_data.get("class_id") and not result_data["class_id"].isdigit():
                messagebox.showerror("Ошибка", "ID Класса должен быть числом.", parent=dialog)
                result_data.clear(); return
            dialog.destroy()

        submit_button = ttk.Button(form_frame, text="Сохранить", command=on_submit)
        submit_button.grid(row=len(fields_config), column=0, columnspan=2, pady=10)
        dialog.wait_window()
        return result_data

    def add_student_dialog(self):
        data = self._get_student_form_data("Добавить ученика")
        if not data: return

        user_id = None
        if data.get("username") and data.get("password"):
            hashed_pwd = hash_password(data["password"])
            user_id_result = self.db_executor.execute_query(
                "INSERT INTO Users (username, password_hash, role) VALUES (%s, %s, 'student') RETURNING user_id",
                (data["username"], hashed_pwd), fetchone=True, commit=True
            )
            if user_id_result: user_id = user_id_result['user_id']
            else: messagebox.showerror("Ошибка", f"Не удалось создать пользователя '{data['username']}'."); return
        
        sql_student = '''
            INSERT INTO Students (user_id, first_name, last_name, class_id, date_of_birth, email, phone)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING student_id
        '''
        class_id_val = int(data['class_id']) if data.get('class_id') else None
        student_id_result = self.db_executor.execute_query(
            sql_student,
            (user_id, data['first_name'], data['last_name'], class_id_val, 
             data.get('date_of_birth'), data.get('email'), data.get('phone')),
            fetchone=True, commit=True
        )

        if student_id_result:
            if user_id:
                 self.db_executor.execute_query("UPDATE Users SET linked_id = %s WHERE user_id = %s", 
                                                (student_id_result['student_id'], user_id), commit=True)
            messagebox.showinfo("Успех", "Ученик успешно добавлен.")
            self.refresh_student_cards()
        else:
            if user_id: self.db_executor.execute_query("DELETE FROM Users WHERE user_id = %s", (user_id,), commit=True)
            messagebox.showerror("Ошибка", "Не удалось добавить ученика.")

    def edit_student_dialog(self):
        if not self.selected_student_id:
            messagebox.showwarning("Ошибка", "Сначала выберите ученика для изменения.")
            return

        current_data = self.db_executor.execute_query(
            "SELECT student_id, first_name, last_name, class_id, date_of_birth, email, phone FROM Students WHERE student_id = %s",
            (self.selected_student_id,), fetchone=True
        )
        if not current_data: messagebox.showerror("Ошибка", "Не удалось загрузить данные."); return

        data = self._get_student_form_data("Изменить данные ученика", dict(current_data))
        if not data: return

        sql_update = '''
            UPDATE Students SET first_name = %s, last_name = %s, class_id = %s, 
                               date_of_birth = %s, email = %s, phone = %s
            WHERE student_id = %s
        '''
        class_id_val = int(data['class_id']) if data.get('class_id') else None
        self.db_executor.execute_query(
            sql_update,
            (data['first_name'], data['last_name'], class_id_val, data.get('date_of_birth'),
             data.get('email'), data.get('phone'), self.selected_student_id),
            commit=True
        )
        messagebox.showinfo("Успех", "Данные ученика обновлены.")
        self.refresh_student_cards()

    def delete_student(self):
        if not self.selected_student_id:
            messagebox.showwarning("Ошибка", "Сначала выберите ученика для удаления.")
            return

        student_info = self.db_executor.execute_query(
            "SELECT first_name, last_name, user_id FROM Students WHERE student_id = %s",
            (self.selected_student_id,), fetchone=True
        )
        if not student_info: return

        if messagebox.askyesno("Подтверждение", f"Удалить {student_info['first_name']} {student_info['last_name']}?"):
            self.db_executor.execute_query("DELETE FROM Students WHERE student_id = %s", (self.selected_student_id,), commit=True)
            if student_info['user_id']: 
                self.db_executor.execute_query("DELETE FROM Users WHERE user_id = %s", (student_info['user_id'],), commit=True)
            messagebox.showinfo("Успех", "Ученик удален.")
            self.refresh_student_cards()


if __name__ == "__main__":
    db_connector_main = DBConnector(DB_CONFIG)
    if db_connector_main.get_connection():
        query_executor_main = QueryExecutor(db_connector_main)
        
        main_root = tk.Tk()
        app_instance = SchoolApp(main_root, query_executor_main)
        
        def on_app_closing():
            if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
                db_connector_main.close()
                main_root.destroy()
        
        main_root.protocol("WM_DELETE_WINDOW", on_app_closing)
        main_root.mainloop()
    else:
        print("Не удалось подключиться к базе данных. Приложение не будет запущено.")


"""