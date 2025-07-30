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





#example

"""
from db_main_utils import create_buttons_from_data, show_table_in_window, show_details_in_window, DBConnector, QueryExecutor, create_add_record_form, delete_record
from tkinter import ttk, Frame, Toplevel

if __name__ == "__main__":
    # Connect to a PostgreSQL database (modify parameters as needed)
    conn = DBConnector(
        'postgresql',
        user='postgres',
        password='1234',
        host='localhost',
        database='work'
    )

    executor = QueryExecutor(conn.connection)

    # Example query
    query = "SELECT Код_обслед, Дата_Обслед FROM Обследованные"
    data = executor.execute_query(query)

    headers = ["Код_Обслед", "Дата_обслед"]  # Example headers
    headers2 = ["Код_Обслед", "Квартал"] 
    import tkinter as tk
    root = tk.Tk()
    root.title("Database UI Example")
    root.geometry("800x600")

    # Frame for buttons
    content_frame = Frame(root)
    content_frame.pack(fill='both', expand=True)
    def fetch_details(row):
        detail_query = "SELECT Квартал FROM Обследованные WHERE Код_обслед = %s"
        return executor.execute_query(detail_query, params=(row[0],))
    
    # Function to add a record
    def add_record(record):
        insert_query = "INSERT INTO Обследованные (Код_обслед, Квартал) VALUES (%s, %s)"
        executor.execute_non_query(insert_query, params=(record["Код_Обслед"], record["Квартал"]))
        print("Record added successfully.")

    # Function to delete a record
    def delete_selected_record():
        delete_query = "DELETE FROM Обследованные WHERE Код_обслед = %s"
        executor.execute_non_query(delete_query, params=("Код_обслед",))
        print("Record deleted successfully.")

    create_buttons_from_data(content_frame, data, headers, lambda row: show_details_in_window(row, fetch_details))

    # Frame for adding records
    add_frame = Frame(root)
    add_frame.pack(pady=5, anchor='n')
    create_add_record_form(add_frame, headers2, add_record)

    # Button for deleting records
    delete_btn = ttk.Button(root, text="Delete Record", command=lambda: delete_record("Are you sure?", delete_selected_record))
    delete_btn.pack(pady=5, anchor='n')

    table_show_btn = ttk.Button(
        root, 
        command=lambda: show_table_in_window(data, headers, title="Example Table View"), 
        text="Просмотр таблицы"
    )
    table_show_btn.pack(pady=5, anchor='n')
    # Show data in a table
    

    root.mainloop()

    conn.close_connection()

    conn.close_connection()
"""

#clear tkinter + psycopg2
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