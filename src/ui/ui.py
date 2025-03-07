import tkinter as tk
from tkinter import messagebox


class GoogleDriveApp:
    def __init__(self, root, drive_ops):
        """
        Initialize the Google Drive UI.

        Args:
            root: The root Tkinter window.
            drive_ops: The DriveOperations object.
        """
        self.root = root
        self.drive_ops = drive_ops

        # Create a listbox to display files
        self.file_listbox = tk.Listbox(root, width=50, height=10)
        self.file_listbox.pack(pady=20)
        self.file_listbox.bind("<<ListboxSelect>>", self.on_file_select)

        # Property to store file IDs
        self.file_ids = {}

        # Directly update the file list on initialization
        self.update_file_list()

    def update_file_list(self):
        """
        Fetches and displays files from Google Drive.
        """
        try:
            # Call the list_files function with the stored service
            files = self.drive_ops.list_files()
            self.file_listbox.delete(0, tk.END)  # Clear the listbox
            self.file_ids = self.drive_ops.map_file_ids(
                files
            )  # Map file names to IDs
            if not files:
                self.file_listbox.insert(tk.END, "No files found.")
            else:
                for file in files:
                    self.file_listbox.insert(tk.END, file["name"])
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def on_file_select(self, event):
        """
        Handles file selection and displays the file name and ID.
        """
        try:
            # Get the selected file name
            selected_index = self.file_listbox.curselection()
            if selected_index:
                selected_file = self.file_listbox.get(selected_index)
                file_id = self.file_ids[selected_file]
                print(f"Selected File: {selected_file}, ID: {file_id}")

                # Fetch file versions from DriveOperations
                revisions = self.drive_ops.list_file_versions(file_id)
                if revisions:
                    self.display_file_versions(revisions)
                else:
                    print("No revisions found for this file.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def display_file_versions(self, revisions):
        """
        Displays file versions in a new window or dialog.

        Args:
            revisions: A list of revision dictionaries.
        """
        # Create a new window to display revisions
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
            text_widget.insert(tk.END, "-" * 40 + "\n")
