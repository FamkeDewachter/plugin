from tkinter import messagebox, filedialog
from datetime import datetime
from models.google_drive_utils import (
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
        self.ui.wdgt_search_bar.search_button.bind(
            "<Button-1>", self.search_clicked
        )
        self.ui.file_listbox.bind("<<ListboxSelect>>", self.file_clicked)
        self.ui.version_listbox.bind("<<ListboxSelect>>", self.version_clicked)
        self.ui.upload_new_version_button.bind(
            "<Button-1>", self.upload_version_clicked
        )
        self.ui.revert_button.bind("<Button-1>", self.revert_version_clicked)

        self.ui.wdgt_browse_upload_version.browse_button.bind(
            "<Button-1>",
            lambda event: self.browse_file(
                event, self.ui.wdgt_browse_upload_version
            ),
        )
        self.ui.wdgt_browse_new_file.browse_button.bind(
            "<Button-1>",
            lambda event: self.browse_file(
                event, self.ui.wdgt_browse_new_file
            ),
        )

    def browse_file(self, event, widget):
        """
        Handles the browse button click event for different file selection actions.
        """
        file_path = filedialog.askopenfilename(title="Select a file.")

        # If the user closes the dialog without selecting a file
        if not file_path:
            return

        widget.display_file_path(file_path)

    def upload_version_clicked(self, event):
        """
        Handles uploading a new version of the selected file.
        """

        # Validate the form fields
        file_path = self.ui.wdgt_browse_upload_version.get_file_path()
        description = self.ui.description_entry.get_text()

        if not self._validate_upload_version(file_path, description):
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
                self.ui.reset_versioning_section()

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"An error occurred while uploading the new version: {e}",
            )

    def _validate_upload_version(self, file_path, description):
        """
        Validates the upload version form fields.

        Args:
            file_path: The path of the file to upload.
            description: The description of the new version.
        """
        if not self.selected_file:
            messagebox.showerror("Error", "Please select a file to upload.")
            return False

        if not file_path:
            messagebox.showerror(
                "No File Selected",
                "Please select a file to upload as a new version for.",
            )

            return False

        return True

        if not description:
            proceed = messagebox.askokcancel(
                "No Description",
                "Please provide a description for the new version. Do you want to proceed without it?",
            )
            if not proceed:
                return False

        return True

    def revert_version_clicked(self, event):
        """
        Handles the "Revert to Version" button click.
        """
        if not self.selected_version:
            messagebox.showerror("Error", "No version selected.")
            return

        version_id = self.selected_version["id"]
        file_id = self.selected_file["id"]

        print(f"Reverting to version ID: {version_id} for file ID: {file_id}")

    def search_clicked(self, event):
        """
        Handles the search button click.
        """
        search_term = self.ui.wdgt_search_bar.get_search_text()
        if not search_term:
            messagebox.showerror(
                "No Search Term", "Please enter a file name to search for."
            )
            return

        files = gds_get_files(self.drive_service, search_term=search_term)
        if not files:
            self.ui.wdgt_search_bar.clear()
            messagebox.showwarning(
                "No Results",
                f"No files found matching the search term '{search_term}'.",
            )
            return

        self.files = files

        # Update the file listbox with the search results
        self.ui.file_listbox.clear_placeholder()
        self.ui.file_listbox.clear_items()

        for file in self.files:
            self.ui.file_listbox.add_item(file["name"], file["id"])

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
            unsorted_versions = gds_get_versions_of_file(
                self.drive_service, selected_file_id
            )

            if not unsorted_versions:
                messagebox.showinfo(
                    "No Versions",
                    "This file has no versions available.",
                )
                return

            self.versions = sorted(
                unsorted_versions,
                key=lambda rev: datetime.fromisoformat(
                    rev["modifiedTime"].rstrip("Z")
                ),
                reverse=True,
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
        self.ui.reset_full_ui()
