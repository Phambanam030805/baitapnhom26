import tkinter as tk
from tkinter import ttk, messagebox
from gui_styles import StyleConfig, DashboardBase, StatCard, add_treeview_style, insert_tree_row


class TeacherDashboard(DashboardBase):
    def __init__(self, root, user_data, db, on_logout):
        super().__init__(root, user_data, db, on_logout)
        self.gv_id = user_data[3]

        a1 = self.add_menu_item("Nhập điểm",  "📝", self.page_grade)
        self.add_menu_item("Thống kê",         "📊", self.page_stats)
        self.add_menu_item("Thông báo",        "📢", self.page_notice)
        a1()

    # ── Grade entry page ───────────────────────────────────────────────────
    def page_grade(self):
        self.header_title.config(text="📝  Nhập điểm sinh viên")
        for w in self.content_area.winfo_children(): w.destroy()

        # ── Top: class selector ────────────────────────────────────────────
        top = tk.Frame(self.content_area, bg=StyleConfig.CARD_BG, padx=20, pady=14)
        top.pack(fill='x', pady=(0, 16))

        tk.Label(top, text="Chọn lớp học phần:",
                 font=StyleConfig.FONT_BOLD, fg=StyleConfig.TEXT_GRAY,
                 bg=StyleConfig.CARD_BG).pack(side='left', padx=(0, 10))

        cb = ttk.Combobox(top, width=45, state="readonly",
                          font=StyleConfig.FONT_MD)
        cb.pack(side='left', padx=(0, 16))

        # Status badge next to combobox
        self.lhp_status = tk.Label(top, text="", font=StyleConfig.FONT_SM,
                                   bg=StyleConfig.CARD_BG)
        self.lhp_status.pack(side='left')

        # ── Middle: student table ──────────────────────────────────────────
        mid = tk.Frame(self.content_area, bg=StyleConfig.CARD_BG,
                       padx=20, pady=16)
        mid.pack(fill='both', expand=True)
        tk.Label(mid, text="Danh sách sinh viên & điểm",
                 font=StyleConfig.FONT_BOLD, fg=StyleConfig.TEXT_GRAY,
                 bg=StyleConfig.CARD_BG).pack(anchor='w', pady=(0, 10))

        cols = ("ID", "MSV", "Họ tên", "CC", "GK", "CK", "TB", "Xếp loại")
        tree = ttk.Treeview(mid, columns=cols, show='headings', selectmode='browse')
        add_treeview_style(tree)
        widths = [50, 90, 220, 70, 70, 70, 80, 90]
        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w,
                        anchor='center' if col != "Họ tên" else 'w')

        sb = ttk.Scrollbar(mid, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        tree.pack(fill='both', expand=True)

        # ── Bottom: score entry form ───────────────────────────────────────
        bot = tk.Frame(self.content_area, bg=StyleConfig.CARD_BG,
                       padx=20, pady=16)
        bot.pack(fill='x', pady=(16, 0))

        tk.Label(bot, text="Nhập điểm cho sinh viên được chọn:",
                 font=StyleConfig.FONT_BOLD, fg=StyleConfig.TEXT_GRAY,
                 bg=StyleConfig.CARD_BG).grid(row=0, column=0, columnspan=8,
                                              sticky='w', pady=(0, 10))

        ents = []
        for i, (lbl, tip) in enumerate([
            ("CC (Chuyên cần)", "0–10"),
            ("GK (Giữa kỳ)",   "0–10"),
            ("CK (Cuối kỳ)",   "0–10"),
        ]):
            tk.Label(bot, text=lbl, font=StyleConfig.FONT_SM,
                     fg=StyleConfig.TEXT_GRAY,
                     bg=StyleConfig.CARD_BG).grid(row=1, column=i*3, sticky='w', padx=(0,4))
            e = ttk.Entry(bot, width=8, font=StyleConfig.FONT_MD)
            e.grid(row=1, column=i*3+1, padx=(0, 16))
            ents.append(e)

        # Auto-fill when a row is selected
        def on_select(evt):
            sel = tree.selection()
            if not sel: return
            vals = tree.item(sel[0])['values']
            for i, e in enumerate(ents):
                e.delete(0, tk.END)
                e.insert(0, vals[3 + i] if vals[3 + i] else "")

        tree.bind("<<TreeviewSelect>>", on_select)

        def save():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Chưa chọn", "Vui lòng chọn sinh viên!"); return
            if not cb.get():
                messagebox.showwarning("Chưa chọn lớp", "Vui lòng chọn lớp học phần!"); return
            try:
                cc = float(ents[0].get() or 0)
                gk = float(ents[1].get() or 0)
                ck = float(ents[2].get() or 0)
                if not all(0 <= x <= 10 for x in [cc, gk, ck]):
                    raise ValueError
            except ValueError:
                messagebox.showerror("Lỗi", "Điểm phải là số từ 0 đến 10!"); return

            sv_id  = tree.item(sel[0])['values'][0]
            lhp_id = self.lhp_map[cb.get()]
            ok, msg = self.db.update_diem(sv_id, lhp_id, cc, gk, ck, self.user_data[0])
            if ok:
                self.set_status(f"✅ Đã lưu điểm SV #{sv_id}", ok=True)
                load_sv(None)
            else:
                messagebox.showerror("Lỗi", msg)

        ttk.Button(bot, text="💾  Lưu điểm",
                   style="Primary.TButton", command=save).grid(
            row=1, column=9, padx=(10, 0))

        # ── Wire up combobox ───────────────────────────────────────────────
        def load_sv(evt):
            for i in tree.get_children(): tree.delete(i)
            if not cb.get(): return
            lhp_id = self.lhp_map[cb.get()]
            data = self.db.get_bang_diem_lop(lhp_id)
            for r in data:
                insert_tree_row(tree, r)
            # Status badge
            self.db.cursor.execute("SELECT status FROM lop_hoc_phan WHERE id=?", (lhp_id,))
            row = self.db.cursor.fetchone()
            if row:
                if row[0] == 'open':
                    self.lhp_status.config(text="🟢 Đang mở", fg=StyleConfig.SUCCESS)
                else:
                    self.lhp_status.config(text="🔴 Đã khóa", fg=StyleConfig.DANGER)
            self.set_status(f"Lớp có {len(data)} sinh viên")

        lhps = self.db.get_lhp_by_giang_vien(self.gv_id)
        self.lhp_map = {f"{r[1]}  —  {r[2]}  ({r[3]})": r[0] for r in lhps}
        cb['values'] = list(self.lhp_map.keys())
        cb.bind("<<ComboboxSelected>>", load_sv)

        if cb['values']:
            cb.current(0)
            load_sv(None)

    # ── Stats page ─────────────────────────────────────────────────────────
    def page_stats(self):
        self.header_title.config(text="📊  Thống kê giảng dạy")
        for w in self.content_area.winfo_children(): w.destroy()

        data = self.db.get_teacher_stats(self.gv_id)

        # Summary stat cards
        total_sv  = sum(r[2] for r in data if r[2])
        total_dat = sum(r[3] for r in data if r[3])
        total_rot = sum(r[4] for r in data if r[4])
        sf = tk.Frame(self.content_area, bg=StyleConfig.CONTENT_BG)
        sf.pack(fill='x', pady=(0, 18))
        StatCard(sf, "Tổng sinh viên", total_sv,  "👥", StyleConfig.PRIMARY)
        StatCard(sf, "SV đạt",         total_dat, "✅", StyleConfig.SUCCESS)
        StatCard(sf, "SV rớt",         total_rot, "❌", StyleConfig.DANGER)
        pct = f"{total_dat/total_sv*100:.0f}%" if total_sv else "—"
        StatCard(sf, "Tỷ lệ qua môn", pct,       "📈", StyleConfig.INFO)

        # Table
        card = tk.Frame(self.content_area, bg=StyleConfig.CARD_BG,
                        padx=20, pady=16)
        card.pack(fill='both', expand=True)
        tk.Label(card, text="Chi tiết theo lớp học phần",
                 font=StyleConfig.FONT_BOLD, fg=StyleConfig.TEXT_GRAY,
                 bg=StyleConfig.CARD_BG).pack(anchor='w', pady=(0, 10))

        cols = ("Tên môn", "Mã lớp HP", "Số SV", "Đạt", "Rớt")
        tree = ttk.Treeview(card, columns=cols, show='headings')
        add_treeview_style(tree)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=180 if col in ("Tên môn",) else 110, anchor='center')
        tree.column("Tên môn", anchor='w')

        sb = ttk.Scrollbar(card, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        tree.pack(fill='both', expand=True)

        for r in data:
            insert_tree_row(tree, r)

    # ── Notice page ────────────────────────────────────────────────────────
    def page_notice(self):
        self.header_title.config(text="📢  Thông báo")
        for w in self.content_area.winfo_children(): w.destroy()

        notices = self.db.get_all_thong_bao()
        if not notices:
            tk.Label(self.content_area, text="📭  Chưa có thông báo nào",
                     font=StyleConfig.FONT_LG, fg=StyleConfig.TEXT_LIGHT,
                     bg=StyleConfig.CONTENT_BG).pack(expand=True)
            return

        for r in notices:
            card = tk.Frame(self.content_area, bg=StyleConfig.CARD_BG,
                            padx=0, pady=0)
            card.pack(fill='x', pady=5)
            bar = tk.Frame(card, bg=StyleConfig.INFO, width=5)
            bar.pack(side='left', fill='y')
            inner = tk.Frame(card, bg=StyleConfig.CARD_BG, padx=16, pady=12)
            inner.pack(side='left', fill='x', expand=True)
            tk.Label(inner, text=r[1], font=StyleConfig.FONT_BOLD,
                     fg=StyleConfig.TEXT_DARK, bg=StyleConfig.CARD_BG).pack(anchor='w')
            tk.Label(inner, text=r[2], font=StyleConfig.FONT_SM,
                     fg=StyleConfig.TEXT_GRAY, bg=StyleConfig.CARD_BG,
                     wraplength=800).pack(anchor='w', pady=(4, 0))
            tk.Label(inner, text=f"📅 {r[3]}  •  👤 {r[4]}",
                     font=StyleConfig.FONT_XS, fg=StyleConfig.TEXT_LIGHT,
                     bg=StyleConfig.CARD_BG).pack(anchor='w', pady=(6, 0))
