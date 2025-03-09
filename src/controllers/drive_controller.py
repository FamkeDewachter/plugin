from models.drive_operations import (
    get_most_recent_files,
    get_file_metadata,
    get_files,
    get_versions_of_file,
    upload_new_version,
    get_current_version_id,
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

        # Dictionary to cache additional file metadata
        self.file_metadata_cache = {}

        # Dictionary to store version details
        self.version_details = {}

        # Bind UI events to controller methods
        self.ui.search_button.bind("<Button-1>", self.on_search)
        self.ui.file_listbox.bind("<<ListboxSelect>>", self.on_file_select)
        self.ui.version_listbox.bind(
            "<<ListboxSelect>>", self.on_version_select
        )
        self.ui.upload_button.bind("<Button-1>", self.on_upload_new_version)
        self.ui.revert_button.bind("<Button-1>", self.on_revert_version)

        self.on_startup()

    def on_startup(self):
        """
        Fetches the most recent files from Google Drive and updates the UI.
        """
        print("Fetching most recent files on startup...")
        recent_files = get_most_recent_files(self.drive_service)
        if recent_files:
            # Pass only the file names to the UI
            file_names = [file["name"] for file in recent_files]
            self.ui.display_files(file_names)
        else:
            print("No recent files found.")

    def on_search(self, event):
        """
        Handles the search button click.
        """
        search_term = self.ui.search_entry.get().strip()
        if not search_term:
            self.ui.show_message(
                "Search", "Please enter a file name to search."
            )
            return

        self.search_files(search_term)

    def search_files(self, search_term):
        """
        Searches for files in Google Drive by name and updates the file listbox.
        """
        print(f"Searching for files with term: {search_term}")
        files = get_files(self.drive_service, search_term)
        # Pass only the file names to the UI
        file_names = [file["name"] for file in files]
        self.ui.display_files(file_names)

    def on_file_select(self, event):
        """
        Handles file selection.
        """
        selected_index = self.ui.file_listbox.curselection()
        if selected_index:
            selected_file = self.ui.file_listbox.get(selected_index)
            # Check if the selected item is the placeholder
            if (
                selected_file
                == "Please search for files to display them here."
            ):
                return  # Ignore selection of placeholder
            print(f"Selected File: {selected_file}")
            self.update_versions(selected_file)

    def update_versions(self, file_name):
        """
        Fetches and sorts file versions for the selected file,
        then passes them to the UI for display.
        """
        # Fetch the file ID based on the file name
        files = get_files(self.drive_service, search_term=file_name)
        if not files:
            self.ui.show_message("Error", "File not found.")
            return

        file_id = files[0]["id"]

        # Fetch additional metadata if not already cached
        if file_id not in self.file_metadata_cache:
            print(f"Fetching metadata for file ID: {file_id}...")
            additional_metadata = get_file_metadata(
                self.drive_service, file_id
            )
            if additional_metadata:
                # Cache the metadata
                self.file_metadata_cache[file_id] = additional_metadata
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

            # Fetch descriptions from MongoDB and add them to the versions
            for version in sorted_versions:
                version_id = version["id"]
                description = get_version_description(file_id, version_id)
                version["description"] = description if description else ""

            # Store version details in the controller
            self.version_details = {
                version["originalFilename"]: {
                    "modified_time": version["modifiedTime"],
                    "description": version["description"],
                }
                for version in sorted_versions
            }
        else:
            sorted_versions = []
            self.version_details = {}

        # Pass the sorted revisions to the UI for display
        self.ui.display_versions(sorted_versions)

    def on_version_select(self, event):
        """
        Handles version selection and updates the version details section.
        """
        selected_index = self.ui.version_listbox.curselection()
        if selected_index:
            selected_version = self.ui.version_listbox.get(selected_index)
            # Check if the selected item is the placeholder
            if selected_version == "Please select a file to view versions.":
                return  # Ignore selection of placeholder
            print(f"Selected Version: {selected_version}")
            self.update_version_details(selected_version)

    def update_version_details(self, version_name):
        """
        Updates the version details section with the selected version's details.
        """
        details = self.version_details.get(
            version_name, {"modified_time": "", "description": ""}
        )
        self.ui.version_details_section.update_details(
            details["modified_time"], details["description"]
        )

    def on_upload_new_version(self, event):
        """
        Handles uploading a new version of the selected file.
        """
        print("Upload New Version button clicked")
        selected_file_index = self.ui.file_listbox.curselection()
        if not selected_file_index:
            self.ui.show_message(
                "No File Selected",
                "Please select a file to upload a new version.",
            )
            return

        selected_file = self.ui.file_listbox.get(selected_file_index)

        # Open a file dialog to select the new file
        file_path = self.ui.open_file_dialog(title="Select New Version")

        # The user canceled the file dialog
        if not file_path:
            return

        # Get the description
        description = self.ui.description_entry.get()
        # If the placeholder is still there, treat it as an empty description
        if description == "Description":
            description = ""

        self.upload_new_version(selected_file, file_path, description)

    def upload_new_version(self, file_name, file_path, description):
        """
        Uploads a new version of the selected file
        and saves the description to MongoDB.
        """
        print(
            f"Uploading new version for file: {file_name} from path: {file_path}"
        )

        # Fetch the file ID based on the file name
        files = get_files(self.drive_service, search_term=file_name)
        if not files:
            self.ui.show_message("Error", "File not found.")
            return

        file_id = files[0]["id"]

        # Upload the new version to Google Drive
        upload_new_version(self.drive_service, file_id, file_path)

        if upload_new_version:
            # Fetch the latest revision ID
            revision_id = get_current_version_id(self.drive_service, file_id)

            if revision_id:
                # Save the description to MongoDB
                save_revision_description(file_id, revision_id, description)

                self.ui.show_message(
                    "Success", "New version uploaded successfully!"
                )

                print(
                    "New version uploaded successfully"
                    " and description saved to MongoDB."
                )

                # Clear the search bar and description entry
                self.ui.reset_search_entry()
                self.ui.reset_description_entry()
        else:
            self.ui.show_message(
                "Error", "Failed to fetch the latest revision ID."
            )
            print("Failed to fetch the latest revision ID.")

    def on_revert_version(self, event):
        """
        Handles the "Revert to Version" button click.
        """
        print("Revert to Version button clicked.")
