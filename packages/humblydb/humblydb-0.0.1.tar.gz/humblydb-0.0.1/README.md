# HumblyTkinter

**HumblyTkinter** is a lightweight and user-friendly library designed to simplify the process of creating graphical user interfaces (GUIs) using Python's built-in **Tkinter** module. With EasyTkinter, you can quickly build functional and visually appealing GUIs without diving into the complexities of Tkinter.

---

## Features

- **Easy Window Creation**: Use `make_window` to create a new window with a custom title.
- **Widget Creation**:
  - **Labels**: Add text labels to your GUI with `make_label`.
  - **Buttons**: Create buttons with custom actions using `make_button`.
  - **Entry Fields**: Add text input fields with `make_entry`.
- **Widget Management**: All widgets are stored in a dictionary for easy access and manipulation.
- **Retrieve Input Values**: Use `get_output` to fetch the text entered in an input field.
- **Simple Execution**: Run your GUI application with a single call to `last_code`.

---

## Installation

To use EasyTkinter, simply include the library files in your project and import it:

```python
from humblytkinter import *