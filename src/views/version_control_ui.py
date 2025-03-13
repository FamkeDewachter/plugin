import tkinter as tk
from views.widget_library import (
    widget_entryfield,
    widget_listbox,
    widget_button,
    WdgtDetailsSection,
    WidgetFileBrowser,
    widget_search_bar,
    WidgetFolderBrowser,
)


class VersionControlUI:
    def __init__(self, parent):
        """
        Initializes the Version Control UI.

        Args:
            parent: The parent Tkinter frame.
        """
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        """
        Sets up the UI components.
        """
        # Create a canvas and a vertical scrollbar
        self.canvas = tk.Canvas(self.parent)
        self.scrollbar = tk.Scrollbar(
            self.parent, orient="vertical", command=self.canvas.yview
        )
        self.scrollable_frame = tk.Frame(self.canvas)

        # Configure the canvas
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            ),
        )

        self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack the canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bind the canvas to window resize
        self.parent.bind("<Configure>", self.on_window_resize)

        # Create a frame for uploading a new file
        self.frame_upload_new_file = tk.Frame(
            self.scrollable_frame, relief="raised", borderwidth=2
        )
        self.frame_upload_new_file.pack(fill="x", side="top", pady=(5, 20))

        # Create a frame for the versioning sections
        self.frame_versioning = tk.Frame(self.scrollable_frame)
        self.frame_versioning.pack(fill="both", expand=True, side="top")
        self.create_section_title(self.frame_versioning, "Version Control:")

        # Initialize sections
        self.upload_new_files_section()
        self.versioning_files_section()
        self.versioning_versions_section()

    def on_window_resize(self, event):
        """
        Handles window resizing to adjust the canvas and scrollable frame.
        """
        # Update the canvas scroll region to fit the new window size
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # Adjust the width of the scrollable frame to match the canvas width
        canvas_width = self.canvas.winfo_width()
        self.canvas.itemconfig("all", width=canvas_width)

    def upload_new_files_section(self):
        """
        Creates the section for uploading a completely new file.
        """
        self.create_section_title(
            self.frame_upload_new_file, "Upload New File:"
        )

        self.wdgt_browse_new_file = WidgetFileBrowser(
            self.frame_upload_new_file,
            label_text="Selected File:",
        )
        self.wdgt_browse_new_file.pack(fill="x", pady=5)

        # Folder browser widget for selecting a Google Drive folder
        self.wdgt_browse_folder = WidgetFolderBrowser(
            self.frame_upload_new_file,
            label_text="Selected Google Drive Folder:",
        )
        self.wdgt_browse_folder.pack(fill="x", pady=5)
        self.wdgt_description_new_file = widget_entryfield(
            self.frame_upload_new_file,
            placeholder="Description",
            width=50,
            font=("Arial", 10),
        )
        self.wdgt_description_new_file.pack(fill="x")

        self.upload_new_file_button = widget_button(
            self.frame_upload_new_file,
            text="Upload New File",
            bg_color="#4CAF50",
            fg_color="white",
        )
        self.upload_new_file_button.pack(pady=5, fill="x")

    def versioning_files_section(self):
        """
        Creates the file listbox, file details panel, and search bar.
        """
        versioning_files_frame = self.create_frame(
            self.scrollable_frame, side="left"
        )
        self.create_section_subtitle(versioning_files_frame, "Files:")

        self.wdgt_search_bar = widget_search_bar(versioning_files_frame)
        self.wdgt_search_bar.pack(fill="x", pady=5)

        # Creating the file listbox separately
        frame_file_listbox = self.create_frame(versioning_files_frame)
        self.file_listbox = widget_listbox(
            frame_file_listbox, width=40, height=15, font=("Arial", 10)
        )
        self.file_listbox.pack(pady=5, fill="both", expand=True)

        primary_labels = ["File_Type", "Size", "Last_Modified"]
        secondary_labels = [
            "Date_Created",
            "Original_Description",
        ]

        self.file_details_section = WdgtDetailsSection(
            versioning_files_frame,
            primary_labels=primary_labels,
            secondary_labels=secondary_labels,
            title="File Details",
        )
        self.create_upload_version_section(versioning_files_frame)

    def create_upload_version_section(self, parent):
        """
        Creates the section for selecting a file to upload as a new version.
        """
        upload_frame = self.create_frame(parent)
        self.create_section_title(upload_frame, "Upload New Version:")

        self.wdgt_browse_upload_version = WidgetFileBrowser(
            upload_frame,
            label_text="Select(ed) file:",
        )
        self.wdgt_browse_upload_version.pack(fill="x", pady=5)

        self.wdgt_description_new_version = widget_entryfield(
            upload_frame,
            placeholder="Description",
            width=50,
            font=("Arial", 10),
        )
        self.wdgt_description_new_version.pack(fill="x")

        self.upload_new_version_button = widget_button(
            upload_frame,
            text="Upload New Version",
            bg_color="#4CAF50",
            fg_color="white",
        )
        self.upload_new_version_button.pack(pady=5, fill="x")

    def versioning_versions_section(self):
        """
        Creates the version listbox, version details panel, and revert button.
        """
        version_frame = self.create_frame(self.scrollable_frame, side="left")
        self.create_section_subtitle(version_frame, "Versions:")

        # Creating the version listbox separately
        frame_version_listbox = self.create_frame(version_frame)
        self.version_listbox = widget_listbox(
            frame_version_listbox, width=40, height=15, font=("Arial", 10)
        )
        self.version_listbox.pack(pady=5, fill="both", expand=True)

        primary_labels = ["Version_Number", "Date_added", "Size"]
        secondary_labels = [
            "Date_Created",
            "Description",
        ]
        self.version_details_section = WdgtDetailsSection(
            version_frame,
            primary_labels=primary_labels,
            secondary_labels=secondary_labels,
            title="Version Details",
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

    def create_section_title(self, parent, title):
        """
        Creates a section title label.

        Args:
            parent: The parent widget.
            title: The title text for the section.
        """
        title_label = tk.Label(parent, text=title, font=("Arial", 12, "bold"))
        title_label.pack(anchor="w", pady=5)

    def create_section_subtitle(self, parent, subtitle):
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
        self.wdgt_description_new_version.clear()
        self.wdgt_browse_upload_version.clear()
        self.wdgt_browse_new_file.clear()

    def reset_upload_new_file_section(self):
        """
        Resets the upload new file section of the UI.
        """
        self.wdgt_browse_folder.clear()
        self.wdgt_browse_new_file.clear()
        self.wdgt_description_new_file.clear()
