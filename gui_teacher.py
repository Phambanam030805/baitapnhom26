import tkinter as tk
from tkinter import ttk, messagebox
from gui_styles import StyleConfig, DashboardBase, StatCard, add_treeview_style, insert_tree_row, ScrollableFrame, add_search_bar
import excel_export
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Segoe UI'


class TeacherDashboard(DashboardBase):
    def __init__(self, root, user_data, db, on_logout):
        super().__init__(root, user_data, db, on_logout)
        self.gv_id = user_data[3]

        a1 = self.add_menu_item("Nhập điểm",  "📝", self.page_grade)
        self.add_menu_item("Điểm danh",       "📅", self.page_attendance)
        self.add_menu_item("Thống kê",         "📊", self.page_stats)
        self.add_menu_item("Thông báo",        "📢", self.page_notice)
        self.add_menu_item("Hồ sơ",            "👤", self.page_profile)
        a1()

    # ── Grade entry page ───────────────────────────────────────────────────
    def page_grade(self):
        self.header_icon.config(text="📝")
        self.header_title.config(text="Nhập điểm sinh viên")
        self.set_scrollable(False)
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

        # Status badge
        self.lhp_status = tk.Label(top, text="", font=StyleConfig.FONT_SM,
                                   bg=StyleConfig.CARD_BG)
        self.lhp_status.pack(side='left')

        # ── Middle: student list ───────────────────────────────────────────
        mid = tk.Frame(self.content_area, bg=StyleConfig.CARD_BG, padx=20, pady=16)
        mid.pack(fill='both', expand=True)

        cols = ("ID", "Mã SV", "Họ tên", "Chuyên cần", "Giữa kỳ", "Cuối kỳ", "Trung bình", "Xếp loại", "Trạng thái")
        tree = ttk.Treeview(mid, columns=cols, show='headings')
        add_treeview_style(tree)
        for col in cols:
            tree.heading(col, text=col)
            w = 80 if col not in ["Họ tên", "Trạng thái"] else 150
            tree.column(col, width=w, anchor='center' if col != "Họ tên" else 'w')

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
                # Handle "-" placeholder
                val = str(vals[3 + i])
                e.insert(0, val if val != "-" else "")

        tree.bind("<<TreeviewSelect>>", on_select)

        def save():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Chưa chọn", "Vui lòng chọn sinh viên!"); return
            if not cb.get():
                messagebox.showwarning("Chưa chọn lớp", "Vui lòng chọn lớp học phần!"); return
            
            try:
                # Use None if empty, so we don't accidentally save 0.0
                cc_txt = ents[0].get().strip()
                gk_txt = ents[1].get().strip()
                ck_txt = ents[2].get().strip()
                
                cc = float(cc_txt) if cc_txt else None
                gk = float(gk_txt) if gk_txt else None
                ck = float(ck_txt) if ck_txt else None
                
                if cc is not None and not (0 <= cc <= 10): raise ValueError
                if gk is not None and not (0 <= gk <= 10): raise ValueError
                if ck is not None and not (0 <= ck <= 10): raise ValueError
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

        def clear_points():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Chưa chọn", "Vui lòng chọn sinh viên!"); return
            if not cb.get(): return
            
            if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa trắng điểm của sinh viên này?"):
                sv_id  = tree.item(sel[0])['values'][0]
                lhp_id = self.lhp_map[cb.get()]
                # Pass None for all grades to reset
                ok, msg = self.db.update_diem(sv_id, lhp_id, None, None, None, self.user_data[0])
                if ok:
                    self.set_status(f"🧹 Đã xóa trắng điểm SV #{sv_id}", ok=True)
                    for e in ents: e.delete(0, tk.END)
                    load_sv(None)
                else:
                    messagebox.showerror("Lỗi", msg)

        btn_save = ttk.Button(bot, text="Lưu điểm", style="Primary.TButton", command=save)
        btn_save.grid(row=1, column=9, padx=(10, 0))

        btn_clear = ttk.Button(bot, text="Xóa điểm", style="Warning.TButton", command=clear_points)
        btn_clear.grid(row=1, column=10, padx=(10, 0))

        btn_lock = ttk.Button(bot, text="Khóa điểm", style="Danger.TButton", command=lock_class)
        btn_lock.grid(row=1, column=11, padx=(10, 0))

        # Export button
        def do_export():
            if not cb.get():
                messagebox.showwarning('Chưa chọn lớp', 'Vui lòng chọn lớp học phần trước!'); return
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

        ttk.Button(bot, text="Xuất Excel",
                   style="Success.TButton", command=do_export).grid(row=1, column=12, padx=(10, 0))

        # ── Wire up combobox ───────────────────────────────────────────────
        def load_sv(evt):
            for i in tree.get_children(): tree.delete(i)
            if not cb.get(): return
            lhp_id = self.lhp_map[cb.get()]
            
            # Fetch raw data with trang_thai
            raw_data = self.db.get_bang_diem_lop(lhp_id)
            
            for r in raw_data:
                # r = (id, ma_sv, ho_ten, cc, gk, ck, tb, chu, trang_thai)
                formatted = list(r)
                
                # Format Trạng thái thi for display
                st = str(r[8]).strip() if r[8] else ""
                if st == 'Cam thi':
                    formatted[8] = "⚠️ Cấm thi"
                elif st == 'Du dieu kien':
                    formatted[8] = "✅ Đủ ĐK thi"
                elif st == 'Đang học' or st == "":
                    formatted[8] = "Đang học"

                # Logic: Nếu chưa có điểm TB (None) hoặc trạng thái là 'Đang học'
                if formatted[6] is None or st == 'Đang học' or st == "":
                    # Sử dụng dấu gạch ngang '-' để nhận biết chưa nhập điểm
                    for i in [3, 4, 5, 6, 7]: # CC, GK, CK, TB, Xếp loại
                        formatted[i] = "-"
                else:
                    # Nếu đã có điểm nhưng có cột nào đó bị NULL thì cũng hiện "-"
                    for i in [3, 4, 5, 6]:
                        if formatted[i] is None:
                            formatted[i] = "-"
                    if formatted[7] is None:
                        formatted[7] = "-"
                
                insert_tree_row(tree, formatted)
                
            # Status badge
            self.db.cursor.execute("SELECT status FROM lop_hoc_phan WHERE id=%s", (lhp_id,))
            row = self.db.cursor.fetchone()
            if row:
                if row[0] == 'open':
                    self.lhp_status.config(text="Đang mở", fg=StyleConfig.SUCCESS)
                    btn_save.state(['!disabled'])
                    btn_lock.state(['!disabled'])
                else:
                    self.lhp_status.config(text="Đã khóa", fg=StyleConfig.DANGER)
                    btn_save.state(['disabled'])
                    btn_lock.state(['disabled'])
            self.set_status(f"Lớp có {len(raw_data)} sinh viên")

        # Search badge
        add_search_bar(top, tree, lambda: load_sv(None))

        lhps = self.db.get_lhp_by_giang_vien(self.gv_id)
        self.lhp_map = {f"{r[1]}  -  {r[2]}  ({r[3]})": r[0] for r in lhps}
        cb['values'] = list(self.lhp_map.keys())
        cb.bind("<<ComboboxSelected>>", load_sv)

        if cb['values']:
            cb.current(0)
            load_sv(None)

    # ── Stats page ─────────────────────────────────────────────────────────
    def page_stats(self):
        self.header_icon.config(text="📊")
        self.header_title.config(text="Thống kê giảng dạy")
        self.set_scrollable(False)
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
            tree.column(col, width=120, minwidth=100, anchor='center')
        tree.column("Tên môn", width=220, anchor='w')

        def refresh_stats():
            for i in tree.get_children(): tree.delete(i)
            for r in self.db.get_teacher_stats(self.gv_id):
                insert_tree_row(tree, r)

        add_search_bar(left, tree, refresh_stats)

        sb = ttk.Scrollbar(left, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        tree.pack(fill='both', expand=True)

        for r in data:
            insert_tree_row(tree, r)

        # Right column for Chart
        right = tk.Frame(main_frame, bg=StyleConfig.CARD_BG, width=350, padx=20, pady=20)
        right.pack(side='right', fill='both')

        tk.Label(right, text="Tỷ lệ Đạt/Trượt tổng quát", font=StyleConfig.FONT_BOLD, 
                 bg=StyleConfig.CARD_BG, fg=StyleConfig.TEXT_DARK).pack(pady=(0, 20))

        fig = Figure(figsize=(4, 4), dpi=100)
        fig.patch.set_facecolor(StyleConfig.CARD_BG)
        ax = fig.add_subplot(111)

        tong_dat = sum(r[3] for r in data)
        tong_rot = sum(r[4] for r in data)

        if tong_dat + tong_rot > 0:
            labels = ['Đạt', 'Trượt']
            sizes = [tong_dat, tong_rot]
            colors = ['#10b981', '#ef4444'] # Green, Red
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors,
                   textprops={'color': StyleConfig.TEXT_DARK, 'weight': 'bold'})
            ax.axis('equal')
        else:
            ax.text(0.5, 0.5, 'Chưa có dữ liệu', ha='center', va='center')
            ax.axis('off')

        canvas = FigureCanvasTkAgg(fig, master=right)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

        # Alerts at the bottom of right column
        alert_frame = tk.Frame(right, bg=StyleConfig.CARD_BG, pady=20)
        alert_frame.pack(fill='x')
        tk.Label(alert_frame, text="⚠️ Cảnh báo sinh viên yếu", font=StyleConfig.FONT_SM, 
                 bg=StyleConfig.CARD_BG, fg=StyleConfig.DANGER).pack(anchor='w')
        
        cam_thi_all = []
        for r in self.db.get_lhp_by_giang_vien(self.gv_id):
            list_ct = self.db.get_ds_cam_thi(r[0])
            for ct in list_ct: cam_thi_all.append(f"{ct[1]} ({r[1]})")
        
        if cam_thi_all:
            for ct in cam_thi_all[:5]:
                tk.Label(alert_frame, text=f"• {ct}", font=StyleConfig.FONT_XS, 
                         bg=StyleConfig.CARD_BG, fg=StyleConfig.TEXT_GRAY).pack(anchor='w')
        else:
            tk.Label(alert_frame, text="Không có cảnh báo", font=StyleConfig.FONT_XS, 
                     bg=StyleConfig.CARD_BG, fg=StyleConfig.TEXT_LIGHT).pack(anchor='w')

    # ── Notice page ────────────────────────────────────────────────────────
    def page_notice(self):
        self.header_icon.config(text="📢")
        self.header_title.config(text="Thông báo")
        self.set_scrollable(True)
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

    # ── Attendance page V3 (Premium Aesthetic) ──────────────────────────────────────────────────
    def page_attendance(self):
        self.header_icon.config(text="📅")
        self.header_title.config(text="Hệ thống Điểm danh Thông minh")
        self.set_scrollable(False)
        for w in self.content_area.winfo_children(): w.destroy()

        # Dashboard Container
        dash = tk.Frame(self.content_area, bg=StyleConfig.CONTENT_BG, padx=25, pady=20)
        dash.pack(fill='both', expand=True)

        # --- Top Section: Stats & Config ---
        top_frame = tk.Frame(dash, bg=StyleConfig.CONTENT_BG)
        top_frame.pack(fill='x', pady=(0, 25))

        # Stats Cards
        stats_box = tk.Frame(top_frame, bg=StyleConfig.CONTENT_BG)
        stats_box.pack(fill='x', pady=(0, 20))
        
        self._st_buoi = StatCard(stats_box, "Số buổi đã dạy", "0", "📚", "#4f46e5")
        self._st_ti_le = StatCard(stats_box, "Tỉ lệ chuyên cần", "0%", "📈", "#10b981")
        self._st_cam   = StatCard(stats_box, "Cảnh báo cấm thi", "0", "⚠️", "#f59e0b")

        # Config Row
        cfg_row = tk.Frame(top_frame, bg=StyleConfig.CARD_BG, padx=20, pady=20)
        cfg_row.pack(fill='x')
        # Border bottom for cfg_row
        tk.Frame(top_frame, bg=StyleConfig.PRIMARY, height=3).pack(fill='x')

        # Class Selection
        f1 = tk.Frame(cfg_row, bg=StyleConfig.CARD_BG)
        f1.pack(side='left')
        tk.Label(f1, text="CHỌN LỚP HỌC PHẦN", font=("Segoe UI", 9, "bold"), 
                 bg=StyleConfig.CARD_BG, fg=StyleConfig.TEXT_GRAY).pack(anchor='w')
        cb_lhp = ttk.Combobox(f1, width=50, state="readonly", font=StyleConfig.FONT_MD)
        cb_lhp.pack(pady=(5, 0))

        # Date Selection
        f2 = tk.Frame(cfg_row, bg=StyleConfig.CARD_BG, padx=40)
        f2.pack(side='left')
        tk.Label(f2, text="NGÀY ĐIỂM DANH", font=("Segoe UI", 9, "bold"), 
                 bg=StyleConfig.CARD_BG, fg=StyleConfig.TEXT_GRAY).pack(anchor='w')
        from datetime import date
        ent_date = ttk.Entry(f2, width=15, font=StyleConfig.FONT_MD, justify='center')
        ent_date.insert(0, date.today().strftime("%Y-%m-%d"))
        ent_date.pack(pady=(5, 0))

        # --- Main Body: [History | Student List] ---
        body = tk.Frame(dash, bg=StyleConfig.CONTENT_BG)
        body.pack(fill='both', expand=True)

        # Left: History (Modern Sidebar)
        hist_col = tk.Frame(body, bg=StyleConfig.CARD_BG, width=220)
        hist_col.pack(side='left', fill='y', padx=(0, 20))
        hist_col.pack_propagate(False)
        
        tk.Label(hist_col, text="LỊCH SỬ DẠY", font=("Segoe UI", 9, "bold"), 
                 bg=StyleConfig.CARD_BG, fg=StyleConfig.PRIMARY, pady=15).pack()
        tk.Frame(hist_col, bg=StyleConfig.BORDER, height=1).pack(fill='x', padx=15)
        
        hist_list = tk.Frame(hist_col, bg=StyleConfig.CARD_BG)
        hist_list.pack(fill='both', expand=True, pady=10)

        # Right: Attendance List
        list_col = tk.Frame(body, bg=StyleConfig.CARD_BG)
        list_col.pack(side='left', fill='both', expand=True)

        # List Header
        list_header = tk.Frame(list_col, bg="#f8faff", pady=15, padx=20)
        list_header.pack(fill='x')
        tk.Label(list_header, text="Danh sách sinh viên & Trạng thái", font=StyleConfig.FONT_BOLD, 
                 bg="#f8faff", fg=StyleConfig.TEXT_DARK).pack(side='left')

        def set_all(val):
            for v in self._att_vars.values(): v.set(val)

        ttk.Button(list_header, text="Toàn bộ có mặt", style="Success.TButton", 
                   command=lambda: set_all(1)).pack(side='right', padx=5)
        ttk.Button(list_header, text="Vắng hết", style="Danger.TButton", 
                   command=lambda: set_all(0)).pack(side='right')

        # Sheet Header (Column titles)
        s_header = tk.Frame(list_col, bg=StyleConfig.PRIMARY, pady=12)
        s_header.pack(fill='x')
        col_defs = [("MSV", 12), ("Họ và tên", 28), ("Nghỉ (K/P)", 12), ("Tỉ lệ", 10), ("Điểm danh hôm nay", 25)]
        for t, w in col_defs:
            tk.Label(s_header, text=t.upper(), font=("Segoe UI", 9, "bold"), 
                     fg="white", bg=StyleConfig.PRIMARY, width=w, anchor='w' if w>15 else 'center').pack(side='left', padx=5)

        # Scrollable Sheet
        sheet_container = ScrollableFrame(list_col, bg=StyleConfig.CARD_BG)
        sheet_container.pack(fill='both', expand=True)
        sheet = sheet_container.scrollable_frame

        self._att_vars = {}

        def load_all_data(evt=None):
            for w in sheet.winfo_children(): w.destroy()
            for w in hist_list.winfo_children(): w.destroy()
            if not cb_lhp.get(): return
            lhp_id = self.lhp_map[cb_lhp.get()]
            
            # 1. Sidebar History
            dates = self.db.get_attendance_dates(lhp_id)
            for d_val in dates:
                d_str = d_val.strftime("%Y-%m-%d")
                is_active = (d_str == ent_date.get())
                f = tk.Frame(hist_list, bg=StyleConfig.PRIMARY_LIGHT if is_active else StyleConfig.CARD_BG)
                f.pack(fill='x', pady=1)
                
                lbl = tk.Label(f, text=f"📅  {d_str}", font=StyleConfig.FONT_SM, 
                              bg=StyleConfig.PRIMARY_LIGHT if is_active else StyleConfig.CARD_BG,
                              fg=StyleConfig.PRIMARY if is_active else StyleConfig.TEXT_GRAY, 
                              padx=20, pady=10, anchor='w', cursor='hand2')
                lbl.pack(fill='x')
                lbl.bind("<Button-1>", lambda e, d=d_str: (ent_date.delete(0, 'end'), ent_date.insert(0, d), load_all_data()))

            # 2. Data & Stats
            report = self.db.get_attendance_report(lhp_id)
            current_detail = self.db.get_attendance_detail(lhp_id, ent_date.get())
            
            # Update Dashboard Stats
            self._st_buoi.update(len(dates))
            b_count = sum(1 for r in report if r[5] > 0 and (r[3]/r[5] > 0.15))
            self._st_cam.update(b_count)
            # Tính tỉ lệ chuyên cần tổng
            total_nghi_k = sum(r[3] for r in report)
            total_buoi = sum(r[5] for r in report) if report else 1
            ti_le_cc = max(0, 100 - (total_nghi_k / total_buoi * 100)) if total_buoi > 0 else 100
            self._st_ti_le.update(f"{ti_le_cc:.0f}%")
            self.set_status(f"Tải xong danh sách: {len(report)} sinh viên", ok=True)
            
            self._att_vars = {}
            if not report:
                tk.Label(sheet, text="Chưa có sinh viên nào đăng ký lớp này", bg=StyleConfig.CARD_BG).pack(pady=20)
                return

            for i, r in enumerate(report):
                id_sv, msv, ho_ten, nghi_k, nghi_p, tong_buoi = r
                bg = StyleConfig.CARD_BG if i % 2 == 0 else "#fbfcfd"
                row = tk.Frame(sheet, bg=bg, pady=12)
                row.pack(fill='x', pady=1)
                
                ratio = (nghi_k / tong_buoi) * 100 if tong_buoi > 0 else 0
                color = StyleConfig.TEXT_DARK
                if ratio > 20: color = StyleConfig.DANGER
                elif ratio > 15: color = StyleConfig.WARNING

                tk.Label(row, text=msv, font=StyleConfig.FONT_SM, bg=bg, width=12).pack(side='left', padx=5)
                tk.Label(row, text=ho_ten, font=StyleConfig.FONT_BOLD, bg=bg, width=28, anchor='w').pack(side='left', padx=5)
                tk.Label(row, text=f"{nghi_k}K - {nghi_p}P", font=StyleConfig.FONT_SM, bg=bg, width=12, fg=StyleConfig.TEXT_GRAY).pack(side='left', padx=5)
                
                # Progress-like ratio label
                r_lbl = tk.Label(row, text=f"{ratio:.0f}%", font=("Segoe UI", 10, "bold"), bg=bg, width=10, fg=color)
                r_lbl.pack(side='left', padx=5)

                # Radio Options
                opt_frame = tk.Frame(row, bg=bg)
                opt_frame.pack(side='left', fill='x', expand=True)
                var = tk.IntVar(value=current_detail.get(id_sv, 1))
                self._att_vars[id_sv] = var
                
                for val, txt in [(1, "Có mặt"), (0, "Vắng"), (2, "Phép")]:
                    tk.Radiobutton(opt_frame, text=txt, variable=var, value=val, 
                                   bg=bg, font=StyleConfig.FONT_XS, fg=StyleConfig.TEXT_GRAY,
                                   activebackground=bg, selectcolor="white").pack(side='left', padx=15)

        def do_save():
            if not cb_lhp.get(): return
            lhp_id = self.lhp_map[cb_lhp.get()]
            d_str = ent_date.get().strip()
            
            # Validation định dạng YYYY-MM-DD
            import re
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", d_str):
                messagebox.showerror("Sai định dạng", "Ngày phải có định dạng YYYY-MM-DD\nVí dụ: 2024-05-12"); return

            att_list = [(id_sv, var.get()) for id_sv, var in self._att_vars.items()]
            ok, msg = self.db.save_attendance(lhp_id, att_list, d_str)
            if ok:
                self.set_status(msg, ok=True)
                load_all_data()
            else:
                messagebox.showerror("Lỗi", msg)

        # Footer Action
        footer = tk.Frame(dash, bg=StyleConfig.CONTENT_BG, pady=20)
        footer.pack(fill='x')
        ttk.Button(footer, text="CẬP NHẬT BẢNG ĐIỂM DANH", style="Primary.TButton", command=do_save).pack(side='right')

        # Load Initial
        lhps = self.db.get_lhp_by_giang_vien(self.gv_id)
        self.lhp_map = {f"{r[1]}  -  {r[2]}  ({r[3]})": r[0] for r in lhps}
        cb_lhp['values'] = list(self.lhp_map.keys())
        cb_lhp.bind("<<ComboboxSelected>>", load_all_data)
        
        if cb_lhp['values']:
            cb_lhp.current(0)
            load_all_data()

