import tkinter as tk


class widget_button(tk.Button):
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


class widget_details_section:
    def __init__(self, parent, labels):
        """
        Initialize the DetailsSection with a list of labels.

        Args:
            parent: The parent widget.
            labels: A list of label names (e.g., ["File_Size", "MIME_Type"]).
        """
        self.frame = tk.Frame(parent)
        self.frame.pack(pady=10, padx=10, fill="x")

        self.labels = {}
        for label_text in labels:
            label = tk.Label(
                self.frame, text=f"{label_text}: ", font=("Arial", 10)
            )
            label.pack(anchor="w")
            self.labels[label_text] = label

    def update_details(self, **kwargs):
        """
        Update the details section with the provided key-value pairs.
        """
        for key, value in kwargs.items():
            if key in self.labels:
                self.labels[key].config(text=f"{key}: {value}")


class widget_listbox(tk.Listbox):
    def __init__(self, parent, placeholder, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.placeholder = placeholder
        self.file_ids = {}
        self.insert_placeholder()

    def insert_placeholder(self):
        """Insert placeholder text into the listbox and disable it."""
        self.delete(0, tk.END)
        self.insert(tk.END, self.placeholder)
        self.itemconfig(
            0, fg="gray", selectbackground="white", selectforeground="gray"
        )
        self.config(state=tk.DISABLED)  # Disable the listbox

    def clear_placeholder(self):
        """Clear the placeholder text if it exists anywhere in the listbox."""
        for i in range(self.size()):
            if self.get(i) == self.placeholder:
                self.delete(i)
                self.config(state=tk.NORMAL)  # Re-enable the listbox
                break  # Exit after removing the placeholder

    def add_item(self, name, file_id):
        """
        Add an item to the listbox and store its ID.

        Args:
            name: The name of the file to display.
            file_id: The ID of the file to store.
        """
        self.clear_placeholder()  # Ensure placeholder is removed before adding new items
        index = self.size()
        self.insert(tk.END, name)
        self.file_ids[index] = (
            file_id  # Store the file ID at the correct index
        )

    def get_id(self, index):
        """
        Retrieve the ID of the item at the specified index.

        Args:
            index: The index of the item in the listbox.

        Returns:
            The ID of the item, or None if the index is invalid.
        """
        return self.file_ids.get(index, None)

    def reset(self):
        """
        Clear the listbox completely and restore the placeholder.
        """
        self.delete(0, tk.END)
        self.file_ids = {}
        self.insert_placeholder()


class widget_entryfield(tk.Entry):
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

    def on_focus_in(self, event):
        """Clear placeholder text when the entry gains focus."""
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(fg=self.default_fg)

    def on_focus_out(self, event):
        """Restore placeholder text if the entry is empty."""
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(fg=self.placeholder_fg)

    def on_key_press(self, event):
        """Clear placeholder text when the user starts typing."""
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(fg=self.default_fg)

    def reset(self):
        """Reset the entry to the placeholder text."""
        self.delete(0, tk.END)
        self.insert(0, self.placeholder)
        self.config(fg=self.placeholder_fg)
