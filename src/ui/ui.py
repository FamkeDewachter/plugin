import tkinter as tk
from tkinter import messagebox
from drive.drive_operations import list_files, map_file_ids


class GoogleDriveApp:
    def __init__(self, root, drive_service):
        """
        Initialize the Google Drive UI.

        Args:
            root: The root Tkinter window.
            drive_service: The Google Drive service object.
        """
        self.root = root

        # Store the Google Drive service
        self.drive_service = drive_service

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
            files = list_files(self.drive_service)
            self.file_listbox.delete(0, tk.END)  # Clear the listbox
            self.file_ids = map_file_ids(files)  # Map file names to IDs
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
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
