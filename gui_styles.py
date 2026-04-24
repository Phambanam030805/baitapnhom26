import tkinter as tk
from tkinter import ttk
from datetime import datetime


class StyleConfig:
    # ── Sidebar ────────────────────────────────────────────────────────────
    SIDEBAR_BG    = "#16213e"
    SIDEBAR_ITEM  = "#1a2850"
    SIDEBAR_TEXT  = "#8899cc"

    # ── Primary / Accent ───────────────────────────────────────────────────
    PRIMARY       = "#4f46e5"
    PRIMARY_DARK  = "#3730a3"
    PRIMARY_LIGHT = "#e0e7ff"

    # ── Status ─────────────────────────────────────────────────────────────
    SUCCESS = "#10b981"
    DANGER  = "#ef4444"
    WARNING = "#f59e0b"
    INFO    = "#06b6d4"

    # ── Neutral ────────────────────────────────────────────────────────────
    CONTENT_BG = "#f1f5f9"
    CARD_BG    = "#ffffff"
    BORDER     = "#e2e8f0"
    SHADOW     = "#cbd5e1"
    TEXT_DARK  = "#1e293b"
    TEXT_GRAY  = "#64748b"
    TEXT_LIGHT = "#94a3b8"

    # ── Backward compat ────────────────────────────────────────────────────
    NAVY_DARK    = "#3730a3"
    NAVY_MED     = "#4f46e5"
    SIDEBAR_HOVER = "#1a2850"
    WHITE        = "#ffffff"
    TEXT_MAIN    = "#1e293b"
    TEXT_SUB     = "#64748b"

    # ── Fonts ──────────────────────────────────────────────────────────────
    FONT_FAMILY = "Segoe UI"
    FONT_XS     = ("Segoe UI", 8)
    FONT_SM     = ("Segoe UI", 9)
    FONT_MD     = ("Segoe UI", 10)
    FONT_BOLD   = ("Segoe UI", 10, "bold")
    FONT_LG     = ("Segoe UI", 13, "bold")
    FONT_XL     = ("Segoe UI", 18, "bold")
    FONT_TITLE  = ("Segoe UI", 22, "bold")

    @staticmethod
    def draw_gradient(canvas, width, height, c1, c2):
        r1,g1,b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
        r2,g2,b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
        for i in range(height):
            t = i / max(height-1, 1)
            r = int(r1+(r2-r1)*t)
            g = int(g1+(g2-g1)*t)
            b = int(b1+(b2-b1)*t)
            canvas.create_line(0, i, width, i, fill=f"#{r:02x}{g:02x}{b:02x}")

    @staticmethod
    def apply(root):
        style = ttk.Style(root)
        style.theme_use('clam')

        # ── Treeview ───────────────────────────────────────────────────────
        style.configure("Treeview",
            font=StyleConfig.FONT_MD, rowheight=36,
            fieldbackground=StyleConfig.CARD_BG,
            background=StyleConfig.CARD_BG,
            foreground=StyleConfig.TEXT_DARK,
            borderwidth=0, relief='flat')
        style.configure("Treeview.Heading",
            font=StyleConfig.FONT_BOLD,
            background=StyleConfig.PRIMARY,
            foreground="white", padding=10, relief='flat')
        style.map("Treeview",
            background=[('selected', StyleConfig.PRIMARY_LIGHT)],
            foreground=[('selected', StyleConfig.PRIMARY)])
        style.map("Treeview.Heading",
            background=[('active', StyleConfig.PRIMARY_DARK)])

        # ── Buttons ────────────────────────────────────────────────────────
        style.configure("TButton",
            font=StyleConfig.FONT_BOLD, padding=[14, 8],
            relief='flat', borderwidth=0)
        for name, bg, hover in [
            ("Primary", StyleConfig.PRIMARY,  "#3730a3"),
            ("Danger",  StyleConfig.DANGER,   "#dc2626"),
            ("Success", StyleConfig.SUCCESS,  "#059669"),
            ("Warning", StyleConfig.WARNING,  "#d97706"),
            ("Info",    StyleConfig.INFO,     "#0891b2"),
        ]:
            style.configure(f"{name}.TButton", background=bg, foreground="white")
            style.map(f"{name}.TButton",
                      background=[('active', hover), ('pressed', hover)])

        # ── Entry / Combobox ───────────────────────────────────────────────
        style.configure("TEntry",
            padding=[8, 6], relief='flat',
            fieldbackground="white", borderwidth=1)
        style.configure("TCombobox", padding=[8, 6], relief='flat')
        style.configure("TSeparator", background=StyleConfig.BORDER)
        style.configure("TScrollbar",
            background=StyleConfig.BORDER,
            troughcolor=StyleConfig.CONTENT_BG,
            borderwidth=0, relief='flat', arrowsize=12)
        return style


# ── Utility widgets ────────────────────────────────────────────────────────────

def add_treeview_style(tree):
    """Apply alternating row colors to a Treeview."""
    tree.tag_configure('odd',  background="#f8faff")
    tree.tag_configure('even', background=StyleConfig.CARD_BG)


def insert_tree_row(tree, values):
    tag = 'odd' if len(tree.get_children()) % 2 else 'even'
    tree.insert("", "end", values=values, tags=(tag,))


class StatCard:
    """Small KPI card."""
    def __init__(self, parent, title, value, icon, color):
        outer = tk.Frame(parent, bg=StyleConfig.SHADOW, padx=1, pady=1)
        outer.pack(side='left', padx=8, fill='y')
        self.frame = tk.Frame(outer, bg=StyleConfig.CARD_BG, padx=18, pady=14)
        self.frame.pack(fill='both', expand=True)

        # Icon badge
        badge = tk.Frame(self.frame, bg=color, width=46, height=46)
        badge.pack(side='left', padx=(0, 14))
        badge.pack_propagate(False)
        tk.Label(badge, text=icon, font=("Segoe UI", 18),
                 bg=color, fg='white').place(relx=.5, rely=.5, anchor='center')

        # Text
        right = tk.Frame(self.frame, bg=StyleConfig.CARD_BG)
        right.pack(side='left', fill='y')
        self.val_lbl = tk.Label(right, text=str(value),
                                font=StyleConfig.FONT_LG,
                                bg=StyleConfig.CARD_BG, fg=StyleConfig.TEXT_DARK)
        self.val_lbl.pack(anchor='w')
        tk.Label(right, text=title, font=StyleConfig.FONT_SM,
                 bg=StyleConfig.CARD_BG, fg=StyleConfig.TEXT_GRAY).pack(anchor='w')

    def update(self, value):
        self.val_lbl.config(text=str(value))


# ── Dashboard Base ─────────────────────────────────────────────────────────────

class DashboardBase:
    def __init__(self, root, user_data, db, on_logout):
        self.root      = root
        self.user_data = user_data
        self.db        = db
        self.on_logout = on_logout
        self._menu_parts: list = []   # (frame, indicator, inner, icon_lbl, txt_lbl)

        StyleConfig.apply(self.root)
        self.root.geometry("1440x900")
        self.root.minsize(1200, 700)
        self.root.resizable(True, True)
        self.root.state('zoomed')
        self.root.configure(bg=StyleConfig.SIDEBAR_BG)

        self._build_sidebar()
        self._build_main()

    # ── Sidebar ────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg=StyleConfig.SIDEBAR_BG, width=240)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)

        # Logo
        logo = tk.Frame(self.sidebar, bg=StyleConfig.SIDEBAR_BG, pady=22)
        logo.pack(fill='x')
        tk.Label(logo, text="🎓", font=("Segoe UI", 30),
                 bg=StyleConfig.SIDEBAR_BG, fg=StyleConfig.PRIMARY).pack()
        tk.Label(logo, text="QUẢN LÝ ĐIỂM ĐẠI HỌC", font=("Segoe UI", 10, "bold"),
                 bg=StyleConfig.SIDEBAR_BG, fg="white").pack()

        # Divider
        tk.Frame(self.sidebar, bg=StyleConfig.SIDEBAR_ITEM, height=1).pack(fill='x', padx=20, pady=4)

        # Menu area
        self.menu_frame = tk.Frame(self.sidebar, bg=StyleConfig.SIDEBAR_BG)
        self.menu_frame.pack(fill='x', pady=8)

        # Bottom user card
        self._build_user_card()

    def _build_user_card(self):
        role_color = {'admin': '#f59e0b', 'teacher': '#10b981', 'student': '#06b6d4'}
        role_name  = {'admin': 'Quản trị viên', 'teacher': 'Giảng viên', 'student': 'Sinh viên'}
        role = self.user_data[2]
        color = role_color.get(role, StyleConfig.PRIMARY)

        bottom = tk.Frame(self.sidebar, bg=StyleConfig.SIDEBAR_ITEM, padx=16, pady=12)
        bottom.pack(side='bottom', fill='x')
        tk.Frame(self.sidebar, bg="#0a1628", height=1).pack(side='bottom', fill='x')

        # Avatar
        av = tk.Label(bottom, text=self.user_data[1][0].upper(),
                      font=("Segoe UI", 12, "bold"),
                      bg=color, fg="white", width=3, height=1)
        av.pack(side='left', padx=(0, 10))

        info = tk.Frame(bottom, bg=StyleConfig.SIDEBAR_ITEM)
        info.pack(side='left', fill='x', expand=True)
        tk.Label(info, text=self.user_data[1], font=StyleConfig.FONT_BOLD,
                 bg=StyleConfig.SIDEBAR_ITEM, fg="white").pack(anchor='w')
        tk.Label(info, text=role_name.get(role, role), font=StyleConfig.FONT_XS,
                 bg=StyleConfig.SIDEBAR_ITEM, fg=StyleConfig.SIDEBAR_TEXT).pack(anchor='w')

        logout_btn = tk.Label(bottom, text="⏻", font=("Segoe UI", 16),
                              bg=StyleConfig.SIDEBAR_ITEM, fg="#ef4444", cursor='hand2')
        logout_btn.pack(side='right')
        logout_btn.bind("<Button-1>", lambda e: self.on_logout())

    # ── Main area ──────────────────────────────────────────────────────────
    def _build_main(self):
        main = tk.Frame(self.root, bg=StyleConfig.CONTENT_BG)
        main.pack(side='left', fill='both', expand=True)

        # Header
        self.header = tk.Frame(main, bg=StyleConfig.CARD_BG, height=60)
        self.header.pack(fill='x')
        self.header.pack_propagate(False)
        tk.Frame(main, bg=StyleConfig.BORDER, height=1).pack(fill='x')

        self.header_title = tk.Label(self.header, text="",
                                     font=StyleConfig.FONT_LG,
                                     bg=StyleConfig.CARD_BG, fg=StyleConfig.TEXT_DARK)
        self.header_title.pack(side='left', padx=24, pady=12)

        # Logout Button in Header
        logout_btn = tk.Button(self.header, text="Đăng xuất", 
                               font=StyleConfig.FONT_BOLD,
                               bg=StyleConfig.CARD_BG, fg=StyleConfig.DANGER,
                               relief='flat', cursor='hand2', command=self.on_logout)
        logout_btn.pack(side='right', padx=24)

        self._clock = tk.Label(self.header, font=StyleConfig.FONT_SM,
                               bg=StyleConfig.CARD_BG, fg=StyleConfig.TEXT_GRAY)
        self._clock.pack(side='right', padx=(0, 20))
        self._tick()

        # Content
        self.content_area = tk.Frame(main, bg=StyleConfig.CONTENT_BG, padx=24, pady=20)
        self.content_area.pack(fill='both', expand=True)

        # Status bar
        tk.Frame(main, bg=StyleConfig.BORDER, height=1).pack(fill='x', side='bottom')
        sb = tk.Frame(main, bg=StyleConfig.CARD_BG, height=26)
        sb.pack(fill='x', side='bottom')
        sb.pack_propagate(False)
        self.status_lbl = tk.Label(sb, text="● Sẵn sàng",
                                   font=StyleConfig.FONT_XS,
                                   bg=StyleConfig.CARD_BG, fg=StyleConfig.SUCCESS)
        self.status_lbl.pack(side='left', padx=16)
        tk.Label(sb, text="Phần mềm Quản lý điểm hệ Đại học  v5.0",
                 font=StyleConfig.FONT_XS,
                 bg=StyleConfig.CARD_BG, fg=StyleConfig.TEXT_LIGHT).pack(side='right', padx=16)

    def _tick(self):
        self._clock.config(text=f"🕐  {datetime.now().strftime('%d/%m/%Y   %H:%M:%S')}")
        self.root.after(1000, self._tick)

    def set_status(self, text, ok=True):
        color = StyleConfig.SUCCESS if ok else StyleConfig.DANGER
        self.status_lbl.config(text=f"● {text}", fg=color)

    # ── Menu item ──────────────────────────────────────────────────────────
    def add_menu_item(self, text, icon, cmd):
        idx = len(self._menu_parts)

        wrap = tk.Frame(self.menu_frame, bg=StyleConfig.SIDEBAR_BG, cursor='hand2')
        wrap.pack(fill='x', padx=10, pady=2)

        indicator = tk.Frame(wrap, bg=StyleConfig.SIDEBAR_BG, width=4)
        indicator.pack(side='left', fill='y')

        inner = tk.Frame(wrap, bg=StyleConfig.SIDEBAR_BG, padx=12, pady=9)
        inner.pack(side='left', fill='both', expand=True)

        ico = tk.Label(inner, text=icon, font=("Segoe UI", 13),
                       bg=StyleConfig.SIDEBAR_BG, fg=StyleConfig.SIDEBAR_TEXT)
        ico.pack(side='left')
        txt = tk.Label(inner, text=f"  {text}", font=StyleConfig.FONT_MD,
                       bg=StyleConfig.SIDEBAR_BG, fg=StyleConfig.SIDEBAR_TEXT)
        txt.pack(side='left')

        self._menu_parts.append((wrap, indicator, inner, ico, txt))

        def activate():
            self._set_active(idx)
            cmd()

        def on_enter(e):
            if self._get_active() != idx:
                for w in [wrap, inner, ico, txt]:
                    w.config(bg=StyleConfig.SIDEBAR_ITEM)
                ico.config(fg="white"); txt.config(fg="white")

        def on_leave(e):
            if self._get_active() != idx:
                for w in [wrap, inner, ico, txt]:
                    w.config(bg=StyleConfig.SIDEBAR_BG)
                ico.config(fg=StyleConfig.SIDEBAR_TEXT)
                txt.config(fg=StyleConfig.SIDEBAR_TEXT)

        for w in [wrap, inner, ico, txt]:
            w.bind("<Button-1>", lambda e, f=activate: f())
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

        return activate   # caller can fire it to auto-activate

    def _get_active(self):
        return getattr(self, '_active_idx', -1)

    def _set_active(self, idx):
        self._active_idx = idx
        for i, (wrap, ind, inner, ico, txt) in enumerate(self._menu_parts):
            if i == idx:
                wrap.config(bg=StyleConfig.SIDEBAR_ITEM)
                ind.config(bg=StyleConfig.PRIMARY)
                inner.config(bg=StyleConfig.SIDEBAR_ITEM)
                ico.config(bg=StyleConfig.SIDEBAR_ITEM, fg="white")
                txt.config(bg=StyleConfig.SIDEBAR_ITEM, fg="white")
            else:
                wrap.config(bg=StyleConfig.SIDEBAR_BG)
                ind.config(bg=StyleConfig.SIDEBAR_BG)
                inner.config(bg=StyleConfig.SIDEBAR_BG)
                ico.config(bg=StyleConfig.SIDEBAR_BG, fg=StyleConfig.SIDEBAR_TEXT)
                txt.config(bg=StyleConfig.SIDEBAR_BG, fg=StyleConfig.SIDEBAR_TEXT)
