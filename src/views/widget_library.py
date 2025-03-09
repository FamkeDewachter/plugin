import tkinter as tk


class StyledButton(tk.Button):
    def __init__(self, parent, text, bg_color, fg_color, *args, **kwargs):
        super().__init__(
            parent,
            text=text,
            bg=bg_color,
            fg=fg_color,
            font=("Arial", 10, "bold"),
            *args,
            **kwargs,
        )


class VersionDetailsSection:
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.frame.pack(pady=10, padx=10, fill="x")

        self.modified_time_label = tk.Label(
            self.frame, text="Modified Time: ", font=("Arial", 10)
        )
        self.modified_time_label.pack(anchor="w")

        self.description_label = tk.Label(
            self.frame, text="Description: ", font=("Arial", 10)
        )
        self.description_label.pack(anchor="w")

    def update_details(self, modified_time, description):
        """Update the version details."""
        self.modified_time_label.config(text=f"Modified Time: {modified_time}")
        self.description_label.config(text=f"Description: {description}")


class PlaceholderListbox(tk.Listbox):
    def __init__(self, parent, placeholder, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.placeholder = placeholder
        self.insert_placeholder()

    def insert_placeholder(self):
        """Insert placeholder text into the listbox."""
        self.insert(tk.END, self.placeholder)
        self.itemconfig(
            0, fg="gray", selectbackground="white", selectforeground="gray"
        )

    def clear_placeholder(self):
        """Clear the placeholder text if it exists."""
        if self.get(0) == self.placeholder:
            self.delete(0)

    def add_item(self, item):
        """Add an item to the listbox, ensuring the placeholder is cleared."""
        self.clear_placeholder()
        self.insert(tk.END, item)

    def reset(self):
        """Reset the listbox to show the placeholder."""
        self.delete(0, tk.END)
        self.insert_placeholder()


class PlaceholderEntry(tk.Entry):
    def __init__(self, parent, placeholder, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.placeholder = placeholder
        self.default_fg = self.cget("fg")
        self.placeholder_fg = "grey"

        self.insert(0, self.placeholder)
        self.config(fg=self.placeholder_fg)

        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        self.bind("<Key>", self.on_key_press)

    def on_focus_in(self):
        """Clear placeholder text when the entry gains focus."""
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(fg=self.default_fg)

    def on_focus_out(self):
        """Restore placeholder text if the entry is empty."""
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(fg=self.placeholder_fg)

    def on_key_press(self):
        """Clear placeholder text when the user starts typing."""
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(fg=self.default_fg)

    def reset(self):
        """Reset the entry to the placeholder text."""
        self.delete(0, tk.END)
        self.insert(0, self.placeholder)
        self.config(fg=self.placeholder_fg)
