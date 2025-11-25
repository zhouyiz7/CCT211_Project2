import tkinter as tk
from tkinter import ttk, messagebox

# 从db模块导入数据库操作函数
from db import (
    init_db,
    create_new_idea,
    get_all_ideas,
    get_ideas_by_filter,
    update_idea,
    delete_idea,
    verify_user,
)

# 定义创意分类列表
CATEGORIES = ["gameplay", "character", "level", "skin", "operation"]


# 登录窗口类
class LoginWindow(tk.Tk):
    def __init__(self):
        """初始化登录窗口"""
        super().__init__()
        self.title("GIB - Login")
        self.geometry("400x260")
        self.resizable(False, False)
        
        self.build_widgets()
        
        # 窗口居中
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
    def build_widgets(self):
        """构建登录界面控件"""
        # 主框架
        main_frame = ttk.Frame(self, padding="40 40 40 40")
        main_frame.pack(fill="both", expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="Gameplay Idea Brainstormer",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 30))
        
        # 用户名
        username_frame = ttk.Frame(main_frame)
        username_frame.pack(fill="x", pady=5)
        ttk.Label(username_frame, text="Username:", width=12).pack(side="left")
        self.username_entry = ttk.Entry(username_frame, width=25)
        self.username_entry.pack(side="left", padx=(5, 0))
        
        # 密码
        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill="x", pady=5)
        ttk.Label(password_frame, text="Password:", width=12).pack(side="left")
        self.password_entry = ttk.Entry(password_frame, width=25, show="*")
        self.password_entry.pack(side="left", padx=(5, 0))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(15, 0))
        
        # From Lab 8 Ex3
        exit_btn = ttk.Button(button_frame, text="Exit", command=self.quit, width=20)
        exit_btn.pack(side="left", padx=10, ipady=10)

        login_btn = ttk.Button(button_frame, text="Login", command=self.login, width=20)
        login_btn.pack(side="left", padx=10, ipady=10)
        
        # 绑定回车键到登录
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda e: self.login())
        
        # 设置焦点
        self.username_entry.focus()
        
    def login(self):
        """处理登录逻辑"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if verify_user(username, password):
            # 登录成功，关闭登录窗口并打开主窗口
            self.destroy()
            app = MainApp()
            app.mainloop()
        else:
            # 登录失败，显示错误消息
            messagebox.showerror(
                "Login Failed",
                "Invalid username or password.\nPlease try again."
            )
            self.password_entry.delete(0, "end")
            self.username_entry.focus()


# 创意表单窗口类，用于添加和编辑创意
class IdeaForm(tk.Toplevel):

    def __init__(self, master, mode="create", idea=None, on_saved=None):
        """初始化表单窗口
        mode: 'create'创建新创意 或 'edit'编辑现有创意
        idea: 要编辑的创意数据
        on_saved: 保存后的回调函数
        """
        super().__init__(master)
        self.mode = mode
        self.idea = idea
        self.on_saved = on_saved

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
        """构建表单的所有输入控件"""
        padding = {"padx": 8, "pady": 5}

        ttk.Label(self, text="Idea Title:").grid(row=0, column=0, sticky="w", **padding)
        self.entry_title = ttk.Entry(self, width=40, justify="center")
        self.entry_title.grid(row=0, column=1, **padding)

        ttk.Label(self, text="Category:").grid(row=1, column=0, sticky="w", **padding)
        self.combo_category = ttk.Combobox(self, values=CATEGORIES, state="readonly", width=40)
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
        """在编辑模式下，用现有数据填充表单字段"""
        self.entry_title.insert(0, self.idea.get("title", ""))

        category = self.idea.get("category", "")
        if category in CATEGORIES:
            self.combo_category.set(category)

        self.entry_tags.insert(0, self.idea.get("tags", ""))
        self.text_description.insert("1.0", self.idea.get("description", ""))

    def on_save(self):
        """保存按钮的处理函数，验证并保存数据"""
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

        # 根据模式调用相应的数据库函数
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

        # 调用保存后的回调函数
        if self.on_saved is not None:
            self.on_saved()

        self.destroy()


# 主应用程序窗口类
class MainApp(tk.Tk):
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        self.title("Gameplay Idea Brainstormer")
        self.geometry("1200x800")

        self.current_ideas = []  # 存储当前显示的创意列表
        self.build_widgets()
        self.load_ideas()

    def build_widgets(self):
        """构建主窗口的所有界面元素"""
        # 顶部过滤栏
        top_frame = ttk.Frame(self)
        top_frame.pack(side="top", fill="x", padx=10, pady=5)

        ttk.Label(top_frame, text="Category:").pack(side="left")
        self.category_var = tk.StringVar(value="all")
        self.category_combo = ttk.Combobox(
            top_frame,
            textvariable=self.category_var,
            values=["all"] + CATEGORIES,
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

        # 操作按钮栏
        btn_frame = ttk.Frame(self)
        btn_frame.pack(side="top", fill="x", padx=10, pady=(0, 5))

        ttk.Button(btn_frame, text="Add Idea", command=self.add_idea).pack(side="left")
        ttk.Button(btn_frame, text="Edit Idea", command=self.edit_idea).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete Idea", command=self.delete_idea).pack(side="left")

        # 主内容区域，分为左右两个面板
        main_frame = ttk.PanedWindow(self, orient="horizontal")
        main_frame.pack(side="top", fill="both", expand=True, padx=10, pady=5)

        # 左侧面板：创意列表
        left_frame = ttk.Frame(main_frame)
        main_frame.add(left_frame, weight=2)

        # 创建树形视图显示创意列表
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

        # 绑定选择事件
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # 右侧面板：创意详情
        right_frame = ttk.Frame(main_frame)
        main_frame.add(right_frame, weight=1)

        ttk.Label(right_frame, text="Idea Details:").pack(anchor="w")

        self.details_text = tk.Text(right_frame, wrap="word", state="disabled")
        self.details_text.pack(fill="both", expand=True, pady=(5, 0))

    def load_ideas(self, ideas=None):
        """加载并显示创意列表"""
        if ideas is None:
            ideas = get_all_ideas()
        self.current_ideas = ideas

        # 清空现有列表
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 填充新数据
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
        """应用分类和搜索过滤器"""
        category = self.category_var.get()
        search_text = self.search_var.get().strip()
        ideas = get_ideas_by_filter(category=category, search_text=search_text)
        self.load_ideas(ideas)

    def clear_filters(self):
        """清除所有过滤器，显示全部创意"""
        self.category_var.set("all")
        self.search_var.set("")
        self.load_ideas()

    def on_tree_select(self, event=None):
        """处理树形视图选择事件，显示选中创意的详情"""

        selection = self.tree.selection()
        if not selection:
            self.show_details(None)
            return

        item_id = int(selection[0])
        idea = next((i for i in self.current_ideas if i["id"] == item_id), None)
        self.show_details(idea)

    def show_details(self, idea):
        """在右侧面板显示创意详情"""
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
        """打开表单窗口添加新创意"""
        IdeaForm(self, mode="create", idea=None, on_saved=self.apply_filters)

    def edit_idea(self):
        """打开表单窗口编辑选中的创意"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("No selection", "Please select an idea to edit.")
            return

        item_id = int(selection[0])
        idea = next((i for i in self.current_ideas if i["id"] == item_id), None)

        IdeaForm(self, mode="edit", idea=idea, on_saved=self.apply_filters)

    def delete_idea(self):
        """删除选中的创意"""
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


# 程序入口
if __name__ == "__main__":
    init_db()  # 初始化数据库
    login_window = LoginWindow()  # 创建登录窗口
    login_window.mainloop()  # 启动事件循环
