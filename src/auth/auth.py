import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]


def authenticate_google_drive():
    """
    Authenticates the user and returns Google Drive API service.
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

    # Build the service and return it
    service = build("drive", "v3", credentials=creds)
    return service
