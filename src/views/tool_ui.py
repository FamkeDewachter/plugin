import tkinter as tk
from tkinter import messagebox, filedialog
from views.widget_library import (
    widget_entryfield,
    widget_listbox,
    widget_button,
    widget_details_section,
    widget_file_browser,  # Import the widget_file_browser
)


class GoogleDriveUI:
    def __init__(self, root):
        """
        Initialize the Google Drive UI.

        Args:
            root: The root Tkinter window.
        """
        self.root = root
        self.setup_ui()

    def setup_ui(self):
        """
        Sets up the UI components.
        """
        self.root.title("Google Drive Versions")
        self.root.geometry("1000x700")

        # Placeholder texts
        self.placeholders = {
            "file_listbox": "Please search for files.",
            "version_listbox": "Please select a file to view versions.",
        }

        self.create_files_section()
        self.create_versions_section()
        self.create_new_file_section()

    def create_files_section(self):
        """
        Creates the file listbox, file details panel, and search bar.
        """
        file_frame = tk.Frame(self.root)
        file_frame.pack(
            pady=10, padx=10, fill="both", expand=True, side="left"
        )

        # Title for the file section
        file_section_title = tk.Label(
            file_frame,
            text="Files:",
            font=("Arial", 12, "bold"),
        )
        file_section_title.pack(anchor="w", pady=5)

        # Search bar (moved to the file section)
        self.create_search_bar(file_frame)

        # File Listbox
        self.file_listbox = self.create_listbox(
            file_frame,
            placeholder=self.placeholders["file_listbox"],
        )

        # File Details Panel
        self.file_details_section = widget_details_section(
            file_frame, labels=["File_Size", "MIME_Type"]
        )

        # File Upload Section
        self.create_upload_version_section(file_frame)

    def create_search_bar(self, parent):
        """
        Creates the search bar under the file section title.

        Args:
            parent: The parent widget (file_frame).
        """
        search_frame = tk.Frame(parent)
        search_frame.pack(pady=5, padx=10, fill="x")

        self.search_entry = tk.Entry(search_frame, width=50)
        self.search_entry.pack(side="left", padx=5, expand=True, fill="x")

        self.search_button = widget_button(
            search_frame,
            text="Search",
            bg_color="#007BFF",  # Blue color
            fg_color="white",
        )
        self.search_button.pack(side="left")

    def create_upload_version_section(self, parent):
        """
        Creates the section for selecting a file to upload as a new version.

        Args:
            parent: The parent widget.
        """
        upload_frame = tk.Frame(parent)
        upload_frame.pack(pady=10, padx=10, fill="x")

        # Label for the upload section
        upload_label = tk.Label(
            upload_frame,
            text="Upload New Version:",
            font=("Arial", 12, "bold"),
        )
        upload_label.pack(anchor="w", pady=5)

        # Use widget_file_browser for file selection
        self.browse_button_up = widget_file_browser(
            upload_frame,
            label_text="Select(ed) file:",
            browse_callback=self.open_file_dialog,
        )
        self.browse_button_up.pack(fill="x", pady=5)

        # Description entry
        description_frame = tk.Frame(upload_frame)
        description_frame.pack(pady=10, padx=10, fill="x")

        self.description_entry = widget_entryfield(
            description_frame,
            placeholder="Description",
            width=50,
            font=("Arial", 10),
        )
        self.description_entry.pack(fill="x")

        # Upload button
        self.upload_new_version_button = widget_button(
            upload_frame,
            text="Upload New Version",
            bg_color="#4CAF50",  # Green color
            fg_color="white",
        )
        self.upload_new_version_button.pack(pady=5, fill="x")

    def create_new_file_section(self):
        """
        Creates the section for uploading a completely new file.
        """
        upload_new_file_frame = tk.Frame(self.root)
        upload_new_file_frame.pack(pady=10, padx=10, fill="x")

        # Label for the upload new file section
        upload_new_file_label = tk.Label(
            upload_new_file_frame,
            text="Upload New File:",
            font=("Arial", 12, "bold"),
        )
        upload_new_file_label.pack(anchor="w", pady=5)

        # Use widget_file_browser for file selection
        self.browse_button_unf = widget_file_browser(
            upload_new_file_frame,
            label_text="Select(ed) File:",
            browse_callback=self.open_file_dialog,
        )
        self.browse_button_unf.pack(fill="x", pady=5)

        # Description entry for new file
        description_new_file_frame = tk.Frame(upload_new_file_frame)
        description_new_file_frame.pack(pady=10, padx=10, fill="x")

        self.description_new_file_entry = widget_entryfield(
            description_new_file_frame,
            placeholder="Description",
            width=50,
            font=("Arial", 10),
        )
        self.description_new_file_entry.pack(fill="x")

        # Upload button for new file
        self.upload_new_file_button = widget_button(
            upload_new_file_frame,
            text="Upload New File",
            bg_color="#4CAF50",  # Green color
            fg_color="white",
        )
        self.upload_new_file_button.pack(pady=5, fill="x")

    def create_versions_section(self):
        """
        Creates the version listbox, version details panel, and revert button.
        """
        version_frame = tk.Frame(self.root)
        version_frame.pack(
            pady=10, padx=10, fill="both", expand=True, side="left"
        )

        # Title for the version section
        version_section_title = tk.Label(
            version_frame,
            text="Versions:",
            font=("Arial", 12, "bold"),
        )
        version_section_title.pack(anchor="w", pady=5)

        # Version Listbox
        self.version_listbox = self.create_listbox(
            version_frame,
            placeholder=self.placeholders["version_listbox"],
        )

        # Version Details Panel
        self.version_details_section = widget_details_section(
            version_frame, labels=["Modified_Time", "Description"]
        )

        # Revert button
        self.revert_button = widget_button(
            version_frame,
            text="Revert to Version",
            bg_color="#f44336",  # Red color
            fg_color="white",
        )
        self.revert_button.pack(pady=5, fill="x")

    def create_listbox(self, parent, placeholder, label=None):
        """
        Creates a listbox with placeholder text.

        Args:
            parent: The parent widget.
            placeholder: The placeholder text to display.
            show_label: Whether to show a label for the listbox. Defaults to True.
        """
        frame = tk.Frame(parent)
        frame.pack(pady=5, fill="both", expand=True)

        # Add a label if specified
        if label:
            label = tk.Label(frame, text=label, font=("Arial", 12, "bold"))
            label.pack(anchor="w")

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

    def open_file_dialog(self, event=None):
        """
        Opens a file dialog and returns the selected file path.
        Also updates the label to show the selected file path.

        Returns:
            str: The selected file path, or None if the user cancels.
        """
        file_path = filedialog.askopenfilename(title="Select File")
        if file_path:
            # Update the file path in the widget_file_browser
            if event and hasattr(event.widget, "master"):
                if isinstance(event.widget.master, widget_file_browser):
                    event.widget.master.set_file_path(file_path)
        return file_path

    def show_message(self, title, message):
        """
        Displays a message box.

        Args:
            title: The title of the message box.
            message: The message to display.
        """
        messagebox.showinfo(title, message)

    def reset_search_entry(self):
        """
        Resets the search entry to an empty string.
        """
        self.search_entry.delete(0, tk.END)

    def reset_description_entry(self):
        """
        Resets the description entry to the placeholder text.
        """
        self.description_entry.reset()

    def get_upload_file_path(self):
        """
        Returns the selected file path for upload.

        Returns:
            str: The selected file path, or None if no file is selected.
        """
        return self.browse_button_up.get_file_path()

    def reset_all(self):
        """
        Resets all UI components to their initial state.
        """
        self.reset_search_entry()
        self.reset_description_entry()
        self.browse_button_up.set_file_path(None)
        self.browse_button_unf.set_file_path(None)
        self.file_listbox.reset()
        self.version_listbox.reset()
        self.file_details_section.clear()
        self.version_details_section.clear()


if __name__ == "__main__":
    root = tk.Tk()
    ui = GoogleDriveUI(root)
    root.mainloop()
