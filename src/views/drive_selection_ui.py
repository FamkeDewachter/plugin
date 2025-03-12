# views/drive_selection_ui.py
import tkinter as tk
from tkinter import messagebox
from operator import itemgetter
from models.drive_model import DriveModel


class DriveSelectionUI:
    def __init__(self, drive_service):
        self.drive_model = DriveModel(drive_service)

    def select_drive(self):
        """Prompt the user to select a Google Drive using radio buttons."""
        drives = self.drive_model.get_drives()

        if not drives:
            messagebox.showerror("Error", "No shared drives found!")
            return None

        # If there's only one drive, return its ID immediately
        if len(drives) == 1:
            return drives[0]["id"]

        # Sort drives alphabetically by name
        drives.sort(key=itemgetter("name"))

        # Create a new window for the drive selection UI
        drive_selection = tk.Tk()
        drive_selection.title("Select Google Drive")

        # Add a header with instructions
        tk.Label(
            drive_selection,
            text="Please select a Google Drive from the list below:",
            font=("Arial", 12),
        ).pack(pady=10)

        # Create a frame to hold the radio buttons
        radio_frame = tk.Frame(drive_selection)
        radio_frame.pack(padx=10, pady=10)

        # Map drive names to IDs internally
        drive_options = {drive["name"]: drive["id"] for drive in drives}

        # Variable to store the selected drive name
        selected_drive = tk.StringVar(
            value=drives[0]["name"]
        )  # Default to first drive

        # Add radio buttons for each drive
        for drive in drives:
            tk.Radiobutton(
                radio_frame,
                text=drive["name"],  # Display only the drive name
                variable=selected_drive,
                value=drive["name"],  # Use the drive name as the value
                font=("Arial", 10),
            ).pack(
                anchor="w"
            )  # Align radio buttons to the left

        # Add a confirmation button
        def on_select():
            self.selected_drive_id = drive_options[
                selected_drive.get()
            ]  # Get ID from name
            drive_selection.destroy()

        confirm_button = tk.Button(
            drive_selection,
            text="Confirm Selection",
            command=on_select,
            bg="green",
            fg="white",
            font=("Arial", 10),
        )
        confirm_button.pack(pady=10)

        drive_selection.mainloop()
        return getattr(self, "selected_drive_id", None)
