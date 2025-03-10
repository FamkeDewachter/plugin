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


import tkinter as tk
from tkinter import ttk


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
        browse_callback=None,
        *args,
        **kwargs,
    ):
        super().__init__(parent, *args, **kwargs)
        self.placeholder = "No file selected"
        self.file_path = None
        self.browse_callback = browse_callback

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

        # Bind the browse button to the callback
        if self.browse_callback:
            self.browse_button.bind("<Button-1>", self.browse_callback)

    def get_file_path(self):
        """
        Returns the selected file path.

        Returns:
            str: The selected file path, or None if no file is selected.
        """
        return self.file_path

    def set_file_path(self, file_path):
        """
        Sets the file path and updates the label.

        Args:
            file_path (str): The file path to set.
        """
        self.file_path = file_path
        if file_path:
            self.file_label.config(text=file_path, fg="black")
        else:
            self.file_label.config(text=self.placeholder, fg="gray")


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

    def clear_items(self):
        """Clear all items from the listbox."""
        self.delete(0, tk.END)
        self.file_ids = {}

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
