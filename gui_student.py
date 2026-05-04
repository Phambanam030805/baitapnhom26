import tkinter as tk
from tkinter import ttk, messagebox
from gui_styles import StyleConfig, DashboardBase, StatCard, add_treeview_style, insert_tree_row
import excel_export


class StudentDashboard(DashboardBase):
    def __init__(self, root, user_data, db, on_logout):
        super().__init__(root, user_data, db, on_logout)
        self.sv_id = user_data[3]

        a1 = self.add_menu_item("Bảng điểm",   "📜", self.page_grade)
        a2 = self.add_menu_item("Đăng ký môn", "📝", self.page_reg)
        self.add_menu_item("Lịch sử điểm",     "🕰️", self.page_history)
        self.add_menu_item("Thông báo",         "📢", self.page_notice)
        self.add_menu_item("Hồ sơ",            "👤", self.page_profile)
        a1()   # auto-activate first item

    # ── Grade page ─────────────────────────────────────────────────────────
    def page_grade(self):
        self.header_title.config(text="Bảng điểm")
        for w in self.content_area.winfo_children(): w.destroy()

        # Stats row
        gpa  = self.db.get_gpa(self.sv_id)
        rows = self.db.get_diem_sinh_vien(self.sv_id)
        passed = sum(1 for r in rows if r[6] and r[6] >= 4.0)
        total_tc = self.db.get_tien_do_sinh_vien(self.sv_id)

        sf = tk.Frame(self.content_area, bg=StyleConfig.CONTENT_BG)
        sf.pack(fill='x', pady=(0, 18))
        StatCard(sf, "GPA Tich luy",   f"{gpa:.2f}", "Diem", StyleConfig.PRIMARY)
        StatCard(sf, "So mon hoc",      len(rows),   "Mon",  StyleConfig.INFO)
        StatCard(sf, "Mon dat",         passed,      "Dat",  StyleConfig.SUCCESS)
        StatCard(sf, "Tin chi tich luy", total_tc,   "TC",   StyleConfig.WARNING)

        # ── Filter / Export toolbar ────────────────────────────────────────
        toolbar = tk.Frame(self.content_area, bg=StyleConfig.CARD_BG, padx=16, pady=10)
        toolbar.pack(fill='x', pady=(0, 8))

        tk.Label(toolbar, text="Hoc ky:", font=StyleConfig.FONT_SM,
                 fg=StyleConfig.TEXT_GRAY, bg=StyleConfig.CARD_BG).pack(side='left')

        hoc_ky_list = self.db.get_all_hoc_ky()
        hk_names = ["Tat ca"] + [f"{r[1]} {r[2]}" for r in hoc_ky_list]
        hk_ids   = {f"{r[1]} {r[2]}": r[0] for r in hoc_ky_list}

        cb_hk = ttk.Combobox(toolbar, values=hk_names, state='readonly', width=22)
        cb_hk.current(0)
        cb_hk.pack(side='left', padx=(6, 24))

        tk.Label(toolbar, text="Tim kiem:", font=StyleConfig.FONT_SM,
                 fg=StyleConfig.TEXT_GRAY, bg=StyleConfig.CARD_BG).pack(side='left')
        ent_search = ttk.Entry(toolbar, width=22)
        ent_search.pack(side='left', padx=(6, 0))

        # Table card
        card = tk.Frame(self.content_area, bg=StyleConfig.CARD_BG, padx=20, pady=18)
        card.pack(fill='both', expand=True)
        tk.Label(card, text="Chi tiet ket qua hoc tap",
                 font=StyleConfig.FONT_BOLD, fg=StyleConfig.TEXT_GRAY,
                 bg=StyleConfig.CARD_BG).pack(anchor='w', pady=(0, 10))

        cols = ("Ma MH","Ten Mon","TC","CC","GK","CK","TB","Chu","He 4","Trang thai")
        tree = ttk.Treeview(card, columns=cols, show='headings')
        add_treeview_style(tree)
        widths = [80, 180, 40, 50, 50, 50, 60, 50, 50, 100]
        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor='center' if w < 150 else 'w')
        tree.column("Ten Mon", anchor='w')

        sb = ttk.Scrollbar(card, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        tree.pack(fill='both', expand=True)

        # Fetch & display helper
        self._grade_rows_cache = []  # cache for export

        def load_grades():
            for i in tree.get_children(): tree.delete(i)
            hk_sel = cb_hk.get()
            keyword = ent_search.get().strip().lower()

            if hk_sel == "Tat ca":
                query = """
                    SELECT m.ma_mh, m.ten_mh, m.so_tin_chi, d.diem_cc, d.diem_gk,
                           d.diem_ck, d.diem_tb, d.diem_chu, d.diem_he4, d.trang_thai
                    FROM diem d
                    JOIN lop_hoc_phan l ON d.id_lop_hp=l.id
                    JOIN mon_hoc m ON l.id_mon_hoc=m.id
                    WHERE d.id_sinh_vien=%s
                """
                self.db.cursor.execute(query, (self.sv_id,))
            else:
                hk_id = hk_ids.get(hk_sel)
                query = """
                    SELECT m.ma_mh, m.ten_mh, m.so_tin_chi, d.diem_cc, d.diem_gk,
                           d.diem_ck, d.diem_tb, d.diem_chu, d.diem_he4, d.trang_thai
                    FROM diem d
                    JOIN lop_hoc_phan l ON d.id_lop_hp=l.id
                    JOIN mon_hoc m ON l.id_mon_hoc=m.id
                    WHERE d.id_sinh_vien=%s AND l.id_hoc_ky=%s
                """
                self.db.cursor.execute(query, (self.sv_id, hk_id))

            all_rows = self.db.cursor.fetchall()
            # Filter by search keyword
            filtered = [r for r in all_rows
                        if not keyword or keyword in r[0].lower() or keyword in r[1].lower()]
            self._grade_rows_cache = filtered
            for r in filtered:
                clean = tuple(x if x is not None else '-' for x in r)
                insert_tree_row(tree, clean)
            self.set_status(f"Hien thi {len(filtered)} mon hoc")

        cb_hk.bind("<<ComboboxSelected>>", lambda e: load_grades())
        ent_search.bind("<KeyRelease>", lambda e: load_grades())

        # Export button in toolbar
        def do_export():
            sv_info = self.db.get_user_profile('student', self.sv_id)
            if not sv_info:
                messagebox.showwarning('Loi', 'Khong lay duoc thong tin sinh vien!'); return
            excel_export.export_bang_diem_ca_nhan(
                sv_info, self._grade_rows_cache, hk_filter=cb_hk.get())

        ttk.Button(toolbar, text="Xuat Excel",
                   style="Success.TButton", command=do_export).pack(side='right', padx=4)

        load_grades()
        self.set_status(f"Hien thi {len(rows)} mon hoc")


    # ── Registration page ──────────────────────────────────────────────────
    def page_reg(self):
        self.header_title.config(text="Dang ky mon hoc")
        for w in self.content_area.winfo_children(): w.destroy()

        # Toolbar with search
        toolbar = tk.Frame(self.content_area, bg=StyleConfig.PRIMARY_LIGHT, padx=16, pady=10)
        toolbar.pack(fill='x', pady=(0, 16))
        tk.Label(toolbar,
                 text="Chon lop hoc phan trong bang, sau do nhan 'Dang ky'.",
                 font=StyleConfig.FONT_SM, fg=StyleConfig.PRIMARY,
                 bg=StyleConfig.PRIMARY_LIGHT).pack(side='left')

        tk.Label(toolbar, text="Tim:", font=StyleConfig.FONT_SM,
                 fg=StyleConfig.PRIMARY, bg=StyleConfig.PRIMARY_LIGHT).pack(side='right', padx=(8,4))
        ent_search = ttk.Entry(toolbar, width=22)
        ent_search.pack(side='right')

        # Table card
        card = tk.Frame(self.content_area, bg=StyleConfig.CARD_BG, padx=20, pady=18)
        card.pack(fill='both', expand=True)

        cols = ("ID", "Ma Lop", "Ten Mon", "Giang vien", "Lich hoc")
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

        self._reg_all_data = []

        def refresh():
            self._reg_all_data = self.db.get_available_classes(self.sv_id)
            _apply_filter()

        def _apply_filter():
            for i in tree.get_children(): tree.delete(i)
            kw = ent_search.get().strip().lower()
            filtered = [r for r in self._reg_all_data
                        if not kw or kw in str(r[1]).lower() or kw in str(r[2]).lower() or kw in str(r[3]).lower()]
            for r in filtered: insert_tree_row(tree, r)
            self.set_status(f"{len(filtered)} lop co the dang ky")

        ent_search.bind("<KeyRelease>", lambda e: _apply_filter())

        def register():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Chua chon", "Vui long chon lop hoc phan!")
                return
            lop_id = tree.item(sel[0])['values'][0]
            if self.db.dang_ky_sinh_vien_vao_lop(lop_id, self.sv_id):
                messagebox.showinfo("Thanh cong", "Dang ky thanh cong!")
                refresh()
            else:
                messagebox.showerror("Loi", "Dang ky that bai. Ban co the da dang ky lop nay.")

        btn_frame = tk.Frame(card, bg=StyleConfig.CARD_BG)
        btn_frame.pack(fill='x', pady=(12, 0))
        ttk.Button(btn_frame, text="Dang ky lop da chon",
                   style="Primary.TButton", command=register).pack(side='left')
        ttk.Button(btn_frame, text="Lam moi",
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

    # ── Grade History (Tính năng mới) ──────────────────────────────────────
    def page_history(self):
        self.header_title.config(text="🕰️  Lịch sử thay đổi điểm")
        for w in self.content_area.winfo_children(): w.destroy()

        card = tk.Frame(self.content_area, bg=StyleConfig.CARD_BG, padx=20, pady=18)
        card.pack(fill='both', expand=True)

        tk.Label(card, text="Nhật ký các lần cập nhật điểm của bạn", font=StyleConfig.FONT_MD,
                 bg=StyleConfig.CARD_BG, fg=StyleConfig.TEXT_GRAY).pack(anchor='w', pady=(0,10))

        cols = ("Thời gian", "Người cập nhật", "Chi tiết thay đổi")
        tree = ttk.Treeview(card, columns=cols, show='headings')
        add_treeview_style(tree)
        for col, w in zip(cols, [160, 150, 450]):
            tree.heading(col, text=col)
            tree.column(col, width=w, anchor='w' if col=="Chi tiết thay đổi" else 'center')
        
        sb = ttk.Scrollbar(card, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        tree.pack(fill='both', expand=True)

        query = """
            SELECT n.thoi_gian, u.username, n.chi_tiet
            FROM nhat_ky n JOIN users u ON n.user_id=u.id
            WHERE n.chi_tiet LIKE %s
            ORDER BY n.id DESC
        """
        search_str = f"SV ID {self.sv_id}, %"
        self.db.cursor.execute(query, (search_str,))
        
        for r in self.db.cursor.fetchall():
            insert_tree_row(tree, r)
