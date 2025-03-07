import tkinter as tk
from auth.auth import authenticate_google_drive
from ui.ui import GoogleDriveApp


def main():
    # Initialize the Tkinter root window
    root = tk.Tk()
    root.title("Google Drive File Lister")
    root.geometry("400x300")

    # Authenticate and create the Google Drive service
    drive_service = authenticate_google_drive()

    # Initialize the Google Drive UI and pass the service to it
    app = GoogleDriveApp(root, drive_service)
    app.update_file_list()  # Directly update the file list on initialization

    # Start the Tkinter main loop
    root.mainloop()


if __name__ == "__main__":
    main()
