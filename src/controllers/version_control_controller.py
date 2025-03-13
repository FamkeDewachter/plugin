from tkinter import messagebox, filedialog
from datetime import datetime
import os
from models.drive_model import (
    gds_upload_new_version,
    gds_get_version_info,
    gds_get_current_version,
    get_folders_hierarchy,
    gds_upload_file_shared_drive,
    gds_get_files_shared_drive,
    gds_get_versions_of_file_shared_drive,
    gds_get_file_info_shared_drive,
    gds_revert_version,
)
from models.mongodb_model import (
    mongo_save_description,
    mongo_get_version_description,
    mongo_get_file_description,
    mongo_get_version_number,
)
from views.widget_library import FolderPickerUI


class VersionControlController:
    def __init__(self, ui, drive_service, drive_id):
        """
        Initialize the VersionControlController.

        Args:
            ui: The GoogleDriveUI object.
            drive_service: The Google Drive service object.
        """
        self.drive_service = drive_service
        self.ui = ui
        self.drive_id = drive_id

        self.selected_file = None
        self.selected_version = None
        self.selected_folder = None

        # Bind UI events to controller methods
        self._bind_ui_events()

    def _bind_ui_events(self):
        """
        Binds UI events to their corresponding methods.
        """
        # upload new file
        self.ui.wdgt_browse_new_file.browse_button.bind(
            "<Button-1>",
            lambda event: self.browse_file(
                event, self.ui.wdgt_browse_new_file
            ),
        )
        self.ui.wdgt_browse_folder.browse_button.bind(
            "<Button-1>", self._choose_google_drive_folder
        )
        self.ui.upload_new_file_button.bind(
            "<Button-1>", self.upload_new_file_clicked
        )

        # version control files
        self.ui.wdgt_search_bar.search_button.bind(
            "<Button-1>", self._search_clicked
        )
        self.ui.file_listbox.on_select_callback = self.file_clicked
        self.ui.wdgt_browse_upload_version.browse_button.bind(
            "<Button-1>",
            lambda event: self.browse_file(
                event, self.ui.wdgt_browse_upload_version
            ),
        )

        self.ui.upload_new_version_button.bind(
            "<Button-1>", self.upload_version_clicked
        )

        # version control versions
        self.ui.version_listbox.on_select_callback = self.version_clicked
        self.ui.revert_button.bind("<Button-1>", self.revert_version_clicked)

    def _choose_google_drive_folder(self, event):
        """Opens the folder picker UI and updates the selected folder."""
        # Fetch available folders (You need
        # to replace this with actual API data)
        folders = get_folders_hierarchy(self.drive_service, self.drive_id)

        # Create a new window for folder selection
        folder_picker_window = FolderPickerUI(self.ui.parent, folders)
        self.ui.parent.wait_window(folder_picker_window.window)
        self.selected_folder = folder_picker_window.selected_folder

        # If the user closed the window without selecting a folder
        if not self.selected_folder:
            self.ui.wdgt_browse_folder.clear()
            return

        # If a folder was selected, update the UI
        folder_name = self.selected_folder["name"]
        self.ui.wdgt_browse_folder.update_display(folder_name)

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

        selected_file = self.selected_file

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
        if not self.selected_file:
            messagebox.showerror(
                "Error",
                "No file selected to revert a version for,"
                " please select a file from the list.",
            )
            return

        if not self.selected_version:
            messagebox.showerror(
                "Error",
                "No version selected to revert to,"
                " please select a version from the list.",
            )
            return

        # description = self.ui.wdgt_description_revert_version.get_text()
        # if not description:
        #     proceed = messagebox.askokcancel(
        #         "No Description",
        #         "Please provide a description for the revert action."
        #         " Do you want to proceed without it?",
        #     )
        #     if not proceed:
        #         return

        selected_version_id = self.selected_version["id"]
        version_name = self.selected_version["name"]

        # Revert the file to the selected version
        gds_revert_version(
            self.drive_service,
            "1p_8vsQs-4zYTvPtvbIhTYkJ85Gf7cAgX",
            "version_04.txt",
            selected_version_id,
            version_name,
        )

        messagebox.showinfo(
            "Success",
            "The file has been reverted to the selected version.",
        )

        self.clear_versionning_section()

    def _search_clicked(self, event):
        """
        Handles the search button click.
        """

        search_term = self.ui.wdgt_search_bar.get_search_term()
        if not search_term:
            messagebox.showerror(
                "No Search Term", "Please enter a file name to search for."
            )
            return

        # Clear the file listbox and version listbox
        self.ui.reset_versioning_section()

        # Get files from the shared drive based on the search term
        files = gds_get_files_shared_drive(
            self.drive_service,
            self.drive_id,
            search_term,
            fields="files(id, name)",
        )

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
        self.selected_file = self.ui.file_listbox.get_selected_item()
        selected_file_id = self.selected_file["id"]

        # Update details of the selected file
        file_info = gds_get_file_info_shared_drive(
            self.drive_service,
            selected_file_id,
            fields="id, name, size, mimeType, modifiedTime, createdTime",
        )

        description = mongo_get_file_description(selected_file_id)

        if not file_info:
            messagebox.showerror(
                "Error",
                "An error occurred while retrieving the file information from Google Drive.",
            )

        description = (
            description if description else "No description available."
        )
        file_type = (
            file_info.get("mimeType")
            if file_info.get("mimeType")
            else "No type available"
        )
        file_size = (
            file_info.get("size")
            if file_info.get("size")
            else "No size available"
        )
        file_last_modified = (
            file_info.get("modifiedTime")
            if file_info.get("modifiedTime")
            else "No data available."
        )
        file_date_created = (
            file_info.get("createdTime")
            if file_info.get("createdTime")
            else "No data available."
        )

        self.ui.file_details_section.update_details(
            File_Type=file_type,
            Size=file_size,
            Last_Modified=file_last_modified,
            Date_Created=file_date_created,
            Original_Description=description,
        )

        # get versions of the selected file
        unsorted_versions = gds_get_versions_of_file_shared_drive(
            self.drive_service,
            selected_file_id,
            fields="id, originalFilename, modifiedTime",
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
        self.selected_version = self.ui.version_listbox.get_selected_item()

        version_id = self.selected_version["id"]
        file_id = self.selected_file["id"]
        version_info = gds_get_version_info(
            self.drive_service,
            file_id,
            version_id,
            fields="id, originalFilename, modifiedTime, size",
        )
        if not version_info:
            messagebox.showerror(
                "Error", "An error occurred while retrieving the version info."
            )

        version_number = mongo_get_version_number(
            self.selected_file["id"], version_id
        )

        version_last_modiefied = (
            version_info["modifiedTime"]
            if version_info.get("modifiedTime")
            else "No data available."
        )
        version_size = (
            version_info.get("size") if version_info.get("size") else "No size"
        )
        version_date_created = (
            version_info.get("createdTime")
            if version_info.get("createdTime")
            else "No data available."
        )

        version_id = version_info["id"]
        description = mongo_get_version_description(file_id, version_id)
        self.ui.version_details_section.update_details(
            Version_Number=version_number,
            Date_added=version_last_modiefied,
            Size=version_size,
            Date_Created=version_date_created,
            Description=description,
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
            uploaded_file = gds_upload_file_shared_drive(
                self.drive_service,
                self.drive_id,
                file_path,
                folder_id=self.selected_folder["id"],
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

            self.clear_new_file_section()
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
        if not self.selected_folder:
            messagebox.showerror(
                "No Folder Selected",
                "Please select a folder to upload the file to.",
            )

        if not description:
            proceed = messagebox.askokcancel(
                "No Description",
                "Please provide a description for the new file."
                " Do you want to proceed without it?",
            )
            if not proceed:
                return False

        return True

    def clear_new_file_section(self):
        """
        Clears the new file upload section
        and the variables associated with it.
        """
        self.selected_folder = None
        self.ui.reset_upload_new_file_section()

    def clear_versionning_section(self):
        """
        Clears the versioning section
        and the variables associated with it.
        """
        self.selected_file = None
        self.selected_version = None
        self.ui.reset_versioning_section()

    def _extract_modified_time(self, rev):
        return datetime.fromisoformat(rev["modifiedTime"].rstrip("Z"))
