import tkinter as tk
from auth.auth import authenticate_google_drive
from ui.ui import GoogleDriveApp
from drive.drive_operations import DriveOperations


def main():
    # Initialize the Tkinter root window
    root = tk.Tk()
    root.title("Google Drive File Lister")
    root.geometry("400x300")

    # Authenticate and create the Google Drive service
    drive_service = authenticate_google_drive()

    # Initialize the DriveOperations class with the service
    drive_ops = DriveOperations(drive_service)

    # Initialize the Google Drive UI and pass the drive operations to it
    app = GoogleDriveApp(root, drive_ops)
    app.update_file_list()  # Directly update the file list on initialization

    # Start the Tkinter main loop
    root.mainloop()


if __name__ == "__main__":
    main()
