import tkinter as tk
from tkinter import ttk


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


class FolderPickerUI:
    """A Tkinter UI to display and select folders from Google Drive."""

    def __init__(self, master, folders):
        self.master = master
        self.master.title("Google Drive Folder Picker")
        self.folders = folders
        self.selected_folder = None  # Store selected folder (name, ID)

        # Create TreeView
        self.tree = ttk.Treeview(self.master)
        self.tree.heading("#0", text="Folders", anchor="w")
        self.tree.pack(fill="both", expand=True)

        # Populate TreeView
        self.populate_tree("", self.folders)

        # Select Button
        self.select_button = ttk.Button(
            self.master, text="Select Folder", command=self.select_folder
        )
        self.select_button.pack(pady=5)

    def populate_tree(self, parent, folders):
        """Recursively populates the treeview with folders."""
        for folder_id, folder_data in folders.items():
            node = self.tree.insert(
                parent,
                "end",
                iid=folder_id,
                text=folder_data["name"],
                open=False,
            )
            if folder_data["children"]:
                self.populate_tree(
                    node,
                    {child["id"]: child for child in folder_data["children"]},
                )

    def select_folder(self):
        """Handles folder selection and closes the window."""
        selected_item = self.tree.focus()  # Get selected tree item
        if selected_item:
            folder_name = self.tree.item(selected_item)["text"]
            folder_id = selected_item  # Treeview item ID is the folder ID
            self.selected_folder = {"name": folder_name, "id": folder_id}
            self.master.quit()

    def get_selected_folder(self):
        """Returns the selected folder after the UI closes."""
        self.master.mainloop()
        return self.selected_folder


class widget_file_browser(tk.Frame):
    def __init__(
        self,
        parent,
        label_text,
        *args,
        **kwargs,
    ):
        super().__init__(parent, *args, **kwargs)
        self.placeholder = "No file selected"

        # Label for the description (passed as parameter)
        self.description_label = tk.Label(self, text=label_text)
        self.description_label.pack(side="left", padx=5)

        # Label to display the selected file path
        self.file_label = tk.Label(
            self, text=self.placeholder, fg="gray", wraplength=400
        )
        self.file_label.pack(side="left", padx=5, fill="x", expand=True)

        # Browse button
        self.browse_button = widget_button(
            self,
            text="Browse",
            bg_color="#007BFF",  # Blue color
            fg_color="white",
        )
        self.browse_button.pack(side="right", padx=5)

    def get_file_path(self):
        """Returns the selected file path."""
        # If no file path is set, return None or placeholder
        if self.file_label.cget("text") == self.placeholder:
            return None
        return self.file_label.cget("text")

    def clear(self, event=None):
        """Resets the file path label to the placeholder."""
        self.file_label.config(text=self.placeholder, fg="gray")

    def display_file_path(self, file_path):
        """Displays the selected file path, hiding the placeholder."""
        if file_path:
            self.file_label.config(text=file_path, fg="black")
        else:
            self.clear()


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

    def clear(self):
        """
        Clear the details section.
        """
        for label in self.labels.values():
            label.config(text="")


class widget_listbox(tk.Listbox):
    def __init__(self, parent, on_select_callback=None, *args, **kwargs):
        kwargs["selectmode"] = "single"
        super().__init__(parent, *args, **kwargs)
        self.items = {}

        # If focus is lost, curselction is None
        # so we need to store the selected item in a variable
        self.selected_item = None
        self.on_select_callback = on_select_callback

        # Bind selection event
        self.bind("<<ListboxSelect>>", self._on_select)

    def add_item(self, name, file_id):
        """
        Add an item to the listbox and store its index and name in the items dictionary.

        Args:
            name: The name of the item.
            file_id: The ID of the item.
        """
        index = self.size()
        self.insert(tk.END, name)
        self.items[index] = {"name": name, "id": file_id}

    def _on_select(self, event):
        item = self.curselection()
        if item:
            index = item[0]
            self.selected_item = {"index": index, **self.items[index]}
            print(self.selected_item)
            if self.on_select_callback:
                self.on_select_callback()
        else:
            self.selected_item = None

    def remove_item(self, index):
        """
        Remove an item from the listbox by index.

        Args:
            index: The index of the item to remove.
        """
        if index in self.items:
            del self.items[index]
            self.delete(index)

    def get_selected_item(self):
        """
        Get the currently selected item.

        Returns:
            The selected item, or None if no item is selected.
        """
        print("selected item", self.selected_item)
        return self.selected_item if self.selected_item else None

    def clear(self):
        """
        Clear the listbox completely.
        """
        self.items = {}
        self.selected_item = None
        self.delete(0, tk.END)


class widget_search_bar(tk.Frame):
    def __init__(self, parent, placeholder="Search...", *args, **kwargs):
        """
        A reusable search bar widget with an entry field and a search button.

        Args:
            parent: The parent widget.
            placeholder: Placeholder text for the search entry field.
        """
        super().__init__(parent, *args, **kwargs)
        self.placeholder = placeholder

        # Search entry field
        self.search_entry = tk.Entry(self, width=50, fg="gray")
        self.search_entry.insert(0, placeholder)
        self.search_entry.bind("<FocusIn>", self._clear_placeholder)
        self.search_entry.pack(side="left", padx=5, expand=True, fill="x")

        # Search button
        self.search_button = widget_button(
            self, text="Search", bg_color="#007BFF", fg_color="white"
        )
        self.search_button.pack(side="left")

    def get_search_term(self):
        """Returns the current text in the search entry field if it's not the placeholder text, otherwise returns None."""
        search_term = self.search_entry.get().strip()
        if search_term == self.placeholder:
            return None
        return search_term

    def clear(self):
        """Clears the search field."""
        self.search_entry.delete(0, tk.END)
        self._restore_placeholder("Search...")

    def _clear_placeholder(self, event):
        """Clears the placeholder text when the entry gains focus."""
        if self.search_entry.get() == "Search...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg="black")

    def _restore_placeholder(self, placeholder):
        """Restores the placeholder text if the entry is empty."""
        if not self.search_entry.get():
            self.search_entry.insert(0, placeholder)
            self.search_entry.config(fg="gray")


class widget_entryfield(tk.Entry):
    def __init__(self, parent, placeholder="Enter text...", *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.placeholder = placeholder
        self.default_fg = self.cget("fg")
        self.placeholder_fg = "gray"

        self.insert(0, self.placeholder)
        self.config(fg=self.placeholder_fg)

        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._restore_placeholder)

    def _clear_placeholder(self, event):
        """Clears the placeholder text when the entry gains focus."""
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(fg=self.default_fg)

    def _restore_placeholder(self, event):
        """Restores the placeholder text if the entry is empty."""
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(fg=self.placeholder_fg)

    def get_text(self):
        """Returns the current text, excluding placeholder."""
        text = self.get().strip()
        return "" if text == self.placeholder else text

    def clear(self):
        """Resets the entry to the placeholder text."""
        self.delete(0, tk.END)
        self._restore_placeholder(None)
        self.config(fg=self.placeholder_fg)
