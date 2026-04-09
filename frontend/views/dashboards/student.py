import tkinter as tk
from tkinter import ttk, messagebox
from frontend.core.api_client import api
from frontend.core.styles import COLORS, setup_card
from frontend.views.dashboards.base_dashboard import BaseDashboard

class StudentDashboard(BaseDashboard):
    def __init__(self, root, on_logout):
        self.on_logout_callback = on_logout
        # Set ma_sv BEFORE super().__init__
        self.ma_sv = api.user.get("ma_sv")
        self.nav_buttons = {}
        super().__init__(root, "Cổng Thông Tin Sinh Viên")

    def setup_ui(self):
        try:
            # Header (Reverted to Blue)
            header = tk.Frame(self.root, bg=COLORS["PRIMARY"], height=70)
            header.pack(fill="x")
            header.pack_propagate(False)

            tk.Label(header, text="CỔNG THÔNG TIN SINH VIÊN",
                    font=("Segoe UI", 18, "bold"),
                    bg=COLORS["PRIMARY"], fg="white").pack(side="left", padx=30)

            user_info_frame = tk.Frame(header, bg=COLORS["PRIMARY"])
            user_info_frame.pack(side="right", padx=30)
            
            user_name = api.user.get('ho_ten', 'Sinh viên')
            tk.Label(user_info_frame, text=user_name,
                    font=("Segoe UI", 10, "bold"), bg=COLORS["PRIMARY"], fg="white").pack(side="left", padx=10)

            tk.Button(user_info_frame, text="Đăng xuất", 
                     command=lambda: self.logout(self.on_logout_callback),
                     font=("Segoe UI", 9, "bold"),
                     bg=COLORS["DANGER"], fg="white", relief="flat",
                     padx=15, pady=5, cursor="hand2").pack(side="right")

            # Main Layout
            main_frame = tk.Frame(self.root, bg=COLORS["BG"])
            main_frame.pack(fill="both", expand=True)

            # Sidebar (Reverted to Dark)
            sidebar = tk.Frame(main_frame, bg=COLORS["NAV_BG"], width=240)
            sidebar.pack(side="left", fill="y")
            sidebar.pack_propagate(False)

            tk.Label(sidebar, text="DANH MỤC", font=("Segoe UI", 8, "bold"),
                    bg=COLORS["NAV_BG"], fg="#94a3b8").pack(pady=(30, 10), padx=25, anchor="w")

            nav_items = [
                ("👤 Thông tin cá nhân", self.show_profile, "profile"),
                ("📊 Bảng điểm học tập", self.show_transcript, "transcript"),
                ("💰 Học phí - Lệ phí", self.show_fees, "fees"),
                ("🔔 Thông báo", self.show_notifications, "notifications"),
            ]

            for text, cmd, key in nav_items:
                btn = self.create_nav_button(sidebar, text, cmd)
                btn.pack(fill="x", padx=10, pady=2)
                self.nav_buttons[key] = btn

            # Content Area with Scrollbar (Inherited)
            self.setup_scrollable_area(main_frame)
            self.content.configure(padx=40, pady=30)

            self.set_active_nav("profile")
            self.show_profile()
        except Exception as e:
            messagebox.showerror("Lỗi Giao diện", f"Lỗi khởi tạo: {e}")

    def set_active_nav(self, key):
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.configure(bg=COLORS["NAV_HOVER"], fg="white")
            else:
                btn.configure(bg=COLORS["NAV_BG"], fg="#cbd5e1")

    def show_profile(self):
        self.clear_content()
        self.set_active_nav("profile")
        if not self.ma_sv: return

        result = api.get(f"/sinh-vien/{self.ma_sv}")
        if "error" in result or not result.get("success"):
            self.show_error_state("Không thể tải thông tin sinh viên")
            return

        data = result["data"]
        sv = data.get("sinh_vien", {})
        
        # Profile Header
        header_card = tk.Frame(self.content, bg="white", pady=30)
        header_card.pack(fill="x", pady=(0, 25))
        setup_card(header_card)
        
        # Avatar Circle
        avatar_frame = tk.Frame(header_card, bg=COLORS["PRIMARY"], width=90, height=90)
        avatar_frame.pack(side="left", padx=(30, 25))
        avatar_frame.pack_propagate(False)
        
        initials = "".join([n[0] for n in sv.get("ho_ten", "S").split()[:2]]).upper()
        tk.Label(avatar_frame, text=initials, font=("Segoe UI", 28, "bold"), 
                bg=COLORS["PRIMARY"], fg="white").pack(expand=True)

        # Name & Info Details
        name_info = tk.Frame(header_card, bg="white")
        name_info.pack(side="left", fill="y")
        
        tk.Label(name_info, text=sv.get("ho_ten", "N/A"), font=("Segoe UI", 20, "bold"), 
                bg="white", fg=COLORS["TEXT_PRIMARY"]).pack(anchor="w")
        
        badge_frame = tk.Frame(name_info, bg="white")
        badge_frame.pack(anchor="w", pady=5)
        
        tk.Label(badge_frame, text=f"MSSV: {sv.get('ma_sv')}", font=("Segoe UI", 10), 
                bg="white", fg=COLORS["TEXT_SECONDARY"]).pack(side="left")
        
        status_raw = sv.get("trang_thai", "active")
        status_map = {
            "active": "Đang học",
            "suspended": "Bảo lưu",
            "dropped": "Nghỉ học"
        }
        status_text = status_map.get(status_raw, status_raw)
        
        status_colors = {
            "Đang học": ("#f0fdf4", COLORS["SUCCESS"]),
            "Bảo lưu": ("#fffbeb", "#d97706"),
            "Nghỉ học": ("#fef2f2", COLORS["DANGER"])
        }
        bg_col, fg_col = status_colors.get(status_text, ("#f1f5f9", COLORS["TEXT_SECONDARY"]))

        tk.Label(badge_frame, text=status_text, font=("Segoe UI", 8, "bold"), 
                bg=bg_col, fg=fg_col, padx=8, pady=2).pack(side="left", padx=10)

        # Main Info Grid
        info_container = tk.Frame(self.content, bg=COLORS["BG"])
        info_container.pack(fill="both", expand=True)

        # Calculation SV năm mấy
        adm_date_str = sv.get("ngay_nhap_hoc")
        try:
            if adm_date_str:
                # Expecting 'YYYY-MM-DD'
                year_admitted = int(str(adm_date_str).split('-')[0])
            else:
                # Fallback to ma_sv parsing
                ma_sv = sv.get("ma_sv", "SV23")
                if ma_sv == "SV001" or not ma_sv[2:4].isdigit():
                    year_admitted = 2023
                else:
                    year_admitted = 2000 + int(ma_sv[2:4])
            
            # Use 2026 as current year per user request
            current_year = 2026
            student_year = current_year - year_admitted 
            if student_year < 1: student_year = 1
            year_text = f"Năm {student_year}"
        except:
            year_text = "N/A"


        # Basic Info
        pers_card = self.create_card(info_container, "Thông tin cá nhân")
        self.add_field(pers_card, "Họ và tên", sv.get("ho_ten"), 0, 0)
        self.add_field(pers_card, "Ngày sinh", sv.get("ngay_sinh"), 0, 1)
        self.add_field(pers_card, "Email", sv.get("email"), 1, 0)
        self.add_field(pers_card, "Số điện thoại", sv.get("so_dien_thoai"), 1, 1)


        # Academic info
        acad_card = self.create_card(info_container, "Thông tin học vụ")
        
        # Data extraction with fallbacks
        ng_name = (data.get("nganh") or {}).get("ten_nganh") or "Chưa cập nhật"
        lp_name = (data.get("lop") or {}).get("ten_lop") or "Chưa xếp lớp"
        kh_name = (data.get("khoa") or {}).get("ten_khoa") or "Đại học"
        
        self.add_field(acad_card, "Ngành đào tạo", ng_name, 0, 0)
        self.add_field(acad_card, "Lớp sinh hoạt", lp_name, 0, 1)
        self.add_field(acad_card, "Trình độ đào tạo", "Đại học chính quy", 1, 0)
        self.add_field(acad_card, "Sinh viên năm", year_text, 1, 1)
        self.add_field(acad_card, "Khoa", kh_name, 2, 0)
        self.add_field(acad_card, "Trạng thái", "Đang học", 2, 1)

    def show_transcript(self):
        self.clear_content()
        self.set_active_nav("transcript")
        if not self.ma_sv: return
        
        self.canvas.yview_moveto(0) # Reset scroll position

        result = api.get(f"/hoc-tap/diem/{self.ma_sv}")
        print(f"DEBUG: Transcript API Result: {result.get('success')}, Grouped Data Keys: {list(result.get('grouped_data', {}).keys())}")
        
        tk.Label(self.content, text="KẾT QUẢ HỌC TẬP", 
                font=("Segoe UI", 20, "bold"), bg=COLORS["BG"], fg=COLORS["TEXT_PRIMARY"]).pack(pady=(0, 20), anchor="w")

        if "error" in result or not result.get("success"):
            self.show_error_state("Chưa có dữ liệu bảng điểm")
            return

        # GPA Stats Cards
        stats_frame = tk.Frame(self.content, bg=COLORS["BG"])
        stats_frame.pack(fill="x", pady=(0, 25))
        
        def add_stat(parent, label, value, color=COLORS["PRIMARY"]):
            card = tk.Frame(parent)
            card.pack(side="left", padx=(0, 20))
            setup_card(card)
            inner = tk.Frame(card, bg="white", padx=25, pady=15)
            inner.pack()
            tk.Label(inner, text=label, font=("Segoe UI", 8, "bold"), bg="white", fg=COLORS["TEXT_SECONDARY"]).pack()
            tk.Label(inner, text=value, font=("Segoe UI", 18, "bold"), bg="white", fg=color).pack()

        add_stat(stats_frame, "GPA HỆ 10", f"{result.get('gpa10', 0.0):.2f}")
        add_stat(stats_frame, "GPA HỆ 4", f"{result.get('gpa4', 0.0):.2f}", COLORS["SECONDARY"])
        
        rank = result.get('rank', 'N/A')
        rank_color = COLORS["SUCCESS"] if rank in ['Xuất sắc', 'Giỏi'] else COLORS["WARNING"]
        add_stat(stats_frame, "XẾP LOẠI", rank, rank_color)

        # Transcript Tables grouped by Semester
        grouped_data = result.get("grouped_data") if isinstance(result, dict) else None
        if not grouped_data:
            keys = list(result.get("grouped_data", {}).keys()) if isinstance(result, dict) else "N/A"
            self.show_error_state(f"Chưa có kết quả học tập cho kỳ này.\n(DEBUG: Keys found: {keys})")
            return

        # Create a scrollable container for multiple tables
        scroll_container = tk.Frame(self.content, bg=COLORS["BG"])
        scroll_container.pack(fill="both", expand=True)

        for hk, items in grouped_data.items():
            section_label = tk.Label(scroll_container, text=f"📅 {hk}", 
                                   font=("Segoe UI", 11, "bold"), bg=COLORS["BG"], fg=COLORS["PRIMARY"])
            section_label.pack(anchor="w", pady=(15, 10))
            
            table_card = tk.Frame(scroll_container)
            table_card.pack(fill="x", pady=(0, 15))
            setup_card(table_card)

            inner_table = tk.Frame(table_card, bg="white", padx=10, pady=10)
            inner_table.pack(fill="x")

            style = ttk.Style()
            style.theme_use("clam")
            style.configure("Custom.Treeview", background="white", rowheight=35, font=("Segoe UI", 9))
            style.configure("Custom.Treeview.Heading", font=("Segoe UI", 9, "bold"), background="#f8fafc", relief="flat")
            
            columns = ("ma_mh", "ten_mh", "tin_chi", "diem10", "diem4", "status")
            tree = ttk.Treeview(inner_table, columns=columns, show="headings", style="Custom.Treeview", height=len(items))
            
            tree.heading("ma_mh", text="MÃ MÔN")
            tree.heading("ten_mh", text="TÊN MÔN HỌC")
            tree.heading("tin_chi", text="TÍN CHỈ")
            tree.heading("diem10", text="ĐIỂM (10)")
            tree.heading("diem4", text="ĐIỂM (4)")
            tree.heading("status", text="TRẠNG THÁI")
            
            tree.column("ma_mh", width=80, anchor="center")
            tree.column("ten_mh", width=250, anchor="w")
            tree.column("tin_chi", width=80, anchor="center")
            tree.column("diem10", width=80, anchor="center")
            tree.column("diem4", width=80, anchor="center")
            tree.column("status", width=120, anchor="center")

            for row in items:
                d10 = row["diem"]
                d4 = row.get("diem4", 0.0)
                status = "Đạt" if d10 >= 4.0 else "Học lại"
                tree.insert("", "end", values=(row["ma_mh"], row["ten_mh"], row["so_tin_chi"], d10, f"{d4:.2f}", status))

            tree.pack(fill="x")

    def show_fees(self):
        self.clear_content()
        self.set_active_nav("fees")
        if not self.ma_sv: return
        
        self.canvas.yview_moveto(0) # Reset scroll position

        result = api.get(f"/hoc-tap/tuition/{self.ma_sv}")
        print(f"DEBUG: Tuition API Result: {result.get('success')}")

        data = result.get("data", {}) if result.get("success") else {}

        header_frame = tk.Frame(self.content, bg=COLORS["BG"])
        header_frame.pack(fill="x", pady=(0, 25))
        tk.Label(header_frame, text="HỌC PHÍ & LỆ PHÍ", 
                font=("Segoe UI", 20, "bold"), bg=COLORS["BG"], fg=COLORS["TEXT_PRIMARY"]).pack(side="left")
        
        tk.Button(header_frame, text="📥 Xuất hóa đơn (PDF)", font=("Segoe UI", 9, "bold"),
                 bg=COLORS["NAV_BG"], fg="white", relief="flat", padx=15, pady=5, cursor="hand2").pack(side="right")

        semesters = data.get("semesters", []) if isinstance(data, dict) else []
        if not semesters:
            self.show_error_state("Chưa có thông tin học phí.")
            return

        for sem in semesters:
            sem_name = sem.get("semester_name", "Học kỳ")
            tk.Label(self.content, text=f"📂 {sem_name}", font=("Segoe UI", 11, "bold"), 
                    bg=COLORS["BG"], fg=COLORS["TEXT_PRIMARY"]).pack(anchor="w", pady=(10, 10))

            invoice_card = tk.Frame(self.content)
            invoice_card.pack(fill="x", pady=(0, 20))
            setup_card(invoice_card)
            
            inner_invoice = tk.Frame(invoice_card, bg="white", padx=30, pady=25)
            inner_invoice.pack(fill="x")

            # Money Summary Row
            summary_row = tk.Frame(inner_invoice, bg="#f8fafc", padx=20, pady=15)
            summary_row.pack(fill="x", pady=(0, 20))
            
            def add_money(parent, label, value, color=COLORS["TEXT_PRIMARY"]):
                f = tk.Frame(parent, bg="#f8fafc")
                f.pack(side="left", expand=True)
                tk.Label(f, text=label, font=("Segoe UI", 8), bg="#f8fafc", fg=COLORS["TEXT_SECONDARY"]).pack()
                tk.Label(f, text=value, font=("Segoe UI", 14, "bold"), bg="#f8fafc", fg=color).pack(pady=(2, 0))

            add_money(summary_row, "TỔNG HỌC PHÍ", f"{sem.get('total_tuition', 0):,} đ")
            add_money(summary_row, "ĐÃ THANH TOÁN", f"{sem.get('paid', 0):,} đ", COLORS["SUCCESS"])
            add_money(summary_row, "CÒN LẠI", f"{sem.get('remaining', 0):,} đ", COLORS["DANGER"] if sem.get('remaining',0) > 0 else COLORS["TEXT_SECONDARY"])

            # Table Listing for this semester
            details = sem.get("details", [])
            for d in details:
                row = tk.Frame(inner_invoice, bg="white", pady=8)
                row.pack(fill="x")
                tk.Label(row, text=d["name"], bg="white", font=("Segoe UI", 9)).pack(side="left")
                tk.Label(row, text=f"{d['amount']:,} đ", bg="white", font=("Segoe UI", 9, "bold"), width=15, anchor="e").pack(side="right")
                
                st_color = COLORS["SUCCESS"] if "Đã" in d["status"] else COLORS["WARNING"]
                tk.Label(row, text=d["status"], font=("Segoe UI", 8), fg=st_color, bg="white", width=12).pack(side="right", padx=10)
                tk.Frame(inner_invoice, height=1, bg="#f1f5f9").pack(fill="x")

            tk.Label(inner_invoice, text=f"Hạn nộp: {sem.get('deadline', 'N/A')}", 
                    font=("Segoe UI", 8, "italic"), bg="white", fg=COLORS["TEXT_SECONDARY"]).pack(anchor="w", pady=(15, 0))

    def show_notifications(self):
        self.clear_content()
        self.set_active_nav("notifications")
        
        tk.Label(self.content, text="THÔNG BÁO TỪ NHÀ TRƯỜNG", 
                font=("Segoe UI", 20, "bold"), bg=COLORS["BG"], fg=COLORS["TEXT_PRIMARY"]).pack(pady=(0, 20), anchor="w")

        result = api.get("/thong-bao/my")
        if not result.get("success") or not result.get("data"):
            self.show_error_state("Chưa có thông báo nào dành cho bạn.")
            return

        tbs = result["data"]["thong_bao"]
        if not tbs:
            self.show_error_state("Chưa có thông báo nào dành cho bạn.")
            return

        for tb in tbs:
            self.render_notification_card(tb)

    def render_notification_card(self, tb):
        card = tk.Frame(self.content, bg="white", padx=25, pady=25)
        card.pack(fill="x", pady=(0, 15))
        setup_card(card)

        # Header with Title and Date
        header = tk.Frame(card, bg="white")
        header.pack(fill="x")

        title_col = COLORS["PRIMARY"]
        if not tb.get("da_doc"):
            title_col = "#1A73E8"
            # Unread Badge
            tk.Label(header, text="NEW", font=("Segoe UI", 8, "bold"), bg="#E8F0FE", fg="#1A73E8", padx=8).pack(side="right")

        tk.Label(header, text=tb.get("tieu_de"), font=("Segoe UI", 13, "bold"), bg="white", fg=title_col).pack(side="left")
        
        # Content
        content_txt = tb.get("noi_dung", "")
        tk.Label(card, text=content_txt, font=("Segoe UI", 10), bg="white", fg=COLORS["TEXT_PRIMARY"], 
                justify="left", wraplength=800).pack(anchor="w", pady=15)

        # Footer
        footer = tk.Frame(card, bg="white")
        footer.pack(fill="x")
        
        date_str = tb.get("created_at", "").split("T")[0]
        tk.Label(footer, text=f"📅 Ngày đăng: {date_str}", font=("Segoe UI", 8), bg="white", fg=COLORS["TEXT_SECONDARY"]).pack(side="left")

        if not tb.get("da_doc"):
            tk.Button(footer, text="Đánh dấu đã đọc", font=("Segoe UI", 8, "bold"), bg="#f8fafc", fg=COLORS["PRIMARY"],
                     relief="flat", cursor="hand2", command=lambda: self.mark_notification_read(tb.get("ma_tb"))).pack(side="right")

    def mark_notification_read(self, ma_tb):
        res = api.post(f"/thong-bao/read/{ma_tb}")
        if res.get("success"):
            self.show_notifications() # Refresh

    def show_error_state(self, msg):
        err_frame = tk.Frame(self.content, bg=COLORS["BG"])
        err_frame.pack(expand=True)
        tk.Label(err_frame, text="⚠️", font=("Segoe UI", 36), bg=COLORS["BG"], fg="#94a3b8").pack()
        tk.Label(err_frame, text=msg, font=("Segoe UI", 11), bg=COLORS["BG"], fg="#64748b").pack(pady=10)

    def clear_content(self):
        """Clear central content area and reset scroll (Inherited)"""
        super().clear_content()

    def create_card(self, parent, title):
        c = tk.Frame(parent, bg="white", padx=25, pady=25)
        c.pack(fill="x", pady=(0, 20))
        setup_card(c)
        tk.Label(c, text=title, font=("Segoe UI", 13, "bold"), 
                bg="white", fg=COLORS["TEXT_PRIMARY"]).pack(anchor="w", pady=(0, 20))
        
        content_f = tk.Frame(c, bg="white")
        content_f.pack(fill="both", expand=True)
        return content_f

    def add_field(self, parent, label, value, row, col, width=30):
        f = tk.Frame(parent, bg="white")
        f.grid(row=row, column=col, sticky="w", padx=15, pady=10)
        tk.Label(f, text=label, font=("Segoe UI", 9), 
                bg="white", fg=COLORS["TEXT_SECONDARY"]).pack(anchor="w")
        
        val_label = tk.Label(f, text=str(value or "N/A"), font=("Segoe UI", 10, "bold"), 
                           bg="white", fg=COLORS["TEXT_PRIMARY"], width=width, anchor="w")
        val_label.pack(pady=5)
        tk.Frame(f, height=1, bg=COLORS["BORDER"], width=width*8).pack(fill="x")
