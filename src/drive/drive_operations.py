from googleapiclient.discovery import build
from auth.auth import authenticate_google_drive


def list_files():
    """
    Lists the first 10 files in the user's Google Drive.
    """
    creds = authenticate_google_drive()
    service = build("drive", "v3", credentials=creds)
    results = (
        service.files()
        .list(pageSize=10, fields="nextPageToken, files(id, name)")
        .execute()
    )
    return results.get("files", [])
