import tkinter as tk
from tkinter import ttk
from views.version_control_ui import VersionControlUI
from views.comments_ui import CommentsUI
from views.roles_ui import RolesUI


class MainWindow:
    def __init__(self, root):
        """
        Initializes the main window with a Notebook containing
        Version Control, Comments, and Assigning Roles sections.

        Args:
            root: The root Tkinter window.
        """
        self.root = root
        self.root.title("Google Drive Asset Management")
        self.root.geometry("1000x800")

        # Create Notebook (Tabbed Layout)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        # Initialize tabs
        self.version_control_frame = ttk.Frame(self.notebook)
        self.comments_frame = ttk.Frame(self.notebook)
        self.roles_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.version_control_frame, text="Version Control")
        self.notebook.add(self.comments_frame, text="Comments")
        self.notebook.add(self.roles_frame, text="Assigning Roles")

        # Add UI Components to Tabs
        self.version_control_ui = VersionControlUI(self.version_control_frame)
        self.comments_ui = CommentsUI(self.comments_frame)
        self.roles_ui = RolesUI(self.roles_frame)


if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
