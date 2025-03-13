import tkinter as tk
from tkinter import ttk, messagebox


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

    def __init__(self, parent, folders):
        self.window = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Google Drive Folder Picker")

        self.folders = folders
        self.selected_folder = None  # Store selected folder (name, ID)

        # Create TreeView
        self.tree = ttk.Treeview(self.window)
        self.tree.heading("#0", text="Folders", anchor="w")
        self.tree.pack(fill="both", expand=True)

        # Populate TreeView
        self.populate_tree("", self.folders)

        # Select Button
        self.select_button = ttk.Button(
            self.window, text="Select Folder", command=self.select_folder
        )
        self.select_button.pack(pady=5)

        self.window.grab_set()  # Ensure the parent window is disabled
        # Handle window close event
        self.window.protocol("WM_DELETE_WINDOW", self.select_folder)

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
        if not selected_item:
            messagebox.showerror("Error", "No folder selected!")

            self.window.grab_release()  # Re-enable the parent window
            self.window.destroy()  # Close the folder picker window
            return None

        folder_name = self.tree.item(selected_item)["text"]
        folder_id = selected_item  # Treeview item ID is the folder ID
        self.selected_folder = {"name": folder_name, "id": folder_id}

        self.window.grab_release()  # Re-enable the parent window
        self.window.destroy()  # Close the folder picker window

        return self.selected_folder


class WidgetFileBrowser(tk.Frame):
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
        self.description_label.pack(
            side="top", anchor="w", padx=5, pady=(0, 2)
        )

        # Label to display the selected file path (below the description)
        self.file_label = tk.Label(
            self, text=self.placeholder, fg="gray", wraplength=400
        )
        self.file_label.pack(
            side="top", anchor="w", padx=5, pady=(0, 4), fill="x"
        )

        # Browse button (full width)
        self.browse_button = tk.Button(
            self, text="Browse", bg="#007BFF", fg="white"
        )
        self.browse_button.pack(side="top", padx=5, pady=5, fill="x")

    def get_file_path(self):
        """Returns the selected file path."""
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


class WidgetFolderBrowser(tk.Frame):
    def __init__(
        self,
        parent,
        label_text,
        *args,
        **kwargs,
    ):
        super().__init__(parent, *args, **kwargs)
        self.placeholder = "No folder selected"

        # Label for the description (passed as parameter)
        self.description_label = tk.Label(self, text=label_text)
        self.description_label.pack(
            side="top", anchor="w", padx=5, pady=(0, 2)
        )

        # Label to display the selected folder path (below the description)
        self.folder_label = tk.Label(
            self, text=self.placeholder, fg="gray", wraplength=400
        )
        self.folder_label.pack(
            side="top", anchor="w", padx=5, pady=(0, 4), fill="x"
        )

        # Browse button (full width)
        self.browse_button = tk.Button(
            self, text="Browse", bg="#007BFF", fg="white"
        )
        self.browse_button.pack(side="top", padx=5, pady=5, fill="x")

    def get_folder_path(self):
        """Returns the selected folder path."""
        if self.folder_label.cget("text") == self.placeholder:
            return None
        return self.folder_label.cget("text")

    def clear(self, event=None):
        """Resets the folder path label to the placeholder."""
        self.folder_label.config(text=self.placeholder, fg="gray")

    def update_display(self, folder_path):
        """Displays the selected folder path, hiding the placeholder."""
        if folder_path:
            self.folder_label.config(text=folder_path, fg="black")
        else:
            self.clear()


class WdgtDetailsSection:
    def __init__(self, parent, labels, title="Details"):
        """
        Initialize the DetailsSection with a list of labels and a title.

        Args:
            parent: The parent widget.
            labels: A list of label names (e.g., ["File_Size", "MIME_Type"]).
            title: The title of the details section (default is "Details").
        """
        self.frame = ttk.LabelFrame(parent, text=title, padding=(10, 5))
        self.frame.pack(pady=10, padx=10, fill="x")

        self.labels = {}
        for i, label_text in enumerate(labels):
            # Create a label for the key
            key_label = ttk.Label(
                self.frame,
                text=f"{label_text}:",
                font=("Arial", 10),
                anchor="e",
            )
            key_label.grid(row=i, column=0, sticky="e", padx=(0, 5), pady=2)

            # Create a label for the value
            value_label = ttk.Label(
                self.frame, text="", font=("Arial", 10), anchor="w"
            )
            value_label.grid(row=i, column=1, sticky="w", pady=2)

            # Store the value label in the dictionary
            self.labels[label_text] = value_label

    def update_details(self, **kwargs):
        """
        Update the details section with the provided key-value pairs.
        """
        for key, value in kwargs.items():
            if key in self.labels:
                self.labels[key].config(text=f"{value}")

    def clear(self):
        """
        Clear the values of the keys but keep the keys themselves.
        """
        for key, label in self.labels.items():
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
        Add an item to the listbox.

        :param name: The name of the item.
        :param file_id: The ID of the file.
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
        """
        Returns the current text in the search entry field if it's not the
        placeholder text, otherwise returns None.
        """
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
