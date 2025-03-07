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
            command=self.upload_new_version,
        )
        self.upload_button.pack(pady=5)

    def on_file_select(self, event):
        """
        Handles file selection and displays the file name and ID.
        """
        selected_index = self.file_listbox.curselection()
        if selected_index:
            selected_file = self.file_listbox.get(selected_index)
            file_id = self.file_ids[selected_file]
            print(f"Selected File: {selected_file}, ID: {file_id}")

    def on_version_select(self, event):
        """
        Handles version selection and displays the version details.
        """
        selected_index = self.version_listbox.curselection()
        if selected_index:
            selected_version = self.version_listbox.get(selected_index)
            print(f"Selected Version: {selected_version}")

    def upload_new_version(self):
        """
        Handles uploading a new version of the selected file.
        """
        selected_index = self.file_listbox.curselection()
        if not selected_index:
            messagebox.showwarning(
                "No File Selected",
                "Please select a file to upload a new version.",
            )
            return

        # Open a file dialog to select the new file
        file_path = filedialog.askopenfilename(
            title="Select a file to upload as a new version"
        )
        if not file_path:
            return  # User canceled the dialog

        print(f"Uploading new version from: {file_path}")

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

    def on_search(self):
        """
        Handles the search button click event.
        """
        search_term = self.search_entry.get().strip()
        if not search_term:
            messagebox.showinfo(
                "Search", "Please enter a file name to search."
            )
            return

        # Call the controller's search method
        self.controller.search_files(search_term)
