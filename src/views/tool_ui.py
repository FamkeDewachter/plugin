import tkinter as tk
from tkinter import messagebox, filedialog
from widget_library import (
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
        Sets up the UI components by calling smaller, focused functions.
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
        file_path = filedialog.askopenfilename(
            title=title,
        )
        return file_path

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
        self.create_file_details_section(file_frame)

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
        self.create_version_details_section(version_frame)

    def create_listbox(self, parent, label_text, placeholder):
        """
        Creates a labeled listbox with placeholder text.
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

    def create_file_details_section(self, parent):
        self.file_details_section = DetailsSection(
            parent, labels=["File Name", "File Size", "MIME Type"]
        )

    def create_version_details_section(self, parent):
        self.version_details_section = DetailsSection(
            parent, labels=["Modified Time", "Description"]
        )

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

    def display_files(self, file_names):
        """
        Displays the list of files in the file listbox.

        Args:
            file_names: A list of file names to display.
        """
        self.file_listbox.delete(0, tk.END)
        if file_names:
            for file_name in file_names:
                self.file_listbox.insert(tk.END, file_name)
        else:
            # Add placeholder text if no files are found
            self.file_listbox.insert(
                tk.END, "Please search for files to display them here."
            )
            self.file_listbox.itemconfig(
                0, fg="gray", selectbackground="white", selectforeground="gray"
            )

    def display_versions(self, revisions):
        """
        Displays file versions in the version listbox using the original file names.

        Args:
            revisions: A list of revision dictionaries, already sorted.
        """
        self.version_listbox.delete(0, tk.END)
        if revisions:
            for revision in revisions:
                original_filename = revision.get(
                    "originalFilename", "Unknown File"
                )
                self.version_listbox.insert(tk.END, original_filename)
        else:
            # Add placeholder text if no versions are found
            self.add_placeholder(
                self.version_listbox, "Please select a file to view versions."
            )

    def display_file_details(self, file_name, file_size, mime_type):
        """
        Updates the file details section with the provided information.

        Args:
            file_name: The name of the file.
            file_size: The size of the file.
            mime_type: The MIME type of the file.
        """
        self.file_details_section.update_details(
            File_Name=file_name, File_Size=file_size, MIME_Type=mime_type
        )

    def display_version_details(self, modified_time, description):
        """
        Updates the version details section with the provided information.

        Args:
            modified_time: The modified time of the version.
            description: The description of the version.
        """
        self.version_details_section.update_details(
            Modified_Time=modified_time, Description=description
        )

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
