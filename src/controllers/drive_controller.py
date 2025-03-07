from models.drive_operations import DriveOperations
from views.ui import GoogleDriveUI
import tkinter as tk
from tkinter import messagebox, filedialog


class DriveController:
    def __init__(self, root, drive_service):
        """
        Initialize the DriveController.

        Args:
            root: The root Tkinter window.
            drive_service: The Google Drive service object.
        """
        self.drive_ops = DriveOperations(drive_service)
        self.ui = GoogleDriveUI(root)
        self.ui.controller = self  # Pass the controller reference to the UI
        self.ui.upload_button.config(command=self.upload_new_version)
        self.ui.file_listbox.bind("<<ListboxSelect>>", self.on_file_select)

    def update_file_list(self, files):
        """
        Updates the file listbox with the given files.

        Args:
            files: A list of file dictionaries with 'id' and 'name' keys.
        """
        self.ui.file_listbox.delete(0, tk.END)
        if files:
            self.ui.file_ids = self.drive_ops.map_file_ids(files)
            for file in files:
                self.ui.file_listbox.insert(tk.END, file["name"])
        else:
            self.ui.file_listbox.insert(tk.END, "No files found.")

    def on_file_select(self, event):
        """
        Handles file selection and displays file versions.
        """
        selected_index = self.ui.file_listbox.curselection()
        if selected_index:
            selected_file = self.ui.file_listbox.get(selected_index)
            file_info = self.ui.file_ids[selected_file]

            file_id = file_info["id"]
            print(f"Selected File: {selected_file}, File ID: {file_id}")
            revisions = self.drive_ops.list_file_versions(file_id)
            self.ui.display_file_versions(revisions)

        else:
            self.ui.display_file_versions([])

    def upload_new_version(self):
        """
        Handles uploading a new version of the selected file.
        """
        selected_index = self.ui.file_listbox.curselection()
        if not selected_index:
            messagebox.showwarning(
                "No File Selected",
                "Please select a file to upload a new version.",
            )
            return

        selected_file = self.ui.file_listbox.get(selected_index)
        file_id = self.ui.file_ids[selected_file]
        file_path = filedialog.askopenfilename(
            title="Select a file to upload as a new version"
        )
        if file_path:
            if self.drive_ops.upload_new_version(file_id, file_path):
                messagebox.showinfo(
                    "Success", "New version uploaded successfully!"
                )
            else:
                messagebox.showerror("Error", "Failed to upload new version.")

    def search_files(self, search_term):
        """
        Searches for files in Google Drive by name and updates the file listbox.

        Args:
            search_term (str): The name or part of the file name to search.
        """
        files = self.drive_ops.search_files(search_term)
        self.update_file_list(files)
