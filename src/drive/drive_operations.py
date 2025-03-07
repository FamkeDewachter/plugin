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
        results = (
            self.service.files()
            .list(pageSize=10, fields="nextPageToken, files(id, name)")
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
