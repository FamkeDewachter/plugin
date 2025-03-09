from models.google_drive_utils import (
    get_most_recent_files,
    get_files,
    get_file_info,
    get_versions_of_file,
    upload_version,
    get_latest_version_id,
)
from models.mongo_utils import (
    save_revision_description,
    get_version_description,
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

        # Store file and version information
        self.files = []  # List of files
        self.selected_file = None  # Selected file
        self.versions = []  # List of versions for the selected file
        self.selected_version = None  # Selected version

        # Bind UI events to controller methods
        self.ui.search_button.bind("<Button-1>", self.search_clicked)
        self.ui.file_listbox.bind("<<ListboxSelect>>", self.file_selected)
        self.ui.version_listbox.bind(
            "<<ListboxSelect>>", self.version_selected
        )
        self.ui.upload_new_version_button.bind(
            "<Button-1>", self.upload_version_clicked
        )

        self.ui.revert_button.bind("<Button-1>", self.revert_version_clicked)

    def upload_version_clicked(self, event):
        """
        Handles uploading a new version of the selected file.
        """
        print("Upload New Version button clicked")

        # Check if a file is selected from the listbox
        selected_file_index = self.ui.file_listbox.curselection()
        if not selected_file_index:
            self.ui.show_message(
                "No File Selected",
                "Please select a file from the list to upload a new version.",
            )
            return

        # Check if a file is selected for upload
        upload_file_path = self.ui.get_upload_file_path()
        if not upload_file_path:
            self.ui.show_message(
                "No File Selected",
                "Please select a file to upload as a new version.",
            )
            return

        # Get the description
        description = self.ui.description_entry.get()
        if description == "Description" or not description:
            self.ui.show_message(
                "No Description",
                "Please provide a description for the new version.",
            )
            return

        selected_file_id = self.selected_file["id"]
        self.upload_new_version(
            selected_file_id, upload_file_path, description
        )

    def upload_new_version(self, file_id, file_path, description):
        """
        Uploads a new version to Google Drive
        and saves the description to MongoDB.
        """
        if not self.selected_file:
            self.ui.show_message("Error", "No file selected.")
            return

        print(
            f"Uploading new version for file ID: {file_id} from path: {file_path}..."
        )

        # Upload the new version to Google Drive
        upload_version(self.drive_service, file_id, file_path)

        if upload_version:
            # Fetch the id of the version i just uploaded
            revision_id = get_latest_version_id(self.drive_service, file_id)

            if revision_id:
                # Save the description to MongoDB
                save_revision_description(file_id, revision_id, description)

                self.ui.show_message(
                    "Success", "New version uploaded successfully!"
                )
                print(
                    "New version uploaded successfully and description saved to MongoDB."
                )

                self.reset_tool()
        else:
            self.reset_tool()
            self.ui.show_message(
                "Error", "Failed to fetch the latest revision ID."
            )
            print("Failed to fetch the latest revision ID.")

    def revert_version_clicked(self, event):
        """
        Handles the "Revert to Version" button click.
        """
        if not self.selected_version:
            self.ui.show_message("Error", "No version selected.")
            return

        version_id = self.selected_version["id"]
        file_id = self.selected_file["id"]

        # Implement the revert logic here
        print(f"Reverting to version ID: {version_id} for file ID: {file_id}")

        self.reset_tool()

    def search_clicked(self, event):
        """
        Handles the search button click.
        """
        search_term = self.ui.search_entry.get()
        if not search_term:
            self.ui.show_message(
                "No Search Term", "Please enter a file name to search for."
            )
            return

        self.files = get_files(self.drive_service, search_term=search_term)

        if not self.files:
            self.ui.reset_search_entry()
            self.ui.show_message(
                "No Results", "No files found matching the search term."
            )
            return

        # Add the files to the file listbox
        self.ui.file_listbox.clear_placeholder()
        for file in self.files:
            self.ui.file_listbox.add_item(file["name"], file["id"])

        else:
            return

    def file_selected(self, event):
        """
        Handles the file selection from the listbox.
        """
        selected_file_index = self.ui.file_listbox.curselection()
        if selected_file_index:
            selected_file_id = self.ui.file_listbox.get_id(
                selected_file_index[0]
            )
            # Store the selected file and its versions
            self.selected_file = get_file_info(
                self.drive_service, selected_file_id
            )
            self.versions = get_versions_of_file(
                self.drive_service, selected_file_id
            )

            # Display the file details
            self.ui.file_details_section.update_details(
                File_Size=self.selected_file["size"],
                MIME_Type=self.selected_file["mimeType"],
            )

            if not self.versions:
                return

            # Add the versions to the version listbox
            self.ui.version_listbox.clear_placeholder()
            for version in self.versions:
                self.ui.version_listbox.add_item(
                    version["originalFilename"], version["id"]
                )

    def version_selected(self, event):
        """
        Handles the version selection from the listbox.
        """
        selected_version_index = self.ui.version_listbox.curselection()
        if selected_version_index:
            selected_version_id = self.ui.version_listbox.get_id(
                selected_version_index[0]
            )
            self.selected_version = next(
                (
                    version
                    for version in self.versions
                    if version["id"] == selected_version_id
                ),
                None,
            )
            if self.selected_version:
                description = get_version_description(
                    self.selected_file["id"], self.selected_version["id"]
                )
                self.ui.version_details_section.update_details(
                    Modified_Time=self.selected_version["modifiedTime"],
                    Description=(
                        description
                        if description
                        else "No description available."
                    ),
                )

    def reset_tool(self):
        """
        Reset the controller state.
        """
        self.files = []
        self.selected_file = None
        self.versions = []
        self.selected_version = None
        self.ui.reset_all()
