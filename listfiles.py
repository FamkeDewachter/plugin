from googleapiclient.discovery import build
from auth import (
    authenticate_google_drive,
)  # Import the authentication function


def list_files():
    """
    Lists the first 10 files in the user's Google Drive.
    """
    creds = authenticate_google_drive()  # Get credentials
    service = build("drive", "v3", credentials=creds)
    results = (
        service.files()
        .list(pageSize=10, fields="nextPageToken, files(id, name)")
        .execute()
    )
    items = results.get("files", [])
    if not items:
        print("No files found.")
    else:
        print("Files:")
        for item in items:
            print(f"{item['name']} ({item['id']})")


if __name__ == "__main__":
    list_files()
