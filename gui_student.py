import tkinter as tk
from tkinter import ttk, messagebox
from gui_styles import StyleConfig, DashboardBase, StatCard, add_treeview_style, insert_tree_row, ScrollableFrame
import excel_export


class StudentDashboard(DashboardBase):
    def __init__(self, root, user_data, db, on_logout):
        super().__init__(root, user_data, db, on_logout)
        self.sv_id = user_data[3]

        a1 = self.add_menu_item("Bảng điểm",   "📜", self.page_grade)
        a2 = self.add_menu_item("Đăng ký môn", "📝", self.page_reg)
        self.add_menu_item("Điểm danh",       "📅", self.page_attendance)
        self.add_menu_item("Lịch sử điểm",     "🕰️", self.page_history)
        self.add_menu_item("Thông báo",         "📢", self.page_notice)
        self.add_menu_item("Hồ sơ",            "👤", self.page_profile)
        a1()   # auto-activate first item

    # ── Grade page ─────────────────────────────────────────────────────────
    def page_grade(self):
        self.header_icon.config(text="📜")
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

        cols = ("Học kỳ","Mã MH","Tên Môn","TC","CC","GK","CK","TB","Chữ","Hệ 4","Trạng thái")
        tree = ttk.Treeview(card, columns=cols, show='headings')
        add_treeview_style(tree)
        widths = [130, 90, 200, 45, 55, 55, 55, 65, 55, 55, 110]
        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, minwidth=w, anchor='center' if w < 180 else 'w')
        tree.column("Học kỳ", anchor='w')
        tree.column("Tên Môn", anchor='w')

        sb = ttk.Scrollbar(card, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        tree.pack(fill='both', expand=True)

        # ── TÍNH NĂNG MỚI: BIỂU ĐỒ GPA TREND ──
        from gui_styles import ModernChart
        query_trend = """
            SELECT CONCAT(h.ten_hoc_ky, ' ', h.nam_hoc) as ky, 
                   ROUND(SUM(d.diem_he4 * m.so_tin_chi) / SUM(m.so_tin_chi), 2) as gpa_ky
            FROM diem d
            JOIN lop_hoc_phan l ON d.id_lop_hp = l.id
            JOIN mon_hoc m ON l.id_mon_hoc = m.id
            JOIN hoc_ky h ON l.id_hoc_ky = h.id
            WHERE d.id_sinh_vien = %s
            GROUP BY h.id
            HAVING gpa_ky IS NOT NULL
            ORDER BY h.nam_hoc, h.ten_hoc_ky
        """
        self.db.cursor.execute(query_trend, (self.sv_id,))
        trend_data = self.db.cursor.fetchall()
        if trend_data:
            ModernChart.draw_line_chart(self.content_area, "Xu hướng GPA qua các kỳ học", trend_data, color=StyleConfig.PRIMARY)

        # Fetch & display helper
        self._grade_rows_cache = []  # cache for export

        def load_grades():
            for i in tree.get_children(): tree.delete(i)
            hk_sel = cb_hk.get()
            keyword = ent_search.get().strip().lower()

            if hk_sel == "Tat ca":
                query = """
                    SELECT CONCAT(h.ten_hoc_ky, ' ', h.nam_hoc),
                           m.ma_mh, m.ten_mh, m.so_tin_chi, d.diem_cc, d.diem_gk,
                           d.diem_ck, d.diem_tb, d.diem_chu, d.diem_he4, d.trang_thai
                    FROM diem d
                    JOIN lop_hoc_phan l ON d.id_lop_hp=l.id
                    JOIN mon_hoc m ON l.id_mon_hoc=m.id
                    JOIN hoc_ky h ON l.id_hoc_ky=h.id
                    WHERE d.id_sinh_vien=%s
                    ORDER BY h.nam_hoc, h.ten_hoc_ky, m.ma_mh
                """
                self.db.cursor.execute(query, (self.sv_id,))
            else:
                hk_id = hk_ids.get(hk_sel)
                query = """
                    SELECT CONCAT(h.ten_hoc_ky, ' ', h.nam_hoc),
                           m.ma_mh, m.ten_mh, m.so_tin_chi, d.diem_cc, d.diem_gk,
                           d.diem_ck, d.diem_tb, d.diem_chu, d.diem_he4, d.trang_thai
                    FROM diem d
                    JOIN lop_hoc_phan l ON d.id_lop_hp=l.id
                    JOIN mon_hoc m ON l.id_mon_hoc=m.id
                    JOIN hoc_ky h ON l.id_hoc_ky=h.id
                    WHERE d.id_sinh_vien=%s AND l.id_hoc_ky=%s
                    ORDER BY m.ma_mh
                """
                self.db.cursor.execute(query, (self.sv_id, hk_id))

            all_rows = self.db.cursor.fetchall()
            # Filter by search keyword (tìm theo mã MH [1] hoặc tên môn [2])
            filtered = [r for r in all_rows
                        if not keyword or keyword in str(r[1]).lower() or keyword in str(r[2]).lower()]
            self._grade_rows_cache = filtered
            for r in filtered:
                # Format Trạng thái for display
                row_list = list(r)
                st = str(row_list[10]).strip() if row_list[10] else ""
                if st == 'Cam thi':
                    row_list[10] = "⚠️ Cấm thi"
                elif st == 'Du dieu kien':
                    row_list[10] = "✅ Đủ ĐK thi"
                elif st == 'Đang học' or st == "":
                    row_list[10] = "Đang học"
                
                clean = tuple(x if x is not None else '-' for x in row_list)
                insert_tree_row(tree, clean)
            self.set_status(f"Hiển thị {len(filtered)} môn học")

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
        self.header_icon.config(text="📝")
        self.header_title.config(text="Đăng ký môn học")
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

        cols = ("ID", "Mã Lớp", "Tên Môn", "Giảng viên", "Lịch học")
        tree = ttk.Treeview(card, columns=cols, show='headings', selectmode='browse')
        add_treeview_style(tree)
        widths = [55, 120, 270, 240, 200]
        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, width=w, minwidth=w, anchor='center' if w < 180 else 'w')
        tree.column("ID", width=55, anchor='center')

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
                messagebox.showwarning("Chưa chọn", "Vui lòng chọn lớp học phần!")
                return
            lop_id = tree.item(sel[0])['values'][0]
            
            # --- TÍNH NĂNG MỚI: KIỂM TRA TRÙNG LỊCH ---
            has_conflict, msg = self.db.check_schedule_conflict(self.sv_id, lop_id)
            if has_conflict:
                messagebox.showerror("Trùng lịch học", f"⚠️ KHÔNG THỂ ĐĂNG KÝ:\n\n{msg}")
                return
            
            ok, msg = self.db.dang_ky_sinh_vien_vao_lop(lop_id, self.sv_id)
            if ok:
                messagebox.showinfo("Thành công", msg)
                refresh()
            else:
                messagebox.showerror("Lỗi", msg)

        btn_frame = tk.Frame(card, bg=StyleConfig.CARD_BG)
        btn_frame.pack(fill='x', pady=(12, 0))
        ttk.Button(btn_frame, text="Dang ky lop da chon",
                   style="Primary.TButton", command=register).pack(side='left')
        ttk.Button(btn_frame, text="Lam moi",
                   command=refresh).pack(side='left', padx=10)
        refresh()

    # ── Notice page ────────────────────────────────────────────────────────
    def page_notice(self):
        self.header_icon.config(text="📢")
        self.header_title.config(text="Thông báo")
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
        self.header_icon.config(text="🕰️")
        self.header_title.config(text="Lịch sử thay đổi điểm")
        for w in self.content_area.winfo_children(): w.destroy()

        card = tk.Frame(self.content_area, bg=StyleConfig.CARD_BG, padx=20, pady=18)
        card.pack(fill='both', expand=True)

        tk.Label(card, text="Nhật ký các lần cập nhật điểm của bạn", font=StyleConfig.FONT_BOLD,
                 bg=StyleConfig.CARD_BG, fg=StyleConfig.TEXT_GRAY).pack(anchor='w', pady=(0,10))

        cols = ("Thời gian", "Người cập nhật", "Chi tiết thay đổi")
        tree = ttk.Treeview(card, columns=cols, show='headings')
        add_treeview_style(tree)
        for col, w in zip(cols, [200, 180, 560]):
            tree.heading(col, text=col)
            tree.column(col, width=w, minwidth=w, anchor='w' if w > 150 else 'center')
        
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

    # ── Attendance page (Premium V2) ──────────────────────────────────────────────────
    def page_attendance(self):
        self.header_icon.config(text="📅")
        self.header_title.config(text="Theo dõi Chuyên cần & Điều kiện thi")
        for w in self.content_area.winfo_children(): w.destroy()

        summary = self.db.get_student_attendance_summary(self.sv_id)
        if not summary:
            tk.Label(self.content_area, text="📭 Bạn chưa tham gia lớp học phần nào", 
                     font=StyleConfig.FONT_LG, bg=StyleConfig.CONTENT_BG, fg=StyleConfig.TEXT_GRAY).pack(expand=True)
            return

        # Container with padding
        dash = tk.Frame(self.content_area, bg=StyleConfig.CONTENT_BG, padx=25, pady=20)
        dash.pack(fill='both', expand=True)

        # 1. Top Stats Row (Overview)
        stats_row = tk.Frame(dash, bg=StyleConfig.CONTENT_BG)
        stats_row.pack(fill='x', pady=(0, 25))
        
        total_nghi = sum(r[3] + r[4] for r in summary)
        at_risk = sum(1 for r in summary if (r[3]/r[5] > 0.15))
        
        StatCard(stats_row, "Tổng số buổi nghỉ", total_nghi, "📅", StyleConfig.INFO)
        StatCard(stats_row, "Môn học nguy cơ", at_risk, "⚠️", StyleConfig.DANGER if at_risk > 0 else StyleConfig.SUCCESS)
        StatCard(stats_row, "Số môn đang học", len(summary), "📚", StyleConfig.PRIMARY)

        # 2. Main Body: [Left: Course Cards | Right: Detailed Log]
        body = tk.Frame(dash, bg=StyleConfig.CONTENT_BG)
        body.pack(fill='both', expand=True)

        # Left Column: Course Cards Scrollable
        left_col = tk.Frame(body, bg=StyleConfig.CONTENT_BG, width=380)
        left_col.pack(side='left', fill='y', padx=(0, 20))
        left_col.pack_propagate(False)
        
        tk.Label(left_col, text="DANH SÁCH MÔN HỌC", font=("Segoe UI", 9, "bold"), 
                 bg=StyleConfig.CONTENT_BG, fg=StyleConfig.TEXT_GRAY).pack(anchor='w', pady=(0, 10))
        
        card_scroll = ScrollableFrame(left_col, bg=StyleConfig.CONTENT_BG)
        card_scroll.pack(fill='both', expand=True)
        card_container = card_scroll.scrollable_frame
        
        # Force a minimum width for the scrollable area
        tk.Frame(card_container, width=350, height=1, bg=StyleConfig.CONTENT_BG).pack()

        # Right Column: Details Log
        right_col = tk.Frame(body, bg=StyleConfig.CARD_BG)
        right_col.pack(side='left', fill='both', expand=True)
        # Border for right_col
        tk.Frame(right_col, bg=StyleConfig.PRIMARY, height=4).pack(fill='x')
        
        detail_inner = tk.Frame(right_col, bg=StyleConfig.CARD_BG, padx=20, pady=20)
        detail_inner.pack(fill='both', expand=True)

        def show_detail(lhp_id, ten_mon, nk, tong):
            for w in detail_inner.winfo_children(): w.destroy()
            
            # Sub-header & Exam Status
            sh = tk.Frame(detail_inner, bg=StyleConfig.CARD_BG)
            sh.pack(fill='x', pady=(0, 20))
            
            left_info = tk.Frame(sh, bg=StyleConfig.CARD_BG)
            left_info.pack(side='left')
            tk.Label(left_info, text=f"NHẬT KÝ ĐIỂM DANH: ", font=StyleConfig.FONT_SM, bg=StyleConfig.CARD_BG, fg=StyleConfig.TEXT_GRAY).pack(side='left')
            tk.Label(left_info, text=ten_mon.upper(), font=StyleConfig.FONT_BOLD, bg=StyleConfig.CARD_BG, fg=StyleConfig.PRIMARY).pack(side='left')

            # Exam Eligibility Badge
            ratio = (nk / tong) * 100 if tong > 0 else 0
            limit = int(tong * 0.2)
            remains = limit - nk
            
            status_color = StyleConfig.SUCCESS if ratio <= 20 else StyleConfig.DANGER
            status_text = "ĐỦ ĐIỀU KIỆN THI" if ratio <= 20 else "BỊ CẤM THI"
            
            badge = tk.Frame(sh, bg=status_color, padx=12, pady=4)
            badge.pack(side='right')
            tk.Label(badge, text=status_text, font=("Segoe UI", 9, "bold"), fg="white", bg=status_color).pack()
            
            if ratio <= 20:
                tk.Label(detail_inner, text=f"💡 Bạn còn được phép vắng tối đa {remains} buổi nữa.", 
                         font=StyleConfig.FONT_XS, fg=StyleConfig.TEXT_GRAY, bg=StyleConfig.CARD_BG).pack(anchor='w', pady=(0, 15))

            # Table
            t_card = tk.Frame(detail_inner, bg=StyleConfig.BORDER, padx=1, pady=1)
            t_card.pack(fill='both', expand=True)
            
            cols = ("Ngày học", "Trạng thái", "Ghi chú hệ thống")
            tree = ttk.Treeview(t_card, columns=cols, show='headings', height=12)
            from gui_styles import add_treeview_style
            add_treeview_style(tree)
            
            tree.heading("Ngày học", text="NGÀY HỌC")
            tree.heading("Trạng thái", text="TRẠNG THÁI")
            tree.heading("Ghi chú hệ thống", text="GHI CHÚ")
            tree.column("Ngày học", width=120, anchor='center')
            tree.column("Trạng thái", width=150, anchor='center')
            tree.column("Ghi chú hệ thống", width=250, anchor='w')
            tree.pack(fill='both', expand=True)
            
            details = self.db.get_student_attendance_detail(self.sv_id, lhp_id)
            if not details:
                tk.Label(detail_inner, text="Chưa có dữ liệu điểm danh cho môn này", 
                         bg=StyleConfig.CARD_BG, font=StyleConfig.FONT_SM, fg=StyleConfig.TEXT_GRAY).pack(pady=40)
            else:
                for d in details:
                    st_map = {1: ("✅ Có mặt", "success"), 0: ("❌ Vắng mặt", "danger"), 2: ("📝 Có phép", "warning")}
                    txt, tag = st_map.get(d[1], ("-", ""))
                    tree.insert("", "end", values=(d[0], txt, "Hợp lệ" if d[1] != 0 else "Tính vào cấm thi"))

        # Build Course Cards
        self._course_cards = []
        for r in summary:
            ma, ten, tc, nk, np, tong, lhp_id = r
            ratio = (nk / tong) * 100 if tong > 0 else 0
            
            card = tk.Frame(card_container, bg=StyleConfig.CARD_BG, padx=15, pady=15, cursor='hand2')
            card.pack(fill='x', pady=5, padx=2)
            self._course_cards.append((card, lhp_id, ten))

            tk.Label(card, text=ten, font=StyleConfig.FONT_BOLD, bg=StyleConfig.CARD_BG, 
                     fg=StyleConfig.TEXT_DARK, wraplength=340, justify='left', anchor='w').pack(fill='x')
            
            # Progress-like info
            p_bar_bg = tk.Frame(card, bg="#edf2f7", height=6)
            p_bar_bg.pack(fill='x', pady=(12, 8))
            
            bar_color = StyleConfig.SUCCESS
            if ratio > 20: bar_color = StyleConfig.DANGER
            elif ratio > 15: bar_color = StyleConfig.WARNING
            
            p_bar_fg = tk.Frame(p_bar_bg, bg=bar_color, width=int(3.4 * ratio)) # Scale logic
            p_bar_fg.place(x=0, y=0, height=6, relwidth=ratio/100)

            info = tk.Frame(card, bg=StyleConfig.CARD_BG)
            info.pack(fill='x')
            tk.Label(info, text=f"Vắng: {nk}K - {np}P", font=StyleConfig.FONT_XS, bg=StyleConfig.CARD_BG, fg=StyleConfig.TEXT_GRAY).pack(side='left')
            tk.Label(info, text=f"{ratio:.0f}% vắng", font=("Segoe UI", 9, "bold"), bg=StyleConfig.CARD_BG, fg=bar_color).pack(side='right')

            # Interaction
            def make_click_handler(id=lhp_id, t=ten, n_k=nk, t_o=tong, c=card):
                return lambda e: [self._highlight_card(c), show_detail(id, t, n_k, t_o)]

            handler = make_click_handler()
            card.bind("<Button-1>", handler)
            for child in card.winfo_children():
                child.bind("<Button-1>", handler)
                if child.winfo_children():
                    for gchild in child.winfo_children(): gchild.bind("<Button-1>", handler)

        # Highlight function
        def _highlight_card(self, active_card):
            for c, _, _ in self._course_cards:
                c.config(bg=StyleConfig.CARD_BG)
                if c.winfo_exists():
                    for child in c.winfo_children(): 
                        if child.winfo_exists(): child.config(bg=StyleConfig.CARD_BG)
                        if isinstance(child, tk.Frame): # Progress bar parts
                             for gchild in child.winfo_children(): 
                                 if gchild.winfo_exists(): gchild.config(bg=StyleConfig.CARD_BG)

            active_card.config(bg="#f0f4ff")
            for child in active_card.winfo_children(): 
                if child.winfo_exists(): child.config(bg="#f0f4ff")

        self._highlight_card = _highlight_card.__get__(self)

        # Show default
        if summary:
            self._highlight_card(self._course_cards[0][0])
            show_detail(summary[0][6], summary[0][1], summary[0][3], summary[0][5])

