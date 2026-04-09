import tkinter as tk
import sys
import os

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frontend.core.api_client import api
from frontend.views.login_view import LoginWindow
from frontend.views.dashboards.admin import AdminDashboard
from frontend.views.dashboards.student import StudentDashboard
from frontend.views.dashboards.admission_dashboard import AdmissionDashboard

class AppController:
    def __init__(self):
        self.root = None
        self.show_login()

    def show_login(self):
        if self.root:
            self.root.destroy()
        self.root = tk.Tk()
        LoginWindow(self.root, self.on_login_success)
        self.root.mainloop()

    def on_login_success(self):
        role = api.role
        user_data = api.user
        
        # Switch to Dashboard
        self.root.withdraw()
        dashboard_root = tk.Toplevel()
        dashboard_root.protocol("WM_DELETE_WINDOW", self.exit_app)
        
        if role == "admin":
            AdminDashboard(dashboard_root, self.show_login)
        elif role == "student":
            StudentDashboard(dashboard_root, self.show_login)
        elif role == "candidate":
            AdmissionDashboard(dashboard_root, self.show_login)

    def exit_app(self):
        sys.exit()

if __name__ == "__main__":
    controller = AppController()
