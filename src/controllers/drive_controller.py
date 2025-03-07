from models.drive_operations import (
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
        self.ui.set_controller(self)

    def update_file_list(self, files):
        """
        Updates the file listbox with the given files.

        Args:
            files: A list of file dictionaries with 'id' and 'name' keys.
        """
        self.ui.update_file_list(files)

    def display_file_versions(self, file_info):
        """
        Displays file versions for the selected file.

        Args:
            file_info: The dictionary containing file information.
        """
        file_id = file_info["id"]
        revisions = get_versions_of_file(self.drive_service, file_id)
        self.ui.display_file_versions(revisions)

    def upload_file_version(self, file_info, file_path):
        """
        Uploads a new version of the selected file.

        Args:
            file_info: The dictionary containing file information.
            file_path: The path to the new file to upload.
        """
        file_id = file_info["id"]
        if upload_new_version(self.drive_service, file_id, file_path):
            self.ui.show_message(
                "Success", "New version uploaded successfully!"
            )
        else:
            self.ui.show_message("Error", "Failed to upload new version.")

    def search_files(self, search_term):
        """
        Searches for files in Google Drive by name and updates the file listbox.

        Args:
            search_term (str): The name or part of the file name to search.
        """
        files = search_files(self.drive_service, search_term)
        self.update_file_list(files)
