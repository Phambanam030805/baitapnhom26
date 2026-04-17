import sqlite3
import hashlib
from datetime import datetime

class Database:
    def __init__(self, db_file="ql_diem.db"):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.create_default_data()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                reference_id INTEGER
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS giang_vien (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ma_gv TEXT UNIQUE NOT NULL,
                ho_ten TEXT NOT NULL,
                khoa TEXT,
                email TEXT,
                sdt TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sinh_vien (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ma_sv TEXT UNIQUE NOT NULL,
                ho_ten TEXT NOT NULL,
                ngay_sinh TEXT,
                gioi_tinh TEXT,
                lop_hanh_chinh TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS hoc_ky (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ten_hoc_ky TEXT NOT NULL,
                nam_hoc TEXT NOT NULL,
                trang_thai TEXT DEFAULT 'mo'
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS mon_hoc (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ma_mh TEXT UNIQUE NOT NULL,
                ten_mh TEXT NOT NULL,
                so_tin_chi INTEGER,
                mo_ta TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS lop_hoc_phan (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ma_lop_hp TEXT UNIQUE NOT NULL,
                id_mon_hoc INTEGER,
                id_giang_vien INTEGER,
                id_hoc_ky INTEGER,
                status TEXT DEFAULT 'open',
                w_cc REAL DEFAULT 0.2,
                w_gk REAL DEFAULT 0.3,
                w_ck REAL DEFAULT 0.5,
                FOREIGN KEY (id_mon_hoc) REFERENCES mon_hoc (id),
                FOREIGN KEY (id_giang_vien) REFERENCES giang_vien (id),
                FOREIGN KEY (id_hoc_ky) REFERENCES hoc_ky (id)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS dang_ky_lop (
                id_lop_hp INTEGER,
                id_sinh_vien INTEGER,
                PRIMARY KEY (id_lop_hp, id_sinh_vien),
                FOREIGN KEY (id_lop_hp) REFERENCES lop_hoc_phan (id),
                FOREIGN KEY (id_sinh_vien) REFERENCES sinh_vien (id)
            )
        ''')
        self.cursor.execute('''
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
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS nhat_ky (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                hanh_dong TEXT,
                thoi_gian TEXT,
                chi_tiet TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        self.conn.commit()

    def create_default_data(self):
        self.add_user("admin", "123", "admin")

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def add_user(self, username, password, role, reference_id=None):
        hashed_pw = self.hash_password(password)
        try:
            self.cursor.execute("INSERT INTO users (username, password, role, reference_id) VALUES (?, ?, ?, ?)",
                               (username, hashed_pw, role, reference_id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def verify_login(self, username, password):
        hashed_pw = self.hash_password(password)
        self.cursor.execute("SELECT id, username, role, reference_id FROM users WHERE username=? AND password=?", 
                           (username, hashed_pw))
        return self.cursor.fetchone()

    def log_action(self, user_id, action, details):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO nhat_ky (user_id, hanh_dong, thoi_gian, chi_tiet) VALUES (?, ?, ?, ?)",
                           (user_id, action, now, details))
        self.conn.commit()

    def quy_doi_diem(self, tb):
        if tb >= 8.5: return ('A', 4.0)
        elif tb >= 7.0: return ('B', 3.0)
        elif tb >= 5.5: return ('C', 2.0)
        elif tb >= 4.0: return ('D', 1.0)
        else: return ('F', 0.0)

    def insert_sinh_vien(self, ma_sv, ho_ten, ngay_sinh, gioi_tinh, lop_hanh_chinh):
        try:
            self.cursor.execute("INSERT INTO sinh_vien (ma_sv, ho_ten, ngay_sinh, gioi_tinh, lop_hanh_chinh) VALUES (?, ?, ?, ?, ?)",
                               (ma_sv, ho_ten, ngay_sinh, gioi_tinh, lop_hanh_chinh))
            sv_id = self.cursor.lastrowid
            self.add_user(ma_sv, "123", "student", sv_id)
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_all_sinh_vien(self, search=""):
        if search:
            self.cursor.execute("SELECT * FROM sinh_vien WHERE ma_sv LIKE ? OR ho_ten LIKE ?", (f'%{search}%', f'%{search}%'))
        else:
            self.cursor.execute("SELECT * FROM sinh_vien")
        return self.cursor.fetchall()

    def insert_giang_vien(self, ma_gv, ho_ten, khoa, email, sdt):
        try:
            self.cursor.execute("INSERT INTO giang_vien (ma_gv, ho_ten, khoa, email, sdt) VALUES (?, ?, ?, ?, ?)",
                               (ma_gv, ho_ten, khoa, email, sdt))
            gv_id = self.cursor.lastrowid
            self.add_user(ma_gv, "123", "teacher", gv_id)
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_all_giang_vien(self, search=""):
        if search:
            self.cursor.execute("SELECT * FROM giang_vien WHERE ma_gv LIKE ? OR ho_ten LIKE ?", (f'%{search}%', f'%{search}%'))
        else:
            self.cursor.execute("SELECT * FROM giang_vien")
        return self.cursor.fetchall()

    def insert_mon_hoc(self, ma_mh, ten_mh, so_tin_chi, mo_ta=""):
        try:
            self.cursor.execute("INSERT INTO mon_hoc (ma_mh, ten_mh, so_tin_chi, mo_ta) VALUES (?, ?, ?, ?)",
                               (ma_mh, ten_mh, so_tin_chi, mo_ta))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_all_mon_hoc(self):
        self.cursor.execute("SELECT * FROM mon_hoc")
        return self.cursor.fetchall()

    def insert_hoc_ky(self, ten_hk, nam_hoc):
        self.cursor.execute("INSERT INTO hoc_ky (ten_hoc_ky, nam_hoc) VALUES (?, ?)", (ten_hk, nam_hoc))
        self.conn.commit()

    def get_all_hoc_ky(self):
        self.cursor.execute("SELECT * FROM hoc_ky")
        return self.cursor.fetchall()

    def insert_lop_hoc_phan(self, ma_lop_hp, id_mh, id_gv, id_hk, w_cc=0.2, w_gk=0.3, w_ck=0.5):
        try:
            self.cursor.execute('''
                INSERT INTO lop_hoc_phan (ma_lop_hp, id_mon_hoc, id_giang_vien, id_hoc_ky, w_cc, w_gk, w_ck) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (ma_lop_hp, id_mh, id_gv, id_hk, w_cc, w_gk, w_ck))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_all_lop_hp(self):
        query = '''
            SELECT lhp.id, lhp.ma_lop_hp, mh.ten_mh, gv.ho_ten, hk.ten_hoc_ky || ' ' || hk.nam_hoc, lhp.status
            FROM lop_hoc_phan lhp
            JOIN mon_hoc mh ON lhp.id_mon_hoc = mh.id
            JOIN giang_vien gv ON lhp.id_giang_vien = gv.id
            JOIN hoc_ky hk ON lhp.id_hoc_ky = hk.id
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def update_lhp_status(self, id_lhp, status):
        self.cursor.execute("UPDATE lop_hoc_phan SET status=? WHERE id=?", (status, id_lhp))
        self.conn.commit()

    def dang_ky_sinh_vien_vao_lop(self, id_lop_hp, id_sv):
        try:
            self.cursor.execute("INSERT INTO dang_ky_lop (id_lop_hp, id_sinh_vien) VALUES (?, ?)", (id_lop_hp, id_sv))
            self.cursor.execute("INSERT INTO diem (id_sinh_vien, id_lop_hp) VALUES (?, ?)", (id_sv, id_lop_hp))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def update_diem(self, id_sv, id_lop_hp, d_cc, d_gk, d_ck, user_id):
        self.cursor.execute("SELECT status, w_cc, w_gk, w_ck FROM lop_hoc_phan WHERE id=?", (id_lop_hp,))
        lhp_info = self.cursor.fetchone()
        if lhp_info[0] == 'closed':
            return False, "Lớp học phần này đã bị khóa điểm!"
        w_cc, w_gk, w_ck = lhp_info[1], lhp_info[2], lhp_info[3]
        d_tb = d_cc * w_cc + d_gk * w_gk + d_ck * w_ck
        d_chu, d_he4 = self.quy_doi_diem(d_tb)
        self.cursor.execute('''
            UPDATE diem SET diem_cc=?, diem_gk=?, diem_ck=?, diem_tb=?, diem_chu=?, diem_he4=?
            WHERE id_sinh_vien=? AND id_lop_hp=?
        ''', (d_cc, d_gk, d_ck, d_tb, d_chu, d_he4, id_sv, id_lop_hp))
        self.log_action(user_id, "UPDATE_GRADE", f"Sửa điểm SV {id_sv} Lớp {id_lop_hp}")
        self.conn.commit()
        return True, "Cập nhật thành công"

    def get_bang_diem_lop(self, id_lop_hp):
        query = '''
            SELECT sv.ma_sv, sv.ho_ten, d.diem_cc, d.diem_gk, d.diem_ck, d.diem_tb, d.diem_chu
            FROM diem d
            JOIN sinh_vien sv ON d.id_sinh_vien = sv.id
            WHERE d.id_lop_hp = ?
        '''
        self.cursor.execute(query, (id_lop_hp,))
        return self.cursor.fetchall()

    def get_diem_sinh_vien(self, id_sv):
        query = '''
            SELECT mh.ma_mh, mh.ten_mh, hk.ten_hoc_ky, d.diem_cc, d.diem_gk, d.diem_ck, d.diem_tb, d.diem_chu, d.diem_he4
            FROM diem d
            JOIN lop_hoc_phan lhp ON d.id_lop_hp = lhp.id
            JOIN mon_hoc mh ON lhp.id_mon_hoc = mh.id
            JOIN hoc_ky hk ON lhp.id_hoc_ky = hk.id
            WHERE d.id_sinh_vien = ?
        '''
        self.cursor.execute(query, (id_sv,))
        return self.cursor.fetchall()

    def get_gpa(self, id_sv):
        query = '''
            SELECT SUM(d.diem_he4 * mh.so_tin_chi), SUM(mh.so_tin_chi)
            FROM diem d
            JOIN lop_hoc_phan lhp ON d.id_lop_hp = lhp.id
            JOIN mon_hoc mh ON lhp.id_mon_hoc = mh.id
            WHERE d.id_sinh_vien = ? AND d.diem_tb IS NOT NULL
        '''
        self.cursor.execute(query, (id_sv,))
        res = self.cursor.fetchone()
        if res and res[1] and res[1] > 0:
            return round(res[0] / res[1], 2)
        return 0.0

    def get_nhat_ky(self):
        query = '''
            SELECT u.username, n.hanh_dong, n.thoi_gian, n.chi_tiet
            FROM nhat_ky n
            JOIN users u ON n.user_id = u.id
            ORDER BY n.id DESC
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()
