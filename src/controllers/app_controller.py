# controllers/app_controller.py
from tkinter import messagebox
from models.auth import authenticate_google_drive
from models.drive_model import DriveModel
from views.drive_selection_ui import DriveSelectionUI
from utils.config_manager import get_stored_drive_data, store_drive_data
from views.main_window import MainWindow
from controllers.version_control_controller import VersionControlController
from controllers.comments_controller import CommentsController
from controllers.roles_controller import RolesController


class AppController:
    def __init__(self):
        self.drive_service = authenticate_google_drive()
        self.drive_model = DriveModel(self.drive_service)
        self.selected_drive_id, self.all_drives = (
            get_stored_drive_data()
        )  # Get both selected drive and all drives

    def start(self):
        # Check if a selected_drive_id is stored and valid
        if self.selected_drive_id and not any(
            drive["id"] == self.selected_drive_id for drive in self.all_drives
        ):
            print(
                "Stored selected_drive_id is no longer valid. Clearing config."
            )
            store_drive_data(
                None, []
            )  # Clear the invalid selected_drive_id and all_drives
            self.selected_drive_id = None  # Reset the selected_drive_id

        if not self.selected_drive_id:
            # Fetch the list of drives
            drives = self.drive_model.get_drives()

            if not drives:
                messagebox.showerror("Error", "No shared drives found!")
                return

            # If there's only one drive, automatically use it
            if len(drives) == 1:
                self.selected_drive_id = drives[0]["id"]
                self.all_drives = drives
                store_drive_data(
                    self.selected_drive_id, self.all_drives
                )  # Store selected drive and all drives
                print(f"Automatically selected drive: {drives[0]['name']}")
            else:
                # If there are multiple drives, show the selection UI
                drive_selection_ui = DriveSelectionUI(self.drive_service)
                self.selected_drive_id = drive_selection_ui.select_drive()

                if self.selected_drive_id:
                    self.all_drives = [
                        {"name": drive["name"], "id": drive["id"]}
                        for drive in self.drive_model.get_drives()
                    ]  # Update the list of all drives
                    store_drive_data(
                        self.selected_drive_id, self.all_drives
                    )  # Store selected drive and all drives
                else:
                    print("No Drive selected. Exiting.")
                    return

        import tkinter as tk

        root = tk.Tk()

        main_window = MainWindow(root)
        version_control_controller = VersionControlController(
            main_window.version_control_ui,
            self.drive_service,
            self.selected_drive_id,
        )
        comments_controller = CommentsController(
            main_window.comments_ui, self.drive_service, self.selected_drive_id
        )
        roles_controller = RolesController(
            main_window.roles_ui, self.drive_service, self.selected_drive_id
        )

        root.mainloop()
