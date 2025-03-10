import tkinter as tk
from views.widget_library import (
    widget_entryfield,
    widget_listbox,
    widget_button,
    widget_details_section,
    widget_file_browser,
    widget_search_bar,
)


class GoogleDriveUI:
    def __init__(self, root):
        """
        Initializes the Google Drive UI.

        Args:
            root: The root Tkinter window.
        """
        self.root = root
        self.placeholders = {
            "file_listbox": "Please search for files.",
            "version_listbox": "Please select a file to view versions.",
        }
        self.setup_ui()

    def setup_ui(self):
        """
        Sets up the UI components.
        """
        self.root.title("Google Drive Versions")
        self.root.geometry("1000x800")

        # Create a frame for uploading a new file
        self.frame_upload_new_file = tk.Frame(
            self.root, relief="raised", borderwidth=2
        )
        self.frame_upload_new_file.pack(fill="x", side="top", pady=(5, 20))

        # Create a frame for the versioning sections
        self.frame_versioning = tk.Frame(self.root)
        self.frame_versioning.pack(fill="both", expand=True, side="top")
        self.create_section_title(self.frame_versioning, "Versioning:")

        # Initialize sections
        self.upload_new_files_section()
        self.versioning_files_section()
        self.versioning_versions_section()

    def versioning_files_section(self):
        """
        Creates the file listbox, file details panel, and search bar.
        """
        versioning_files_frame = self.create_frame(self.root, side="left")
        self.create_section_subtitle(versioning_files_frame, "Files:")

        self.wdgt_search_bar = widget_search_bar(versioning_files_frame)
        self.wdgt_search_bar.pack(fill="x", pady=5)

        self.file_listbox = self.create_listbox(
            versioning_files_frame, self.placeholders["file_listbox"]
        )
        self.file_details_section = widget_details_section(
            versioning_files_frame, labels=["File_Size", "MIME_Type"]
        )

        self.create_upload_version_section(versioning_files_frame)

    def create_upload_version_section(self, parent):
        """
        Creates the section for selecting a file to upload as a new version.
        """
        upload_frame = self.create_frame(parent)
        self.create_section_title(upload_frame, "Upload New Version:")

        self.wdgt_browse_upload_version = widget_file_browser(
            upload_frame,
            label_text="Select(ed) file:",
        )
        self.wdgt_browse_upload_version.pack(fill="x", pady=5)

        self.description_entry = widget_entryfield(
            upload_frame,
            placeholder="Description",
            width=50,
            font=("Arial", 10),
        )
        self.description_entry.pack(fill="x")

        self.upload_new_version_button = widget_button(
            upload_frame,
            text="Upload New Version",
            bg_color="#4CAF50",
            fg_color="white",
        )
        self.upload_new_version_button.pack(pady=5, fill="x")

    def upload_new_files_section(self):
        """
        Creates the section for uploading a completely new file.
        """
        self.create_section_title(
            self.frame_upload_new_file, "Upload New File:"
        )

        self.wdgt_browse_new_file = widget_file_browser(
            self.frame_upload_new_file,
            label_text="Select(ed) File:",
        )
        self.wdgt_browse_new_file.pack(fill="x", pady=5)

        self.description_new_file_entry = widget_entryfield(
            self.frame_upload_new_file,
            placeholder="Description",
            width=50,
            font=("Arial", 10),
        )
        self.description_new_file_entry.pack(fill="x")

        self.upload_new_file_button = widget_button(
            self.frame_upload_new_file,
            text="Upload New File",
            bg_color="#4CAF50",
            fg_color="white",
        )
        self.upload_new_file_button.pack(pady=5, fill="x")

    def versioning_versions_section(self):
        """
        Creates the version listbox, version details panel, and revert button.
        """
        version_frame = self.create_frame(self.root, side="left")
        self.create_section_subtitle(version_frame, "Versions:")

        self.version_listbox = self.create_listbox(
            version_frame, self.placeholders["version_listbox"]
        )
        self.version_details_section = widget_details_section(
            version_frame, labels=["Modified_Time", "Description"]
        )

        self.revert_button = widget_button(
            version_frame,
            text="Revert to Version",
            bg_color="#f44336",
            fg_color="white",
        )
        self.revert_button.pack(pady=5, fill="x")

    def create_frame(self, parent, side=None):
        """
        Creates a frame for the UI components.

        Args:
            parent: The parent widget.
            side: The side where the frame should be packed (optional).
        """
        frame = tk.Frame(parent)
        frame.pack(pady=10, padx=10, fill="both", expand=True, side=side)
        return frame

    def create_section_title(
        self,
        parent,
        title,
    ):
        """
        Creates a section title label.

        Args:
            parent: The parent widget.
            title: The title text for the section.
        """
        title_label = tk.Label(parent, text=title, font=("Arial", 12, "bold"))
        title_label.pack(anchor="w", pady=5)

    def create_section_subtitle(
        self,
        parent,
        subtitle,
    ):
        """
        Creates a section subtitle label.

        Args:
            parent: The parent widget.
            subtitle: The subtitle text for the section.
        """
        subtitle_label = tk.Label(
            parent, text=subtitle, font=("Arial", 10, "bold")
        )
        subtitle_label.pack(anchor="w", pady=0)

    def create_listbox(self, parent, placeholder):
        """
        Creates a listbox with placeholder text.

        Args:
            parent: The parent widget.
            placeholder: The placeholder text to display.
        """
        frame = self.create_frame(parent)
        listbox = widget_listbox(
            frame,
            placeholder=placeholder,
            width=40,
            height=15,
            exportselection=False,
            font=("Arial", 10),
        )
        listbox.pack(pady=5, fill="both", expand=True)
        return listbox

    def reset_full_ui(self):
        """
        Resets all UI components to their initial state.
        """
        self.reset_versioning_section()
        self.reset_upload_new_file_section()

    def reset_versioning_section(self):
        """
        Resets the versioning section of the UI.
        """
        self.wdgt_search_bar.clear()
        self.file_listbox.clear()
        self.file_details_section.clear()
        self.version_listbox.clear()
        self.version_details_section.clear()
        self.description_entry.clear()
        self.wdgt_browse_upload_version.clear()
        self.wdgt_browse_new_file.clear()

    def reset_upload_new_file_section(self):
        """
        Resets the upload new file section of the UI.
        """
        self.wdgt_browse_new_file.clear()
        self.description_new_file_entry.clear()


if __name__ == "__main__":
    root = tk.Tk()
    ui = GoogleDriveUI(root)
    root.mainloop()
