import tkinter as tk
from tkinter import messagebox
from drive.drive_operations import list_files


class GoogleDriveApp:
    def __init__(self, root, drive_service):
        """
        Initialize the Google Drive UI.

        Args:
            root: The root Tkinter window.
            drive_service: The Google Drive service object.
        """
        self.root = root
        self.root.title("Google Drive File Lister")
        self.root.geometry("400x300")

        # Store the Google Drive service
        self.drive_service = drive_service

        # Create a listbox to display files
        self.file_listbox = tk.Listbox(root, width=50, height=10)
        self.file_listbox.pack(pady=20)

        # Create a button to list files
        self.list_button = tk.Button(
            root, text="List Files", command=self.update_file_list
        )
        self.list_button.pack(pady=10)

    def update_file_list(self):
        """
        Fetches and displays files from Google Drive.
        """
        try:
            # Call the list_files function with the stored service
            files = list_files(self.drive_service)
            self.file_listbox.delete(0, tk.END)  # Clear the listbox
            if not files:
                self.file_listbox.insert(tk.END, "No files found.")
            else:
                for file in files:
                    self.file_listbox.insert(
                        tk.END, f"{file['name']} ({file['id']})"
                    )
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
