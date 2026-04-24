import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from gui_styles import StyleConfig


class LoginWindow:
    W, H = 1000, 700

    def __init__(self, root, on_success, db=None):
        self.root       = root
        self.on_success = on_success
        self.db         = db if db is not None else Database()

        self.root.title("Phần mềm Quản lý điểm hệ Đại học  v5.0")
        self.root.geometry(f"{self.W}x{self.H}")
        self.root.state('normal')
        self.root.resizable(False, False)
        self.root.configure(bg="#16213e")
        self.root.eval('tk::PlaceWindow . center')

        self._build()

    # ── Build ──────────────────────────────────────────────────────────────
    def _build(self):
        # Gradient canvas (left 55%)
        left_w = int(self.W * 0.55)
        canvas = tk.Canvas(self.root, width=left_w, height=self.H,
                           highlightthickness=0, bd=0)
        canvas.place(x=0, y=0)
        StyleConfig.draw_gradient(canvas, left_w, self.H, "#4f46e5", "#06b6d4")

        # Decorative circles on canvas (semi-transparent via stipple)
        canvas.create_oval(-60, -60, 220, 220,
                           fill="#7c6fe8", outline="", stipple="gray25")
        canvas.create_oval(left_w-180, self.H-180, left_w+80, self.H+80,
                           fill="#3ab8c8", outline="", stipple="gray25")
        canvas.create_oval(left_w//2-90, self.H//2-90,
                           left_w//2+90, self.H//2+90,
                           fill="#6366f1", outline="", stipple="gray12")

        # Left text content
        canvas.create_text(left_w//2, self.H//2 - 90,
                           text="🎓", font=("Segoe UI", 56), fill="white")
        canvas.create_text(left_w//2, self.H//2,
                           text="QUẢN LÝ ĐIỂM ĐẠI HỌC",
                           font=("Segoe UI", 22, "bold"), fill="white")
        canvas.create_text(left_w//2, self.H//2 + 44,
                           text="Phần mềm Quản lý điểm hệ Đại học",
                           font=("Segoe UI", 12), fill="#dde8ff")
        canvas.create_text(left_w//2, self.H//2 + 72,
                           text="Phiên bản 5.0  •  Hiện đại  •  Bảo mật",
                           font=("Segoe UI", 9), fill="#b8c8ee")

        # Feature bullets
        features = [("🔐", "Xác thực bảo mật SHA-256"),
                    ("📊", "Quản lý điểm tức thời"),
                    ("👥", "Phân quyền đa cấp")]
        for i, (ico, txt) in enumerate(features):
            y = self.H//2 + 130 + i * 36
            canvas.create_text(left_w//2 - 70, y,
                                text=ico, font=("Segoe UI", 14), fill="white", anchor='w')
            canvas.create_text(left_w//2 - 40, y,
                                text=txt, font=("Segoe UI", 10), fill="#ccd8ff", anchor='w')

        # Right panel (white)
        right_w = self.W - left_w
        right = tk.Frame(self.root, bg=StyleConfig.CARD_BG, width=right_w)
        right.place(x=left_w, y=0, width=right_w, height=self.H)

        # ── Login card ────────────────────────────────────────────────────
        card = tk.Frame(right, bg=StyleConfig.CARD_BG)
        card.place(relx=0.5, rely=0.5, anchor='center')

        # Header
        tk.Label(card, text="Chào mừng trở lại!",
                 font=("Segoe UI", 20, "bold"),
                 fg=StyleConfig.TEXT_DARK, bg=StyleConfig.CARD_BG).pack(anchor='w')
        tk.Label(card, text="Đăng nhập để tiếp tục",
                 font=StyleConfig.FONT_SM, fg=StyleConfig.TEXT_GRAY,
                 bg=StyleConfig.CARD_BG).pack(anchor='w', pady=(2, 28))

        # ── Username field ────────────────────────────────────────────────
        self._field_label(card, "👤  Tên đăng nhập")
        u_wrap = tk.Frame(card, bg=StyleConfig.BORDER, padx=1, pady=1)
        u_wrap.pack(fill='x', pady=(4, 18))
        u_inner = tk.Frame(u_wrap, bg=StyleConfig.CARD_BG)
        u_inner.pack(fill='x')
        self.ent_u = tk.Entry(u_inner, font=StyleConfig.FONT_MD,
                              bg=StyleConfig.CARD_BG, fg=StyleConfig.TEXT_DARK,
                              relief='flat', bd=6, width=26)
        self.ent_u.pack(fill='x')
        self.ent_u.insert(0, "admin")
        self._add_focus_highlight(u_wrap, self.ent_u)

        # ── Password field ────────────────────────────────────────────────
        self._field_label(card, "🔒  Mật khẩu")
        p_wrap = tk.Frame(card, bg=StyleConfig.BORDER, padx=1, pady=1)
        p_wrap.pack(fill='x', pady=(4, 28))
        p_inner = tk.Frame(p_wrap, bg=StyleConfig.CARD_BG)
        p_inner.pack(fill='x')
        self.ent_p = tk.Entry(p_inner, show="●",
                              font=StyleConfig.FONT_MD,
                              bg=StyleConfig.CARD_BG, fg=StyleConfig.TEXT_DARK,
                              relief='flat', bd=6, width=26)
        self.ent_p.pack(fill='x')
        self.ent_p.insert(0, "123")
        self._add_focus_highlight(p_wrap, self.ent_p)

        # ── Login button ──────────────────────────────────────────────────
        self.btn = tk.Button(card, text="ĐĂNG NHẬP  →",
                             font=("Segoe UI", 11, "bold"),
                             bg=StyleConfig.PRIMARY, fg="white",
                             relief='flat', bd=0, cursor='hand2',
                             height=2, width=26,
                             command=self.login)
        self.btn.pack(fill='x')
        self.btn.bind("<Enter>", lambda e: self.btn.config(bg=StyleConfig.PRIMARY_DARK))
        self.btn.bind("<Leave>", lambda e: self.btn.config(bg=StyleConfig.PRIMARY))

        # Bind Enter key
        self.root.bind("<Return>", lambda e: self.login())

        # Footer note
        tk.Label(card, text="Quên mật khẩu? Liên hệ quản trị viên",
                 font=StyleConfig.FONT_XS, fg=StyleConfig.TEXT_LIGHT,
                 bg=StyleConfig.CARD_BG).pack(pady=(16, 0))

    # ── Helpers ────────────────────────────────────────────────────────────
    def _field_label(self, parent, text):
        tk.Label(parent, text=text, font=("Segoe UI", 9, "bold"),
                 fg=StyleConfig.TEXT_GRAY, bg=StyleConfig.CARD_BG).pack(anchor='w')

    def _add_focus_highlight(self, wrapper, entry):
        def on_focus_in(e):
            wrapper.config(bg=StyleConfig.PRIMARY)
        def on_focus_out(e):
            wrapper.config(bg=StyleConfig.BORDER)
        entry.bind("<FocusIn>",  on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    # ── Login logic ────────────────────────────────────────────────────────
    def login(self):
        self.btn.config(text="Đang xác thực...", state='disabled')
        self.root.after(300, self._do_login)

    def _do_login(self):
        res = self.db.verify_login(self.ent_u.get().strip(),
                                   self.ent_p.get().strip())
        if res:
            self.on_success(res)
        else:
            messagebox.showerror("Đăng nhập thất bại",
                                 "❌  Tên đăng nhập hoặc mật khẩu không đúng.\n"
                                 "Tài khoản có thể đã bị khóa.")
        self.btn.config(text="ĐĂNG NHẬP  →", state='normal')
