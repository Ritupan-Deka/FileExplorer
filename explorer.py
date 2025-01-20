import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from ttkthemes import ThemedTk

os.system("cls")

class FileExplorer(ThemedTk):
    def __init__(self):
        super().__init__()

        # Apply dark theme
        self.set_theme("equilux")

        self.title("File Explorer")
        self.geometry("1200x800")

        self.current_path = os.path.expanduser("~")
        self.history = [self.current_path]
        self.history_index = 0

        # Create navigation bar
        self.nav_frame = ttk.Frame(self)
        self.nav_frame.pack(fill=tk.X)

        self.back_button = ttk.Button(self.nav_frame, text="<-", command=self.go_back)
        self.back_button.pack(side=tk.LEFT, padx=5)

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.nav_frame, textvariable=self.search_var, width=50)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<Return>", self.search)
        
        self.forward_button = ttk.Button(self.nav_frame, text="->", command=self.go_forward)
        self.forward_button.pack(side=tk.LEFT, padx=5)

        # Create a PanedWindow for resizable sidebar
        self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # Create the resizable sidebar
        self.side_frame = ttk.Frame(self.paned_window, width=250)  # Initial width
        self.paned_window.add(self.side_frame, weight=1)  # Make resizable

        # Create the main frame
        self.main_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.main_frame, weight=4)  # More weight to main frame

        # Sidebar tree
        self.side_tree = ttk.Treeview(self.side_frame, show="tree")
        self.side_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.side_tree.heading("#0", text="Quick Access")
        self.side_tree.bind("<<TreeviewSelect>>", self.on_side_select)

        # Scrollbar for the sidebar tree
        self.side_scroll = ttk.Scrollbar(self.side_frame, orient="vertical", command=self.side_tree.yview)
        self.side_tree.configure(yscrollcommand=self.side_scroll.set)
        self.side_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Main tree for files and folders
        self.main_tree = ttk.Treeview(
            self.main_frame, 
            columns=("Type", "Size"), 
            show="tree headings"
        )
        self.main_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.main_tree.heading("#0", text="Name")  # Treeview column
        self.main_tree.heading("Type", text="Type", anchor=tk.CENTER)  # Align center
        self.main_tree.heading("Size", text="Size", anchor=tk.CENTER)  # Align center

        # Fix column widths and prevent shrinking
        self.main_tree.column("#0", width=500, stretch=False)
        self.main_tree.column("Type", width=150, anchor=tk.CENTER, stretch=False)
        self.main_tree.column("Size", width=150, anchor=tk.CENTER, stretch=False)

        self.main_tree.bind("<Double-1>", self.on_double_click)

        # Scrollbar for the main tree
        self.main_scroll = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.main_tree.yview)
        self.main_tree.configure(yscrollcommand=self.main_scroll.set)
        self.main_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Populate the sidebar with initial paths
        self.populate_side_tree()

        # Create menu
        self.menu = tk.Menu(self)
        self.config(menu=self.menu)

        file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Folder", command=self.open_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        # Initially populate the main tree
        self.populate_main_tree(self.current_path)

    def populate_side_tree(self):
        # Add Quick Access items
        quick_access = {
            "Desktop": os.path.join(os.path.expanduser("~"), "OneDrive\\Desktop"),
            "Documents": os.path.join(os.path.expanduser("~"), "OneDrive\\Documents"),
            "Downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
            "Music": os.path.join(os.path.expanduser("~"), "Music"),
            "Pictures": os.path.join(os.path.expanduser("~"), "OneDrive\\Pictures"),
            "Videos": os.path.join(os.path.expanduser("~"), "Videos")
        }

        for name, path in quick_access.items():
            self.side_tree.insert("", "end", text=name)

        # Add drives
        drives = self.get_drives()
        for drive in drives:
            self.side_tree.insert("", "end", text=drive)

    def get_drives(self):
        return [f"{chr(d)}:\\" for d in range(65, 91) if os.path.exists(f"{chr(d)}:\\")]

    def populate_main_tree(self, path):
        for item in self.main_tree.get_children():
            self.main_tree.delete(item)
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                item_type = "Folder"
                item_size = ""
            else:
                item_type = "File"
                item_size = self.get_file_size(item_path)
            self.main_tree.insert("", "end", text=item, values=(item_type, item_size))

    def get_file_size(self, path):
        size = os.path.getsize(path)
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024

    def open_folder(self):
        folder_path = filedialog.askdirectory(initialdir=self.current_path)
        if folder_path:
            self.current_path = folder_path
            self.update_history(folder_path)
            self.populate_main_tree(folder_path)

    def on_side_select(self, event):
        selected_item = self.side_tree.selection()[0]
        selected_path = self.side_tree.item(selected_item, "text")
        self.current_path = selected_path
        self.update_history(selected_path)
        self.populate_main_tree(selected_path)

    def on_double_click(self, event):
        selected_item = self.main_tree.selection()[0]
        selected_item_text = self.main_tree.item(selected_item, "text")

        new_path = os.path.join(self.current_path, selected_item_text)
        if os.path.isdir(new_path):
            self.current_path = new_path
            self.update_history(new_path)
            self.populate_main_tree(new_path)
        else:
            try:
                os.startfile(new_path)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open file: {e}")

    def search(self, event):
        query = self.search_var.get().lower()
        matching_items = []
        for item in os.listdir(self.current_path):
            if query in item.lower():
                matching_items.append(item)
        
        for item in self.main_tree.get_children():
            self.main_tree.delete(item)
        
        for item in matching_items:
            item_path = os.path.join(self.current_path, item)
            if os.path.isdir(item_path):
                item_type = "Folder"
                item_size = ""
            else:
                item_type = "File"
                item_size = self.get_file_size(item_path)
            self.main_tree.insert("", "end", text=item, values=(item_type, item_size))

    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.current_path = self.history[self.history_index]
            self.populate_main_tree(self.current_path)

    def go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_path = self.history[self.history_index]
            self.populate_main_tree(self.current_path)

    def update_history(self, new_path):
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        self.history.append(new_path)
        self.history_index += 1

if __name__ == "__main__":
    app = FileExplorer()
    app.mainloop()
