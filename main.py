import tkinter as tk
from tkinter import ttk, messagebox

# Import database-related functions
from db import (
    init_db,
    create_new_idea,
    get_all_ideas,
    get_ideas_by_filter,
    update_idea,
    delete_idea,
    create_user,
    verify_user,
    delete_ideas_by_category,
    reassign_ideas_category,
)

# Default categories available in the app
DEFAULT_CATEGORIES = ["uncategorized", "gameplay", "character", "level", "skin", "operation"]


class LoginWindow(tk.Tk):
    """Main login window for the app."""

    def __init__(self):
        super().__init__()
        self.title("GIB - Login")
        self.geometry("800x400")
        self.resizable(False, False)

        # Build all login widgets
        self.build_widgets()

        # Center the window on the screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def build_widgets(self):
        """Create labels, entries, and buttons for the login form."""

        main_frame = ttk.Frame(self, padding="40 40 40 40")
        main_frame.pack(fill="both", expand=True)

        # App title
        title_label = ttk.Label(
            main_frame,
            text="Gameplay Idea Brainstormer",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 30))

        # Username row
        username_frame = ttk.Frame(main_frame)
        username_frame.pack(fill="x", pady=5)
        ttk.Label(username_frame, text="Username:", width=12).pack(side="left")
        self.username_entry = ttk.Entry(username_frame, width=25)
        self.username_entry.pack(side="left", padx=(5, 0))

        # Password row
        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill="x", pady=5)
        ttk.Label(password_frame, text="Password:", width=12).pack(side="left")
        self.password_entry = ttk.Entry(password_frame, width=25, show="*")
        self.password_entry.pack(side="left", padx=(5, 0))

        # Buttons row (Exit, Login, Create Account)
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(15, 0))

        exit_btn = ttk.Button(button_frame, text="Exit", command=self.quit, width=20)
        exit_btn.pack(side="left", padx=10, ipady=10)

        login_btn = ttk.Button(button_frame, text="Login", command=self.login, width=20)
        login_btn.pack(side="left", padx=10, ipady=10)

        register_btn = ttk.Button(button_frame, text="Create Account", command=self.open_register, width=20)
        register_btn.pack(side="left", padx=10, ipady=10)

        # Enter key behavior
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.login())

        # Start with focus in username field
        self.username_entry.focus()

    def login(self):
        """Handle login click: verify username/password."""

        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if verify_user(username, password):
            # On success, close login window and open main app
            self.destroy()
            app = MainApp()
            app.mainloop()
        else:
            # Show error and reset password field
            messagebox.showerror(
                "Login Failed",
                "Invalid username or password.\nPlease try again."
            )
            self.password_entry.delete(0, "end")
            self.username_entry.focus()

    def open_register(self):
        """Open the account creation window."""
        RegisterWindow(self)


class RegisterWindow(tk.Toplevel):
    """Popup window to create a new user account."""

    def __init__(self, master):
        super().__init__(master)
        self.title("Create Account")
        self.resizable(False, False)

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        # Username input
        ttk.Label(frame, text="Username:").grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(frame, width=25)
        self.username_entry.grid(row=0, column=1, pady=5)

        # Password input
        ttk.Label(frame, text="Password:").grid(row=1, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(frame, width=25, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)

        # Confirm password
        ttk.Label(frame, text="Confirm").grid(row=2, column=0, sticky="w", pady=5)
        self.confirm_entry = ttk.Entry(frame, width=25, show="*")
        self.confirm_entry.grid(row=2, column=1, pady=5)

        # Buttons row
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))

        ttk.Button(btn_frame, text="Create", command=self.create_account).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=5)

        # Focus username by default
        self.username_entry.focus()

    def create_account(self):
        """Validate and create a new user account."""

        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()

        # Basic validation
        if not username or not password:
            messagebox.showwarning("Missing Info", "Please enter both username and password.")
            return

        if password != confirm:
            messagebox.showwarning("Password Mismatch", "Passwords do not match.")
            return

        # Try to create a new user
        ok = create_user(username, password)
        if not ok:
            messagebox.showerror("Error", "This username is already taken.")
            return

        messagebox.showinfo("Success", "Account created. You can now log in.")
        self.destroy()


class IdeaForm(tk.Toplevel):
    """Popup form for adding or editing a single idea."""

    def __init__(self, master, mode="create", idea=None, on_saved=None, categories=None):
        """
        master    : parent window (MainApp)
        mode      : 'create' or 'edit'
        idea      : current idea dict if editing
        on_saved  : callback to refresh list after saving
        categories: category list (currently ignored, using DEFAULT_CATEGORIES)
        """
        super().__init__(master)
        self.mode = mode
        self.idea = idea
        self.on_saved = on_saved
        self.categories = DEFAULT_CATEGORIES

        # Set window title based on mode
        if self.mode == "create":
            self.title("Add New Idea")
        else:
            self.title("Edit Idea")

        self.resizable(False, False)

        # Build form widgets
        self.build_widgets()

        # If editing, populate fields with existing idea
        if self.mode == "edit" and self.idea is not None:
            self.populate_fields()

        # Modal behavior
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def build_widgets(self):
        """Create labels, entries, text areas, and buttons for the idea form."""

        padding = {"padx": 8, "pady": 5}

        # Title
        ttk.Label(self, text="Idea Title:").grid(row=0, column=0, sticky="w", **padding)
        self.entry_title = ttk.Entry(self, width=40, justify="center")
        self.entry_title.grid(row=0, column=1, **padding)

        # Category
        ttk.Label(self, text="Category:").grid(row=1, column=0, sticky="w", **padding)
        self.combo_category = ttk.Combobox(self, values=self.categories, state="readonly", width=40)
        self.combo_category.grid(row=1, column=1, sticky="we", **padding)

        # Tags
        ttk.Label(self, text="Tags (comma-separated):").grid(row=2, column=0, sticky="w", **padding)
        self.entry_tags = ttk.Entry(self, width=40)
        self.entry_tags.grid(row=2, column=1, **padding)

        # Description
        ttk.Label(self, text="Description:").grid(row=3, column=0, sticky="nw", **padding)
        self.text_description = tk.Text(self, width=40, height=10)
        self.text_description.grid(row=3, column=1, **padding)

        # Save / Cancel button bar
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=4, column=0, columnspan=2, sticky="e", padx=10, pady=(0, 10))

        ttk.Button(btn_frame, text="Save", command=self.on_save).pack(side="right", padx=(0, 5))
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right")

    def populate_fields(self):
        """Fill in existing idea data when in edit mode."""

        # Title
        self.entry_title.insert(0, self.idea.get("title", ""))

        # Category
        category = self.idea.get("category", "")
        if category in self.categories:
            self.combo_category.set(category)
        else:
            self.combo_category.set(category)

        # Tags
        self.entry_tags.insert(0, self.idea.get("tags", ""))
        # Description
        self.text_description.insert("1.0", self.idea.get("description", ""))

    def on_save(self):
        """Validate input and either create or update an idea."""

        title = self.entry_title.get().strip()
        category = self.combo_category.get().strip()
        tags = self.entry_tags.get().strip()
        description = self.text_description.get("1.0", "end").strip()

        # Basic required fields checks
        if not title:
            messagebox.showwarning("Missing Title", "Please enter a title.")
            return

        if not category:
            messagebox.showwarning("Missing Category", "Please choose a category.")
            return

        if not description:
            if not messagebox.askyesno(
                    "Empty Description",
                    "Description is empty. Do you still want to save this idea?"
            ):
                return

        # Decide whether to insert or update
        if self.mode == "create":
            create_new_idea(
                title=title,
                category=category,
                description=description,
                tags=tags,
            )
        else:
            update_idea(
                idea_id=self.idea["id"],
                title=title,
                category=category,
                description=description,
                tags=tags,
            )

        # Notify main window to refresh, if callback exists
        if self.on_saved is not None:
            self.on_saved()

        # Close the form
        self.destroy()


class MainApp(tk.Tk):
    """Main application window shown after login."""

    def __init__(self):
        super().__init__()

        # Configure ttk style for retro-looking UI
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            "Retro.TFrame",
            background="#F5EEDC"
        )

        style.configure(
            "Retro.TLabel",
            font=("Courier New", 11),
            background="#F5EEDC",
            foreground="#5A4A42"
        )

        style.configure(
            "Retro.TButton",
            font=("Courier New", 12, "bold"),
            padding=10,
            relief="ridge",
            borderwidth=3,
            background="#E8DCC2",
            foreground="#4B3E35"
        )

        style.map(
            "Retro.TButton",
            background=[
                ("active", "#F2E6CC"),
                ("pressed", "#D6C5A8")
            ],
            relief=[
                ("pressed", "sunken"),
                ("active", "raised")
            ]
        )

        style.configure(
            "Treeview",
            background="#FFF9EF",
            fieldbackground="#FFF9EF",
            foreground="#4B3E35",
            bordercolor="#E8DCC2"
        )
        style.map(
            "Treeview",
            background=[("selected", "#E8D7B8")]
        )

        # Set main window background color
        self.configure(background="#AC9362")

        self.title("Gameplay Idea Brainstormer")
        self.geometry("1000x600")

        # Dynamic category list (starts from default)
        self.categories = DEFAULT_CATEGORIES.copy()
        # In-memory list of currently loaded ideas
        self.current_ideas = []

        # Build UI and load data
        self.build_widgets()
        self.load_ideas()

        # Show welcome popup shortly after UI appears
        self.after(100, self.welcome_message)

    def welcome_message(self):
        """Show an initial help/information popup when app opens."""
        messagebox.showinfo(
            "Welcome!",
            "Welcome to Gameplay Idea Brainstormer!\n\n"
            "You can:\n"
            "Add, edit, and delete ideas\n"
            "Filter, add, and delete category\n"
            "If nothing shows up on the screen, make sure a category is selected\n"
            "Please click on information for more information\n"
            "Click 'Add Idea' to get started!"
        )

    def build_widgets(self):
        """Create the top filter bar, buttons, and main split panels."""

        # Top container frame
        top_frame = ttk.Frame(self, style="Retro.TFrame")
        top_frame.pack(side="top", fill="x", padx=10, pady=5)

        # ===== Row 1: Category + Search + Go/Clear + Info =====
        row1 = ttk.Frame(top_frame, style="Retro.TFrame")
        row1.pack(side="top", fill="x")

        # Category dropdown
        ttk.Label(row1, text="Category:", style="Retro.TLabel").pack(side="left")
        self.category_var = tk.StringVar(value="all")
        self.category_combo = ttk.Combobox(
            row1,
            textvariable=self.category_var,
            values=["all"] + self.categories,
            state="readonly",
            width=15
        )
        self.category_combo.pack(side="left", padx=(5, 15))
        self.category_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        # Search bar
        ttk.Label(row1, text="Search:", style="Retro.TLabel").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(row1, textvariable=self.search_var, width=30)
        self.search_entry.pack(side="left", padx=5)

        # Go button
        ttk.Button(
            row1, text="Go",
            command=self.apply_filters,
            style="Retro.TButton"
        ).pack(side="left", padx=(0, 5))

        # Clear button
        ttk.Button(
            row1, text="Clear",
            command=self.clear_filters,
            style="Retro.TButton"
        ).pack(side="left", padx=(0, 5))

        # Information button
        ttk.Button(
            row1, text="Information",
            command=self.show_info,
            style="Retro.TButton"
        ).pack(side="left", padx=5)

        # ===== Row 2: Idea actions + Category management + Logout =====
        row2 = ttk.Frame(top_frame, style="Retro.TFrame")
        row2.pack(side="top", fill="x", pady=(5, 0))

        # Idea action buttons
        ttk.Button(
            row2, text="Add Idea",
            command=self.add_idea,
            style="Retro.TButton"
        ).pack(side="left")

        ttk.Button(
            row2, text="Edit Idea",
            command=self.edit_idea,
            style="Retro.TButton"
        ).pack(side="left", padx=5)

        ttk.Button(
            row2, text="Delete Idea",
            command=self.delete_idea,
            style="Retro.TButton"
        ).pack(side="left", padx=5)

        # Entry for new category name
        self.new_category_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.new_category_var, width=20).pack(side="left", padx=(20, 5))

        # Add category button
        ttk.Button(
            row2, text="Add Category",
            command=self.add_category,
            style="Retro.TButton"
        ).pack(side="left")

        # Remove category button
        ttk.Button(
            row2, text="Remove this Category",
            command=self.remove_category,
            style="Retro.TButton"
        ).pack(side="left", padx=5)

        # Logout button
        ttk.Button(
            row2, text="Logout",
            command=self.logout,
            style="Retro.TButton"
        ).pack(side="left", padx=5)

        # ===== Main Pane: left (Treeview) and right (details) =====
        main_frame = ttk.PanedWindow(self, orient="horizontal")
        main_frame.pack(side="top", fill="both", expand=True, padx=10, pady=5)

        # Left side: idea list
        left_frame = ttk.Frame(main_frame, style="Retro.TFrame")
        main_frame.add(left_frame, weight=2)

        columns = ("title", "category", "created_at", "updated_at")
        self.tree = ttk.Treeview(
            left_frame,
            columns=columns,
            show="headings",
            height=15
        )
        self.tree.heading("title", text="Title")
        self.tree.heading("category", text="Category")
        self.tree.heading("created_at", text="Created At")
        self.tree.heading("updated_at", text="Updated At")

        self.tree.column("title", width=220)
        self.tree.column("category", width=100)
        self.tree.column("created_at", width=130)
        self.tree.column("updated_at", width=130)

        vsb = ttk.Scrollbar(left_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Update details when selection changes
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Right side: idea details
        right_frame = ttk.Frame(main_frame, style="Retro.TFrame")
        main_frame.add(right_frame, weight=1)

        ttk.Label(right_frame, text="Idea Details:", style="Retro.TLabel").pack(anchor="w")

        self.details_text = tk.Text(
            right_frame,
            wrap="word",
            state="disabled",
            bg="#FFF9EF",
            fg="#4B3E35"
        )
        self.details_text.pack(fill="both", expand=True, pady=(5, 0))

    def show_info(self):
        """Show a help/about dialog with usage tips."""
        messagebox.showinfo(
            "About Gameplay Idea Brainstormer",
            "This app helps you manage gameplay ideas.\n\n"
            "If you are stuck on a blank page, please check\n"
            "that you have selected a category in the drop down\n"
            "menu in the corner\n"
            "If you delete any categories, the ideas under will show up in the\n"
            "uncategorized area\n"
            "The middle bar can be shifted left or right\n"
            "Please have fun with our little project! :)"
        )

    def logout(self):
        """Return to the login screen after confirmation."""
        confirm = messagebox.askyesno("Logout", "Are you sure you want to log out?")
        if not confirm:
            return

        self.destroy()
        login_window = LoginWindow()
        login_window.mainloop()

    def add_category(self):
        """Add a new category from the text field into the dropdown list."""
        name = self.new_category_var.get().strip()
        if not name:
            messagebox.showwarning(
                "No Category Name inputed",
                "Please type a category name in the bar to the left of the 'add category button'"
            )
            return

        # Check for duplicates (case-insensitive)
        for c in self.categories:
            if c.lower() == name.lower():
                messagebox.showinfo(
                    "Category exists",
                    "This category already exist. Please use the search bar to find it."
                )
                return

        # Append to category list and refresh dropdown
        self.categories.append(name)
        self.category_combo["values"] = ["all"] + self.categories
        self.new_category_var.set("")

    def remove_category(self):
        """Remove the currently selected category and handle its ideas."""
        name = self.category_var.get().strip()

        # Disallow removing global options
        if name == "all":
            messagebox.showwarning(
                "Invalid",
                "You cannot remove 'all'.\n\n"
                "Please select a specific category from the drop-down first."
            )
            return

        if name == "uncategorized":
            messagebox.showwarning(
                "Invalid",
                "You cannot remove 'uncategorized'."
            )
            return

        if name not in self.categories:
            messagebox.showwarning(
                "Invalid",
                "Select a category to remove."
            )
            return

        # Count how many ideas use this category
        used_ideas = [i for i in self.current_ideas if i["category"] == name]
        count = len(used_ideas)

        # Ask user what to do with ideas in this category
        if count > 0:
            answer = messagebox.askyesno(
                "Category is in use",
                f"{count} ideas use '{name}'.\n\nDo you want to delete the ideas as well?"
                "Press 'Yes' to delete both the ideas and the Category.\n"
                "Press 'No' delete the category and keep these ideas by moving them to 'uncategorized'."
            )
            if answer:
                delete_ideas_by_category(name)
            else:
                reassign_ideas_category(name, "uncategorized")

        # Remove from category list and refresh category combobox
        self.categories.remove(name)
        self.category_combo["values"] = ["all"] + self.categories
        self.category_var.set("uncategorized")
        self.apply_filters()

    def load_ideas(self, ideas=None):
        """Load ideas into the Treeview (optionally with a provided list)."""

        if ideas is None:
            ideas = get_all_ideas()
        self.current_ideas = ideas

        # Clear current rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert each idea as a row
        for idea in ideas:
            self.tree.insert(
                "",
                "end",
                iid=str(idea["id"]),
                values=(
                    idea["title"],
                    idea["category"],
                    idea["created_at"],
                    idea["updated_at"],
                )
            )

        # Reset details panel
        self.show_details(None)

    def apply_filters(self):
        """Filter ideas based on current category and search text."""
        category = self.category_var.get()
        search_text = self.search_var.get().strip()
        ideas = get_ideas_by_filter(category=category, search_text=search_text)
        self.load_ideas(ideas)

    def clear_filters(self):
        """Reset filters to show all ideas."""
        self.category_var.set("all")
        self.search_var.set("")
        self.load_ideas()

    def on_tree_select(self, event=None):
        """Show idea details when a row in the Treeview is selected."""
        selection = self.tree.selection()
        if not selection:
            self.show_details(None)
            return

        item_id = int(selection[0])
        idea = next((i for i in self.current_ideas if i["id"] == item_id), None)
        self.show_details(idea)

    def show_details(self, idea):
        """Update right-hand text box with idea details or a default message."""

        self.details_text.config(state="normal")
        self.details_text.delete("1.0", "end")

        if idea is None:
            self.details_text.insert("1.0", "Select an idea to see details.")
        else:
            text = (
                f"Title: {idea['title']}\n"
                f"Category: {idea['category']}\n"
                f"Tags: {idea.get('tags', '')}\n"
                f"Created: {idea['created_at']}\n"
                f"Updated: {idea['updated_at']}\n\n"
                f"{idea['description']}"
            )
            self.details_text.insert("1.0", text)

        self.details_text.config(state="disabled")

    def add_idea(self):
        """Open the idea form in create mode."""
        IdeaForm(self, mode="create", idea=None, on_saved=self.apply_filters, categories=self.categories)

    def edit_idea(self):
        """Open the idea form in edit mode for the selected idea."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No selection", "Please select an idea to edit.")
            return

        item_id = int(selection[0])
        idea = next((i for i in self.current_ideas if i["id"] == item_id), None)

        IdeaForm(self, mode="edit", idea=idea, on_saved=self.apply_filters, categories=self.categories)

    def delete_idea(self):
        """Delete the selected idea after confirmation."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No selection", "Please select an idea to delete.")
            return

        item_id = int(selection[0])
        idea = next((i for i in self.current_ideas if i["id"] == item_id), None)

        if not messagebox.askyesno("Confirm Delete", f"Delete idea '{idea['title']}'?"):
            return

        delete_idea(item_id)
        self.apply_filters()

#Multiple accounts have the same files there is no account exclusive files
if __name__ == "__main__":
    # Set up database tables and then start at the login window
    init_db()
    login_window = LoginWindow()
    login_window.mainloop()
