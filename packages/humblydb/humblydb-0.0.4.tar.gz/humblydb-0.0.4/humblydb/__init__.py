import sqlite3 as s
import pickle as p
import tkinter as tk
from tkinter import messagebox

def save_data(db_name = "data", data = None, data_name = None):
    with s.connect(f"{db_name}.db") as con:
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS data(list BLOB)")
        cur.execute("SELECT list FROM data")
        fetched = cur.fetchone()

        if fetched is None:
            data_dict = {data_name: data}
        else:
            try:
                data_dict = p.loads(fetched[0])
                data_dict.update({data_name: data})
            except:
                print("Error loading existing data. Reinitializing...")
                data_dict = {data_name: data}

        data_dict = p.dumps(data_dict)
        cur.execute("DELETE FROM data")
        cur.execute("INSERT INTO data VALUES(?)", (data_dict,))

def see_data(db_name = "data", data_name = None):
    with s.connect(f"{db_name}.db") as con:
        cur = con.cursor()
        cur.execute("SELECT list FROM data")
        fetched = cur.fetchone()
        if fetched is None:
            raise ValueError("No data found. Please save something first.")
        data_dict = p.loads(fetched[0])
        return data_dict.get(data_name)

def help():
    help_text = """
    Library Usage Guide:

    Function to save data:
    save_data(db_name="data", data="value", data_name="key")
    - db_name: Name of the database (without .db extension)
    - data_name: Key for the data
    - data: Value to store

    Function to retrieve data:
    see_data(db_name="data", data_name="key")
    - Returns the value associated with the specified key

    Example:
    save_data("mydb", "1234", "password")
    print(see_data("mydb", "password"))
    """

    # GUI to display the help guide
    root = tk.Tk()
    root.title("Library Usage Guide")
    root.geometry("500x300")

    text_widget = tk.Text(root, wrap="word", padx=10, pady=10)
    text_widget.insert("1.0", help_text)
    text_widget.config(state="disabled")
    text_widget.pack(expand=True, fill="both")

    root.mainloop()
