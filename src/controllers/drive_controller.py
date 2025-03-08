from models.drive_operations import (
    get_file_metadata,
    search_files,
    get_versions_of_file,
    upload_new_version,
)


class DriveController:
    def __init__(self, ui, drive_service):
        """
        Initialize the DriveController.

        Args:
            ui: The GoogleDriveUI object.
            drive_service: The Google Drive service object.
        """
        self.drive_service = drive_service
        self.ui = ui

        # Dictionary to cache additional file metadata
        self.file_metadata_cache = {}

        # Set up callbacks for UI events
        self.ui.set_callback("search", self.search_files)
        self.ui.set_callback("file_select", self.update_file_versions)
        self.ui.set_callback("upload_new_version", self.upload_file_version)

    def update_file_versions(self, file_info):
        """
        Fetches and sorts file versions for the selected file, then passes them to the UI for display.

        Args:
            file_info: The dictionary containing file information.
        """
        file_id = file_info["id"]

        # Fetch additional metadata if not already cached
        if file_id not in self.file_metadata_cache:
            print(f"Fetching metadata for file ID: {file_id}...")
            additional_metadata = get_file_metadata(
                self.drive_service, file_id
            )
            if additional_metadata:
                # Merge additional metadata into file_info
                file_info.update(additional_metadata)
                # Cache the metadata
                self.file_metadata_cache[file_id] = file_info
            else:
                self.ui.show_message("Error", "Failed to fetch file metadata.")
                return

        # Fetch the latest versions of the file
        versions = get_versions_of_file(self.drive_service, file_id)

        if versions:
            # Sort revisions by modifiedTime in descending order (newest first)
            sorted_versions = sorted(
                versions, key=lambda x: x["modifiedTime"], reverse=True
            )
        else:
            sorted_versions = []

        # Pass the sorted revisions to the UI for display
        self.ui.display_file_versions(sorted_versions)

    def upload_file_version(self, file_info, file_path, description):
        """
        Uploads a new version of the selected file.

        Args:
            file_info: The dictionary containing file information.
            file_path: The path to the new file to upload.
            description: The description for the new version.
        """
        print(
            f"Uploading new version for file: {file_info} from path: {file_path}"
        )
        file_id = file_info["id"]

        # Get the file_id of the currently selected file before refreshing the list
        selected_file_id = self.ui.get_selected_file_id()
        print("selected_file_id", selected_file_id)

        # Upload the new version
        if upload_new_version(
            self.drive_service, file_id, file_path, description
        ):
            self.ui.show_message(
                "Success", "New version uploaded successfully!"
            )
            print("New version uploaded successfully")

            # Clear the search bar
            self.ui.reset_search_entry()

            # Refresh the file list with an empty search term (fetch all files)
            self.update_file_list(search_files(self.drive_service, ""))

            # Reselect the previously selected file by its ID
            if selected_file_id:
                self.ui.select_file(file_id=selected_file_id)
        else:
            self.ui.show_message("Error", "Failed to upload new version.")
            print("Failed to upload new version")

    def search_files(self, search_term):
        """
        Searches for files in Google Drive
        by name and updates the file listbox.

        Args:
            search_term (str): The name or part of the file name to search.
        """
        print(f"Searching for files with term: {search_term}")
        files = search_files(self.drive_service, search_term)
        self.ui.update_file_list(files)

    def update_file_list(self, files):
        """
        Updates the file list in the UI.

        Args:
            files: A list of file dictionaries with 'id' and 'name' keys.
        """
        print(f"Updating file list with files: {files}")
        self.ui.update_file_list(files)
