import tkinter as tk
from tkinter import ttk, messagebox
from gui_styles import StyleConfig, DashboardBase, StatCard, add_treeview_style, insert_tree_row


def _make_tree(parent, cols, widths):
    tree = ttk.Treeview(parent, columns=cols, show='headings', selectmode='browse')
    add_treeview_style(tree)
    for col, w in zip(cols, widths):
        tree.heading(col, text=col)
        tree.column(col, width=w, anchor='center' if w < 150 else 'w')
    sb = ttk.Scrollbar(parent, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    sb.pack(side='right', fill='y')
    tree.pack(fill='both', expand=True)
    return tree


def _card(parent, title):
    f = tk.Frame(parent, bg=StyleConfig.CARD_BG, padx=20, pady=16)
    f.pack(fill='both', expand=True, pady=(0, 0))
    if title:
        tk.Label(f, text=title, font=StyleConfig.FONT_BOLD,
                 fg=StyleConfig.TEXT_GRAY, bg=StyleConfig.CARD_BG).pack(anchor='w', pady=(0, 10))
    return f


def _form_card(parent, fields, on_add, on_edit, on_del, tree):
    """Header card with auto-form + buttons. Returns list of entry/combobox widgets."""
    c = tk.Frame(parent, bg=StyleConfig.CARD_BG, padx=20, pady=14)
    c.pack(fill='x', pady=(0, 14))

    form = tk.Frame(c, bg=StyleConfig.CARD_BG)
    form.pack(fill='x')
    ents = []
    for i, (lbl, w, is_cb) in enumerate(fields):
        tk.Label(form, text=lbl, font=StyleConfig.FONT_SM,
                 fg=StyleConfig.TEXT_GRAY, bg=StyleConfig.CARD_BG).grid(row=0, column=i, padx=6, sticky='w')
        e = ttk.Combobox(form, width=w, state='readonly') if is_cb else ttk.Entry(form, width=w)
        e.grid(row=1, column=i, padx=6, pady=4)
        ents.append(e)

    def on_sel(evt):
        sel = tree.selection()
        if not sel: return
        vals = tree.item(sel[0])['values']
        for i, e in enumerate(ents):
            v = vals[i+1] if i+1 < len(vals) else ''
            if isinstance(e, ttk.Combobox): e.set(v)
            else: e.delete(0, tk.END); e.insert(0, v)
    tree.bind('<<TreeviewSelect>>', on_sel)

    bf = tk.Frame(c, bg=StyleConfig.CARD_BG)
    bf.pack(fill='x', pady=(10, 0))
    ttk.Button(bf, text='＋ Thêm',  style='Primary.TButton', command=on_add).pack(side='left', padx=4)
    ttk.Button(bf, text='✎ Sửa',   style='Warning.TButton', command=on_edit).pack(side='left', padx=4)
    ttk.Button(bf, text='✕ Xóa',   style='Danger.TButton',  command=on_del).pack(side='left', padx=4)
    return ents


class AdminDashboard(DashboardBase):
    def __init__(self, root, user_data, db, on_logout):
        super().__init__(root, user_data, db, on_logout)
        items = [
            ('Sinh viên', '👥', 'SV'), ('Giảng viên', '👨‍🏫', 'GV'),
            ('Tài khoản', '🔑', 'USR'), ('Lớp HC', '🏢', 'LHC'),
            ('Khoa', '🏫', 'KH'), ('Môn học', '📚', 'MH'),
            ('Lớp HP', '📅', 'LHP'), ('Học kỳ', '⏱️', 'HK'),
            ('Thông báo', '📢', 'TB'),
        ]
        first = None
        for t, i, c in items:
            fn = self.add_menu_item(t, i, lambda code=c: self.show_page(code))
            if first is None: first = fn
        if first: first()

    def show_page(self, code):
        self.header_title.config(text={
            'SV': '👥  Quản lý Sinh viên', 'GV': '👨‍🏫  Quản lý Giảng viên',
            'USR': '🔑  Quản lý Tài khoản', 'LHC': '🏢  Lớp Hành chính',
            'KH': '🏫  Quản lý Khoa', 'MH': '📚  Quản lý Môn học',
            'LHP': '📅  Lớp Học phần', 'HK': '⏱️  Học kỳ', 'TB': '📢  Thông báo',
        }.get(code, code))
        for w in self.content_area.winfo_children(): w.destroy()
        {'SV': self.page_sv, 'GV': self.page_gv, 'USR': self.page_users,
         'LHC': self.page_lhc, 'KH': self.page_kh, 'MH': self.page_mh,
         'LHP': self.page_lhp, 'HK': self.page_hk, 'TB': self.page_tb}.get(code, lambda: None)()

    # ── SINH VIÊN ──────────────────────────────────────────────────────────
    def page_sv(self):
        cols = ('ID','MSV','Họ tên','Ngày sinh','GT','Lớp HC')
        tree = _make_tree(_card(self.content_area, None), cols, [55,90,200,110,60,140])
        def refresh():
            for i in tree.get_children(): tree.delete(i)
            for r in self.db.get_all_sinh_vien(): insert_tree_row(tree, r)
            lhcs = self.db.get_all_lop_hc()
            self.lhc_map = {r[2]: r[0] for r in lhcs}
            ents[4]['values'] = list(self.lhc_map.keys())
        def add():
            if self.db.insert_sinh_vien(ents[0].get(), ents[1].get(), ents[2].get(),
                                        ents[3].get(), self.lhc_map.get(ents[4].get())):
                messagebox.showinfo('OK', '✅ Đã thêm sinh viên (Pass: 123)'); refresh()
            else: messagebox.showerror('Lỗi', 'Thêm thất bại (trùng mã)')
        def edit():
            sel = tree.selection()
            if sel:
                if self.db.update_sinh_vien(tree.item(sel[0])['values'][0],
                        ents[0].get(), ents[1].get(), ents[2].get(),
                        ents[3].get(), self.lhc_map.get(ents[4].get())):
                    messagebox.showinfo('OK', '✅ Cập nhật thành công'); refresh()
                else: messagebox.showerror('Lỗi', 'Cập nhật thất bại')
        def delete():
            sel = tree.selection()
            if sel and messagebox.askyesno('Xác nhận', 'Xóa sinh viên này?'):
                ok, msg = self.db.delete_sinh_vien(tree.item(sel[0])['values'][0])
                if ok: refresh()
                else: messagebox.showwarning('Cảnh báo', msg)
        ents = _form_card(self.content_area,
                          [('MSV',14,0),('Họ tên',22,0),('Ngày sinh',13,0),('GT',8,0),('Lớp HC',18,1)],
                          add, edit, delete, tree)
        refresh()

    # ── GIẢNG VIÊN ─────────────────────────────────────────────────────────
    def page_gv(self):
        cols = ('ID','Mã GV','Họ tên','Khoa','Email','SĐT')
        tree = _make_tree(_card(self.content_area, None), cols, [55,90,200,150,170,110])
        def refresh():
            for i in tree.get_children(): tree.delete(i)
            for r in self.db.get_all_giang_vien(): insert_tree_row(tree, r)
        def add():
            if self.db.insert_giang_vien(ents[0].get(), ents[1].get(), ents[2].get(), ents[3].get(), ents[4].get()):
                messagebox.showinfo('OK', '✅ Đã thêm giảng viên (Pass: 123)'); refresh()
            else: messagebox.showerror('Lỗi', 'Thêm thất bại')
        def edit():
            sel = tree.selection()
            if sel:
                if self.db.update_giang_vien(tree.item(sel[0])['values'][0],
                        ents[0].get(), ents[1].get(), ents[2].get(), ents[3].get(), ents[4].get()):
                    messagebox.showinfo('OK', '✅ Cập nhật'); refresh()
        def delete():
            sel = tree.selection()
            if sel and messagebox.askyesno('Xác nhận', 'Xóa giảng viên?'):
                ok, msg = self.db.delete_giang_vien(tree.item(sel[0])['values'][0])
                if ok: refresh()
                else: messagebox.showwarning('Cảnh báo', msg)
        ents = _form_card(self.content_area,
                          [('Mã GV',12,0),('Họ tên',22,0),('Khoa',16,0),('Email',18,0),('SĐT',12,0)],
                          add, edit, delete, tree)
        refresh()

    # ── TÀI KHOẢN ──────────────────────────────────────────────────────────
    def page_users(self):
        cols = ('ID','Username','Role','Trạng thái')
        tc = _card(self.content_area, None)
        tree = _make_tree(tc, cols, [55, 180, 100, 130])

        def refresh():
            for i in tree.get_children(): tree.delete(i)
            for r in self.db.get_all_users():
                tag = 'odd' if len(tree.get_children()) % 2 else 'even'
                status = '✅ Hoạt động' if r[3] == 1 else '🔒 Đã khóa'
                tree.insert('', 'end', values=(r[0], r[1], r[2], status), tags=(tag,))

        ctrl = tk.Frame(self.content_area, bg=StyleConfig.CARD_BG, padx=20, pady=14)
        ctrl.pack(fill='x', pady=(0, 12))
        
        # Username
        tk.Label(ctrl, text='Username:', font=StyleConfig.FONT_SM, fg=StyleConfig.TEXT_GRAY, bg=StyleConfig.CARD_BG).grid(row=0, column=0, sticky='w', padx=4)
        ent_u = ttk.Entry(ctrl, width=16)
        ent_u.grid(row=1, column=0, padx=4, pady=3)
        
        # Password
        tk.Label(ctrl, text='Password:', font=StyleConfig.FONT_SM, fg=StyleConfig.TEXT_GRAY, bg=StyleConfig.CARD_BG).grid(row=0, column=1, sticky='w', padx=4)
        ent_pw = ttk.Entry(ctrl, width=16)
        ent_pw.grid(row=1, column=1, padx=4, pady=3)
        
        # Role
        tk.Label(ctrl, text='Role:', font=StyleConfig.FONT_SM, fg=StyleConfig.TEXT_GRAY, bg=StyleConfig.CARD_BG).grid(row=0, column=2, sticky='w', padx=4)
        cb_role = ttk.Combobox(ctrl, width=14, state='readonly', values=['admin','teacher','student'])
        cb_role.grid(row=1, column=2, padx=4)
        cb_role.set('student')

        bf = tk.Frame(ctrl, bg=StyleConfig.CARD_BG)
        bf.grid(row=1, column=3, columnspan=6, padx=16, sticky='w')

        def on_sel(evt):
            sel = tree.selection()
            if not sel: return
            vals = tree.item(sel[0])['values']
            ent_u.delete(0, tk.END); ent_u.insert(0, vals[1])
            ent_pw.delete(0, tk.END) # Clear pw when selecting
            cb_role.set(vals[2])

        tree.bind('<<TreeviewSelect>>', on_sel)

        def _sel_id():
            sel = tree.selection()
            if not sel: messagebox.showwarning('Chưa chọn', 'Vui lòng chọn tài khoản!'); return None
            return tree.item(sel[0])['values'][0], tree.item(sel[0])['values'][1]

        def add_user():
            u, p, r = ent_u.get().strip(), ent_pw.get().strip(), cb_role.get()
            if not u or not p or not r: messagebox.showwarning('Thiếu', 'Vui lòng nhập đủ thông tin (Username, Password, Role)!'); return
            if self.db.insert_user(u, p, r):
                messagebox.showinfo('OK', '✅ Đã thêm tài khoản!'); refresh()
            else:
                messagebox.showerror('Lỗi', 'Thêm thất bại (Username có thể đã tồn tại)')

        def edit_user():
            sel_item = _sel_id()
            if not sel_item: return
            uid, uname = sel_item
            u, p, r = ent_u.get().strip(), ent_pw.get().strip(), cb_role.get()
            if not u or not r: messagebox.showwarning('Thiếu', 'Cần nhập ít nhất Username và Role!'); return
            if self.db.update_user(uid, u, r):
                if p: self.db.reset_password(uid, p) # Only update password if provided
                messagebox.showinfo('OK', '✅ Đã cập nhật tài khoản!'); refresh()
            else:
                messagebox.showerror('Lỗi', 'Cập nhật thất bại (Username có thể bị trùng)')

        def toggle():
            r = _sel_id()
            if not r: return
            uid, uname = r
            if uname == 'admin': messagebox.showwarning('Cảnh báo', 'Không thể khóa admin!'); return
            self.db.toggle_user_active(uid); refresh()

        def del_user():
            r = _sel_id()
            if not r: return
            uid, uname = r
            if uname == 'admin': messagebox.showwarning('Cảnh báo', 'Không thể xóa admin!'); return
            if messagebox.askyesno('Xác nhận', f"Xóa tài khoản '{uname}'?"):
                self.db.delete_user(uid); messagebox.showinfo('OK', '✅ Đã xóa!'); refresh()

        ttk.Button(bf, text='＋ Thêm',      style='Primary.TButton', command=add_user).pack(side='left', padx=3)
        ttk.Button(bf, text='✎ Sửa',       style='Warning.TButton', command=edit_user).pack(side='left', padx=3)
        ttk.Button(bf, text='🔒 Khóa/Mở',   command=toggle).pack(side='left', padx=3)
        ttk.Button(bf, text='✕ Xóa',       style='Danger.TButton',  command=del_user).pack(side='left', padx=3)
        ttk.Button(bf, text='↺ Làm mới',    command=refresh).pack(side='left', padx=10)
        refresh()

    # ── KHOA ───────────────────────────────────────────────────────────────
    def page_kh(self):
        cols = ('ID','Mã Khoa','Tên Khoa')
        tree = _make_tree(_card(self.content_area, None), cols, [55,120,280])
        def refresh():
            for i in tree.get_children(): tree.delete(i)
            for r in self.db.get_all_khoa(): insert_tree_row(tree, r)
        def add():
            if self.db.insert_khoa(ents[0].get(), ents[1].get()):
                messagebox.showinfo('OK','✅ Thêm thành công'); refresh()
            else: messagebox.showerror('Lỗi','Trùng mã khoa')
        def edit():
            sel = tree.selection()
            if sel:
                if self.db.update_khoa(tree.item(sel[0])['values'][0], ents[0].get(), ents[1].get()):
                    messagebox.showinfo('OK','✅ Cập nhật'); refresh()
        def delete():
            sel = tree.selection()
            if sel and messagebox.askyesno('Xác nhận','Xóa khoa này?'):
                ok, msg = self.db.delete_khoa(tree.item(sel[0])['values'][0])
                if ok: refresh()
                else: messagebox.showwarning('Cảnh báo', msg)
        ents = _form_card(self.content_area, [('Mã Khoa',16,0),('Tên Khoa',34,0)], add, edit, delete, tree)
        refresh()

    # ── LỚP HÀNH CHÍNH ─────────────────────────────────────────────────────
    def page_lhc(self):
        cols = ('ID','Mã Lớp','Tên Lớp','Khoa')
        tree = _make_tree(_card(self.content_area, None), cols, [55,110,220,180])
        def refresh():
            for i in tree.get_children(): tree.delete(i)
            for r in self.db.get_all_lop_hc(): insert_tree_row(tree, r)
            khs = self.db.get_all_khoa()
            self.kh_map = {r[2]: r[0] for r in khs}
            ents[2]['values'] = list(self.kh_map.keys())
        def add():
            if self.db.insert_lop_hc(ents[0].get(), ents[1].get(), self.kh_map.get(ents[2].get())):
                messagebox.showinfo('OK','✅ Thêm thành công'); refresh()
        def edit():
            sel = tree.selection()
            if sel:
                if self.db.update_lop_hc(tree.item(sel[0])['values'][0],
                        ents[0].get(), ents[1].get(), self.kh_map.get(ents[2].get())):
                    messagebox.showinfo('OK','✅ Cập nhật'); refresh()
        def delete():
            sel = tree.selection()
            if sel and messagebox.askyesno('Xác nhận','Xóa lớp?'):
                ok, msg = self.db.delete_lop_hc(tree.item(sel[0])['values'][0])
                if ok: refresh()
                else: messagebox.showwarning('Cảnh báo', msg)
        ents = _form_card(self.content_area, [('Mã Lớp',16,0),('Tên Lớp',26,0),('Khoa',20,1)], add, edit, delete, tree)
        refresh()

    # ── MÔN HỌC ────────────────────────────────────────────────────────────
    def page_mh(self):
        cols = ('ID','Mã MH','Tên Môn','Số TC')
        tree = _make_tree(_card(self.content_area, None), cols, [55,100,260,80])
        def refresh():
            for i in tree.get_children(): tree.delete(i)
            for r in self.db.get_all_mon_hoc(): insert_tree_row(tree, r[:4])
        def add():
            try:
                if self.db.insert_mon_hoc(ents[0].get(), ents[1].get(), int(ents[2].get() or 0)):
                    messagebox.showinfo('OK','✅ Thêm thành công'); refresh()
            except: messagebox.showerror('Lỗi','Số tín chỉ phải là số nguyên')
        def edit():
            sel = tree.selection()
            if sel:
                try:
                    if self.db.update_mon_hoc(tree.item(sel[0])['values'][0],
                            ents[0].get(), ents[1].get(), int(ents[2].get() or 0), ''):
                        messagebox.showinfo('OK','✅ Cập nhật'); refresh()
                except: messagebox.showerror('Lỗi','Số tín chỉ phải là số')
        def delete():
            sel = tree.selection()
            if sel and messagebox.askyesno('Xác nhận','Xóa môn học?'):
                ok, msg = self.db.delete_mon_hoc(tree.item(sel[0])['values'][0])
                if ok: refresh()
                else: messagebox.showwarning('Cảnh báo', msg)
        ents = _form_card(self.content_area, [('Mã MH',12,0),('Tên Môn',28,0),('Số TC',8,0)], add, edit, delete, tree)
        refresh()

    # ── LỚP HỌC PHẦN ───────────────────────────────────────────────────────
    def page_lhp(self):
        cols = ('ID','Mã Lớp','Môn','Giảng viên','Học kỳ','Lịch học','Trạng thái')
        tree = _make_tree(_card(self.content_area, None), cols, [50,100,180,160,130,150,90])

        def refresh():
            for i in tree.get_children(): tree.delete(i)
            for r in self.db.get_all_lop_hp(): insert_tree_row(tree, r)
            self.mh_map = {f'{r[1]}-{r[2]}': r[0] for r in self.db.get_all_mon_hoc()}
            self.gv_map = {f'{r[1]}-{r[2]}': r[0] for r in self.db.get_all_giang_vien()}
            self.hk_map = {f'{r[1]} {r[2]}': r[0] for r in self.db.get_all_hoc_ky()}
            ents[1]['values'] = list(self.mh_map.keys())
            ents[2]['values'] = list(self.gv_map.keys())
            ents[3]['values'] = list(self.hk_map.keys())
            ents[4]['values'] = ['Thứ 2','Thứ 3','Thứ 4','Thứ 5','Thứ 6','Thứ 7','Chủ nhật']
            ents[5]['values'] = ['1 (7h-9h)','2 (9h-11h)','3 (13h-15h)','4 (15h-17h)','5 (18h-20h)']

        def on_sel(evt):
            sel = tree.selection()
            if not sel: return
            vals = tree.item(sel[0])['values']
            ents[0].delete(0, tk.END); ents[0].insert(0, vals[1])
            lhp_id = vals[0]
            self.db.cursor.execute(
                'SELECT id_mon_hoc,id_giang_vien,id_hoc_ky,thu,ca_hoc FROM lop_hoc_phan WHERE id=?', (lhp_id,))
            row = self.db.cursor.fetchone()
            if row:
                for key, val in self.mh_map.items():
                    if val == row[0]: ents[1].set(key); break
                for key, val in self.gv_map.items():
                    if val == row[1]: ents[2].set(key); break
                for key, val in self.hk_map.items():
                    if val == row[2]: ents[3].set(key); break
                ents[4].set(row[3] or '')
                ents[5].set(row[4] or '')

        tree.bind('<<TreeviewSelect>>', on_sel)

        def add():
            if self.db.insert_lop_hoc_phan(ents[0].get(),
                    self.mh_map.get(ents[1].get()), self.gv_map.get(ents[2].get()),
                    self.hk_map.get(ents[3].get()), ents[4].get(), ents[5].get()):
                messagebox.showinfo('OK','✅ Thêm lớp thành công'); refresh()
            else: messagebox.showerror('Lỗi','Thêm thất bại (trùng mã hoặc thiếu thông tin)')

        def edit():
            sel = tree.selection()
            if sel:
                if self.db.update_lop_hoc_phan(tree.item(sel[0])['values'][0], ents[0].get(),
                        self.mh_map.get(ents[1].get()), self.gv_map.get(ents[2].get()),
                        self.hk_map.get(ents[3].get()), ents[4].get(), ents[5].get()):
                    messagebox.showinfo('OK','✅ Cập nhật'); refresh()

        def delete():
            sel = tree.selection()
            if sel and messagebox.askyesno('Xác nhận','Xóa lớp học phần?'):
                ok, msg = self.db.delete_lop_hp(tree.item(sel[0])['values'][0])
                if ok: refresh()
                else: messagebox.showwarning('Cảnh báo', msg)

        ents = _form_card(self.content_area,
                          [('Mã Lớp',10,0),('Môn',18,1),('GV',18,1),('Kỳ',14,1),('Thứ',9,1),('Ca',13,1)],
                          add, edit, delete, tree)
        tree.bind('<<TreeviewSelect>>', on_sel)
        refresh()

    # ── HỌC KỲ ─────────────────────────────────────────────────────────────
    def page_hk(self):
        cols = ('ID','Tên Kỳ','Năm học')
        tree = _make_tree(_card(self.content_area, None), cols, [55,200,160])
        def refresh():
            for i in tree.get_children(): tree.delete(i)
            for r in self.db.get_all_hoc_ky(): insert_tree_row(tree, r[:3])
        def add(): self.db.insert_hoc_ky(ents[0].get(), ents[1].get()); refresh()
        ents = _form_card(self.content_area, [('Tên kỳ',18,0),('Năm học',16,0)],
                          add, lambda: None, lambda: None, tree)
        refresh()

    # ── THÔNG BÁO ──────────────────────────────────────────────────────────
    def page_tb(self):
        cols = ('ID','Tiêu đề','Ngày đăng','Người đăng')
        tree = _make_tree(_card(self.content_area, None), cols, [55,300,140,120])
        def refresh():
            for i in tree.get_children(): tree.delete(i)
            for r in self.db.get_all_thong_bao(): insert_tree_row(tree, (r[0],r[1],r[3],r[4]))
        def add():
            t = ents[0].get().strip()
            if not t: messagebox.showwarning('Thiếu','Nhập tiêu đề!'); return
            self.db.insert_thong_bao(t, '(Nội dung...)', self.user_data[1]); refresh()
        def delete():
            sel = tree.selection()
            if sel and messagebox.askyesno('Xác nhận','Xóa thông báo này?'):
                self.db.delete_thong_bao(tree.item(sel[0])['values'][0]); refresh()
        ents = _form_card(self.content_area, [('Tiêu đề',46,0)], add, lambda: None, delete, tree)
        refresh()
