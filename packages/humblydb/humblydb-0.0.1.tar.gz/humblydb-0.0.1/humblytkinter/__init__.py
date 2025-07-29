import tkinter as tk

widgets = {} 

def make_window(window_name):
    root = tk.Tk()
    root.title(window_name)
    return root

def make_label(label_text="Hello World", label_height=2, label_width=30, label_number=None):
    label = tk.Label(
        text=label_text,
        font=("Arial", 15),
        bg="lightgray",
        height=label_height,
        width=label_width
    )
    label.grid(row=label_number + 1, column=0)
    widgets[f"label_{label_number}"] = label 
    return label

def make_button(button_text="Click Me", button_height=2, button_width=30, button_number=None, button_command=None):
    button = tk.Button(
        text=button_text,
        font=("Arial", 15),
        bg="lightgray",
        height=button_height,
        width=button_width,
        activebackground="blue",
        activeforeground="black",
        command=button_command if button_command else lambda: print("Button clicked!")
    )
    button.grid(row=button_number + 1, column=0)
    widgets[f"button_{button_number}"] = button 
    return button

def make_entry(entry_text="Enter text here", entry_width=30, entry_number=None):
    entry = tk.Entry(
        font=("Arial", 15),
        bg="lightgray",
        width=entry_width
    )
    entry.insert(0, entry_text)  
    entry.grid(row=entry_number + 1, column=0)
    widgets[f"entry_{entry_number}"] = entry 
    return entry

def get_output(entry_number):
    entry = widgets.get(f"entry_{entry_number}")
    if entry:
        return entry.get()
    return None

def last_code():
    tk.mainloop()


def help():
    window = tk.Tk()
    window.title("راهنمای humblytkinter")
    window.geometry("700x450")
    window.configure(bg="#e0f7fa")

    text = (
        "make_window(title): ساخت یک پنجره با عنوان دلخواه\n"
        "make_label(text, height, width, number): ساخت لیبل با مشخصات اختیاری، فقط number اجباری است\n"
        "make_button(text, height, width, number, command): ساخت دکمه، فقط number اجباری است\n"
        "make_entry(text, width, number): ساخت ورودی متنی، فقط number اجباری است\n"
        "get_output(number): دریافت مقدار ورودی با شماره مشخص\n"
        "last_code(): اجرای رابط گرافیکی (mainloop)\n\n"
        "توجه: شماره ویجت‌ها باید یکتا باشند و برای دکمه‌ها تابع command را بدون پرانتز وارد کنید."
    )

    label = tk.Label(
        window,
        text=text,
        font=("Arial", 12),
        justify="right",
        bg="#e0f7fa",
        anchor="nw"
    )
    label.pack(padx=20, pady=20, fill="both", expand=True)

    ok_button = tk.Button(
        window,
        text="بستن",
        font=("Arial", 12),
        bg="#00838f",
        fg="white",
        padx=10,
        pady=5,
        command=window.destroy
    )
    ok_button.pack(pady=10)

    window.mainloop()
