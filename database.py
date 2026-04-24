import sqlite3
import hashlib
from datetime import datetime

class Database:
    def __init__(self, db_file="ql_diem.db"):
        self.conn = sqlite3.connect(db_file, timeout=10)
        self.cursor = self.conn.cursor()
        try:
            self.create_tables()
            self.create_default_data()
        except Exception as e:
            print(f"[DB Init Error] {e}")

    def create_tables(self):
        self.cursor.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                reference_id INTEGER,
                is_active INTEGER DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS khoa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ma_khoa TEXT UNIQUE NOT NULL,
                ten_khoa TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS lop_hc (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ma_lop TEXT UNIQUE NOT NULL,
                ten_lop TEXT NOT NULL,
                id_khoa INTEGER,
                FOREIGN KEY (id_khoa) REFERENCES khoa (id)
            );
            CREATE TABLE IF NOT EXISTS giang_vien (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ma_gv TEXT UNIQUE NOT NULL,
                ho_ten TEXT NOT NULL,
                khoa TEXT,
                email TEXT,
                sdt TEXT
            );
            CREATE TABLE IF NOT EXISTS sinh_vien (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ma_sv TEXT UNIQUE NOT NULL,
                ho_ten TEXT NOT NULL,
                ngay_sinh TEXT,
                gioi_tinh TEXT,
                id_lop_hc INTEGER,
                FOREIGN KEY (id_lop_hc) REFERENCES lop_hc (id)
            );
            CREATE TABLE IF NOT EXISTS hoc_ky (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ten_hoc_ky TEXT NOT NULL,
                nam_hoc TEXT NOT NULL,
                trang_thai TEXT DEFAULT 'mo'
            );
            CREATE TABLE IF NOT EXISTS mon_hoc (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ma_mh TEXT UNIQUE NOT NULL,
                ten_mh TEXT NOT NULL,
                so_tin_chi INTEGER,
                mo_ta TEXT
            );
            CREATE TABLE IF NOT EXISTS lop_hoc_phan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ma_lop_hp TEXT UNIQUE NOT NULL,
                id_mon_hoc INTEGER,
                id_giang_vien INTEGER,
                id_hoc_ky INTEGER,
                thu TEXT,
                ca_hoc TEXT,
                status TEXT DEFAULT 'open',
                w_cc REAL DEFAULT 0.2,
                w_gk REAL DEFAULT 0.3,
                w_ck REAL DEFAULT 0.5,
                FOREIGN KEY (id_mon_hoc) REFERENCES mon_hoc (id),
                FOREIGN KEY (id_giang_vien) REFERENCES giang_vien (id),
                FOREIGN KEY (id_hoc_ky) REFERENCES hoc_ky (id)
            );
            CREATE TABLE IF NOT EXISTS dang_ky_lop (
                id_lop_hp INTEGER,
                id_sinh_vien INTEGER,
                PRIMARY KEY (id_lop_hp, id_sinh_vien),
                FOREIGN KEY (id_lop_hp) REFERENCES lop_hoc_phan (id),
                FOREIGN KEY (id_sinh_vien) REFERENCES sinh_vien (id)
            );
            CREATE TABLE IF NOT EXISTS diem (
                id_sinh_vien INTEGER,
                id_lop_hp INTEGER,
                diem_cc REAL DEFAULT 0,
                diem_gk REAL DEFAULT 0,
                diem_ck REAL DEFAULT 0,
                diem_tb REAL DEFAULT 0,
                diem_chu TEXT,
                diem_he4 REAL,
                PRIMARY KEY (id_sinh_vien, id_lop_hp),
                FOREIGN KEY (id_sinh_vien) REFERENCES sinh_vien (id),
                FOREIGN KEY (id_lop_hp) REFERENCES lop_hoc_phan (id)
            );
            CREATE TABLE IF NOT EXISTS nhat_ky (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                hanh_dong TEXT,
                thoi_gian TEXT,
                chi_tiet TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
            CREATE TABLE IF NOT EXISTS thong_bao (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tieu_de TEXT,
                noi_dung TEXT,
                ngay_dang TEXT,
                nguoi_dang TEXT
            );
        ''')
        self.conn.commit()

    def create_default_data(self):
        self.cursor.execute("SELECT 1 FROM users WHERE username='admin'")
        if not self.cursor.fetchone():
            self.add_user("admin", "123", "admin")
        
        self.cursor.execute("SELECT 1 FROM hoc_ky")
        if not self.cursor.fetchone():
            self.insert_hoc_ky("Học kỳ 1", "2023-2024")

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def add_user(self, username, password, role, reference_id=None):
        hashed_pw = self.hash_password(password)
        try:
            self.cursor.execute("INSERT INTO users (username, password, role, reference_id) VALUES (?, ?, ?, ?)",
                               (username, hashed_pw, role, reference_id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError: return False

    def verify_login(self, username, password):
        hashed_pw = self.hash_password(password)
        self.cursor.execute(
            "SELECT id, username, role, reference_id, is_active FROM users "
            "WHERE username=? AND password=? AND is_active=1",
            (username, hashed_pw)
        )
        return self.cursor.fetchone()

    def log_action(self, user_id, action, details):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO nhat_ky (user_id, hanh_dong, thoi_gian, chi_tiet) VALUES (?, ?, ?, ?)", (user_id, action, now, details))
        self.conn.commit()

    def quy_doi_diem(self, tb):
        if tb >= 8.5: return ('A', 4.0)
        elif tb >= 7.0: return ('B', 3.0)
        elif tb >= 5.5: return ('C', 2.0)
        elif tb >= 4.0: return ('D', 1.0)
        else: return ('F', 0.0)

    # --- KHOA ---
    def insert_khoa(self, ma, ten):
        try:
            self.cursor.execute("INSERT INTO khoa (ma_khoa, ten_khoa) VALUES (?, ?)", (ma, ten))
            self.conn.commit(); return True
        except: return False

    def get_all_khoa(self):
        self.cursor.execute("SELECT * FROM khoa"); return self.cursor.fetchall()

    def update_khoa(self, id_k, ma, ten):
        try:
            self.cursor.execute("UPDATE khoa SET ma_khoa=?, ten_khoa=? WHERE id=?", (ma, ten, id_k))
            self.conn.commit(); return True
        except: return False

    def delete_khoa(self, id_k):
        # Kiểm tra lớp HC
        self.cursor.execute("SELECT 1 FROM lop_hc WHERE id_khoa=?", (id_k,))
        if self.cursor.fetchone(): return False, "Đang có lớp hành chính thuộc khoa này!"
        self.cursor.execute("DELETE FROM khoa WHERE id=?", (id_k,))
        self.conn.commit(); return True, "Xóa thành công"

    # --- LỚP HÀNH CHÍNH ---
    def insert_lop_hc(self, ma, ten, id_k):
        try:
            self.cursor.execute("INSERT INTO lop_hc (ma_lop, ten_lop, id_khoa) VALUES (?, ?, ?)", (ma, ten, id_k))
            self.conn.commit(); return True
        except: return False

    def get_all_lop_hc(self):
        self.cursor.execute("SELECT l.id, l.ma_lop, l.ten_lop, k.ten_khoa FROM lop_hc l LEFT JOIN khoa k ON l.id_khoa=k.id")
        return self.cursor.fetchall()

    def update_lop_hc(self, id_l, ma, ten, id_k):
        try:
            self.cursor.execute("UPDATE lop_hc SET ma_lop=?, ten_lop=?, id_khoa=? WHERE id=?", (ma, ten, id_k, id_l))
            self.conn.commit(); return True
        except: return False

    def delete_lop_hc(self, id_l):
        self.cursor.execute("SELECT 1 FROM sinh_vien WHERE id_lop_hc=?", (id_l,))
        if self.cursor.fetchone(): return False, "Đang có sinh viên thuộc lớp này!"
        self.cursor.execute("DELETE FROM lop_hc WHERE id=?", (id_l,))
        self.conn.commit(); return True, "Xóa thành công"

    # --- GIẢNG VIÊN ---
    def insert_giang_vien(self, ma, ho_ten, khoa, email, sdt):
        try:
            self.cursor.execute("INSERT INTO giang_vien (ma_gv, ho_ten, khoa, email, sdt) VALUES (?, ?, ?, ?, ?)", (ma, ho_ten, khoa, email, sdt))
            gv_id = self.cursor.lastrowid
            self.add_user(ma, "123", "teacher", gv_id)
            self.conn.commit(); return True
        except: return False

    def get_all_giang_vien(self):
        self.cursor.execute("SELECT * FROM giang_vien"); return self.cursor.fetchall()

    def update_giang_vien(self, id_gv, ma, ho_ten, khoa, email, sdt):
        try:
            # Lấy mã cũ để cập nhật username trong bảng users
            self.cursor.execute("SELECT ma_gv FROM giang_vien WHERE id=?", (id_gv,))
            old_ma = self.cursor.fetchone()[0]
            
            self.cursor.execute("UPDATE giang_vien SET ma_gv=?, ho_ten=?, khoa=?, email=?, sdt=? WHERE id=?", (ma, ho_ten, khoa, email, sdt, id_gv))
            if old_ma != ma:
                self.cursor.execute("UPDATE users SET username=? WHERE username=? AND role='teacher'", (ma, old_ma))
            
            self.conn.commit(); return True
        except: return False

    def delete_giang_vien(self, id_gv):
        self.cursor.execute("SELECT 1 FROM lop_hoc_phan WHERE id_giang_vien=?", (id_gv,))
        if self.cursor.fetchone(): return False, "Giảng viên đang có lớp dạy, không thể xóa!"
        self.cursor.execute("DELETE FROM users WHERE role='teacher' AND reference_id=?", (id_gv,))
        self.cursor.execute("DELETE FROM giang_vien WHERE id=?", (id_gv,))
        self.conn.commit(); return True, "Xóa thành công"

    # --- SINH VIÊN ---
    def insert_sinh_vien(self, ma, ho_ten, ngay_sinh, gioi_tinh, id_lhc):
        try:
            self.cursor.execute("INSERT INTO sinh_vien (ma_sv, ho_ten, ngay_sinh, gioi_tinh, id_lop_hc) VALUES (?, ?, ?, ?, ?)", (ma, ho_ten, ngay_sinh, gioi_tinh, id_lhc))
            sv_id = self.cursor.lastrowid
            self.add_user(ma, "123", "student", sv_id)
            self.conn.commit(); return True
        except: return False

    def get_all_sinh_vien(self):
        self.cursor.execute("SELECT s.id, s.ma_sv, s.ho_ten, s.ngay_sinh, s.gioi_tinh, l.ten_lop FROM sinh_vien s LEFT JOIN lop_hc l ON s.id_lop_hc=l.id")
        return self.cursor.fetchall()

    def update_sinh_vien(self, id_sv, ma, ho_ten, ns, gt, id_lhc):
        try:
            if not ma or not ho_ten: return False
            # Lấy mã cũ để cập nhật username trong bảng users
            self.cursor.execute("SELECT ma_sv FROM sinh_vien WHERE id=?", (id_sv,))
            res = self.cursor.fetchone()
            if not res: return False
            old_ma = res[0]

            self.cursor.execute("UPDATE sinh_vien SET ma_sv=?, ho_ten=?, ngay_sinh=?, gioi_tinh=?, id_lop_hc=? WHERE id=?", (ma, ho_ten, ns, gt, id_lhc, id_sv))
            if old_ma != ma:
                self.cursor.execute("UPDATE users SET username=? WHERE username=? AND role='student'", (ma, old_ma))
            
            self.conn.commit(); return True
        except Exception as e:
            print(f"Error update_sinh_vien: {e}")
            return False

    def delete_sinh_vien(self, id_sv):
        self.cursor.execute("SELECT 1 FROM dang_ky_lop WHERE id_sinh_vien=?", (id_sv,))
        if self.cursor.fetchone(): return False, "Sinh viên đang đăng ký học, không thể xóa!"
        self.cursor.execute("DELETE FROM users WHERE role='student' AND reference_id=?", (id_sv,))
        self.cursor.execute("DELETE FROM sinh_vien WHERE id=?", (id_sv,))
        self.conn.commit(); return True, "Xóa thành công"

    # --- MÔN HỌC ---
    def insert_mon_hoc(self, ma, ten, stc, mo_ta=""):
        try:
            self.cursor.execute("INSERT INTO mon_hoc (ma_mh, ten_mh, so_tin_chi, mo_ta) VALUES (?, ?, ?, ?)", (ma, ten, stc, mo_ta))
            self.conn.commit(); return True
        except: return False

    def get_all_mon_hoc(self):
        self.cursor.execute("SELECT * FROM mon_hoc"); return self.cursor.fetchall()

    def update_mon_hoc(self, id_m, ma, ten, stc, mo_ta):
        try:
            self.cursor.execute("UPDATE mon_hoc SET ma_mh=?, ten_mh=?, so_tin_chi=?, mo_ta=? WHERE id=?", (ma, ten, stc, mo_ta, id_m))
            self.conn.commit(); return True
        except: return False

    def delete_mon_hoc(self, id_m):
        self.cursor.execute("SELECT 1 FROM lop_hoc_phan WHERE id_mon_hoc=?", (id_m,))
        if self.cursor.fetchone(): return False, "Môn học đang có lớp học phần, không thể xóa!"
        self.cursor.execute("DELETE FROM mon_hoc WHERE id=?", (id_m,))
        self.conn.commit(); return True, "Xóa thành công"

    # --- LỚP HỌC PHẦN ---
    def insert_lop_hoc_phan(self, ma, id_m, id_g, id_h, thu, ca):
        try:
            self.cursor.execute("INSERT INTO lop_hoc_phan (ma_lop_hp, id_mon_hoc, id_giang_vien, id_hoc_ky, thu, ca_hoc) VALUES (?, ?, ?, ?, ?, ?)", (ma, id_m, id_g, id_h, thu, ca))
            self.conn.commit(); return True
        except: return False

    def update_lop_hoc_phan(self, id_l, ma, id_m, id_g, id_h, thu, ca):
        try:
            self.cursor.execute("UPDATE lop_hoc_phan SET ma_lop_hp=?, id_mon_hoc=?, id_giang_vien=?, id_hoc_ky=?, thu=?, ca_hoc=? WHERE id=?", (ma, id_m, id_g, id_h, thu, ca, id_l))
            self.conn.commit(); return True
        except: return False

    def get_all_lop_hp(self):
        query = '''
            SELECT l.id, l.ma_lop_hp, m.ten_mh, g.ho_ten, h.ten_hoc_ky || ' ' || h.nam_hoc, 
                   l.thu || ' (Ca ' || l.ca_hoc || ')', l.status
            FROM lop_hoc_phan l
            LEFT JOIN mon_hoc m ON l.id_mon_hoc=m.id
            LEFT JOIN giang_vien g ON l.id_giang_vien=g.id
            LEFT JOIN hoc_ky h ON l.id_hoc_ky=h.id
        '''
        self.cursor.execute(query); return self.cursor.fetchall()

    def delete_lop_hp(self, id_l):
        self.cursor.execute("SELECT 1 FROM dang_ky_lop WHERE id_lop_hp=?", (id_l,))
        if self.cursor.fetchone(): return False, "Lớp đã có sinh viên đăng ký, không thể xóa!"
        self.cursor.execute("DELETE FROM lop_hoc_phan WHERE id=?", (id_l,))
        self.conn.commit(); return True, "Xóa thành công"

    # --- HỌC KỲ ---
    def insert_hoc_ky(self, ten, nam):
        self.cursor.execute("INSERT INTO hoc_ky (ten_hoc_ky, nam_hoc) VALUES (?, ?)", (ten, nam))
        self.conn.commit()

    def get_all_hoc_ky(self):
        self.cursor.execute("SELECT * FROM hoc_ky"); return self.cursor.fetchall()

    def delete_hoc_ky(self, id_h):
        self.cursor.execute("DELETE FROM hoc_ky WHERE id=?", (id_h,))
        self.conn.commit(); return True

    # --- ĐIỂM & ĐĂNG KÝ ---
    def dang_ky_sinh_vien_vao_lop(self, id_lop, id_sv):
        try:
            self.cursor.execute("INSERT INTO dang_ky_lop (id_lop_hp, id_sinh_vien) VALUES (?, ?)", (id_lop, id_sv))
            self.cursor.execute("INSERT INTO diem (id_sinh_vien, id_lop_hp) VALUES (?, ?)", (id_sv, id_lop))
            self.conn.commit(); return True
        except: return False

    def update_diem(self, id_sv, id_lop, d_cc, d_gk, d_ck, user_id):
        self.cursor.execute("SELECT status, w_cc, w_gk, w_ck FROM lop_hoc_phan WHERE id=?", (id_lop,))
        info = self.cursor.fetchone()
        if not info or info[0] == 'closed': return False, "Lớp đã khóa!"
        w_cc, w_gk, w_ck = info[1], info[2], info[3]
        d_tb = d_cc * w_cc + d_gk * w_gk + d_ck * w_ck
        d_chu, d_he4 = self.quy_doi_diem(d_tb)
        self.cursor.execute("UPDATE diem SET diem_cc=?, diem_gk=?, diem_ck=?, diem_tb=?, diem_chu=?, diem_he4=? WHERE id_sinh_vien=? AND id_lop_hp=?", (d_cc, d_gk, d_ck, d_tb, d_chu, d_he4, id_sv, id_lop))
        self.conn.commit(); return True, "Cập nhật thành công"

    def get_lhp_by_giang_vien(self, id_gv):
        query = "SELECT l.id, l.ma_lop_hp, m.ten_mh, l.thu || ' (Ca ' || l.ca_hoc || ')', l.status FROM lop_hoc_phan l JOIN mon_hoc m ON l.id_mon_hoc=m.id WHERE l.id_giang_vien=?"
        self.cursor.execute(query, (id_gv,)); return self.cursor.fetchall()

    def get_bang_diem_lop(self, id_l):
        query = "SELECT s.id, s.ma_sv, s.ho_ten, d.diem_cc, d.diem_gk, d.diem_ck, d.diem_tb, d.diem_chu FROM diem d JOIN sinh_vien s ON d.id_sinh_vien=s.id WHERE d.id_lop_hp=?"
        self.cursor.execute(query, (id_l,)); return self.cursor.fetchall()

    def get_diem_sinh_vien(self, id_sv):
        query = "SELECT m.ma_mh, m.ten_mh, m.so_tin_chi, d.diem_cc, d.diem_gk, d.diem_ck, d.diem_tb, d.diem_chu, d.diem_he4 FROM diem d JOIN lop_hoc_phan l ON d.id_lop_hp=l.id JOIN mon_hoc m ON l.id_mon_hoc=m.id WHERE d.id_sinh_vien=?"
        self.cursor.execute(query, (id_sv,)); return self.cursor.fetchall()

    def get_gpa(self, id_sv):
        query = "SELECT SUM(d.diem_he4 * m.so_tin_chi), SUM(m.so_tin_chi) FROM diem d JOIN lop_hoc_phan l ON d.id_lop_hp=l.id JOIN mon_hoc m ON l.id_mon_hoc=m.id WHERE d.id_sinh_vien=? AND d.diem_he4 IS NOT NULL"
        self.cursor.execute(query, (id_sv,))
        res = self.cursor.fetchone()
        return round(res[0]/res[1], 2) if res and res[0] is not None and res[1] else 0.0

    def get_available_classes(self, id_sv):
        query = "SELECT l.id, l.ma_lop_hp, m.ten_mh, g.ho_ten, l.thu || ' (Ca ' || l.ca_hoc || ')' FROM lop_hoc_phan l JOIN mon_hoc m ON l.id_mon_hoc=m.id JOIN giang_vien g ON l.id_giang_vien=g.id WHERE l.status='open' AND l.id NOT IN (SELECT id_lop_hp FROM dang_ky_lop WHERE id_sinh_vien=?)"
        self.cursor.execute(query, (id_sv,)); return self.cursor.fetchall()

    def get_all_thong_bao(self):
        self.cursor.execute("SELECT * FROM thong_bao ORDER BY id DESC"); return self.cursor.fetchall()

    def insert_thong_bao(self, tieu_de, noi_dung, nguoi):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO thong_bao (tieu_de, noi_dung, ngay_dang, nguoi_dang) VALUES (?, ?, ?, ?)", (tieu_de, noi_dung, now, nguoi))
        self.conn.commit(); return True

    def delete_thong_bao(self, id_t):
        self.cursor.execute("DELETE FROM thong_bao WHERE id=?", (id_t,)); self.conn.commit()

    def get_user_profile(self, role, ref_id):
        if role == 'student': self.cursor.execute("SELECT s.ma_sv, s.ho_ten, l.ten_lop, s.ngay_sinh, s.gioi_tinh FROM sinh_vien s LEFT JOIN lop_hc l ON s.id_lop_hc=l.id WHERE s.id=?", (ref_id,))
        elif role == 'teacher': self.cursor.execute("SELECT * FROM giang_vien WHERE id=?", (ref_id,))
        else: return None
        return self.cursor.fetchone()

    def get_teacher_stats(self, id_gv):
        query = "SELECT m.ten_mh, l.ma_lop_hp, COUNT(d.id_sinh_vien), SUM(CASE WHEN d.diem_tb >= 4.0 THEN 1 ELSE 0 END), SUM(CASE WHEN d.diem_tb < 4.0 THEN 1 ELSE 0 END) FROM lop_hoc_phan l JOIN mon_hoc m ON l.id_mon_hoc=m.id LEFT JOIN diem d ON l.id=d.id_lop_hp WHERE l.id_giang_vien=? GROUP BY l.id"
        self.cursor.execute(query, (id_gv,)); return self.cursor.fetchall()

    def delete_user(self, id_u):
        self.cursor.execute("DELETE FROM users WHERE id=?", (id_u,)); self.conn.commit(); return True

    def get_all_users(self):
        self.cursor.execute(
            "SELECT id, username, role, is_active FROM users ORDER BY role, username"
        )
        return self.cursor.fetchall()

    def update_user_role(self, id_u, new_role):
        try:
            self.cursor.execute("UPDATE users SET role=? WHERE id=?", (new_role, id_u))
            self.conn.commit(); return True
        except: return False

    def insert_user(self, username, password, role):
        hpw = self.hash_password(password)
        try:
            self.cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                                (username, hpw, role))
            self.conn.commit(); return True
        except: return False

    def update_user(self, id_u, username, role):
        try:
            self.cursor.execute("UPDATE users SET username=?, role=? WHERE id=?",
                                (username, role, id_u))
            self.conn.commit(); return True
        except: return False

    def toggle_user_active(self, id_u):
        """Đổi trạng thái active/inactive của tài khoản."""
        self.cursor.execute("SELECT is_active FROM users WHERE id=?", (id_u,))
        row = self.cursor.fetchone()
        if not row: return False
        new_status = 0 if row[0] == 1 else 1
        self.cursor.execute("UPDATE users SET is_active=? WHERE id=?", (new_status, id_u))
        self.conn.commit(); return True

    def reset_password(self, id_u, new_password="123"):
        hpw = self.hash_password(new_password)
        self.cursor.execute("UPDATE users SET password=? WHERE id=?", (hpw, id_u))
        self.conn.commit(); return True

    def get_nhat_ky(self):
        self.cursor.execute("SELECT u.username, n.hanh_dong, n.thoi_gian, n.chi_tiet FROM nhat_ky n JOIN users u ON n.user_id=u.id ORDER BY n.id DESC")
        return self.cursor.fetchall()
