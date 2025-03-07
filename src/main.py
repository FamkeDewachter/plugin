import tkinter as tk
from models.auth import authenticate_google_drive
from controllers.drive_controller import DriveController
from views.tool_ui import GoogleDriveUI


def main():
    # Initialize the Tkinter root window
    root = tk.Tk()

    # Authenticate and create the Google Drive service
    drive_service = authenticate_google_drive()

    # Initialize the GoogleDriveUI
    ui = GoogleDriveUI(root)

    # Initialize the DriveController
    controller = DriveController(ui, drive_service)

    # Start the Tkinter main loop
    root.mainloop()


if __name__ == "__main__":
    main()
