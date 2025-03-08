import tkinter as tk
from tkinter import messagebox, filedialog


class GoogleDriveUI:
    def __init__(self, root):
        """
        Initialize the Google Drive UI.

        Args:
            root: The root Tkinter window.
        """
        self.root = root
        self.setup_ui()

        # Dictionary to store callbacks for events
        self.callbacks = {
            "search": None,
            "file_select": None,
            "version_select": None,
            "upload_new_version": None,
        }

        # Dictionary to store file IDs
        self.file_ids = {}

    def setup_ui(self):
        """
        Sets up the UI components by calling smaller, focused functions.
        """
        self.root.title("Google Drive Versions")
        self.root.geometry("800x600")  # Adjusted window size for better layout

        # Create and layout the search bar
        self.create_search_bar()

        # Create and layout the file and version listboxes
        self.create_listboxes()

        # Create and layout the action buttons
        self.create_action_buttons()

        # Create and layout the description entry
        self.create_description_entry()

    def create_search_bar(self):
        """
        Creates the search bar at the top of the UI.
        """
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=10, padx=10, fill="x")

        self.search_entry = tk.Entry(search_frame, width=50)
        self.search_entry.pack(side="left", padx=5, expand=True, fill="x")

        self.search_button = tk.Button(
            search_frame, text="Search", command=self.on_search
        )
        self.search_button.pack(side="left")

    def create_listboxes(self):
        """
        Creates the file and version listboxes and places them in the UI.
        """
        listbox_frame = tk.Frame(self.root)
        listbox_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # File Listbox
        self.file_listbox = self.create_listbox(listbox_frame, "Files:")
        self.file_listbox.bind("<<ListboxSelect>>", self.on_file_select)

        # Version Listbox
        self.version_listbox = self.create_listbox(listbox_frame, "Versions:")
        self.version_listbox.bind("<<ListboxSelect>>", self.on_version_select)

        # Add placeholder text to the listboxes
        self.add_placeholder(
            self.file_listbox, "Please search for files to display them here."
        )
        self.add_placeholder(
            self.version_listbox, "Please select a file to view versions."
        )

    def create_listbox(self, parent, label_text):
        """
        Creates a labeled listbox.

        Args:
            parent: The parent widget.
            label_text: The text for the label.

        Returns:
            The listbox widget.
        """
        frame = tk.Frame(parent)
        frame.pack(side="left", padx=10, fill="both", expand=True)

        label = tk.Label(frame, text=label_text, font=("Arial", 12, "bold"))
        label.pack(anchor="w")

        listbox = tk.Listbox(
            frame,
            width=40,
            height=15,
            exportselection=False,
            font=("Arial", 10),
        )
        listbox.pack(pady=5, fill="both", expand=True)

        return listbox

    def add_placeholder(self, listbox, placeholder_text):
        """
        Adds placeholder text to a listbox and disables selection for it.

        Args:
            listbox: The listbox widget.
            placeholder_text: The placeholder text to add.
        """
        listbox.insert(tk.END, placeholder_text)
        listbox.itemconfig(
            0, fg="gray", selectbackground="white", selectforeground="gray"
        )

    def create_action_buttons(self):
        """
        Creates the action buttons (Upload New Version and Revert to Version).
        """
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10, padx=10, fill="x")

        self.upload_button = tk.Button(
            button_frame,
            text="Upload New Version",
            command=self.on_upload_new_version,
            bg="#4CAF50",  # Green color
            fg="white",
            font=("Arial", 10, "bold"),
        )
        self.upload_button.pack(side="left", padx=5, expand=True, fill="x")

        self.revert_button = tk.Button(
            button_frame,
            text="Revert to Version",
            command=self.on_revert_version,
            bg="#f44336",  # Red color
            fg="white",
            font=("Arial", 10, "bold"),
        )
        self.revert_button.pack(side="left", padx=5, expand=True, fill="x")

    def create_description_entry(self):
        """
        Creates the description entry with placeholder text.
        """
        description_frame = tk.Frame(self.root)
        description_frame.pack(pady=10, padx=10, fill="x")

        self.description_entry = tk.Entry(
            description_frame, width=50, fg="grey", font=("Arial", 10)
        )
        self.description_entry.insert(0, "Description")
        self.description_entry.bind("<FocusIn>", self.on_description_focus_in)
        self.description_entry.bind(
            "<FocusOut>", self.on_description_focus_out
        )
        self.description_entry.pack(fill="x")

    def on_description_focus_in(self, event):
        """
        Handles the focus in event for the description entry.
        """
        if self.description_entry.get() == "Description":
            self.description_entry.delete(0, tk.END)
            self.description_entry.config(fg="black")

    def on_description_focus_out(self, event):
        """
        Handles the focus out event for the description entry.
        """
        if not self.description_entry.get():
            self.description_entry.insert(0, "Description")
            self.description_entry.config(fg="grey")

    def set_callback(self, event_name, callback):
        """
        Set a callback for a specific event.

        Args:
            event_name (str): The name of the event
            (e.g., "search", "file_select").
            callback (function): The callback function to be triggered.
        """
        if event_name in self.callbacks:
            self.callbacks[event_name] = callback
        else:
            raise ValueError(f"Invalid event name: {event_name}")

    def on_file_select(self, event):
        """
        Handles file selection and triggers the callback.
        """
        selected_index = self.file_listbox.curselection()
        if selected_index:
            selected_file = self.file_listbox.get(selected_index)
            # Check if the selected item is the placeholder
            if (
                selected_file
                == "Please search for files to display them here."
            ):
                return  # Ignore selection of placeholder
            print(f"Selected File: {selected_file}")

            if self.callbacks["file_select"]:
                self.callbacks["file_select"](self.file_ids[selected_file])

    def on_version_select(self, event):
        """
        Handles version selection and triggers the callback.
        """
        selected_index = self.version_listbox.curselection()
        if selected_index:
            selected_version = self.version_listbox.get(selected_index)
            # Check if the selected item is the placeholder
            if selected_version == "Please select a file to view versions.":
                return  # Ignore selection of placeholder
            print(f"Selected Version: {selected_version}")

            if self.callbacks["version_select"]:
                self.callbacks["version_select"](selected_version)

    def on_upload_new_version(self):
        """
        Handles uploading a new version of the selected file.
        """
        print("Upload New Version button clicked")
        selected_file_index = self.file_listbox.curselection()
        if not selected_file_index:
            self.show_message(
                "No File Selected",
                "Please select a file to upload a new version.",
            )
            return

        selected_file = self.file_listbox.get(selected_file_index)
        file_info = self.file_ids[selected_file]

        # Open a file dialog to select the new file
        file_path = filedialog.askopenfilename(
            title="Select a file to upload as a new version"
        )
        # The user canceled the file dialog
        if not file_path:
            return

        # Get the description
        description = self.description_entry.get()
        if description == "Description":
            description = ""  # If the placeholder is still there, treat it as an empty description

        # Trigger the upload callback
        if self.callbacks["upload_new_version"]:
            self.callbacks["upload_new_version"](
                file_info, file_path, description
            )

    def on_search(self):
        """
        Handles the search button click event.
        """
        print("Search button clicked")
        search_term = self.search_entry.get().strip()
        if not search_term:
            self.show_message("Search", "Please enter a file name to search.")
            return

        # Trigger the search callback
        if self.callbacks["search"]:
            self.callbacks["search"](search_term)

    def on_revert_version(self):
        """
        Handles the "Revert to Version" button click event.
        """
        print("Revert to Version button clicked.")

    def show_message(self, title, message):
        """
        Displays a message box.

        Args:
            title: The title of the message box.
            message: The message to display.
        """
        messagebox.showinfo(title, message)

    def update_file_list(self, files):
        """
        Updates the file listbox with the given files.

        Args:
            files: A list of file dictionaries with 'id' and 'name' keys.
        """
        print(f"Updating file list with files: {files}")
        self.file_listbox.delete(0, tk.END)
        # Clear previous file IDs
        self.file_ids = {}
        if files:
            for file in files:
                self.file_listbox.insert(tk.END, file["name"])
                self.file_ids[file["name"]] = file
        else:
            # Add placeholder text if no files are found
            self.file_listbox.insert(
                tk.END, "Please search for files to display them here."
            )
            self.file_listbox.itemconfig(
                0, fg="gray", selectbackground="white", selectforeground="gray"
            )

    def display_file_versions(self, revisions):
        """
        Displays file versions in the version listbox.

        Args:
            revisions: A list of revision dictionaries.
        """
        print(f"Displaying file versions: {revisions}")
        self.version_listbox.delete(0, tk.END)
        if revisions:
            for revision in revisions:
                revision_info = (
                    f"ID: {revision['id']}, "
                    f"Modified: {revision['modifiedTime']}, "
                    f"Description: {revision.get('description', 'No description')}"
                )
                self.version_listbox.insert(tk.END, revision_info)
        else:
            # Add placeholder text if no versions are found
            self.add_placeholder(
                self.version_listbox, "Please select a file to view versions."
            )

    def get_selected_file_id(self):
        """
        Returns the ID of the currently selected file in the file listbox.

        Returns:
            A string representing the file ID, or None if no file is selected.
        """
        selected_index = self.file_listbox.curselection()
        if selected_index:
            selected_file = self.file_listbox.get(selected_index)
            # Check if the selected item is the placeholder
            if (
                selected_file
                == "Please search for files to display them here."
            ):
                return None
            file_info = self.file_ids.get(selected_file)
            if file_info:
                return file_info["id"]
        return None


if __name__ == "__main__":
    root = tk.Tk()
    ui = GoogleDriveUI(root)
    root.mainloop()
