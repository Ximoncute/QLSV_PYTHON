COLORS = {
    "PRIMARY": "#2563eb",      # modern Blue
    "SECONDARY": "#4f46e5",    # Indigo
    "SUCCESS": "#10b981",      # Emerald
    "DANGER": "#ef4444",       # Rose
    "WARNING": "#f59e0b",      # Amber
    "BG": "#f8fafc",           # Slate 50
    "CARD_BG": "#ffffff",
    "NAV_BG": "#1e293b",       # Slate 800
    "NAV_HOVER": "#334155",    # Slate 700
    "TEXT_PRIMARY": "#0f172a", # Slate 900
    "TEXT_SECONDARY": "#64748b",# Slate 500
    "BORDER": "#e2e8f0"        # Slate 200
}

DARK_THEME = {
    "PRIMARY_BG": "#121212",
    "CARD_BG": "#1e1e1e",
    "BORDER": "#333333",
    "TEXT_PRIMARY": "#ffffff",
    "TEXT_SECONDARY": "#9ca3af",
    "FIELD_BG": "#262626",
    "ACCENT": "#10b981"         # Emerald for badges
}

def center_window(win, width, height):
    """Căn giữa cửa sổ trên màn hình"""
    win.update_idletasks()
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")

def style_button(btn, bg_key="PRIMARY", fg="white"):
    btn.configure(
        bg=COLORS[bg_key], 
        fg=fg,
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        cursor="hand2"
    )

def style_entry(entry):
    """Style cho ô nhập liệu"""
    entry.configure(
        font=("Segoe UI", 10),
        relief="flat",
        highlightthickness=1,
        highlightbackground=COLORS["BORDER"],
        highlightcolor=COLORS["PRIMARY"]
    )

def setup_card(frame):
    """Setup card visual appearance without internal padding in configure"""
    frame.configure(
        bg=COLORS["CARD_BG"],
        highlightbackground=COLORS["BORDER"],
        highlightthickness=1,
        bd=0,
        relief="flat"
    )
