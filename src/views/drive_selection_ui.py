# views/drive_selection_ui.py
import tkinter as tk
from tkinter import messagebox
from models.drive_model import DriveModel


class DriveSelectionUI:
    def __init__(self, drive_service):
        self.drive_model = DriveModel(drive_service)

    def select_drive(self):
        """Prompt the user to select a Google Drive."""
        drives = self.drive_model.get_drives()

        if not drives:
            messagebox.showerror("Error", "No shared drives found!")
            return None

        drive_selection = tk.Tk()
        drive_selection.title("Select Google Drive")

        tk.Label(drive_selection, text="Select a Drive:").pack()

        selected_drive = tk.StringVar(value=drives[0]["name"])
        drive_options = {drive["name"]: drive["id"] for drive in drives}

        def on_select():
            drive_selection.destroy()
            self.selected_drive_id = drive_options[selected_drive.get()]

        for name in drive_options.keys():
            tk.Radiobutton(
                drive_selection,
                text=name,
                variable=selected_drive,
                value=name,
            ).pack()

        tk.Button(drive_selection, text="Confirm", command=on_select).pack(
            pady=5
        )

        drive_selection.mainloop()
        return self.selected_drive_id
