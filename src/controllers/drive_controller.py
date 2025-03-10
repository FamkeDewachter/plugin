import tkinter as tk
from tkinter import messagebox

from models.google_drive_utils import (
    get_most_recent_files,
    gds_get_files,
    gds_get_file_info,
    gds_get_versions_of_file,
    gds_upload_version,
    gds_get_latest_version_id,
)
from models.mongo_utils import (
    mongo_save_description,
    mongo_get_version_description,
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

        # Initialize file and version storage
        self.files = []
        self.selected_file = None
        self.versions = []
        self.selected_version = None

        # Bind UI events to controller methods
        self._bind_ui_events()

    def _bind_ui_events(self):
        """
        Binds UI events to their corresponding methods.
        """
        self.ui.search_button.bind("<Button-1>", self.search_clicked)
        self.ui.file_listbox.bind("<<ListboxSelect>>", self.file_clicked)
        self.ui.version_listbox.bind("<<ListboxSelect>>", self.version_clicked)
        self.ui.upload_new_version_button.bind(
            "<Button-1>", self.upload_version_clicked
        )
        self.ui.revert_button.bind("<Button-1>", self.revert_version_clicked)

    def upload_version_clicked(self, event):
        """
        Handles uploading a new version of the selected file.
        """

        is_valid, file_path, description = self.validate_upload_version()

        if not is_valid:
            return

        selected_file_id = self.selected_file["id"]

        try:

            gds_upload_version(self.drive_service, selected_file_id, file_path)

            revision_id = gds_get_latest_version_id(
                self.drive_service, selected_file_id
            )

            if revision_id:
                mongo_save_description(
                    selected_file_id, revision_id, description
                )

                messagebox.showinfo(
                    "Success",
                    "New version uploaded successfully with description.",
                )

                self.reset_tool()

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"An error occurred while uploading the new version: {e}",
            )

    def validate_upload_version(self):
        """
        Validates the upload version form fields.
        """
        if not self.selected_file:
            messagebox.showerror(
                "Error", "Please select a file to upload a new version for."
            )
            return False, None, None

        upload_file_path = self.ui.get_upload_file_path()
        if not upload_file_path:
            messagebox.showerror(
                "No File Selected",
                "Please select a file to upload as a new version for.",
            )

            return False, None, None

        description = self.get_description()
        if not description:
            proceed = messagebox.askokcancel(
                "No Description",
                "Please provide a description for the new version. Do you want to proceed without it?",
            )
            if not proceed:
                return False, None, None

        return True, upload_file_path, description

    def get_description(self):
        """
        Retrieves and validates the description input.
        """
        description = self.ui.description_entry.get()
        if not description or description == "Description":
            return None

        return description

    def revert_version_clicked(self, event):
        """
        Handles the "Revert to Version" button click.
        """
        if not self.selected_version:
            self.ui.show_message("Error", "No version selected.")
            return

        version_id = self.selected_version["id"]
        file_id = self.selected_file["id"]

        print(f"Reverting to version ID: {version_id} for file ID: {file_id}")

        self.reset_tool()

    def search_clicked(self, event):
        """
        Handles the search button click.
        """
        is_valid, search_term, files = self.validate_search()

        if not is_valid:
            return

        self.files = files

        # Update the file listbox with the search results
        self.ui.file_listbox.clear_placeholder()
        self.ui.file_listbox.clear_items()

        for file in self.files:
            self.ui.file_listbox.add_item(file["name"], file["id"])

    def validate_search(self):
        """
        Validates the search form fields.
        """
        search_term = self.ui.search_entry.get()

        if not search_term:
            messagebox.showerror(
                "No Search Term", "Please enter a file name to search for."
            )
            self.reset_tool()

            return False, None, None

        files = gds_get_files(self.drive_service, search_term=search_term)
        if not files:
            messagebox.showerror(
                "No Results", "No files found matching the search term."
            )
            self.reset_tool()
            return False, None, None

        return True, search_term, files

    def file_clicked(self, event):
        """
        Handles when a file is selected from the listbox.
        """
        selected_file_index = self.ui.file_listbox.curselection()

        if selected_file_index:
            selected_file_id = self.ui.file_listbox.get_id(
                selected_file_index[0]
            )
            self.selected_file = gds_get_file_info(
                self.drive_service, selected_file_id
            )
            self.versions = gds_get_versions_of_file(
                self.drive_service, selected_file_id
            )

            self.ui.file_details_section.update_details(
                File_Size=self.selected_file["size"],
                MIME_Type=self.selected_file["mimeType"],
            )

            self._update_version_listbox()

    def _update_version_listbox(self):
        """
        Updates the version listbox with versions of the selected file.
        """
        if not self.versions:
            return

        self.ui.version_listbox.clear_placeholder()
        self.ui.version_listbox.clear_items()

        for version in self.versions:
            self.ui.version_listbox.add_item(
                version["originalFilename"], version["id"]
            )

    def version_clicked(self, event):
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
                description = mongo_get_version_description(
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
        Resets the controller state and UI.
        """
        self.files = []
        self.selected_file = None
        self.versions = []
        self.selected_version = None
        self.ui.reset_all()
