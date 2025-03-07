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

        # Callbacks for events
        self.on_search_callback = None
        self.on_file_select_callback = None
        self.on_upload_new_version_callback = None

    def create_listbox_frame(self, parent, label_text):
        """
        Creates a labeled frame containing a listbox.
        """
        frame = tk.Frame(parent)
        frame.pack(side="left", padx=10, fill="both", expand=True)

        label = tk.Label(frame, text=label_text)
        label.pack(anchor="w")

        listbox = tk.Listbox(frame, width=30, height=10, exportselection=False)
        listbox.pack(pady=5, fill="both", expand=True)

        return listbox

    def setup_ui(self):
        """
        Sets up the UI components.
        """
        self.root.title("Google Drive versions")
        self.root.geometry("600x400")

        # Create main frame to hold both file and version frames
        main_frame = tk.Frame(self.root)
        main_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Create search frame
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=5, padx=10, fill="x")

        self.search_entry = tk.Entry(search_frame, width=40)
        self.search_entry.pack(side="left", padx=5)

        self.search_button = tk.Button(
            search_frame, text="Search", command=self.on_search
        )
        self.search_button.pack(side="left")

        # Create file and version list frames
        self.file_listbox = self.create_listbox_frame(main_frame, "Files:")
        self.file_listbox.bind("<<ListboxSelect>>", self.on_file_select)
        self.version_listbox = self.create_listbox_frame(
            main_frame, "Versions:"
        )
        self.version_listbox.bind("<<ListboxSelect>>", self.on_version_select)

        # Display initial message in file listbox
        self.file_listbox.insert(
            tk.END, "Please search for files to display them here."
        )

        # Display initial message in version listbox
        self.version_listbox.insert(
            tk.END, "Please select a file to view versions"
        )

        # Property to store file IDs
        self.file_ids = {}

        # Button to upload a new version
        self.upload_button = tk.Button(
            self.root,
            text="Upload New Version",
            command=self.on_upload_new_version,
        )
        self.upload_button.pack(pady=5)

        # Button to revert to a selected version
        self.revert_button = tk.Button(
            self.root,
            text="Revert to Version",
            command=self.on_revert_version,
        )
        self.revert_button.pack(pady=5)

    def set_on_search_callback(self, callback):
        """
        Set the callback for the search event.
        """
        self.on_search_callback = callback

    def set_on_file_select_callback(self, callback):
        """
        Set the callback for the file selection event.
        """
        self.on_file_select_callback = callback

    def set_on_upload_new_version_callback(self, callback):
        """
        Set the callback for the upload new version event.
        """
        self.on_upload_new_version_callback = callback

    def on_file_select(self, event):
        """
        Handles file selection and triggers the callback.
        """
        selected_index = self.file_listbox.curselection()
        if selected_index and self.on_file_select_callback:
            selected_file = self.file_listbox.get(selected_index)
            file_info = self.file_ids[selected_file]
            self.on_file_select_callback(file_info)
            print(f"Selected File: {file_info}")

    def on_version_select(self, event):
        """
        Handles version selection and displays the version details.
        """
        selected_index = self.version_listbox.curselection()
        if selected_index:
            selected_version = self.version_listbox.get(selected_index)
            print(f"Selected Version: {selected_version}")

    def on_upload_new_version(self):
        """
        Handles uploading a new version of the selected file.
        """
        selected_index = self.file_listbox.curselection()
        if not selected_index:
            self.show_message(
                "No File Selected",
                "Please select a file to upload a new version.",
            )
            return

        selected_file = self.file_listbox.get(selected_index)
        file_info = self.file_ids[selected_file]

        # Open a file dialog to select the new file
        file_path = filedialog.askopenfilename(
            title="Select a file to upload as a new version"
        )
        # The user canceled the file dialog
        if not file_path:
            return

        # Trigger the upload callback
        if self.on_upload_new_version_callback:
            self.on_upload_new_version_callback(file_info, file_path)

    def on_search(self):
        """
        Handles the search button click event.
        """
        search_term = self.search_entry.get().strip()
        if not search_term:
            self.show_message("Search", "Please enter a file name to search.")
            return

        # Trigger the search callback
        if self.on_search_callback:
            self.on_search_callback(search_term)

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

    def update_file_list(self, files, auto_select_first=False):
        """
        Updates the file listbox with the given files.

        Args:
            files: A list of file dictionaries with 'id' and 'name' keys.
            auto_select_first: If True, automatically selects the first file in the list.
        """
        self.file_listbox.delete(0, tk.END)
        # Clear previous file IDs
        self.file_ids = {}
        if files:
            for file in files:
                self.file_listbox.insert(tk.END, file["name"])
                self.file_ids[file["name"]] = file

            # Automatically select the first file if auto_select_first is True
            if auto_select_first:
                self.file_listbox.selection_set(0)
                self.file_listbox.event_generate("<<ListboxSelect>>")
        else:
            self.file_listbox.insert(tk.END, "No files found.")

    def display_file_versions(self, revisions):
        """
        Displays file versions in the version listbox.

        Args:
            revisions: A list of revision dictionaries.
        """
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
            self.version_listbox.insert(tk.END, "No versions found")

    def get_selected_file(self):
        """
        Returns the currently selected file in the file listbox.

        Returns:
            A dictionary containing the file's 'id' and 'name', or None if no file is selected.
        """
        selected_index = self.file_listbox.curselection()
        if selected_index:
            selected_file = self.file_listbox.get(selected_index)
            return self.file_ids.get(selected_file)
        return None

    def get_selected_version(self):
        """
        Returns the currently selected version in the version listbox.

        Returns:
            A string representing the selected version, or None if no version is selected.
        """
        selected_index = self.version_listbox.curselection()
        if selected_index:
            return self.version_listbox.get(selected_index)
        return None

    def select_file(self, file_name=None, file_id=None):
        """
        Selects the file with the given name or ID in the file listbox."
        """
        if file_name:
            for i, name in enumerate(self.file_listbox.get(0, tk.END)):
                if name == file_name:
                    self.file_listbox.selection_set(i)
                    self.file_listbox.event_generate("<<ListboxSelect>>")
                    break
        elif file_id:
            for name, info in self.file_ids.items():
                if info["id"] == file_id:
                    self.file_listbox.selection_set(name)
                    self.file_listbox.event_generate("<<ListboxSelect>>")
                    break
