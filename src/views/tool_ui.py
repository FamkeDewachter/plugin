import tkinter as tk
from tkinter import messagebox, filedialog
from views.widget_library import (
    PlaceholderEntry,
    PlaceholderListbox,
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

        self.create_search_bar()
        self.create_file_section()
        self.create_version_section()
        self.create_action_buttons()
        self.create_description_entry()

    def open_file_dialog(self, title):
        """
        Opens a file dialog and returns the selected file path.

        Returns:
            str: The selected file path, or None if the user cancels.
        """
        return filedialog.askopenfilename(title=title)

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
        Creates the file listbox and file details panel.
        """
        file_frame = tk.Frame(self.root)
        file_frame.pack(
            pady=10, padx=10, fill="both", expand=True, side="left"
        )

        # File Listbox
        self.file_listbox = self.create_listbox(
            file_frame,
            label_text="Files:",
            placeholder="Please search for files to display them here.",
        )

        # File Details Panel
        self.file_details_section = DetailsSection(
            file_frame, labels=["File_Size", "MIME_Type"]
        )

    def create_version_section(self):
        """
        Creates the version listbox and version details panel.
        """
        version_frame = tk.Frame(self.root)
        version_frame.pack(
            pady=10, padx=10, fill="both", expand=True, side="left"
        )

        # Version Listbox
        self.version_listbox = self.create_listbox(
            version_frame,
            label_text="Versions:",
            placeholder="Please select a file to view versions.",
        )

        # Version Details Panel
        self.version_details_section = DetailsSection(
            version_frame, labels=["Modified_Time", "Description"]
        )

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

        listbox = PlaceholderListbox(
            frame,
            placeholder=placeholder,
            width=40,
            height=15,
            exportselection=False,
            font=("Arial", 10),
        )
        listbox.pack(pady=5, fill="both", expand=True)

        return listbox

    def create_action_buttons(self):
        """
        Creates the action buttons (Upload New Version and Revert to Version).
        """
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10, padx=10, fill="x")

        self.upload_button = StyledButton(
            button_frame,
            text="Upload New Version",
            bg_color="#4CAF50",  # Green color
            fg_color="white",
        )
        self.upload_button.pack(side="left", padx=5, expand=True, fill="x")

        self.revert_button = StyledButton(
            button_frame,
            text="Revert to Version",
            bg_color="#f44336",  # Red color
            fg_color="white",
        )
        self.revert_button.pack(side="left", padx=5, expand=True, fill="x")

    def create_description_entry(self):
        """
        Creates the description entry with placeholder text.
        """
        description_frame = tk.Frame(self.root)
        description_frame.pack(pady=10, padx=10, fill="x")

        self.description_entry = PlaceholderEntry(
            description_frame,
            placeholder="Description",
            width=50,
            font=("Arial", 10),
        )
        self.description_entry.pack(fill="x")

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


if __name__ == "__main__":
    root = tk.Tk()
    ui = GoogleDriveUI(root)
    root.mainloop()
