import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

class StyleConfig:
    NAVY_DARK = "#1e3a8a"
    NAVY_MED = "#1d4ed8"
    SIDEBAR_BG = "#0f172a"
    SIDEBAR_HOVER = "#1e293b"
    CONTENT_BG = "#f1f5f9"
    WHITE = "#ffffff"
    TEXT_MAIN = "#1e293b"
    TEXT_SUB = "#64748b"
    DANGER = "#ef4444"
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"

    FONT_FAMILY = "Segoe UI"
    FONT_SM = (FONT_FAMILY, 9)
    FONT_MD = (FONT_FAMILY, 10)
    FONT_BOLD = (FONT_FAMILY, 10, "bold")
    FONT_LG = (FONT_FAMILY, 14, "bold")
    FONT_TITLE = (FONT_FAMILY, 18, "bold")

    @staticmethod
    def apply(root):
        style = ttk.Style(root)
        style.theme_use('clam')
        style.configure("Treeview", font=StyleConfig.FONT_MD, rowheight=35, fieldbackground=StyleConfig.WHITE, borderwidth=0)
        style.configure("Treeview.Heading", font=StyleConfig.FONT_BOLD, background="#e2e8f0", foreground=StyleConfig.NAVY_DARK, padding=10)
        style.map("Treeview", background=[('selected', "#dbeafe")], foreground=[('selected', StyleConfig.NAVY_DARK)])
        style.configure("TButton", font=StyleConfig.FONT_BOLD, padding=[12, 6])
        style.configure("Primary.TButton", background=StyleConfig.NAVY_MED, foreground=StyleConfig.WHITE)
        style.configure("Danger.TButton", background=StyleConfig.DANGER, foreground=StyleConfig.WHITE)
        style.configure("Warning.TButton", background=StyleConfig.WARNING, foreground=StyleConfig.WHITE)
        return style

class LoginWindow:
    def __init__(self, root, on_success):
        self.root, self.on_success, self.db = root, on_success, Database()
        StyleConfig.apply(self.root)
        self.root.title("Hệ thống Quản lý Đào tạo v4.0")
        self.root.geometry("1000x700")
        self.root.configure(bg=StyleConfig.NAVY_DARK)
        self.root.eval('tk::PlaceWindow . center')
        
        card = tk.Frame(root, bg=StyleConfig.WHITE, padx=50, pady=50)
        card.place(relx=0.5, rely=0.5, anchor="center", width=400, height=500)
        
        tk.Label(card, text="ĐĂNG NHẬP", font=StyleConfig.FONT_TITLE, fg=StyleConfig.NAVY_DARK, bg=StyleConfig.WHITE).pack(pady=(0, 30))
        tk.Label(card, text="Username", font=StyleConfig.FONT_SM, fg=StyleConfig.TEXT_SUB, bg=StyleConfig.WHITE).pack(anchor='w')
        self.ent_u = ttk.Entry(card); self.ent_u.pack(fill='x', pady=(5, 20)); self.ent_u.insert(0, "admin")
        tk.Label(card, text="Password", font=StyleConfig.FONT_SM, fg=StyleConfig.TEXT_SUB, bg=StyleConfig.WHITE).pack(anchor='w')
        self.ent_p = ttk.Entry(card, show="*"); self.ent_p.pack(fill='x', pady=(5, 40)); self.ent_p.insert(0, "123")
        tk.Button(card, text="ĐĂNG NHẬP", bg=StyleConfig.NAVY_MED, fg="white", font=StyleConfig.FONT_BOLD, relief="flat", height=2, command=self.login).pack(fill='x')

    def login(self):
        res = self.db.verify_login(self.ent_u.get(), self.ent_p.get())
        if res: self.on_success(res)
        else: messagebox.showerror("Lỗi", "Sai thông tin đăng nhập")

class DashboardBase:
    def __init__(self, root, user_data, on_logout):
        self.root, self.user_data, self.db, self.on_logout = root, user_data, Database(), on_logout
        StyleConfig.apply(self.root)
        self.root.geometry("1400x900")
        
        self.sidebar = tk.Frame(self.root, bg=StyleConfig.SIDEBAR_BG, width=260)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)
        
        tk.Label(self.sidebar, text="UNIVERSITY PORTAL", font=StyleConfig.FONT_BOLD, fg="white", bg=StyleConfig.SIDEBAR_BG, pady=30).pack()
        
        self.header = tk.Frame(self.root, bg=StyleConfig.WHITE, height=70)
        self.header.pack(side='top', fill='x')
        
        tk.Label(self.header, text=f"Chào, {user_data[1]}", font=StyleConfig.FONT_BOLD, bg=StyleConfig.WHITE).pack(side='right', padx=20)
        tk.Button(self.header, text="Đăng xuất", fg=StyleConfig.DANGER, bg=StyleConfig.WHITE, relief="flat", command=self.on_logout).pack(side='right')
        
        self.content_area = tk.Frame(self.root, bg=StyleConfig.CONTENT_BG, padx=20, pady=20)
        self.content_area.pack(expand=True, fill='both')

    def add_menu_item(self, text, icon, cmd):
        btn = tk.Button(self.sidebar, text=f"  {icon}  {text}", font=StyleConfig.FONT_MD, fg="#94a3b8", bg=StyleConfig.SIDEBAR_BG, relief="flat", anchor='w', padx=30, pady=12, command=cmd)
        btn.pack(fill='x')
        btn.bind("<Enter>", lambda e: btn.config(bg=StyleConfig.SIDEBAR_HOVER, fg="white"))
        btn.bind("<Leave>", lambda e: btn.config(bg=StyleConfig.SIDEBAR_BG, fg="#94a3b8"))

class AdminDashboard(DashboardBase):
    def __init__(self, root, user_data, on_logout):
        super().__init__(root, user_data, on_logout)
        self.setup_menu()
        self.show_page("SV")

    def setup_menu(self):
        menu = [("Sinh viên", "👥", "SV"), ("Giảng viên", "👨‍🏫", "GV"), ("Lớp HC", "🏢", "LHC"), ("Khoa", "🏫", "KH"), ("Môn học", "📚", "MH"), ("Lớp HP", "📅", "LHP"), ("Học kỳ", "⏱️", "HK"), ("Thông báo", "📢", "TB")]
        for t, i, c in menu: self.add_menu_item(t, i, lambda code=c: self.show_page(code))

    def show_page(self, code):
        for w in self.content_area.winfo_children(): w.destroy()
        if code == "SV": self.page_sv()
        elif code == "GV": self.page_gv()
        elif code == "LHC": self.page_lhc()
        elif code == "KH": self.page_kh()
        elif code == "MH": self.page_mh()
        elif code == "LHP": self.page_lhp()
        elif code == "HK": self.page_hk()
        elif code == "TB": self.page_tb()

    def create_crud_header(self, title, fields, add_cmd, edit_cmd, del_cmd, tree):
        card = tk.Frame(self.content_area, bg=StyleConfig.WHITE, padx=20, pady=20)
        card.pack(fill='x', pady=(0, 20))
        tk.Label(card, text=title, font=StyleConfig.FONT_BOLD, bg=StyleConfig.WHITE).pack(anchor='w', pady=(0,10))
        
        form = tk.Frame(card, bg=StyleConfig.WHITE); form.pack(fill='x')
        ents = []
        for i, (lbl, width, is_cb) in enumerate(fields):
            tk.Label(form, text=lbl, bg=StyleConfig.WHITE).grid(row=0, column=i, padx=5, sticky='w')
            if is_cb:
                e = ttk.Combobox(form, width=width, state="readonly")
            else:
                e = ttk.Entry(form, width=width)
            e.grid(row=1, column=i, padx=5, pady=5)
            ents.append(e)
        
        def on_select(event):
            sel = tree.selection()
            if sel:
                values = tree.item(sel[0])['values']
                # Bỏ ID (cột đầu tiên), lấy các giá trị tiếp theo điền vào form
                for i, val in enumerate(values[1:]):
                    if i < len(ents):
                        if isinstance(ents[i], ttk.Combobox):
                            ents[i].set(val)
                        else:
                            ents[i].delete(0, tk.END)
                            ents[i].insert(0, val)
        
        tree.bind("<<TreeviewSelect>>", on_select)

        btn_f = tk.Frame(card, bg=StyleConfig.WHITE); btn_f.pack(fill='x', pady=10)
        ttk.Button(btn_f, text="+ Thêm", style="Primary.TButton", command=add_cmd).pack(side='left', padx=5)
        ttk.Button(btn_f, text="✎ Sửa", style="Warning.TButton", command=edit_cmd).pack(side='left', padx=5)
        ttk.Button(btn_f, text="Xóa", style="Danger.TButton", command=del_cmd).pack(side='left', padx=5)
        return ents

    # --- QUẢN LÝ KHOA ---
    def page_kh(self):
        tree = ttk.Treeview(self.content_area, columns=(1,2,3), show='headings')
        for i, h in enumerate(["ID","Mã Khoa","Tên Khoa"]): tree.heading(i+1, text=h)
        def refresh():
            for i in tree.get_children(): tree.delete(i)
            for r in self.db.get_all_khoa(): tree.insert("", "end", values=r)
        def add():
            if self.db.insert_khoa(ents[0].get(), ents[1].get()):
                messagebox.showinfo("Thành công", "Đã thêm khoa mới"); refresh()
            else: messagebox.showerror("Lỗi", "Không thể thêm (có thể trùng mã)")
        def edit():
            sel = tree.selection()
            if sel:
                if self.db.update_khoa(tree.item(sel[0])['values'][0], ents[0].get(), ents[1].get()):
                    messagebox.showinfo("Thành công", "Đã cập nhật thông tin"); refresh()
                else: messagebox.showerror("Lỗi", "Cập nhật thất bại")
        def delete():
            sel = tree.selection()
            if sel:
                if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa?"):
                    ok, msg = self.db.delete_khoa(tree.item(sel[0])['values'][0])
                    if ok: messagebox.showinfo("Thành công", msg); refresh()
                    else: messagebox.showwarning("Cảnh báo", msg)
        ents = self.create_crud_header("QUẢN LÝ KHOA", [("Mã Khoa", 20, 0), ("Tên Khoa", 40, 0)], add, edit, delete, tree)
        tree.pack(fill='both', expand=True); refresh()

    # --- QUẢN LÝ LỚP HÀNH CHÍNH ---
    def page_lhc(self):
        tree = ttk.Treeview(self.content_area, columns=(1,2,3,4), show='headings')
        for i, h in enumerate(["ID","Mã Lớp","Tên Lớp","Khoa"]): tree.heading(i+1, text=h)
        def refresh():
            for i in tree.get_children(): tree.delete(i)
            for r in self.db.get_all_lop_hc(): tree.insert("", "end", values=r)
            khs = self.db.get_all_khoa()
            self.kh_map = {r[2]: r[0] for r in khs}
            ents[2]['values'] = list(self.kh_map.keys())
        def add():
            if self.db.insert_lop_hc(ents[0].get(), ents[1].get(), self.kh_map.get(ents[2].get())):
                messagebox.showinfo("Thành công", "Đã thêm lớp hành chính"); refresh()
            else: messagebox.showerror("Lỗi", "Thêm thất bại")
        def edit():
            sel = tree.selection()
            if sel:
                if self.db.update_lop_hc(tree.item(sel[0])['values'][0], ents[0].get(), ents[1].get(), self.kh_map.get(ents[2].get())):
                    messagebox.showinfo("Thành công", "Đã cập nhật"); refresh()
                else: messagebox.showerror("Lỗi", "Thất bại")
        def delete():
            sel = tree.selection()
            if sel:
                if messagebox.askyesno("Xác nhận", "Xóa lớp này?"):
                    ok, msg = self.db.delete_lop_hc(tree.item(sel[0])['values'][0])
                    if ok: refresh()
                    else: messagebox.showwarning("Cảnh báo", msg)
        ents = self.create_crud_header("QUẢN LÝ LỚP HÀNH CHÍNH", [("Mã Lớp", 20, 0), ("Tên Lớp", 30, 0), ("Khoa", 25, 1)], add, edit, delete, tree)
        tree.pack(fill='both', expand=True); refresh()

    # --- QUẢN LÝ SINH VIÊN ---
    def page_sv(self):
        tree = ttk.Treeview(self.content_area, columns=(1,2,3,4,5,6), show='headings')
        for i, h in enumerate(["ID","MSV","Họ tên","Ngày sinh","GT","Lớp HC"]): tree.heading(i+1, text=h)
        def refresh():
            for i in tree.get_children(): tree.delete(i)
            for r in self.db.get_all_sinh_vien(): tree.insert("", "end", values=r)
            lhcs = self.db.get_all_lop_hc()
            self.lhc_map = {r[2]: r[0] for r in lhcs}
            ents[4]['values'] = list(self.lhc_map.keys())
        def add():
            if self.db.insert_sinh_vien(ents[0].get(), ents[1].get(), ents[2].get(), ents[3].get(), self.lhc_map.get(ents[4].get())):
                messagebox.showinfo("Thành công", "Đã thêm sinh viên và tài khoản đăng nhập"); refresh()
            else: messagebox.showerror("Lỗi", "Thêm thất bại (trùng mã)")
        def edit():
            sel = tree.selection()
            if sel:
                if self.db.update_sinh_vien(tree.item(sel[0])['values'][0], ents[0].get(), ents[1].get(), ents[2].get(), ents[3].get(), self.lhc_map.get(ents[4].get())):
                    messagebox.showinfo("Thành công", "Cập nhật thành công"); refresh()
                else: messagebox.showerror("Lỗi", "Cập nhật thất bại (vui lòng điền đủ thông tin)")
        def delete():
            sel = tree.selection()
            if sel:
                if messagebox.askyesno("Xác nhận", "Xóa sinh viên này?"):
                    ok, msg = self.db.delete_sinh_vien(tree.item(sel[0])['values'][0])
                    if ok: refresh()
                    else: messagebox.showwarning("Cảnh báo", msg)
        ents = self.create_crud_header("QUẢN LÝ SINH VIÊN", [("MSV",15,0),("Họ tên",25,0),("Ngày sinh",15,0),("GT",10,0),("Lớp HC",20,1)], add, edit, delete, tree)
        tree.pack(fill='both', expand=True); refresh()

    # --- QUẢN LÝ GIẢNG VIÊN ---
    def page_gv(self):
        tree = ttk.Treeview(self.content_area, columns=(1,2,3,4,5,6), show='headings')
        for i, h in enumerate(["ID","Mã GV","Họ tên","Khoa","Email","SĐT"]): tree.heading(i+1, text=h)
        def refresh():
            for i in tree.get_children(): tree.delete(i)
            for r in self.db.get_all_giang_vien(): tree.insert("", "end", values=r)
        def add():
            if self.db.insert_giang_vien(ents[0].get(), ents[1].get(), ents[2].get(), ents[3].get(), ents[4].get()):
                messagebox.showinfo("Thành công", "Đã thêm giảng viên"); refresh()
            else: messagebox.showerror("Lỗi", "Thêm thất bại")
        def edit():
            sel = tree.selection()
            if sel:
                if self.db.update_giang_vien(tree.item(sel[0])['values'][0], ents[0].get(), ents[1].get(), ents[2].get(), ents[3].get(), ents[4].get()):
                    messagebox.showinfo("Thành công", "Cập nhật thành công"); refresh()
                else: messagebox.showerror("Lỗi", "Thất bại")
        def delete():
            sel = tree.selection()
            if sel:
                if messagebox.askyesno("Xác nhận", "Xóa giảng viên này?"):
                    ok, msg = self.db.delete_giang_vien(tree.item(sel[0])['values'][0])
                    if ok: refresh()
                    else: messagebox.showwarning("Cảnh báo", msg)
        ents = self.create_crud_header("QUẢN LÝ GIẢNG VIÊN", [("Mã GV",15,0),("Họ tên",25,0),("Khoa",20,0),("Email",20,0),("SĐT",15,0)], add, edit, delete, tree)
        tree.pack(fill='both', expand=True); refresh()

    # --- QUẢN LÝ MÔN HỌC ---
    def page_mh(self):
        tree = ttk.Treeview(self.content_area, columns=(1,2,3,4), show='headings')
        for i, h in enumerate(["ID","Mã MH","Tên MH","Số TC"]): tree.heading(i+1, text=h)
        def refresh():
            for i in tree.get_children(): tree.delete(i)
            for r in self.db.get_all_mon_hoc(): tree.insert("", "end", values=r[:4])
        def add():
            try:
                if self.db.insert_mon_hoc(ents[0].get(), ents[1].get(), int(ents[2].get() or 0)):
                    messagebox.showinfo("Thành công", "Đã thêm môn học"); refresh()
                else: messagebox.showerror("Lỗi", "Thêm thất bại")
            except: messagebox.showerror("Lỗi", "Số tín chỉ phải là số")
        def edit():
            sel = tree.selection()
            if sel:
                try:
                    if self.db.update_mon_hoc(tree.item(sel[0])['values'][0], ents[0].get(), ents[1].get(), int(ents[2].get() or 0), ""):
                        messagebox.showinfo("Thành công", "Cập nhật thành công"); refresh()
                    else: messagebox.showerror("Lỗi", "Thất bại")
                except: messagebox.showerror("Lỗi", "Số tín chỉ phải là số")
        def delete():
            sel = tree.selection()
            if sel:
                if messagebox.askyesno("Xác nhận", "Xóa môn học này?"):
                    ok, msg = self.db.delete_mon_hoc(tree.item(sel[0])['values'][0])
                    if ok: refresh()
                    else: messagebox.showwarning("Cảnh báo", msg)
        ents = self.create_crud_header("QUẢN LÝ MÔN HỌC", [("Mã MH",15,0),("Tên MH",30,0),("Số TC",10,0)], add, edit, delete, tree)
        tree.pack(fill='both', expand=True); refresh()

    # --- QUẢN LÝ LỚP HỌC PHẦN (CÓ CA HỌC) ---
    def page_lhp(self):
        tree = ttk.Treeview(self.content_area, columns=(1,2,3,4,5,6,7), show='headings')
        for i, h in enumerate(["ID","Mã Lớp","Môn","GV","Học kỳ","Lịch học","ST"]): tree.heading(i+1, text=h)
        def refresh():
            for i in tree.get_children(): tree.delete(i)
            for r in self.db.get_all_lop_hp(): tree.insert("", "end", values=r)
            self.mh_map = {f"{r[1]}-{r[2]}": r[0] for r in self.db.get_all_mon_hoc()}
            self.gv_map = {f"{r[1]}-{r[2]}": r[0] for r in self.db.get_all_giang_vien()}
            self.hk_map = {f"{r[1]} {r[2]}": r[0] for r in self.db.get_all_hoc_ky()}
            ents[1]['values'] = list(self.mh_map.keys())
            ents[2]['values'] = list(self.gv_map.keys())
            ents[3]['values'] = list(self.hk_map.keys())
            ents[4]['values'] = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
            ents[5]['values'] = ["1 (7h-9h)", "2 (9h-11h)", "3 (13h-15h)", "4 (15h-17h)", "5 (18h-20h)"]
        def add():
            if self.db.insert_lop_hoc_phan(ents[0].get(), self.mh_map.get(ents[1].get()), self.gv_map.get(ents[2].get()), self.hk_map.get(ents[3].get()), ents[4].get(), ents[5].get()): refresh()
        def edit():
            sel = tree.selection()
            if sel: self.db.update_lop_hoc_phan(tree.item(sel[0])['values'][0], ents[0].get(), self.mh_map.get(ents[1].get()), self.gv_map.get(ents[2].get()), self.hk_map.get(ents[3].get()), ents[4].get(), ents[5].get()); refresh()
        def delete():
            sel = tree.selection()
            if sel:
                ok, msg = self.db.delete_lop_hp(tree.item(sel[0])['values'][0])
                if ok: refresh()
                else: messagebox.showwarning("Cảnh báo", msg)
        ents = self.create_crud_header("LỚP HỌC PHẦN & LỊCH HỌC", [("Mã Lớp",12,0),("Môn",20,1),("GV",20,1),("Kỳ",15,1),("Thứ",10,1),("Ca",15,1)], add, edit, delete, tree)
        tree.pack(fill='both', expand=True); refresh()

    def page_hk(self):
        tree = ttk.Treeview(self.content_area, columns=(1,2,3), show='headings')
        for i, h in enumerate(["ID","Tên Kỳ","Năm học"]): tree.heading(i+1, text=h)
        def refresh():
            for i in tree.get_children(): tree.delete(i)
            for r in self.db.get_all_hoc_ky(): tree.insert("", "end", values=r[:3])
        def add(): self.db.insert_hoc_ky(ents[0].get(), ents[1].get()); refresh()
        def delete():
            sel = tree.selection()
            if sel: self.db.delete_hoc_ky(tree.item(sel[0])['values'][0]); refresh()
        ents = self.create_crud_header("HỌC KỲ", [("Tên kỳ",20,0),("Năm học",20,0)], add, lambda: None, delete, tree)
        tree.pack(fill='both', expand=True); refresh()

    def page_tb(self):
        tree = ttk.Treeview(self.content_area, columns=(1,2,3,4), show='headings')
        for i, h in enumerate(["ID","Tiêu đề","Ngày đăng","Người đăng"]): tree.heading(i+1, text=h)
        def refresh():
            for i in tree.get_children(): tree.delete(i)
            for r in self.db.get_all_thong_bao(): tree.insert("", "end", values=(r[0],r[1],r[3],r[4]))
        def add(): self.db.insert_thong_bao(ents[0].get(), "Nội dung...", "Admin"); refresh()
        def delete():
            sel = tree.selection()
            if sel: self.db.delete_thong_bao(tree.item(sel[0])['values'][0]); refresh()
        ents = self.create_crud_header("THÔNG BÁO", [("Tiêu đề",50,0)], add, lambda: None, delete, tree)
        tree.pack(fill='both', expand=True); refresh()

class TeacherDashboard(DashboardBase):
    def __init__(self, root, user_data, on_logout):
        super().__init__(root, user_data, on_logout)
        self.add_menu_item("Nhập điểm", "📝", self.page_grade)
        self.add_menu_item("Thông báo", "📢", self.page_announcements)
        self.page_grade()

    def page_grade(self):
        for w in self.content_area.winfo_children(): w.destroy()
        tk.Label(self.content_area, text="NHẬP ĐIỂM SINH VIÊN", font=StyleConfig.FONT_LG, fg=StyleConfig.NAVY_DARK, bg=StyleConfig.CONTENT_BG).pack(anchor='w', pady=(0,10))
        
        f_top = tk.Frame(self.content_area, bg=StyleConfig.WHITE, padx=20, pady=15); f_top.pack(fill='x', pady=(0,20))
        tk.Label(f_top, text="Chọn lớp:", bg=StyleConfig.WHITE).pack(side='left')
        cb = ttk.Combobox(f_top, width=40, state="readonly"); cb.pack(side='left', padx=10)
        
        tree = ttk.Treeview(self.content_area, columns=(1,2,3,4,5,6,7,8), show='headings')
        for i, h in enumerate(["ID","MSV","Họ tên","CC","GK","CK","TB","Chữ"]): tree.heading(i+1, text=h)
        tree.pack(fill='both', expand=True)
        
        f_bot = tk.Frame(self.content_area, bg=StyleConfig.WHITE, padx=20, pady=20); f_bot.pack(fill='x', pady=20)
        ents = []
        for i, l in enumerate(["CC","GK","CK"]):
            tk.Label(f_bot, text=l, bg=StyleConfig.WHITE).grid(row=0, column=i*2)
            e = ttk.Entry(f_bot, width=10); e.grid(row=0, column=i*2+1, padx=5); ents.append(e)
            
        def save():
            sel = tree.selection()
            if sel and cb.get():
                self.db.update_diem(tree.item(sel[0])['values'][0], self.lhp_map[cb.get()], float(ents[0].get() or 0), float(ents[1].get() or 0), float(ents[2].get() or 0), self.user_data[0])
                load_sv(None)

        ttk.Button(f_bot, text="Lưu điểm", style="Primary.TButton", command=save).grid(row=0, column=6, padx=20)

        def load_sv(e):
            for i in tree.get_children(): tree.delete(i)
            if cb.get():
                for r in self.db.get_bang_diem_lop(self.lhp_map[cb.get()]): tree.insert("", "end", values=r)

        lhps = self.db.get_lhp_by_giang_vien(self.user_data[3])
        self.lhp_map = {f"{r[1]} - {r[2]} ({r[3]})": r[0] for r in lhps}
        cb['values'] = list(self.lhp_map.keys())
        cb.bind("<<ComboboxSelected>>", load_sv)

    def page_announcements(self):
        for w in self.content_area.winfo_children(): w.destroy()
        for r in self.db.get_all_thong_bao():
            card = tk.Frame(self.content_area, bg=StyleConfig.WHITE, padx=20, pady=15); card.pack(fill='x', pady=5)
            tk.Label(card, text=r[1], font=StyleConfig.FONT_BOLD, bg=StyleConfig.WHITE).pack(anchor='w')
            tk.Label(card, text=r[2], bg=StyleConfig.WHITE).pack(anchor='w')

class StudentDashboard(DashboardBase):
    def __init__(self, root, user_data, on_logout):
        super().__init__(root, user_data, on_logout)
        self.add_menu_item("Bảng điểm", "📜", self.page_grade)
        self.add_menu_item("Đăng ký môn", "📝", self.page_reg)
        self.page_grade()

    def page_grade(self):
        for w in self.content_area.winfo_children(): w.destroy()
        tk.Label(self.content_area, text=f"GPA Tích lũy: {self.db.get_gpa(self.user_data[3])}", font=StyleConfig.FONT_LG, bg=StyleConfig.CONTENT_BG).pack(anchor='w', pady=10)
        tree = ttk.Treeview(self.content_area, columns=(1,2,3,4,5,6,7,8,9), show='headings')
        for i, h in enumerate(["Mã MH","Tên MH","TC","CC","GK","CK","TB","Chữ","Hệ 4"]): tree.heading(i+1, text=h)
        tree.pack(fill='both', expand=True)
        for r in self.db.get_diem_sinh_vien(self.user_data[3]): tree.insert("", "end", values=r)

    def page_reg(self):
        for w in self.content_area.winfo_children(): w.destroy()
        tree = ttk.Treeview(self.content_area, columns=(1,2,3,4,5), show='headings')
        for i, h in enumerate(["ID","Mã Lớp","Tên Môn","Giảng viên","Lịch học"]): tree.heading(i+1, text=h)
        tree.pack(fill='both', expand=True)
        def reg():
            sel = tree.selection()
            if sel:
                if self.db.dang_ky_sinh_vien_vao_lop(tree.item(sel[0])['values'][0], self.user_data[3]):
                    messagebox.showinfo("Thành công", "Đăng ký thành công!"); refresh()
        def refresh():
            for i in tree.get_children(): tree.delete(i)
            for r in self.db.get_available_classes(self.user_data[3]): tree.insert("", "end", values=r)
        ttk.Button(self.content_area, text="Đăng ký lớp đã chọn", command=reg).pack(pady=10); refresh()
