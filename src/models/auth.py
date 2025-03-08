import os
import pickle
import json
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = [
    "https://www.googleapis.com/auth/drive",  # Full access to Google Drive (read/write)
    "https://www.googleapis.com/auth/drive.appdata",  # Access to app-specific files
    "https://www.googleapis.com/auth/drive.file",  # Access to files created or opened by the app
]

METADATA_FILE_NAME = "metadata.json"  # Name of the metadata file
METADATA_FILE_CONTENT = (
    {}
)  # Initial content of the metadata file (empty JSON object)


def authenticate_google_drive():
    """
    Authenticates the user and returns Google Drive API service.
    Also ensures that the metadata file exists on Google Drive.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens.
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # If there are no valid credentials, prompt the user to log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                # If the refresh token is invalid, delete the token.pickle file and re-authenticate.
                os.remove("token.pickle")
                # Path to credentials.json in the auth folder
                credentials_path = os.path.join(
                    os.path.dirname(__file__), "credentials.json"
                )
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
        else:
            # Path to credentials.json in the auth folder
            credentials_path = os.path.join(
                os.path.dirname(__file__), "credentials.json"
            )
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    # Build the service
    service = build("drive", "v3", credentials=creds)

    # Ensure the metadata file exists
    ensure_metadata_file_exists(service)

    return service


def ensure_metadata_file_exists(service):
    """
    Checks if the metadata file exists on Google Drive. If not, creates it.

    Args:
        service: The Google Drive service object.
    """
    try:
        # Search for the metadata file by name
        response = (
            service.files()
            .list(q=f"name='{METADATA_FILE_NAME}'", fields="files(id)")
            .execute()
        )
        files = response.get("files", [])

        if not files:
            # Create the metadata file if it doesn't exist
            print(
                f"Creating metadata file '{METADATA_FILE_NAME}' on Google Drive..."
            )
            file_metadata = {
                "name": METADATA_FILE_NAME,
                "mimeType": "application/json",
            }
            media = MediaIoBaseUpload(
                BytesIO(json.dumps(METADATA_FILE_CONTENT).encode("utf-8")),
                mimetype="application/json",
            )
            file = (
                service.files()
                .create(body=file_metadata, media_body=media, fields="id")
                .execute()
            )
            print(f"Metadata file created with ID: {file['id']}")
        else:
            print(f"Metadata file already exists with ID: {files[0]['id']}")
    except Exception as error:
        print(f"Failed to ensure metadata file exists: {error}")
