import tkinter as tk
from tkinter import ttk, messagebox
from gui_styles import StyleConfig, DashboardBase, StatCard, add_treeview_style, insert_tree_row


class StudentDashboard(DashboardBase):
    def __init__(self, root, user_data, db, on_logout):
        super().__init__(root, user_data, db, on_logout)
        self.sv_id = user_data[3]

        a1 = self.add_menu_item("Bảng điểm",   "📜", self.page_grade)
        a2 = self.add_menu_item("Đăng ký môn", "📝", self.page_reg)
        self.add_menu_item("Thông báo",         "📢", self.page_notice)
        a1()   # auto-activate first item

    # ── Grade page ─────────────────────────────────────────────────────────
    def page_grade(self):
        self.header_title.config(text="📜  Bảng điểm")
        for w in self.content_area.winfo_children(): w.destroy()

        # Stats row
        gpa  = self.db.get_gpa(self.sv_id)
        rows = self.db.get_diem_sinh_vien(self.sv_id)
        passed = sum(1 for r in rows if r[6] and r[6] >= 4.0)

        sf = tk.Frame(self.content_area, bg=StyleConfig.CONTENT_BG)
        sf.pack(fill='x', pady=(0, 18))
        StatCard(sf, "GPA Tích lũy",   f"{gpa:.2f}", "🏅", StyleConfig.PRIMARY)
        StatCard(sf, "Số môn học",      len(rows),   "📚", StyleConfig.INFO)
        StatCard(sf, "Môn đạt",         passed,      "✅", StyleConfig.SUCCESS)
        StatCard(sf, "Môn chưa đạt",    len(rows)-passed, "⚠️", StyleConfig.WARNING)

        # Table card
        card = tk.Frame(self.content_area, bg=StyleConfig.CARD_BG,
                        padx=20, pady=18)
        card.pack(fill='both', expand=True)
        tk.Label(card, text="Chi tiết kết quả học tập",
                 font=StyleConfig.FONT_BOLD, fg=StyleConfig.TEXT_GRAY,
                 bg=StyleConfig.CARD_BG).pack(anchor='w', pady=(0, 10))

        cols = ("Mã MH","Tên Môn","TC","CC","GK","CK","TB","Chữ","Hệ 4")
        tree = ttk.Treeview(card, columns=cols, show='headings')
        add_treeview_style(tree)
        widths = [80, 200, 50, 60, 60, 60, 70, 65, 65]
        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor='center' if w < 150 else 'w')
        tree.column("Tên Môn", anchor='w')

        sb = ttk.Scrollbar(card, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        tree.pack(fill='both', expand=True)

        for r in self.db.get_diem_sinh_vien(self.sv_id):
            # Replace None with '-' for display
            clean_r = tuple(x if x is not None else '-' for x in r)
            insert_tree_row(tree, clean_r)

        self.set_status(f"Hiển thị {len(rows)} môn học")

    # ── Registration page ──────────────────────────────────────────────────
    def page_reg(self):
        self.header_title.config(text="📝  Đăng ký môn học")
        for w in self.content_area.winfo_children(): w.destroy()

        # Instruction banner
        banner = tk.Frame(self.content_area, bg=StyleConfig.PRIMARY_LIGHT,
                          padx=16, pady=10)
        banner.pack(fill='x', pady=(0, 16))
        tk.Label(banner,
                 text="💡  Chọn lớp học phần trong bảng, sau đó nhấn 'Đăng ký'.",
                 font=StyleConfig.FONT_SM, fg=StyleConfig.PRIMARY,
                 bg=StyleConfig.PRIMARY_LIGHT).pack(anchor='w')

        # Table card
        card = tk.Frame(self.content_area, bg=StyleConfig.CARD_BG,
                        padx=20, pady=18)
        card.pack(fill='both', expand=True)

        cols = ("ID", "Mã Lớp", "Tên Môn", "Giảng viên", "Lịch học")
        tree = ttk.Treeview(card, columns=cols, show='headings', selectmode='browse')
        add_treeview_style(tree)
        widths = [50, 100, 220, 200, 160]
        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor='center' if w < 150 else 'w')
        tree.column("ID", width=50, anchor='center')

        sb = ttk.Scrollbar(card, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        tree.pack(fill='both', expand=True)

        def refresh():
            for i in tree.get_children(): tree.delete(i)
            data = self.db.get_available_classes(self.sv_id)
            for r in data:
                insert_tree_row(tree, r)
            self.set_status(f"{len(data)} lớp có thể đăng ký")

        def register():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Chưa chọn", "Vui lòng chọn lớp học phần!")
                return
            lop_id = tree.item(sel[0])['values'][0]
            if self.db.dang_ky_sinh_vien_vao_lop(lop_id, self.sv_id):
                messagebox.showinfo("Thành công", "✅  Đăng ký thành công!")
                refresh()
            else:
                messagebox.showerror("Lỗi", "Đăng ký thất bại. Bạn có thể đã đăng ký lớp này.")

        btn_frame = tk.Frame(card, bg=StyleConfig.CARD_BG)
        btn_frame.pack(fill='x', pady=(12, 0))
        ttk.Button(btn_frame, text="✅  Đăng ký lớp đã chọn",
                   style="Primary.TButton", command=register).pack(side='left')
        ttk.Button(btn_frame, text="↺ Làm mới",
                   command=refresh).pack(side='left', padx=10)
        refresh()

    # ── Notice page ────────────────────────────────────────────────────────
    def page_notice(self):
        self.header_title.config(text="📢  Thông báo")
        for w in self.content_area.winfo_children(): w.destroy()

        notices = self.db.get_all_thong_bao()
        if not notices:
            tk.Label(self.content_area,
                     text="📭  Chưa có thông báo nào",
                     font=StyleConfig.FONT_LG, fg=StyleConfig.TEXT_LIGHT,
                     bg=StyleConfig.CONTENT_BG).pack(expand=True)
            return

        canvas = tk.Canvas(self.content_area, bg=StyleConfig.CONTENT_BG,
                           highlightthickness=0)
        sb = ttk.Scrollbar(self.content_area, orient='vertical',
                           command=canvas.yview)
        frame = tk.Frame(canvas, bg=StyleConfig.CONTENT_BG)
        frame.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor='nw')
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        canvas.pack(fill='both', expand=True)

        for r in notices:
            card = tk.Frame(frame, bg=StyleConfig.CARD_BG, padx=20, pady=14)
            card.pack(fill='x', pady=5, padx=2)
            # Left accent bar
            tk.Frame(card, bg=StyleConfig.PRIMARY, width=4).pack(side='left', fill='y', padx=(0,14))
            inner = tk.Frame(card, bg=StyleConfig.CARD_BG)
            inner.pack(side='left', fill='x', expand=True)
            tk.Label(inner, text=r[1], font=StyleConfig.FONT_BOLD,
                     fg=StyleConfig.TEXT_DARK, bg=StyleConfig.CARD_BG).pack(anchor='w')
            tk.Label(inner, text=r[2], font=StyleConfig.FONT_SM,
                     fg=StyleConfig.TEXT_GRAY, bg=StyleConfig.CARD_BG,
                     wraplength=700, justify='left').pack(anchor='w', pady=(4, 0))
            tk.Label(inner, text=f"📅 {r[3]}  •  👤 {r[4]}",
                     font=StyleConfig.FONT_XS, fg=StyleConfig.TEXT_LIGHT,
                     bg=StyleConfig.CARD_BG).pack(anchor='w', pady=(6, 0))
