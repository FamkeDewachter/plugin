from tkinter import messagebox, filedialog
from datetime import datetime
import os
from models.drive_model import (
    gds_get_files,
    gds_get_file_info,
    gds_get_versions_of_file,
    gds_upload_file,
    gds_upload_new_version,
    gds_get_version_info,
    gds_get_current_version,
)
from models.mongodb_models import (
    mongo_save_description,
    mongo_get_version_description,
)


class DriveController:
    def __init__(self, ui, drive_service, drive_id):
        """
        Initialize the DriveController.

        Args:
            ui: The GoogleDriveUI object.
            drive_service: The Google Drive service object.
        """
        self.drive_service = drive_service
        self.ui = ui
        self.drive_id = drive_id

        # Bind UI events to controller methods
        self._bind_ui_events()

    def _bind_ui_events(self):
        """
        Binds UI events to their corresponding methods.
        """
        self.ui.wdgt_search_bar.search_button.bind(
            "<Button-1>", self.search_clicked
        )
        # Pass the callback methods to the listboxes
        self.ui.file_listbox.on_select_callback = self.file_clicked
        self.ui.version_listbox.on_select_callback = self.version_clicked

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
        self.ui.upload_new_file_button.bind(
            "<Button-1>", self.upload_new_file_clicked
        )

    def browse_file(self, event, widget):
        """
        Handles the browse button click
        event for different file selection actions.
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
        description = self.ui.wdgt_description_new_version.get_text()

        selected_file = self.ui.file_listbox.get_selected_item()

        if not self._validate_upload_version(
            selected_file, file_path, description
        ):
            return

        try:
            file_name = selected_file["name"]
            file_id = selected_file["id"]

            gds_upload_new_version(
                self.drive_service, file_id, file_name, file_path
            )

            # Upload the description of the new version to MongoDB
            # current version is the file that was just uploaded
            curr_version = gds_get_current_version(self.drive_service, file_id)
            curr_version_id = curr_version["id"]
            curr_version_file_name = curr_version["originalFilename"]

            mongo_save_description(
                file_id, curr_version_id, curr_version_file_name, description
            )

            version_name = os.path.basename(file_path)
            messagebox.showinfo(
                "Success",
                f"New version '{version_name}' uploaded successfully "
                f"to '{file_name}'.",
            )
            self.ui.reset_versioning_section()

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"An error occurred while uploading the new version: {e}",
            )

    def _validate_upload_version(self, selected_file, file_path, description):
        """
        Validates the upload version form fields.

        Args:
            file_path: The path of the file to upload.
            description: The description of the new version.
        """
        if not selected_file:
            messagebox.showerror(
                "Error",
                "Please select a file to upload a version for from the list.",
            )
            return False

        if not file_path:
            messagebox.showerror(
                "No File Selected",
                "Please browse the file to upload as a new version.",
            )

            return False

        if not description:
            proceed = messagebox.askokcancel(
                "No Description",
                "Please provide a description for the new version. "
                "Do you want to proceed without it?",
            )
            if not proceed:
                return False

        return True

    def revert_version_clicked(self, event):
        """
        Handles the "Revert to Version" button click.
        """
        selected_file = self.ui.file_listbox.get_selected_item()
        if not selected_file:
            messagebox.showerror(
                "Error",
                "No file selected to revert a version for,"
                " please select a file from the list.",
            )
            return

        selected_version = self.ui.version_listbox.get_selected_item()
        if not selected_version:
            messagebox.showerror(
                "Error",
                "No version selected to revert to,"
                " please select a version from the list.",
            )
            return

        description = self.ui.wdgt_description_revert_version.get_text()
        if not description:
            proceed = messagebox.askokcancel(
                "No Description",
                "Please provide a description for the revert action."
                " Do you want to proceed without it?",
            )
            if not proceed:
                return

        # actual logic to revert to the selected version

    def search_clicked(self, event):
        """
        Handles the search button click.
        """
        search_term = self.ui.wdgt_search_bar.get_search_term()
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

        for file in files:
            self.ui.file_listbox.add_item(file["name"], file["id"])

    def file_clicked(self):
        """
        Handles when a file is selected from the listbox.
        """
        selected_file = self.ui.file_listbox.get_selected_item()
        selected_file_id = selected_file["id"]

        # Update details of the selected file
        file_info = gds_get_file_info(
            self.drive_service,
            selected_file_id,
        )

        # logic to get the description from google drive

        file_size = file_info.get("size", "No size available")
        mime_type = file_info.get("mimeType", "No MIME type available")
        self.ui.file_details_section.update_details(
            File_Size=file_size,
            MIME_Type=mime_type,
        )

        # get versions of the selected file
        unsorted_versions = gds_get_versions_of_file(
            self.drive_service, selected_file_id
        )
        self.ui.version_listbox.clear()
        if not unsorted_versions:
            messagebox.showinfo(
                "No Versions",
                "This file has no versions available.",
            )
            return

        versions = sorted(
            unsorted_versions, key=self._extract_modified_time, reverse=True
        )

        for version in versions:
            self.ui.version_listbox.add_item(
                version["originalFilename"], version["id"]
            )

    def version_clicked(self):
        """
        Handles the version selection from the listbox.
        """
        selected_version = self.ui.version_listbox.get_selected_item()
        selected_version_id = selected_version["id"]

        selected_file = self.ui.file_listbox.get_selected_item()
        file_id = selected_file["id"]

        version = gds_get_version_info(
            self.drive_service,
            file_id,
            selected_version_id,
            fields="id,originalFilename,modifiedTime",
        )
        if not version:
            messagebox.showerror(
                "Error", "An error occurred while retrieving the version info."
            )

        version_id = version["id"]
        description = mongo_get_version_description(file_id, version_id)

        modified_time = version["modifiedTime"]
        self.ui.version_details_section.update_details(
            Modified_Time=(
                modified_time if modified_time else "No data available."
            ),
            Description=(description if description else "No description."),
        )

    def upload_new_file_clicked(self, event):
        """
        Handles the "Upload New File" button click.
        """
        file_path = self.ui.wdgt_browse_new_file.get_file_path()
        description = self.ui.wdgt_description_new_file.get_text()

        if not self._validate_upload_new_file(file_path, description):
            return

        try:
            # upload the new file to Google Drive
            uploaded_file = gds_upload_file(
                self.drive_service,
                file_path=file_path,
                description=description,
            )

            # Upload the description to MongoDB
            file_id = uploaded_file["id"]
            curr_version = gds_get_current_version(self.drive_service, file_id)
            curr_version_name = curr_version["originalFilename"]
            curr_version_id = curr_version["id"]

            mongo_save_description(
                file_id,
                curr_version_id,
                curr_version_name,
                description,
                original_description=description,
            )

            self.ui.reset_upload_new_file_section()
            messagebox.showinfo("Success", "New file uploaded successfully.")

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"An error occurred while uploading the new file: {e}",
            )

    def _validate_upload_new_file(self, file_path, description):
        """
        Validates the upload new file form fields.

        Args:
            file_path: The path of the file to upload.
            description: The description of the new file.
        """
        if not file_path:
            messagebox.showerror(
                "No File Selected",
                "Please select a file to upload as a new file.",
            )
            return False

        if not description:
            proceed = messagebox.askokcancel(
                "No Description",
                "Please provide a description for the new file."
                " Do you want to proceed without it?",
            )
            if not proceed:
                return False

        return True

    def _extract_modified_time(self, rev):
        return datetime.fromisoformat(rev["modifiedTime"].rstrip("Z"))
