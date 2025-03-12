# controllers/app_controller.py
from models.auth import authenticate_google_drive
from views.drive_selection_ui import DriveSelectionUI
from models.drive_model import DriveModel
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
            drive_selection_ui = DriveSelectionUI(self.drive_service)
            self.drive_id = drive_selection_ui.select_drive()

            if self.drive_id:
                store_drive_id(self.drive_id)

            else:
                print("No Drive selected. Exiting.")
                return

        # Start the main UI
        from views.tool_ui import GoogleDriveUI
        from controllers.drive_controller import DriveController
        import tkinter as tk

        root = tk.Tk()
        ui = GoogleDriveUI(root)
        DriveController(ui, self.drive_service, self.drive_id)
        root.mainloop()
