import tkinter as tk
from tkinter import messagebox, filedialog
from views.widget_library import (
    widget_entryfield,
    widget_listbox,
    widget_button,
    widget_details_section,
    widget_file_browser,
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
        self.root.geometry("1000x700")

        self.create_files_section()
        self.create_versions_section()
        self.create_new_file_section()

    def create_files_section(self):
        """
        Creates the file listbox, file details panel, and search bar.
        """
        file_frame = self.create_frame(self.root, side="left")
        self.create_section_title(file_frame, "Files:")

        self.create_search_bar(file_frame)
        self.file_listbox = self.create_listbox(
            file_frame, self.placeholders["file_listbox"]
        )
        self.file_details_section = widget_details_section(
            file_frame, labels=["File_Size", "MIME_Type"]
        )

        self.create_upload_version_section(file_frame)

    def create_search_bar(self, parent):
        """
        Creates the search bar under the file section title.

        Args:
            parent: The parent widget (file_frame).
        """
        search_frame = self.create_frame(parent)
        self.search_entry = tk.Entry(search_frame, width=50)
        self.search_entry.pack(side="left", padx=5, expand=True, fill="x")
        self.search_button = widget_button(
            search_frame, text="Search", bg_color="#007BFF", fg_color="white"
        )
        self.search_button.pack(side="left")

    def create_upload_version_section(self, parent):
        """
        Creates the section for selecting a file to upload as a new version.
        """
        upload_frame = self.create_frame(parent)
        self.create_section_title(upload_frame, "Upload New Version:")

        self.browse_button_up = widget_file_browser(
            upload_frame,
            label_text="Select(ed) file:",
            browse_callback=self.open_file_dialog,
        )
        self.browse_button_up.pack(fill="x", pady=5)

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

    def create_new_file_section(self):
        """
        Creates the section for uploading a completely new file.
        """
        upload_new_file_frame = self.create_frame(self.root)
        self.create_section_title(upload_new_file_frame, "Upload New File:")

        self.browse_button_unf = widget_file_browser(
            upload_new_file_frame,
            label_text="Select(ed) File:",
            browse_callback=self.open_file_dialog,
        )
        self.browse_button_unf.pack(fill="x", pady=5)

        self.description_new_file_entry = widget_entryfield(
            upload_new_file_frame,
            placeholder="Description",
            width=50,
            font=("Arial", 10),
        )
        self.description_new_file_entry.pack(fill="x")

        self.upload_new_file_button = widget_button(
            upload_new_file_frame,
            text="Upload New File",
            bg_color="#4CAF50",
            fg_color="white",
        )
        self.upload_new_file_button.pack(pady=5, fill="x")

    def create_versions_section(self):
        """
        Creates the version listbox, version details panel, and revert button.
        """
        version_frame = self.create_frame(self.root, side="left")
        self.create_section_title(version_frame, "Versions:")

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

    def create_section_title(self, parent, title):
        """
        Creates a section title label.

        Args:
            parent: The parent widget.
            title: The title text for the section.
        """
        title_label = tk.Label(parent, text=title, font=("Arial", 12, "bold"))
        title_label.pack(anchor="w", pady=5)

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

    def open_file_dialog(self, event=None):
        """
        Opens a file dialog and returns the selected file path.
        Also updates the label to show the selected file path.

        Returns:
            str: The selected file path, or None if the user cancels.
        """
        file_path = filedialog.askopenfilename(title="Select File")
        if file_path:
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
