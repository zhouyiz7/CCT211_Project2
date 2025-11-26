import tkinter as tk
from tkinter import ttk, messagebox

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

DEFAULT_CATEGORIES = ["gameplay", "character", "level", "skin", "operation"]


class LoginWindow(tk.Tk):
    def __init__(self):

        super().__init__()
        self.title("GIB - Login")
        self.geometry("800x400")
        self.resizable(False, False)

        self.build_widgets()

        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def build_widgets(self):

        main_frame = ttk.Frame(self, padding="40 40 40 40")
        main_frame.pack(fill="both", expand=True)

        title_label = ttk.Label(
            main_frame,
            text="Gameplay Idea Brainstormer",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 30))

        username_frame = ttk.Frame(main_frame)
        username_frame.pack(fill="x", pady=5)
        ttk.Label(username_frame, text="Username:", width=12).pack(side="left")
        self.username_entry = ttk.Entry(username_frame, width=25)
        self.username_entry.pack(side="left", padx=(5, 0))

        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill="x", pady=5)
        ttk.Label(password_frame, text="Password:", width=12).pack(side="left")
        self.password_entry = ttk.Entry(password_frame, width=25, show="*")
        self.password_entry.pack(side="left", padx=(5, 0))

        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(15, 0))

        exit_btn = ttk.Button(button_frame, text="Exit", command=self.quit, width=20)
        exit_btn.pack(side="left", padx=10, ipady=10)

        login_btn = ttk.Button(button_frame, text="Login", command=self.login, width=20)
        login_btn.pack(side="left", padx=10, ipady=10)

        register_btn = ttk.Button(button_frame, text="Create Account", command=self.open_register, width=20)
        register_btn.pack(side="left", padx=10, ipady=10)

        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.login())

        self.username_entry.focus()

    def login(self):

        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if verify_user(username, password):

            self.destroy()
            app = MainApp()
            app.mainloop()
        else:

            messagebox.showerror(
                "Login Failed",
                "Invalid username or password.\nPlease try again."
            )
            self.password_entry.delete(0, "end")
            self.username_entry.focus()

    def open_register(self):
        RegisterWindow(self)


class RegisterWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Create Account")
        self.resizable(False, False)
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Username:").grid(row=0, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(frame, width=25)
        self.username_entry.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Password:").grid(row=1, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(frame, width=25, show="*")
        self.password_entry.grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="Confirm").grid(row=2, column=0, sticky="w", pady=5)
        self.confirm_entry = ttk.Entry(frame, width=25, show="*")
        self.confirm_entry.grid(row=2, column=1, pady=5)

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))

        ttk.Button(btn_frame, text="Create", command=self.create_account).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=5)

        self.username_entry.focus()

    def create_account(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()

        if not username or not password:
            messagebox.showwarning("Missing Info", "Please enter both username and password.")
            return

        if password != confirm:
            messagebox.showwarning("Password Mismatch", "Passwords do not match.")
            return

        ok = create_user(username, password)
        if not ok:
            messagebox.showerror("Error", "This username is already taken.")
            return

        messagebox.showinfo("Success", "Account created. You can now log in.")
        self.destroy()


class IdeaForm(tk.Toplevel):

    def __init__(self, master, mode="create", idea=None, on_saved=None):

        super().__init__(master)
        self.mode = mode
        self.idea = idea
        self.on_saved = on_saved
        self.categories = categories or DEFAULT_CATEGORIES 

        if self.mode == "create":
            self.title("Add New Idea")
        else:
            self.title("Edit Idea")

        self.resizable(False, False)
        self.build_widgets()

        if self.mode == "edit" and self.idea is not None:
            self.populate_fields()

        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def build_widgets(self):

        padding = {"padx": 8, "pady": 5}

        ttk.Label(self, text="Idea Title:").grid(row=0, column=0, sticky="w", **padding)
        self.entry_title = ttk.Entry(self, width=40, justify="center")
        self.entry_title.grid(row=0, column=1, **padding)

        ttk.Label(self, text="Category:").grid(row=1, column=0, sticky="w", **padding)
        
        self.combo_category = ttk.Combobox(self, values=self.categories, state="readonly", width=40)
        self.combo_category.grid(row=1, column=1, sticky="we", **padding)

        ttk.Label(self, text="Tags (comma-separated):").grid(row=2, column=0, sticky="w", **padding)
        self.entry_tags = ttk.Entry(self, width=40)
        self.entry_tags.grid(row=2, column=1, **padding)

        ttk.Label(self, text="Description:").grid(row=3, column=0, sticky="nw", **padding)
        self.text_description = tk.Text(self, width=40, height=10)
        self.text_description.grid(row=3, column=1, **padding)

        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=4, column=0, columnspan=2, sticky="e", padx=10, pady=(0, 10))

        ttk.Button(btn_frame, text="Save", command=self.on_save).pack(side="right", padx=(0, 5))
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="right")

    def populate_fields(self):

        self.entry_title.insert(0, self.idea.get("title", ""))

        category = self.idea.get("category", "")
        if category in self.categories:
            self.combo_category.set(category)
        else:
            self.combo_category.set(category)

        self.entry_tags.insert(0, self.idea.get("tags", ""))
        self.text_description.insert("1.0", self.idea.get("description", ""))

    def on_save(self):

        title = self.entry_title.get().strip()
        category = self.combo_category.get().strip()
        tags = self.entry_tags.get().strip()
        description = self.text_description.get("1.0", "end").strip()

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

        if self.on_saved is not None:
            self.on_saved()

        self.destroy()


class MainApp(tk.Tk):
    def __init__(self):

        super().__init__()
        self.title("Gameplay Idea Brainstormer")
        self.geometry("1200x800")
        self.categories = DEFAULT_CATEGORIES.copy()

        self.current_ideas = []
        self.build_widgets()
        self.load_ideas()

    def build_widgets(self):

        top_frame = ttk.Frame(self)
        top_frame.pack(side="top", fill="x", padx=10, pady=5)

        ttk.Label(top_frame, text="Category:").pack(side="left")
        self.category_var = tk.StringVar(value="all")
        self.category_combo = ttk.Combobox(
            top_frame,
            textvariable=self.category_var,
            values=["all"] + self.categories,
            state="readonly",
            width=15
        )
        self.category_combo.pack(side="left", padx=(5, 15))
        self.category_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        ttk.Label(top_frame, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side="left", padx=5)
        ttk.Button(top_frame, text="Go", command=self.apply_filters).pack(side="left", padx=(0, 5))
        ttk.Button(top_frame, text="Clear", command=self.clear_filters).pack(side="left")

        btn_frame = ttk.Frame(self)
        btn_frame.pack(side="top", fill="x", padx=10, pady=(0, 5))

        ttk.Button(btn_frame, text="Add Idea", command=self.add_idea).pack(side="left")
        ttk.Button(btn_frame, text="Edit Idea", command=self.edit_idea).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete Idea", command=self.delete_idea).pack(side="left")
        
        self.new_category_var = tk.StringVar()
        ttk.Entry(btn_frame, textvariable = self.new_category_var, width=20.pack(side="left", padx=(20,5))
        ttl.Button(btn_frame, text="Add Category, command=self.add_category).pack(side="left")

        main_frame = ttk.PanedWindow(self, orient="horizontal")
        main_frame.pack(side="top", fill="both", expand=True, padx=10, pady=5)

        left_frame = ttk.Frame(main_frame)
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

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        right_frame = ttk.Frame(main_frame)
        main_frame.add(right_frame, weight=1)

        ttk.Label(right_frame, text="Idea Details:").pack(anchor="w")

        self.details_text = tk.Text(right_frame, wrap="word", state="disabled")
        self.details_text.pack(fill="both", expand=True, pady=(5, 0))

    def add_category(self):
        name = self.new_category_var.get().strip()
        if not name:
            return
        for c in self.categories:
            if c.lower == name.lower():
                messagebox.showinfo("Category exists", "This category already exist. Please use the search bar to find it.")
                return
    self.categories.append(name)
    self.category_combo["values"] = ["all"] + self.categories
    self.new_categories_var.set("")


    def load_ideas(self, ideas=None):

        if ideas is None:
            ideas = get_all_ideas()
        self.current_ideas = ideas

        for item in self.tree.get_children():
            self.tree.delete(item)

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

        self.show_details(None)

    def apply_filters(self):

        category = self.category_var.get()
        search_text = self.search_var.get().strip()
        ideas = get_ideas_by_filter(category=category, search_text=search_text)
        self.load_ideas(ideas)

    def clear_filters(self):

        self.category_var.set("all")
        self.search_var.set("")
        self.load_ideas()

    def on_tree_select(self, event=None):

        selection = self.tree.selection()
        if not selection:
            self.show_details(None)
            return

        item_id = int(selection[0])
        idea = next((i for i in self.current_ideas if i["id"] == item_id), None)
        self.show_details(idea)

    def show_details(self, idea):

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

        IdeaForm(self, mode="create", idea=None, on_saved=self.apply_filters, categories=self.categoies)

    def edit_idea(self):

        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No selection", "Please select an idea to edit.")
            return

        item_id = int(selection[0])
        idea = next((i for i in self.current_ideas if i["id"] == item_id), None)

        IdeaForm(self, mode="edit", idea=idea, on_saved=self.apply_filters, categories = self.categories)

    def delete_idea(self):

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


if __name__ == "__main__":
    init_db()
    login_window = LoginWindow()
    login_window.mainloop()
