# controllers/app_controller.py
from tkinter import messagebox
from models.auth import authenticate_google_drive
from models.drive_model import DriveModel
from views.drive_selection_ui import DriveSelectionUI
from utils.config_manager import get_stored_drive_id, store_drive_id


class AppController:
    def __init__(self):
        self.drive_service = authenticate_google_drive()
        self.drive_model = DriveModel(self.drive_service)
        self.drive_id = get_stored_drive_id()

    def start(self):
        # Check if a drive_id is stored and valid
        if self.drive_id and not self.drive_model.drive_exists(self.drive_id):
            print("Stored drive_id is no longer valid. Clearing config.")
            store_drive_id(None)  # Clear the invalid drive_id
            self.drive_id = None  # Reset the drive_id to None

        if not self.drive_id:
            # Fetch the list of drives
            drives = self.drive_model.get_drives()

            if not drives:
                messagebox.showerror("Error", "No shared drives found!")
                return

            # If there's only one drive, automatically use it
            if len(drives) == 1:
                self.drive_id = drives[0]["id"]
                store_drive_id(self.drive_id)
                print(f"Automatically selected drive: {drives[0]['name']}")
            else:
                # If there are multiple drives, show the selection UI
                drive_selection_ui = DriveSelectionUI(self.drive_service)
                self.drive_id = drive_selection_ui.select_drive()

                if self.drive_id:
                    store_drive_id(self.drive_id)
                else:
                    print("No Drive selected. Exiting.")
                    return

        # Start the main UI
        from views.main_ui import GoogleDriveUI
        from controllers.drive_controller import DriveController
        import tkinter as tk

        root = tk.Tk()
        ui = GoogleDriveUI(root)
        DriveController(ui, self.drive_service, self.drive_id)
        root.mainloop()
