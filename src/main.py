import tkinter as tk
from models.auth import authenticate_google_drive
from controllers.drive_controller import DriveController


def main():
    # Initialize the Tkinter root window
    root = tk.Tk()

    # Authenticate and create the Google Drive service
    drive_service = authenticate_google_drive()

    # Initialize the DriveController
    controller = DriveController(root, drive_service)

    # Start the Tkinter main loop
    root.mainloop()


if __name__ == "__main__":
    main()
