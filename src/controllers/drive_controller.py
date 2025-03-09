from models.drive_operations import (
    get_most_recent_files,
    get_files,
    get_file_info,
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

        # Store file and version information
        self.files = []  # List of files
        self.selected_file = None  # Selected file
        self.versions = []  # List of versions for the selected file
        self.selected_version = None  # Selected version

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
        self.files = get_most_recent_files(self.drive_service)

        if self.files:
            # Pass file names to the UI and store IDs as properties
            for file in self.files:
                self.ui.file_listbox.add_item(file["name"], file["id"])
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
        self.files = get_files(self.drive_service, search_term)
        if self.files:
            # Clear the listbox before adding new items
            self.ui.file_listbox.reset()

            # Add file names and IDs to the listbox
            for file in self.files:
                self.ui.file_listbox.add_item(file["name"], file["id"])
        else:
            self.ui.show_message("Search", "No files found.")

    def on_file_select(self, event):
        selected_index = self.ui.file_listbox.curselection()

        if selected_index:
            # Retrieve the ID of the selected file
            selected_file_id = self.ui.file_listbox.get_id(selected_index[0])
            if not selected_file_id:
                return

            print(f"Selected file ID: {selected_file_id}")
            self.selected_file = get_file_info(
                self.drive_service, selected_file_id
            )

            if self.selected_file:
                file_size = self.selected_file.get("size", "Unknown")
                file_mime = self.selected_file.get("mimeType", "Unknown")

                # Update file details in the UI
                self.ui.file_details_section.update_details(
                    File_Size=file_size,
                    MIME_Type=file_mime,
                )

                self.update_versions(selected_file_id)
            else:
                self.ui.show_message(
                    "Error", "Selected file not found in the files list."
                )

    def update_versions(self, file_id):
        """
        Fetches and sorts file versions for the selected file,
        then passes them to the UI for display.
        """
        self.versions = get_versions_of_file(self.drive_service, file_id)

        # Check if versions were found
        if self.versions:
            sorted_versions = sorted(
                self.versions,
                key=lambda x: x["modifiedTime"],
                reverse=True,
            )

            self.ui.display_versions(sorted_versions)
        else:
            self.ui.show_message("Info", "No versions found for this file.")

    def on_version_select(self, event):
        """
        Handles version selection and updates the version details section.
        """
        # Get the selected index from the version listbox
        selected_index = self.ui.version_listbox.curselection()

        if not selected_index:
            return  # No version selected

        # Use the selected index to get the corresponding version from self.versions
        try:
            selected_version = self.versions[selected_index[0]]
        except IndexError:
            self.ui.show_message("Error", "Selected version not found.")
            return

        # Get the selected file ID from the file listbox
        selected_file_index = self.ui.file_listbox.curselection()
        if not selected_file_index:
            return  # No file selected

        selected_file_id = self.ui.file_listbox.get_id(selected_file_index[0])

        # Fetch the version description from MongoDB
        version_description = get_version_description(
            selected_file_id, selected_version["id"]
        )

        # Get the modified time of the selected version
        version_modified_time = selected_version.get("modifiedTime", "Unknown")

        # Update the version details section in the UI
        self.ui.version_details_section.update_details(
            Description=version_description,
            Modified_Time=version_modified_time,
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

        selected_file_id = self.ui.file_listbox.get_id(selected_file_index)
        if not selected_file_id:
            return

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

        self.upload_new_version(selected_file_id, file_path, description)

    def upload_new_version(self, file_id, file_path, description):
        """
        Uploads a new version of the selected file
        and saves the description to MongoDB.
        """
        print(
            f"Uploading new version for file ID: {file_id} from path: {file_path}"
        )

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
                    "New version uploaded successfully and description saved to MongoDB."
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
