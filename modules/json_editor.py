import json
import tkinter as tk
from tkinter import ttk


def save_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f)


def load_json(filename):
    with open(filename, "r") as f:
        return json.load(f)


class JSONEditor(tk.Tk):
    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("JSON Editor")
        self.geometry("600x400")

        self.data = data
        self.tree = ttk.Treeview(self)
        self.tree["columns"] = ("value",)
        self.tree.column("value", width=400)
        self.tree.heading("value", text="Value")

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.populate_tree(self.tree, "", self.data)

    def populate_tree(self, tree, parent, node):
        for key, value in node.items():
            if isinstance(value, dict):
                item = tree.insert(parent, "end", text=key)
                self.populate_tree(tree, item, value)
            else:
                tree.insert(parent, "end", text=key, values=(value,))


def open_json_editor(filename):
    data = load_json(filename)
    app = JSONEditor(data)
    app.mainloop()


if __name__ == "__main__":
    filename = "config/devices.json"
    data = load_json(filename)
    app = JSONEditor(data)
    app.mainloop()
