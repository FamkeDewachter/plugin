from googleapiclient.http import MediaFileUpload


class DriveOperations:
    def __init__(self, service):
        """
        Initialize the DriveOperations with the Google Drive service.

        Args:
            service: The Google Drive service object.
        """
        self.service = service

    def list_files(self):
        """
        Lists the first 10 files in the user's Google Drive.

        Returns:
            A list of file dictionaries with 'id' and 'name' keys.
        """
        query = "mimeType != 'application/vnd.google-apps.folder' and trashed = false"

        results = (
            self.service.files()
            .list(
                q=query, pageSize=10, fields="nextPageToken, files(id, name)"
            )
            .execute()
        )

        return results.get("files", [])

    def search_files(self, search_term):
        """
        Searches for files in Google Drive by name.

        Args:
            search_term (str): The name or part of the file name to search.

        Returns:
            A list of file dictionaries with 'id' and 'name' keys.
        """
        query = f"name contains '{search_term}' and mimeType != 'application/vnd.google-apps.folder' and trashed = false"

        results = (
            self.service.files()
            .list(
                q=query,
                pageSize=20,
                fields="files(id, name)",
            )
            .execute()
        )

        return results.get("files", [])

    def map_file_ids(self, files):
        """
        Maps file names to their IDs.

        Args:
            files: List of file dictionaries with 'id' and 'name' keys.

        Returns:
            A dictionary mapping file names to their IDs.
        """
        return {file["name"]: file["id"] for file in files}

    def list_file_versions(self, file_id):
        """
        List all versions of a file given its file_id.

        Args:
            file_id: The ID of the file to list versions for.

        Returns:
            A list of dictionaries containing revision details.
        """
        try:
            # Call the Drive API to list revisions
            revisions = self.service.revisions().list(fileId=file_id).execute()

            # Check if the file has revisions
            if "revisions" in revisions:
                return revisions["revisions"]
            else:
                return None  # No revisions found
        except Exception as error:
            print(f"An error occurred: {error}")
            return None

    def upload_new_version(self, file_id, file_path):
        """
        Uploads a new version of a file.

        Args:
            file_id: The ID of the file to update.
            file_path: The path to the new file to upload.

        Returns:
            True if successful, False otherwise.
        """
        try:
            media = MediaFileUpload(file_path, resumable=True)
            self.service.files().update(
                fileId=file_id, media_body=media, fields="id"
            ).execute()
            return True
        except Exception as error:
            print(f"An error occurred: {error}")
            return False

    def get_file_content(self, file_id):
        """
        Fetches the content of a file given its ID.

        Args:
            file_id: The ID of the file to fetch content for.

        Returns:
            A tuple containing the content of the file and its MIME type.
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_content = request.execute()
            file_metadata = (
                self.service.files()
                .get(fileId=file_id, fields="mimeType")
                .execute()
            )
            mime_type = file_metadata.get("mimeType", "text/plain")
            return file_content, mime_type
        except Exception as error:
            print(f"An error occurred: {error}")
            return b"Failed to fetch file content.", "text/plain"
