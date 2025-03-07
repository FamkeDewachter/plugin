import tkinter as tk
from auth.auth import authenticate_google_drive
from ui.ui import GoogleDriveApp


def main():
    # Initialize the Tkinter root window
    root = tk.Tk()

    # Authenticate and create the Google Drive service
    drive_service = authenticate_google_drive()

    # Initialize the Google Drive UI and pass the service to it
    app = GoogleDriveApp(root, drive_service)

    # Start the Tkinter main loop
    root.mainloop()


if __name__ == "__main__":
    main()
