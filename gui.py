import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import Database
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

class LoginWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success
        self.root.title("SIS - Đăng nhập")
        self.root.geometry("400x300")
        self.db = Database()
        self.root.eval('tk::PlaceWindow . center')
        main_frame = ttk.Frame(root, padding="30")
        main_frame.pack(expand=True, fill='both')
        ttk.Label(main_frame, text="HỆ THỐNG QUẢN LÝ ĐÀO TẠO", font=("Arial", 14, "bold")).pack(pady=20)
        ttk.Label(main_frame, text="Tên đăng nhập:").pack(anchor='w')
        self.ent_user = ttk.Entry(main_frame)
        self.ent_user.pack(fill='x', pady=5)
        ttk.Label(main_frame, text="Mật khẩu:").pack(anchor='w')
        self.ent_pw = ttk.Entry(main_frame, show="*")
        self.ent_pw.pack(fill='x', pady=5)
        ttk.Button(main_frame, text="Đăng nhập", command=self.login).pack(pady=20, fill='x')
    def login(self):
        user_data = self.db.verify_login(self.ent_user.get(), self.ent_pw.get())
        if user_data: self.on_success(user_data)
        else: messagebox.showerror("Lỗi", "Sai thông tin đăng nhập!")

class AdminDashboard:
    def __init__(self, root, user_data):
        self.root = root
        self.db = Database()
        self.root.title(f"Admin: {user_data[1]}")
        self.root.geometry("1100x700")
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both')
        self.frame_sv = ttk.Frame(self.notebook)
        self.frame_gv = ttk.Frame(self.notebook)
        self.frame_mh = ttk.Frame(self.notebook)
        self.frame_lhp = ttk.Frame(self.notebook)
        self.frame_log = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_sv, text="Sinh viên")
        self.notebook.add(self.frame_gv, text="Giảng viên")
        self.notebook.add(self.frame_mh, text="Môn học")
        self.notebook.add(self.frame_lhp, text="Lớp HP")
        self.notebook.add(self.frame_log, text="Nhật ký")
        self.setup_sv_tab()
        self.setup_gv_tab()
        self.setup_mh_tab()
        self.setup_lhp_tab()
        self.setup_log_tab()
    def setup_sv_tab(self):
        f = ttk.LabelFrame(self.frame_sv, text="Thêm SV")
        f.pack(fill='x', padx=10, pady=10)
        self.sv_ent = [ttk.Entry(f) for _ in range(5)]
        lbls = ["Mã SV", "Họ tên", "Ngày sinh", "GT", "Lớp HC"]
        for i, l in enumerate(lbls):
            ttk.Label(f, text=l).grid(row=0, column=i*2)
            self.sv_ent[i].grid(row=0, column=i*2+1)
        ttk.Button(f, text="Thêm", command=self.add_sv).grid(row=1, column=0)
        self.sv_tree = ttk.Treeview(self.frame_sv, columns=(1,2,3,4,5,6), show='headings')
        for i, c in enumerate(["ID","Mã SV","Họ tên","Ngày sinh","GT","Lớp"]): self.sv_tree.heading(i+1, text=c)
        self.sv_tree.pack(fill='both', expand=True)
        self.refresh_sv()
    def add_sv(self):
        if self.db.insert_sinh_vien(*[e.get() for e in self.sv_ent]): self.refresh_sv()
    def refresh_sv(self):
        for i in self.sv_tree.get_children(): self.sv_tree.delete(i)
        for r in self.db.get_all_sinh_vien(): self.sv_tree.insert("", "end", values=r)
    def setup_gv_tab(self):
        f = ttk.LabelFrame(self.frame_gv, text="Thêm GV")
        f.pack(fill='x', padx=10, pady=10)
        self.gv_ent = [ttk.Entry(f) for _ in range(5)]
        lbls = ["Mã GV", "Họ tên", "Khoa", "Email", "SĐT"]
        for i, l in enumerate(lbls):
            ttk.Label(f, text=l).grid(row=0, column=i*2)
            self.gv_ent[i].grid(row=0, column=i*2+1)
        ttk.Button(f, text="Thêm", command=self.add_gv).grid(row=1, column=0)
        self.gv_tree = ttk.Treeview(self.frame_gv, columns=(1,2,3,4,5,6), show='headings')
        for i, c in enumerate(["ID","Mã GV","Họ tên","Khoa","Email","SĐT"]): self.gv_tree.heading(i+1, text=c)
        self.gv_tree.pack(fill='both', expand=True)
        self.refresh_gv()
    def add_gv(self):
        if self.db.insert_giang_vien(*[e.get() for e in self.gv_ent]): self.refresh_gv()
    def refresh_gv(self):
        for i in self.gv_tree.get_children(): self.gv_tree.delete(i)
        for r in self.db.get_all_giang_vien(): self.gv_tree.insert("", "end", values=r)
    def setup_mh_tab(self):
        f = ttk.LabelFrame(self.frame_mh, text="Môn học")
        f.pack(fill='x')
        self.mh_ent = [ttk.Entry(f) for _ in range(3)]
        for i, l in enumerate(["Mã MH", "Tên MH", "STC"]):
            ttk.Label(f, text=l).grid(row=0, column=i*2)
            self.mh_ent[i].grid(row=0, column=i*2+1)
        ttk.Button(f, text="Thêm", command=self.add_mh).grid(row=1, column=0)
        self.mh_tree = ttk.Treeview(self.frame_mh, columns=(1,2,3,4), show='headings')
        for i, c in enumerate(["ID","Mã","Tên","STC"]): self.mh_tree.heading(i+1, text=c)
        self.mh_tree.pack(fill='both', expand=True)
        self.refresh_mh()
    def add_mh(self):
        if self.db.insert_mon_hoc(self.mh_ent[0].get(), self.mh_ent[1].get(), int(self.mh_ent[2].get())): self.refresh_mh()
    def refresh_mh(self):
        for i in self.mh_tree.get_children(): self.mh_tree.delete(i)
        for r in self.db.get_all_mon_hoc(): self.mh_tree.insert("", "end", values=r)
    def setup_lhp_tab(self):
        f = ttk.LabelFrame(self.frame_lhp, text="Lớp HP")
        f.pack(fill='x')
        self.lhp_ent = [ttk.Entry(f) for _ in range(4)]
        for i, l in enumerate(["Mã Lớp", "ID MH", "ID GV", "ID HK"]):
            ttk.Label(f, text=l).grid(row=0, column=i*2)
            self.lhp_ent[i].grid(row=0, column=i*2+1)
        ttk.Button(f, text="Thêm", command=self.add_lhp).grid(row=1, column=0)
        self.lhp_tree = ttk.Treeview(self.frame_lhp, columns=(1,2,3,4,5,6), show='headings')
        for i, c in enumerate(["ID","Mã Lớp","Môn","GV","HK","TT"]): self.lhp_tree.heading(i+1, text=c)
        self.lhp_tree.pack(fill='both', expand=True)
        self.refresh_lhp()
    def add_lhp(self):
        if self.db.insert_lop_hoc_phan(self.lhp_ent[0].get(), int(self.lhp_ent[1].get()), int(self.lhp_ent[2].get()), int(self.lhp_ent[3].get())): self.refresh_lhp()
    def refresh_lhp(self):
        for i in self.lhp_tree.get_children(): self.lhp_tree.delete(i)
        for r in self.db.get_all_lop_hp(): self.lhp_tree.insert("", "end", values=r)
    def setup_log_tab(self):
        self.log_tree = ttk.Treeview(self.frame_log, columns=(1,2,3,4), show='headings')
        for i, c in enumerate(["User","Hành động","Thời gian","Chi tiết"]): self.log_tree.heading(i+1, text=c)
        self.log_tree.pack(fill='both', expand=True)
        ttk.Button(self.frame_log, text="Refresh", command=self.refresh_log).pack()
    def refresh_log(self):
        for i in self.log_tree.get_children(): self.log_tree.delete(i)
        for r in self.db.get_nhat_ky(): self.log_tree.insert("", "end", values=r)

class TeacherDashboard:
    def __init__(self, root, user_data):
        self.root, self.user_data, self.db = root, user_data, Database()
        self.root.title(f"Giảng viên: {user_data[1]}"), self.root.geometry("900x600")
        f = ttk.Frame(self.root, padding="10")
        f.pack(fill='both', expand=True)
        ttk.Label(f, text="ID Lớp:").pack(side='top')
        self.ent_lhp = ttk.Entry(f)
        self.ent_lhp.pack(side='top')
        ttk.Button(f, text="Tải lớp", command=self.load).pack(side='top')
        self.tree = ttk.Treeview(f, columns=(1,2,3,4,5,6,7), show='headings')
        for i, c in enumerate(["Mã SV","Họ tên","CC","GK","CK","TB","Chữ"]): self.tree.heading(i+1, text=c)
        self.tree.pack(fill='both', expand=True)
        ef = ttk.LabelFrame(f, text="Nhập điểm")
        ef.pack(fill='x')
        self.ents = [ttk.Entry(ef, width=10) for _ in range(4)]
        for i, l in enumerate(["ID SV", "CC", "GK", "CK"]):
            ttk.Label(ef, text=l).grid(row=0, column=i*2)
            self.ents[i].grid(row=0, column=i*2+1)
        ttk.Button(ef, text="Lưu", command=self.save).grid(row=0, column=8)
    def load(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        self.data = self.db.get_bang_diem_lop(int(self.ent_lhp.get()))
        for r in self.data: self.tree.insert("", "end", values=r)
    def save(self):
        s, m = self.db.update_diem(int(self.ents[0].get()), int(self.ent_lhp.get()), float(self.ents[1].get()), float(self.ents[2].get()), float(self.ents[3].get()), self.user_data[0])
        messagebox.showinfo("TB", m), self.load()

class StudentDashboard:
    def __init__(self, root, user_data):
        self.root, self.user_data, self.db = root, user_data, Database()
        self.root.title(f"Sinh viên: {user_data[1]}"), self.root.geometry("800x500")
        f = ttk.Frame(self.root, padding="20")
        f.pack(fill='both', expand=True)
        gpa = self.db.get_gpa(self.user_data[3])
        ttk.Label(f, text=f"GPA: {gpa}", font=("Arial", 12, "bold")).pack()
        self.tree = ttk.Treeview(f, columns=(1,2,3,4,5,6,7,8,9), show='headings')
        for i, c in enumerate(["Mã MH","Tên MH","HK","CC","GK","CK","TB","Chữ","Hệ 4"]): self.tree.heading(i+1, text=c)
        self.tree.pack(fill='both', expand=True)
        for r in self.db.get_diem_sinh_vien(self.user_data[3]): self.tree.insert("", "end", values=r)
