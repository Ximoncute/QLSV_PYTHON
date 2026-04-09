import tkinter as tk
from tkinter import messagebox
from frontend.core.api_client import api
from frontend.core.styles import center_window, COLORS

class LoginWindow:
    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success
        self.root.title("QLSVSDH - Đăng nhập")
        center_window(self.root, 450, 480)
        self.root.configure(bg=COLORS["BG"])

        self.setup_ui()

    def setup_ui(self):
        # Title
        title_frame = tk.Frame(self.root, bg=COLORS["PRIMARY"], height=100)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text="QLSVSDH",
                               font=("Segoe UI", 24, "bold"),
                               bg=COLORS["PRIMARY"], fg="white").pack(pady=15)

        tk.Label(title_frame, text="University Management System - Modern",
                           font=("Segoe UI", 9), bg=COLORS["PRIMARY"], fg="#BBDEFB").pack()

        # Login form
        form_frame = tk.Frame(self.root, bg="white", bd=1, relief="solid")
        form_frame.pack(pady=20, padx=30, fill="both", expand=True)

        tk.Label(form_frame, text="ĐĂNG NHẬP",
                font=("Segoe UI", 14, "bold"), bg="white",
                fg="#333").pack(pady=15)

        # Role selection
        self.role_var = tk.StringVar(value="student")
        role_frame = tk.Frame(form_frame, bg="white")
        role_frame.pack(pady=10)

        roles = [("Thí sinh", "candidate"), ("Sinh viên", "student"), ("Quản trị", "admin")]
        for text, value in roles:
            tk.Radiobutton(role_frame, text=text, variable=self.role_var,
                                value=value, font=("Segoe UI", 9), bg="white",
                                command=self.on_role_change).pack(side="left", padx=10)

        # Fields
        self.fields_frame = tk.Frame(form_frame, bg="white")
        self.fields_frame.pack(pady=10, padx=50, fill="x")

        self.user_label = tk.Label(self.fields_frame, text="Mã sinh viên:", bg="white")
        self.user_label.pack(anchor="w")
        self.user_entry = tk.Entry(self.fields_frame, font=("Segoe UI", 11))
        self.user_entry.pack(pady=5, fill="x", ipady=5)

        tk.Label(self.fields_frame, text="Mật khẩu:", bg="white").pack(anchor="w")
        self.pass_entry = tk.Entry(self.fields_frame, font=("Segoe UI", 11), show="*")
        self.pass_entry.pack(pady=5, fill="x", ipady=5)

        # Button
        self.login_btn = tk.Button(form_frame, text="VÀO HỆ THỐNG",
                                   command=self.do_login,
                                   font=("Segoe UI", 10, "bold"),
                                   bg=COLORS["SECONDARY"], fg="white",
                                   relief="flat", cursor="hand2", pady=8)
        self.login_btn.pack(pady=10, fill="x", padx=50)

        # Register Link
        tk.Button(form_frame, text="Chưa có tài khoản? Đăng ký thí sinh ngay", 
                  command=self.open_register_modal,
                  font=("Segoe UI", 8, "underline"), bg="white", fg="#1A73E8",
                  relief="flat", cursor="hand2", bd=0).pack(pady=5)

        self.pass_entry.bind("<Return>", lambda e: self.do_login())

    def on_role_change(self):
        role = self.role_var.get()
        if role == "admin":
            self.user_label.config(text="Email Quản trị:")
        elif role == "student":
            self.user_label.config(text="Mã sinh viên:")
        else:
            self.user_label.config(text="Email Thí sinh:")

    def open_register_modal(self):
        reg_win = tk.Toplevel(self.root)
        reg_win.title("Đăng ký tài khoản Thí sinh")
        center_window(reg_win, 350, 400)
        reg_win.configure(bg="white")
        
        tk.Label(reg_win, text="ĐĂNG KÝ THÍ SINH", font=("Segoe UI", 14, "bold"), bg="white").pack(pady=20)
        
        tk.Label(reg_win, text="Email đăng ký:", bg="white").pack(padx=30, anchor="w")
        email_e = tk.Entry(reg_win, font=("Segoe UI", 11))
        email_e.pack(padx=30, pady=5, fill="x", ipady=5)
        
        tk.Label(reg_win, text="Mật khẩu:", bg="white").pack(padx=30, anchor="w")
        pass_e = tk.Entry(reg_win, font=("Segoe UI", 11), show="*")
        pass_e.pack(padx=30, pady=5, fill="x", ipady=5)
        
        tk.Label(reg_win, text="Xác nhận mật khẩu:", bg="white").pack(padx=30, anchor="w")
        conf_e = tk.Entry(reg_win, font=("Segoe UI", 11), show="*")
        conf_e.pack(padx=30, pady=5, fill="x", ipady=5)
        
        def do_register():
            email = email_e.get().strip()
            pw = pass_e.get().strip()
            if pw != conf_e.get().strip():
                messagebox.showerror("Lỗi", "Mật khẩu không khớp")
                return
            
            res = api.post("/auth/register/candidate", {"email": email, "password": pw})
            if res.get("success"):
                messagebox.showinfo("Thành công", "Đăng ký thành công! Hãy dùng Email này để đăng nhập.")
                reg_win.destroy()
            else:
                messagebox.showerror("Thất bại", res.get("detail", "Lỗi xảy ra"))
                
        tk.Button(reg_win, text="ĐĂNG KÝ NGAY", command=do_register,
                 bg="#34A853", fg="white", font=("Segoe UI", 10, "bold"), pady=8).pack(pady=30, padx=30, fill="x")

    def do_login(self):
        role = self.role_var.get()
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập đầy đủ thông tin")
            return

        self.login_btn.config(state="disabled", text="Đang xử lý...")
        result = api.login(role, username, password)
        self.login_btn.config(state="normal", text="VÀO HỆ THỐNG")

        if result.get("success"):
            api.set_auth(result["token"], result["user"], role)
            self.on_login_success()
        else:
            messagebox.showerror("Đăng nhập thất bại", result.get("message", "Sai thông tin đăng nhập"))
