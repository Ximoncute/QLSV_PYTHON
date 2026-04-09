import tkinter as tk
from tkinter import ttk, messagebox
from frontend.core.api_client import api
from frontend.core.styles import COLORS, setup_card, style_button
from frontend.views.dashboards.base_dashboard import BaseDashboard

class AdmissionDashboard(BaseDashboard):
    def __init__(self, root, on_logout):
        self.on_logout_callback = on_logout
        self.current_view = None
        self.nav_buttons = {}
        super().__init__(root, "Cổng Tuyển sinh")

    def setup_ui(self):
        # 1. Main Header (Admission Green)
        self.header = tk.Frame(self.root, bg="#2E7D32", height=70)
        self.header.pack(fill="x", side="top")
        self.header.pack_propagate(False)

        tk.Label(self.header, text="CỔNG TUYỂN SINH", 
                 font=("Segoe UI", 18, "bold"), bg="#2E7D32", fg="white").pack(side="left", padx=30)

        # Right side info
        user_info = tk.Frame(self.header, bg="#2E7D32")
        user_info.pack(side="right", padx=20)

        name = api.user.get('ho_ten', 'Thí sinh')
        tk.Label(user_info, text=name, font=("Segoe UI", 10, "bold"), bg="#2E7D32", fg="white").pack(side="left", padx=10)
        
        tk.Button(user_info, text="Đăng xuất", command=lambda: self.logout(self.on_logout_callback),
                 bg="#D32F2F", fg="white", font=("Segoe UI", 9, "bold"), 
                 relief="flat", cursor="hand2", padx=15, pady=5).pack(side="left", padx=10)

        # 2. Body Container
        self.body = tk.Frame(self.root, bg=COLORS["BG"])
        self.body.pack(fill="both", expand=True)

        # 3. Sidebar (Admission Dark Green)
        self.sidebar = tk.Frame(self.body, bg="#1B5E20", width=260)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        tk.Label(self.sidebar, text="CỔNG THÍ SINH", font=("Segoe UI", 10, "bold"), 
                 bg="#1B5E20", fg="#A5D6A7").pack(pady=(30, 20), padx=20, anchor="w")

        # Nav items
        nav_items = [
            ("Tổng quan", "📊", self.show_home),
            ("Hồ sơ cá nhân", "🆔", self.show_profile),
            ("Nguyện vọng", "🎓", self.show_methods),
            ("Thông báo", "🔔", self.show_notifications),
        ]

        for text, icon, cmd in nav_items:
            self.add_nav_item(text, icon, cmd)

        # 4. Content Area with Scrollbar (Inherited)
        self.setup_scrollable_area(self.body)
        self.content.configure(padx=40, pady=30)

        self.show_home()

    def add_nav_item(self, text, icon, command):
        btn = tk.Button(self.sidebar, text=f"  {icon}   {text}", 
                       command=lambda t=text, c=command: self.handle_nav_click(t, c),
                       font=("Segoe UI", 11), bg="#1B5E20", fg="white",
                       relief="flat", anchor="w", padx=25, pady=12,
                       cursor="hand2", activebackground="#2E7D32", activeforeground="white")
        btn.pack(fill="x")
        self.nav_buttons[text] = btn
        
        # Hover effect
        btn.bind("<Enter>", lambda e: btn.configure(bg="#2E7D32") if self.current_view != text else None)
        btn.bind("<Leave>", lambda e: btn.configure(bg="#1B5E20") if self.current_view != text else None)

    def handle_nav_click(self, text, command):
        self.clear_content()
        self.current_view = text
        for t, b in self.nav_buttons.items():
            b.configure(bg="#1B5E20")
        self.nav_buttons[text].configure(bg="#2E7D32")
        command()

    def show_home(self):
        self.clear_content()
        self.current_view = "Tổng quan"
        self.nav_buttons["Tổng quan"].configure(bg="#2E7D32")

        # Page Header
        header_fr = tk.Frame(self.content, bg=COLORS["BG"])
        header_fr.pack(fill="x", pady=(0, 20))
        tk.Label(header_fr, text=f"Chào mừng, {api.user.get('ho_ten', 'Thí sinh')}", 
                 font=("Segoe UI", 24, "bold"), bg=COLORS["BG"], fg="#1B5E20").pack(side="left")

        # Fetch data
        res = api.get("/admission/my")
        data = res.get("data", {}) if res.get("success") else {}
        status = data.get("status", "Đang xử lý")
        
        # 1. Status Overview Card
        status_card = tk.Frame(self.content, bg="white", padx=25, pady=25)
        status_card.pack(fill="x", pady=10)
        setup_card(status_card)

        tk.Label(status_card, text="Tình trạng hồ sơ", font=("Segoe UI", 12, "bold"), bg="white").pack(anchor="w")
        
        # Badge
        status_colors = {"Đã duyệt": "#2E7D32", "Cần bổ sung": "#F9AB00", "Bị từ chối": "#D93025"}
        bg_col = status_colors.get(status, "#1A73E8")
        
        badge = tk.Frame(status_card, bg=bg_col, padx=20, pady=8)
        badge.pack(anchor="w", pady=15)
        tk.Label(badge, text=status.upper(), font=("Segoe UI", 12, "bold"), bg=bg_col, fg="white").pack()
        
        tk.Label(status_card, text=f"Mã hồ sơ: {data.get('ma_hso', 'N/A')}", font=("Segoe UI", 10), bg="white", fg="#5F6368").pack(anchor="w")

        # 2. Content Row
        row_fr = tk.Frame(self.content, bg=COLORS["BG"])
        row_fr.pack(fill="x", pady=20)
        
        # Summary Card
        sum_card = tk.Frame(row_fr, bg="white", padx=25, pady=25)
        sum_card.place(relx=0, rely=0, relwidth=0.48, relheight=1)
        setup_card(sum_card)
        tk.Label(sum_card, text="Thông tin đăng ký", font=("Segoe UI", 12, "bold"), bg="white").pack(anchor="w", pady=(0, 15))
        
        method = data.get("method", {})
        info = [
            ("Ngành:", method.get("ten_nganh", "N/A")),
            ("Phương thức:", method.get("phuong_thuc", "N/A")),
            ("Điểm xét:", method.get("diem", "0.0"))
        ]
        for l, v in info:
            f = tk.Frame(sum_card, bg="white", pady=5)
            f.pack(fill="x")
            tk.Label(f, text=l, font=("Segoe UI", 10), bg="white", fg="#5F6368", width=12, anchor="w").pack(side="left")
            tk.Label(f, text=v, font=("Segoe UI", 10, "bold"), bg="white").pack(side="left")

        # Task/Guide Card
        guide_card = tk.Frame(row_fr, bg="white", padx=25, pady=25)
        guide_card.place(relx=0.52, rely=0, relwidth=0.48, relheight=1)
        setup_card(guide_card)
        tk.Label(guide_card, text="Các bước cần làm", font=("Segoe UI", 12, "bold"), bg="white").pack(anchor="w", pady=(0, 15))
        
        steps = [
            ("Kiểm tra thông tin cá nhân", "✅"),
            ("Cập nhật học bạ (nếu thiếu)", "⏳"),
            ("Nộp lệ phí xét tuyển", status == "Đã duyệt" and "✅" or "⏳")
        ]
        for txt, icon in steps:
            f = tk.Frame(guide_card, bg="white", pady=5)
            f.pack(fill="x")
            tk.Label(f, text=f"{icon} {txt}", font=("Segoe UI", 10), bg="white").pack(side="left")

        row_fr.configure(height=200)

    def show_profile(self):
        self.clear_content()
        tk.Label(self.content, text="Hồ sơ cá nhân", font=("Segoe UI", 20, "bold"), bg=COLORS["BG"]).pack(anchor="w", pady=(0, 20))
        
        res = api.get("/admission/my")
        data = res.get("data", {}) if res.get("success") else {}
        
        card = tk.Frame(self.content, bg="white", padx=30, pady=30)
        card.pack(fill="x")
        setup_card(card)
        
        fields = [
            ("Mã tài khoản", data.get("ma_tk", "N/A"), "👤"),
            ("Mã hồ sơ", data.get("ma_hso", "N/A"), "📄"),
            ("Họ và Tên", data.get("ho_ten", "N/A"), "🏷️"),
            ("Số CCCD", data.get("cccd", "N/A"), "🆔"),
            ("Số điện thoại", data.get("sdt", "N/A"), "📞")
        ]
        
        for label, val, icon in fields:
            row = tk.Frame(card, bg="white", pady=12)
            row.pack(fill="x")
            tk.Label(row, text=f"{icon}  {label}", font=("Segoe UI", 10, "bold"), bg="white", fg="#5F6368", width=25, anchor="w").pack(side="left")
            tk.Label(row, text=val, font=("Segoe UI", 11), bg="white").pack(side="left")
            tk.Frame(card, bg="#F1F3F4", height=1).pack(fill="x")

    def show_methods(self):
        self.clear_content()
        self.current_view = "Nguyện vọng"
        header = tk.Frame(self.content, bg=COLORS["BG"])
        header.pack(fill="x", pady=(0, 20))
        tk.Label(header, text="Nguyện vọng xét tuyển", font=("Segoe UI", 20, "bold"), bg=COLORS["BG"]).pack(side="left")
        
        res = api.get("/admission/my")
        data = res.get("data", {}) if res.get("success") else {}
        method = data.get("method", {})
        
        # Determine mode: View or Register
        is_registered = method.get("ma_ptxt") != "N/A"
        
        if is_registered and method.get("trang_thai") == "Đã duyệt":
            # Read-only View for Approved status
            self.render_method_view(method)
        else:
            # Registration / Edit Form
            self.render_method_form(method)

    def render_method_view(self, method):
        card = tk.Frame(self.content, bg="white", padx=30, pady=30)
        card.pack(fill="x")
        setup_card(card)
        
        tk.Label(card, text="HỒ SƠ ĐÃ ĐƯỢC DUYỆT", font=("Segoe UI", 12, "bold"), bg="white", fg="#2E7D32").pack(anchor="w", pady=(0, 20))
        
        fields = [
            ("Ngành đăng ký", method.get("ten_nganh", "N/A")),
            ("Mã ngành", method.get("ma_nganh", "N/A")),
            ("Phương thức xét tuyển", method.get("phuong_thuc", "N/A")),
            ("Điểm xét tuyển", method.get("diem", "0.0")),
            ("Trạng thái", method.get("trang_thai", "N/A"))
        ]
        
        for label, val in fields:
            row = tk.Frame(card, bg="white", pady=10)
            row.pack(fill="x")
            tk.Label(row, text=label, font=("Segoe UI", 10), bg="white", fg="#757575", width=20, anchor="w").pack(side="left")
            tk.Label(row, text=val, font=("Segoe UI", 10, "bold"), bg="white").pack(side="left")
            
        tk.Label(card, text="* Hồ sơ đã duyệt không thể thay đổi thông tin.", font=("Segoe UI", 9, "italic"), bg="white", fg="#D93025").pack(anchor="w", pady=(20, 0))

    def render_method_form(self, method):
        container = tk.Frame(self.content, bg="white", padx=35, pady=35)
        container.pack(fill="x")
        setup_card(container)
        
        title = "ĐĂNG KÝ XÉT TUYỂN" if method.get("ma_ptxt") == "N/A" else "CẬP NHẬT NGUYỆN VỌNG"
        tk.Label(container, text=title, font=("Segoe UI", 14, "bold"), bg="white", fg="#1B5E20").pack(anchor="w", pady=(0, 25))
        
        # 1. Major Selection
        tk.Label(container, text="Chọn Ngành học đăng ký", font=("Segoe UI", 10, "bold"), bg="white").pack(anchor="w", pady=(10, 5))
        
        nganh_res = api.get("/nganh/")
        all_nganh = nganh_res.get("data", []) if nganh_res.get("success") else []
        nganh_options = {n['ten_nganh']: n['ma_nganh'] for n in all_nganh}
        
        self.sel_nganh = tk.StringVar(value=method.get("ten_nganh", "Chọn ngành..."))
        nganh_menu = ttk.OptionMenu(container, self.sel_nganh, self.sel_nganh.get(), *list(nganh_options.keys()))
        nganh_menu.pack(fill="x", pady=5)
        
        # 2. Method Selection
        tk.Label(container, text="Phương thức xét tuyển", font=("Segoe UI", 10, "bold"), bg="white").pack(anchor="w", pady=(15, 5))
        pt_options = ["Xét điểm thi THPT", "Xét học bạ (GPA)", "Xét tuyển thẳng", "Xét điểm IELTS/Chứng chỉ quốc tế"]
        self.sel_pt = tk.StringVar(value=method.get("phuong_thuc", pt_options[0]))
        pt_menu = ttk.OptionMenu(container, self.sel_pt, self.sel_pt.get(), *pt_options)
        pt_menu.pack(fill="x", pady=5)
        
        # 3. Score Entry
        tk.Label(container, text="Điểm xét tuyển của bạn", font=("Segoe UI", 10, "bold"), bg="white").pack(anchor="w", pady=(15, 5))
        self.score_var = tk.StringVar(value=method.get("diem", "0.0"))
        score_entry = tk.Entry(container, textvariable=self.score_var, font=("Segoe UI", 11), relief="flat", highlightthickness=1, highlightbackground="#CFD8DC")
        score_entry.pack(fill="x", pady=5, ipady=8)
        
        # 4. Action Button
        btn_text = "Nộp hồ sơ ngay" if method.get("ma_ptxt") == "N/A" else "Cập nhật thay đổi"
        tk.Button(container, text=btn_text, command=lambda: self.submit_registration(nganh_options),
                  bg="#2E7D32", fg="white", font=("Segoe UI", 11, "bold"), 
                  relief="flat", cursor="hand2", pady=12).pack(fill="x", pady=(30, 0))

    def submit_registration(self, nganh_map):
        nganh_name = self.sel_nganh.get()
        if nganh_name == "Chọn ngành...":
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn ngành học bạn muốn đăng ký.")
            return
            
        payload = {
            "ma_nganh": nganh_map.get(nganh_name),
            "phuong_thuc": self.sel_pt.get(),
            "diem": self.score_var.get()
        }
        
        res = api.post("/admission/submit", payload)
        if res.get("success"):
            messagebox.showinfo("Thành công", "Hồ sơ của bạn đã được ghi nhận và đang chờ duyệt.")
            self.show_methods() # Refresh
        else:
            messagebox.showerror("Lỗi", res.get("error", "Không thể nộp hồ sơ"))

    def show_notifications(self):
        self.clear_content()
        tk.Label(self.content, text="Thông báo", font=("Segoe UI", 20, "bold"), bg=COLORS["BG"]).pack(anchor="w", pady=(0, 20))
        
        res = api.get("/thong-bao/my")
        data = res.get("data", {}).get("thong_bao", []) if res.get("success") else []
        
        if not data:
            tk.Label(self.content, text="Chưa có thông báo nào.", bg=COLORS["BG"], fg="#757575").pack(pady=40)
            return
            
        for tb in data:
            card = tk.Frame(self.content, bg="white", padx=20, pady=20)
            card.pack(fill="x", pady=10)
            setup_card(card)
            
            tk.Label(card, text=tb.get("tieu_de"), font=("Segoe UI", 13, "bold"), bg="white").pack(anchor="w")
            tk.Label(card, text=tb.get("created_at", "").split("T")[0], font=("Segoe UI", 9), bg="white", fg="#757575").pack(anchor="w", pady=5)
            tk.Label(card, text=tb.get("noi_dung"), font=("Segoe UI", 10), bg="white", justify="left", wraplength=700).pack(anchor="w", pady=10)
