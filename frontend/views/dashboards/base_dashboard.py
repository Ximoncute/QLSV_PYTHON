import tkinter as tk
from tkinter import messagebox, ttk
from frontend.core.api_client import api
from frontend.core.styles import center_window, COLORS

class BaseDashboard:
    def __init__(self, root, title: str):
        self.root = root
        self.root.title(f"QLSVSDH - {title}")
        center_window(self.root, 1100, 700)
        self.root.configure(bg=COLORS["BG"])

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Override in subclass"""
        pass

    def setup_scrollable_area(self, parent):
        """Standardized scrollable container with MouseWheel support"""
        self.container = tk.Frame(parent, bg=COLORS["BG"])
        self.container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self.container, bg=COLORS["BG"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.content = tk.Frame(self.canvas, bg=COLORS["BG"])
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content, anchor="nw")

        # Bindings
        self.content.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def on_canvas_configure(self, event):
        """Keep content frame width at 100% of canvas width"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        """Global mousewheel handling"""
        try:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        except: pass

    def load_data(self):
        """Override in subclass"""
        pass

    def clear_content(self):
        """Clear central content area and reset scroll to top"""
        for widget in self.content.winfo_children():
            widget.destroy()
        if hasattr(self, 'canvas'):
            self.canvas.yview_moveto(0)

    def create_nav_button(self, parent, text, command):
        """Tạo nav button"""
        btn = tk.Button(parent, text=text, command=command,
                       font=("Segoe UI", 10), bg=COLORS["NAV_BG"], fg="white",
                       relief="flat", anchor="w", padx=20, pady=12,
                       cursor="hand2")
        btn.bind("<Enter>", lambda e: btn.configure(bg=COLORS["NAV_HOVER"]))
        btn.bind("<Leave>", lambda e: btn.configure(bg=COLORS["NAV_BG"]))
        return btn

    def logout(self, on_logout):
        """Đăng xuất"""
        if messagebox.askyesno("Xác nhận", "Bạn có muốn đăng xuất?"):
            api.clear_auth()
            self.root.destroy()
            on_logout()

    def show_error(self, msg):
        messagebox.showerror("Lỗi", msg)
