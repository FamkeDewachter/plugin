import tkinter as tk
from tkinter import messagebox, filedialog
from views.widget_library import (
    Entryfield,
    Listbox,
    StyledButton,
    DetailsSection,
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

        self.create_search_bar()
        self.create_file_section()
        self.create_version_section()

    def create_search_bar(self):
        """
        Creates the search bar at the top of the UI.
        """
        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=10, padx=10, fill="x")

        self.search_entry = tk.Entry(search_frame, width=50)
        self.search_entry.pack(side="left", padx=5, expand=True, fill="x")

        self.search_button = tk.Button(search_frame, text="Search")
        self.search_button.pack(side="left")

    def create_file_section(self):
        """
        Creates the file listbox, file details panel, and file upload section.
        """
        file_frame = tk.Frame(self.root)
        file_frame.pack(
            pady=10, padx=10, fill="both", expand=True, side="left"
        )

        # File Listbox
        self.file_listbox = self.create_listbox(
            file_frame,
            label_text="Files:",
            placeholder=self.placeholders["file_listbox"],
        )

        # File Details Panel
        self.file_details_section = DetailsSection(
            file_frame, labels=["File_Size", "MIME_Type"]
        )

        # File Upload Section
        self.create_upload_file_section(file_frame)

    def create_upload_file_section(self, parent):
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

        # Frame to hold the file path display and browse button
        browse_frame = tk.Frame(upload_frame)
        browse_frame.pack(fill="x", pady=5)

        # Label to display the selected file path
        self.upload_file_label = tk.Label(
            browse_frame, text="No file selected", fg="gray", wraplength=400
        )
        self.upload_file_label.pack(side="left", padx=5, fill="x", expand=True)

        # Browse button
        self.browse_button = StyledButton(
            browse_frame,
            text="Browse",
            bg_color="#007BFF",  # Blue color
            fg_color="white",
        )
        self.browse_button.pack(side="right", padx=5)

        # Description entry
        description_frame = tk.Frame(upload_frame)
        description_frame.pack(pady=10, padx=10, fill="x")

        self.description_entry = Entryfield(
            description_frame,
            placeholder="Description",
            width=50,
            font=("Arial", 10),
        )
        self.description_entry.pack(fill="x")

        # Upload button
        self.upload_button = StyledButton(
            upload_frame,
            text="Upload New Version",
            bg_color="#4CAF50",  # Green color
            fg_color="white",
        )
        self.upload_button.pack(pady=5, fill="x")

    def create_version_section(self):
        """
        Creates the version listbox, version details panel, and revert button.
        """
        version_frame = tk.Frame(self.root)
        version_frame.pack(
            pady=10, padx=10, fill="both", expand=True, side="left"
        )

        # Version Listbox
        self.version_listbox = self.create_listbox(
            version_frame,
            label_text="Versions:",
            placeholder=self.placeholders["version_listbox"],
        )

        # Version Details Panel
        self.version_details_section = DetailsSection(
            version_frame, labels=["Modified_Time", "Description"]
        )

        # Revert button
        self.revert_button = StyledButton(
            version_frame,
            text="Revert to Version",
            bg_color="#f44336",  # Red color
            fg_color="white",
        )
        self.revert_button.pack(pady=5, fill="x")

    def create_listbox(self, parent, label_text, placeholder):
        """
        Creates a labeled listbox with placeholder text.

        Args:
            parent: The parent widget.
            label_text: The text for the label.
            placeholder: The placeholder text for the listbox.

        Returns:
            PlaceholderListbox: The created listbox.
        """
        frame = tk.Frame(parent)
        frame.pack(pady=5, fill="both", expand=True)

        label = tk.Label(frame, text=label_text, font=("Arial", 12, "bold"))
        label.pack(anchor="w")

        listbox = Listbox(
            frame,
            placeholder=placeholder,
            width=40,
            height=15,
            exportselection=False,
            font=("Arial", 10),
        )
        listbox.pack(pady=5, fill="both", expand=True)

        return listbox

    def open_file_dialog(self, title):
        """
        Opens a file dialog and returns the selected file path.
        Also updates the label to show the selected file path.

        Returns:
            str: The selected file path, or None if the user cancels.
        """
        file_path = filedialog.askopenfilename(title=title)
        if file_path:
            self.upload_file_label.config(text=file_path, fg="black")
        return file_path

    def show_message(self, title, message):
        """
        Displays a message box.

        Args:
            title: The title of the message box.
            message: The message to display.
        """
        messagebox.showinfo(title, message)

    def display_versions(self, revisions):
        """
        Displays file versions in the version listbox.

        Args:
            revisions: A list of revision dictionaries, already sorted.
        """
        self.version_listbox.reset()
        if revisions:
            for revision in revisions:
                original_filename = revision.get(
                    "originalFilename", "Unknown File"
                )
                self.version_listbox.add_item(
                    original_filename, revision["id"]
                )
        else:
            self.version_listbox.insert_placeholder()

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
        return (
            self.upload_file_label.cget("text")
            if self.upload_file_label.cget("text") != "No file selected"
            else None
        )

    def reset_all(self):
        """
        Resets all UI components to their initial state.
        """
        self.reset_search_entry()
        self.reset_description_entry()
        self.upload_file_label.config(text="No file selected", fg="gray")
        self.file_listbox.reset()
        self.version_listbox.reset()
        self.file_details_section.clear()
        self.version_details_section.clear()


if __name__ == "__main__":
    root = tk.Tk()
    ui = GoogleDriveUI(root)
    root.mainloop()
