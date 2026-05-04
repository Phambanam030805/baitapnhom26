import tkinter as tk
from tkinter import ttk, messagebox
from gui_styles import StyleConfig, DashboardBase, StatCard, add_treeview_style, insert_tree_row
import excel_export


class TeacherDashboard(DashboardBase):
    def __init__(self, root, user_data, db, on_logout):
        super().__init__(root, user_data, db, on_logout)
        self.gv_id = user_data[3]

        a1 = self.add_menu_item("Nhập điểm",  "📝", self.page_grade)
        self.add_menu_item("Thống kê",         "📊", self.page_stats)
        self.add_menu_item("Thông báo",        "📢", self.page_notice)
        self.add_menu_item("Hồ sơ",            "👤", self.page_profile)
        a1()

    # ── Grade entry page ───────────────────────────────────────────────────
    def page_grade(self):
        self.header_title.config(text="📝  Nhập điểm sinh viên")
        for w in self.content_area.winfo_children(): w.destroy()

        # ── Top: class selector ────────────────────────────────────────────
        top = tk.Frame(self.content_area, bg=StyleConfig.CARD_BG, padx=20, pady=14)
        top.pack(fill='x', pady=(0, 16))

        tk.Label(top, text="Chon lop hoc phan:",
                 font=StyleConfig.FONT_BOLD, fg=StyleConfig.TEXT_GRAY,
                 bg=StyleConfig.CARD_BG).pack(side='left', padx=(0, 10))

        cb = ttk.Combobox(top, width=45, state="readonly",
                          font=StyleConfig.FONT_MD)
        cb.pack(side='left', padx=(0, 16))

        # Status badge
        self.lhp_status = tk.Label(top, text="", font=StyleConfig.FONT_SM,
                                   bg=StyleConfig.CARD_BG)
        self.lhp_status.pack(side='left')

        # Search box on the right
        tk.Label(top, text="Tim SV:", font=StyleConfig.FONT_SM,
                 fg=StyleConfig.TEXT_GRAY, bg=StyleConfig.CARD_BG).pack(side='right', padx=(8,4))
        ent_sv_search = ttk.Entry(top, width=20)
        ent_sv_search.pack(side='right')

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

        def lock_class():
            if not cb.get(): return
            lhp_id = self.lhp_map[cb.get()]
            if messagebox.askyesno("Xác nhận", "Sau khi khóa, bạn sẽ không thể sửa điểm nữa. Bạn chắc chắn chứ?"):
                if self.db.lock_lop_hoc_phan(lhp_id):
                    self.set_status("🔒 Đã khóa điểm lớp học phần", ok=True)
                    load_sv(None)
                else:
                    messagebox.showerror("Lỗi", "Không thể khóa lớp!")

        btn_save = ttk.Button(bot, text="Luu diem", style="Primary.TButton", command=save)
        btn_save.grid(row=1, column=9, padx=(10, 0))

        btn_lock = ttk.Button(bot, text="Khoa diem", style="Danger.TButton", command=lock_class)
        btn_lock.grid(row=1, column=10, padx=(10, 0))

        # Export button
        def do_export():
            if not cb.get():
                messagebox.showwarning('Chua chon lop', 'Vui long chon lop hoc phan truoc!'); return
            lhp_id = self.lhp_map[cb.get()]
            # Get full class info
            self.db.cursor.execute(
                "SELECT l.ma_lop_hp, m.ten_mh, g.ho_ten, CONCAT(h.ten_hoc_ky,' ',h.nam_hoc) "
                "FROM lop_hoc_phan l "
                "JOIN mon_hoc m ON l.id_mon_hoc=m.id "
                "JOIN giang_vien g ON l.id_giang_vien=g.id "
                "JOIN hoc_ky h ON l.id_hoc_ky=h.id "
                "WHERE l.id=%s", (lhp_id,))
            lop_info = self.db.cursor.fetchone()
            # Get grade data with trang_thai
            self.db.cursor.execute(
                "SELECT s.id, s.ma_sv, s.ho_ten, d.diem_cc, d.diem_gk, d.diem_ck, "
                "d.diem_tb, d.diem_chu, d.trang_thai "
                "FROM diem d JOIN sinh_vien s ON d.id_sinh_vien=s.id "
                "WHERE d.id_lop_hp=%s", (lhp_id,))
            rows = self.db.cursor.fetchall()
            if lop_info:
                excel_export.export_bang_diem_lop(lop_info, rows)

        ttk.Button(bot, text="Xuat Excel",
                   style="Success.TButton", command=do_export).grid(row=1, column=11, padx=(10, 0))

        # ── Wire up combobox ───────────────────────────────────────────────
        self._lhp_data_cache = []

        def load_sv(evt):
            for i in tree.get_children(): tree.delete(i)
            if not cb.get(): return
            lhp_id = self.lhp_map[cb.get()]
            self._lhp_data_cache = self.db.get_bang_diem_lop(lhp_id)
            _apply_sv_filter()
            # Status badge
            self.db.cursor.execute("SELECT status FROM lop_hoc_phan WHERE id=%s", (lhp_id,))
            row = self.db.cursor.fetchone()
            if row:
                if row[0] == 'open':
                    self.lhp_status.config(text="Dang mo", fg=StyleConfig.SUCCESS)
                    btn_save.state(['!disabled'])
                    btn_lock.state(['!disabled'])
                else:
                    self.lhp_status.config(text="Da khoa", fg=StyleConfig.DANGER)
                    btn_save.state(['disabled'])
                    btn_lock.state(['disabled'])
            self.set_status(f"Lop co {len(self._lhp_data_cache)} sinh vien")

        def _apply_sv_filter():
            for i in tree.get_children(): tree.delete(i)
            kw = ent_sv_search.get().strip().lower()
            filtered = [r for r in self._lhp_data_cache
                        if not kw or kw in str(r[1]).lower() or kw in str(r[2]).lower()]
            for r in filtered: insert_tree_row(tree, r)

        ent_sv_search.bind("<KeyRelease>", lambda e: _apply_sv_filter())

        lhps = self.db.get_lhp_by_giang_vien(self.gv_id)
        self.lhp_map = {f"{r[1]}  -  {r[2]}  ({r[3]})": r[0] for r in lhps}
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

        # Main Layout: Left (Table), Right (Distribution + Alerts)
        main_frame = tk.Frame(self.content_area, bg=StyleConfig.CONTENT_BG)
        main_frame.pack(fill='both', expand=True)

        left = tk.Frame(main_frame, bg=StyleConfig.CARD_BG, padx=20, pady=16)
        left.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(left, text="Chi tiết theo lớp học phần",
                 font=StyleConfig.FONT_BOLD, fg=StyleConfig.TEXT_GRAY,
                 bg=StyleConfig.CARD_BG).pack(anchor='w', pady=(0, 10))

        cols = ("Tên môn", "Mã lớp HP", "Số SV", "Đạt", "Rớt")
        tree = ttk.Treeview(left, columns=cols, show='headings')
        add_treeview_style(tree)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor='center')
        tree.column("Tên môn", width=180, anchor='w')

        sb = ttk.Scrollbar(left, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        tree.pack(fill='both', expand=True)

        for r in data:
            insert_tree_row(tree, r)

        # Right column for specific alerts
        right = tk.Frame(main_frame, bg=StyleConfig.CONTENT_BG, width=300)
        right.pack(side='right', fill='both')

        # Grade Distribution Card
        dist_card = tk.Frame(right, bg=StyleConfig.CARD_BG, padx=16, pady=14)
        dist_card.pack(fill='x', pady=(0, 10))
        tk.Label(dist_card, text="Phổ điểm (Toàn bộ)", font=StyleConfig.FONT_BOLD, 
                 bg=StyleConfig.CARD_BG, fg=StyleConfig.TEXT_DARK).pack(anchor='w')
        
        # Simple text-based bar chart
        all_diem = []
        for r in self.db.get_lhp_by_giang_vien(self.gv_id):
            dist = self.db.get_thong_ke_lop(r[0])
            all_diem.append(dist)
        
        totals = {'A':0, 'B':0, 'C':0, 'D':0, 'F':0}
        for d in all_diem:
            for k, v in d.items(): 
                if k in totals: totals[k] += v
        
        max_v = max(totals.values()) if any(totals.values()) else 1
        for char, count in totals.items():
            row = tk.Frame(dist_card, bg=StyleConfig.CARD_BG, pady=2)
            row.pack(fill='x')
            tk.Label(row, text=f"{char}: {count}", font=StyleConfig.FONT_SM, width=5, 
                     bg=StyleConfig.CARD_BG, anchor='w').pack(side='left')
            bar_w = int((count/max_v) * 150)
            if bar_w < 1: bar_w = 1
            tk.Frame(row, bg=StyleConfig.INFO, width=bar_w, height=12).pack(side='left', padx=5)

        # Cấm thi Alerts
        alert_card = tk.Frame(right, bg=StyleConfig.CARD_BG, padx=16, pady=14)
        alert_card.pack(fill='both', expand=True)
        tk.Label(alert_card, text="⚠️ Sinh viên bị cấm thi", font=StyleConfig.FONT_BOLD, 
                 bg=StyleConfig.CARD_BG, fg=StyleConfig.DANGER).pack(anchor='w')
        
        alert_scroll = tk.Frame(alert_card, bg=StyleConfig.CARD_BG)
        alert_scroll.pack(fill='both', expand=True, pady=10)
        
        cam_thi_all = []
        for r in self.db.get_lhp_by_giang_vien(self.gv_id):
            list_ct = self.db.get_ds_cam_thi(r[0])
            for ct in list_ct: cam_thi_all.append((ct[0], ct[1], r[1])) # MSV, HoTen, MaLHP
        
        if not cam_thi_all:
            tk.Label(alert_scroll, text="Không có sinh viên nào", font=StyleConfig.FONT_XS, 
                     bg=StyleConfig.CARD_BG, fg=StyleConfig.TEXT_LIGHT).pack()
        else:
            for ct in cam_thi_all[:8]: # Show top 8
                tk.Label(alert_scroll, text=f"• {ct[1]} ({ct[2]})", font=StyleConfig.FONT_XS, 
                         bg=StyleConfig.CARD_BG, fg=StyleConfig.TEXT_GRAY, anchor='w').pack(fill='x')
            if len(cam_thi_all) > 8:
                tk.Label(alert_scroll, text=f"... và {len(cam_thi_all)-8} SV khác", font=StyleConfig.FONT_XS, 
                         bg=StyleConfig.CARD_BG, fg=StyleConfig.TEXT_LIGHT).pack()

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
