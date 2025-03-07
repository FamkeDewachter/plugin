from models.drive_operations import (
    list_files,
    search_files,
    get_versions_of_file,
    upload_new_version,
)
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
        self.drive_service = drive_service
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
        self.ui.file_ids = {}  # Clear previous file IDs
        if files:
            for file in files:
                self.ui.file_listbox.insert(tk.END, file["name"])
                self.ui.file_ids[file["name"]] = file
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
            self.display_file_versions(file_info)

    def display_file_versions(self, file_info):
        """
        Displays file versions for the selected file.

        Args:
            file_info: The dictionary containing file information.
        """
        file_id = file_info["id"]
        print(f"Selected File: {file_info['name']}, File ID: {file_id}")
        revisions = get_versions_of_file(self.drive_service, file_id)
        self.ui.display_file_versions(revisions)

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
        file_info = self.ui.file_ids[selected_file]
        self.upload_file_version(file_info)

    def upload_file_version(self, file_info, file_path=None):
        """
        Uploads a new version of the selected file.

        Args:
            file_info: The dictionary containing file information.
            file_path: The path to the new file to upload.
        """
        if not file_path:
            file_path = filedialog.askopenfilename(
                title="Select a file to upload as a new version"
            )
            if not file_path:
                return  # User canceled the dialog

        file_id = file_info["id"]
        if upload_new_version(self.drive_service, file_id, file_path):
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
        files = search_files(self.drive_service, search_term)
        self.update_file_list(files)
