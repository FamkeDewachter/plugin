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

    def setup_ui(self):
        """
        Sets up the UI components.
        """
        self.root.title("Google Drive File Lister")
        self.root.geometry("400x300")

        # Create a listbox to display files
        self.file_listbox = tk.Listbox(self.root, width=50, height=10)
        self.file_listbox.pack(pady=20)
        self.file_listbox.bind("<<ListboxSelect>>", self.on_file_select)

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
        Displays file versions in a new window with options to revert.

        Args:
            revisions: A list of revision dictionaries.
        """
        revision_window = tk.Toplevel(self.root)
        revision_window.title("File Versions")

        # Create a text widget to display revision details
        text_widget = tk.Text(
            revision_window, wrap=tk.WORD, width=60, height=20
        )
        text_widget.pack(padx=10, pady=10)

        # Insert revision details into the text widget
        for revision in revisions:
            text_widget.insert(tk.END, f"Revision ID: {revision['id']}\n")
            text_widget.insert(
                tk.END, f"Modified Time: {revision['modifiedTime']}\n"
            )
            text_widget.insert(
                tk.END,
                f"Description: {revision.get('description', 'No description')}\n",
            )
            text_widget.insert(
                tk.END,
                f"MD5Checksum: {revision.get('md5Checksum', 'No checksum')}\n",
            )

            # Add a "Revert" button for each revision
            revert_button = tk.Button(
                revision_window,
                text="Revert to This Version",
                command=lambda rev_id=revision["id"]: self.revert_to_version(
                    rev_id
                ),
            )
            text_widget.window_create(tk.END, window=revert_button)
            text_widget.insert(tk.END, "\n" + "-" * 40 + "\n")

    def revert_to_version(self, revision_id):
        """
        Handles reverting to a specific version of a file.

        Args:
            revision_id: The ID of the revision to revert to.
        """
        print(f"Reverting to revision ID: {revision_id}")
