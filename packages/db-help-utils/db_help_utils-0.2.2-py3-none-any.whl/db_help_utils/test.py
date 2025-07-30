from db_help_utils import create_buttons_from_data, show_table_in_window, show_details_in_window, DBConnector, QueryExecutor, create_add_record_form, delete_record
from tkinter import ttk, Frame, Toplevel

if __name__ == "__main__":
    # Connect to a PostgreSQL database (modify parameters as needed)
    conn = DBConnector(
        'postgresql',
        user='postgres',
        password='1234',
        host='localhost',
        database='prac_2025'
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