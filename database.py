import mysql.connector
import hashlib
from datetime import datetime

class Database:
    def __init__(self, host="localhost", user="root", password="", database="ql_diem_dh"):
        self._db_cfg = dict(host=host, user=user, password=password, database=database)
        try:
            self.conn = mysql.connector.connect(**self._db_cfg)
            self.cursor = self.conn.cursor(buffered=True)
            self.create_tables()
            self.migrate_tables()
            self.create_default_data()
            self.seed_data_if_empty() 
        except mysql.connector.Error as e:
            print(f"[DB Connection Error] {e}")
            raise e

    def _ping(self):
        """Bug #2: Tu dong ket noi lai neu MySQL da dong connection (sau 8h idle)."""
        try:
            self.conn.ping(reconnect=True, attempts=3, delay=2)
        except:
            try:
                self.conn = mysql.connector.connect(**self._db_cfg)
                self.cursor = self.conn.cursor(buffered=True)
            except mysql.connector.Error as e:
                print(f"[DB Reconnect Error] {e}")

    def create_tables(self):
        tables = [
            '''CREATE TABLE IF NOT EXISTS users (
                id INT PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL,
                reference_id INT,
                is_active INT DEFAULT 1
            )''',
            '''CREATE TABLE IF NOT EXISTS khoa (
                id INT PRIMARY KEY AUTO_INCREMENT,
                ma_khoa VARCHAR(20) UNIQUE NOT NULL,
                ten_khoa VARCHAR(100) NOT NULL
            )''',
            '''CREATE TABLE IF NOT EXISTS lop_hc (
                id INT PRIMARY KEY AUTO_INCREMENT,
                ma_lop VARCHAR(20) UNIQUE NOT NULL,
                ten_lop VARCHAR(100) NOT NULL,
                id_khoa INT,
                FOREIGN KEY (id_khoa) REFERENCES khoa (id)
            )''',
            '''CREATE TABLE IF NOT EXISTS giang_vien (
                id INT PRIMARY KEY AUTO_INCREMENT,
                ma_gv VARCHAR(20) UNIQUE NOT NULL,
                ho_ten VARCHAR(100) NOT NULL,
                khoa VARCHAR(100),
                email VARCHAR(100),
                sdt VARCHAR(15)
            )''',
            '''CREATE TABLE IF NOT EXISTS sinh_vien (
                id INT PRIMARY KEY AUTO_INCREMENT,
                ma_sv VARCHAR(20) UNIQUE NOT NULL,
                ho_ten VARCHAR(100) NOT NULL,
                ngay_sinh VARCHAR(20),
                gioi_tinh VARCHAR(10),
                id_lop_hc INT,
                FOREIGN KEY (id_lop_hc) REFERENCES lop_hc (id)
            )''',
            '''CREATE TABLE IF NOT EXISTS hoc_ky (
                id INT PRIMARY KEY AUTO_INCREMENT,
                ten_hoc_ky VARCHAR(50) NOT NULL,
                nam_hoc VARCHAR(20) NOT NULL,
                trang_thai VARCHAR(20) DEFAULT 'mo'
            )''',
            '''CREATE TABLE IF NOT EXISTS mon_hoc (
                id INT PRIMARY KEY AUTO_INCREMENT,
                ma_mh VARCHAR(20) UNIQUE NOT NULL,
                ten_mh VARCHAR(100) NOT NULL,
                so_tin_chi INT,
                mo_ta TEXT
            )''',
            '''CREATE TABLE IF NOT EXISTS lop_hoc_phan (
                id INT PRIMARY KEY AUTO_INCREMENT,
                ma_lop_hp VARCHAR(20) UNIQUE NOT NULL,
                id_mon_hoc INT,
                id_giang_vien INT,
                id_hoc_ky INT,
                thu VARCHAR(20),
                ca_hoc VARCHAR(20),
                status VARCHAR(20) DEFAULT 'open',
                w_cc FLOAT DEFAULT 0.2,
                w_gk FLOAT DEFAULT 0.3,
                w_ck FLOAT DEFAULT 0.5,
                FOREIGN KEY (id_mon_hoc) REFERENCES mon_hoc (id),
                FOREIGN KEY (id_giang_vien) REFERENCES giang_vien (id),
                FOREIGN KEY (id_hoc_ky) REFERENCES hoc_ky (id)
            )''',
            '''CREATE TABLE IF NOT EXISTS dang_ky_lop (
                id_lop_hp INT,
                id_sinh_vien INT,
                PRIMARY KEY (id_lop_hp, id_sinh_vien),
                FOREIGN KEY (id_lop_hp) REFERENCES lop_hoc_phan (id),
                FOREIGN KEY (id_sinh_vien) REFERENCES sinh_vien (id)
            )''',
            '''CREATE TABLE IF NOT EXISTS diem (
                id_sinh_vien INT,
                id_lop_hp INT,
                lan_thi INT DEFAULT 1,
                diem_cc FLOAT DEFAULT NULL,
                diem_gk FLOAT DEFAULT NULL,
                diem_ck FLOAT DEFAULT NULL,
                diem_tb FLOAT DEFAULT NULL,
                diem_chu VARCHAR(5),
                diem_he4 FLOAT,
                trang_thai VARCHAR(20) DEFAULT \'Đang học\',
                PRIMARY KEY (id_sinh_vien, id_lop_hp),
                FOREIGN KEY (id_sinh_vien) REFERENCES sinh_vien (id),
                FOREIGN KEY (id_lop_hp) REFERENCES lop_hoc_phan (id)
            )''',
            '''CREATE TABLE IF NOT EXISTS nhat_ky (
                id INT PRIMARY KEY AUTO_INCREMENT,
                user_id INT,
                hanh_dong TEXT,
                thoi_gian VARCHAR(30),
                chi_tiet TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )''',
            '''CREATE TABLE IF NOT EXISTS thong_bao (
                id INT PRIMARY KEY AUTO_INCREMENT,
                tieu_de VARCHAR(255),
                noi_dung TEXT,
                ngay_dang VARCHAR(30),
                nguoi_dang VARCHAR(100)
            )''',
            '''CREATE TABLE IF NOT EXISTS diem_danh (
                id INT AUTO_INCREMENT PRIMARY KEY,
                id_sinh_vien INT,
                id_lop_hp INT,
                ngay DATE,
                trang_thai TINYINT DEFAULT 1,
                FOREIGN KEY (id_sinh_vien) REFERENCES sinh_vien(id),
                FOREIGN KEY (id_lop_hp) REFERENCES lop_hoc_phan(id)
            )'''
        ]
        for table_sql in tables:
            try:
                self.cursor.execute(table_sql)
                # Đảm bảo dọn sạch kết quả nếu có (tránh lỗi sync)
                while self.cursor.nextset(): pass
            except Exception as e:
                print(f"[DB Error] {e}")
        self.conn.commit()

    def migrate_tables(self):
        """Tự động thêm các cột còn thiếu vào DB đã tồn tại (XAMPP sync)."""
        migrations = [
            # Fix bug nghiêm trọng: trang_thai bị dùng trong code nhưng chưa có trong bảng
            ("diem", "trang_thai",
             "ALTER TABLE diem ADD COLUMN trang_thai VARCHAR(20) DEFAULT 'Đang học'"),
            # Thêm lan_thi để hỗ trợ thi lại
            ("diem", "lan_thi",
             "ALTER TABLE diem ADD COLUMN lan_thi INT DEFAULT 1 AFTER id_lop_hp"),
            # Thêm ngay_bat_dau / ngay_ket_thuc vào hoc_ky
            ("hoc_ky", "ngay_bat_dau",
             "ALTER TABLE hoc_ky ADD COLUMN ngay_bat_dau DATE DEFAULT NULL"),
            ("hoc_ky", "ngay_ket_thuc",
             "ALTER TABLE hoc_ky ADD COLUMN ngay_ket_thuc DATE DEFAULT NULL"),
            # Thêm si_so_toi_da cho lop_hoc_phan
            ("lop_hoc_phan", "si_so_toi_da",
             "ALTER TABLE lop_hoc_phan ADD COLUMN si_so_toi_da INT DEFAULT NULL"),
        ]
        for table, column, sql in migrations:
            try:
                # Kiểm tra xem cột đã tồn tại chưa qua INFORMATION_SCHEMA
                self.cursor.execute(
                    "SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS "
                    "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND COLUMN_NAME = %s",
                    (table, column)
                )
                if self.cursor.fetchone()[0] == 0:
                    self.cursor.execute(sql)
                    print(f"[Migration] [OK] Da them cot '{column}' vao bang '{table}'")
                else:
                    print(f"[Migration] [SKIP] Bo qua '{table}.{column}' - da ton tai")
            except Exception as e:
                print(f"[Migration] [ERR] Loi khi migrate '{table}.{column}': {e}")
        self.conn.commit()

    def create_default_data(self):
        self.cursor.execute("SELECT 1 FROM users WHERE username='admin'")
        if not self.cursor.fetchone():
            self.add_user("admin", "123", "admin")
        
        self.cursor.execute("SELECT 1 FROM hoc_ky")
        if not self.cursor.fetchone():
            self.insert_hoc_ky("Học kỳ 1", "2023-2024")

    def seed_data_if_empty(self):
        """Nếu DB chưa có dữ liệu, tự động tạo 1 ít dữ liệu mẫu để chạy thử."""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM sinh_vien")
            if self.cursor.fetchone()[0] == 0:
                print("[System] Phat hien DB trong, dang nap du lieu mau...")
                # 1. Khoa & Mon hoc
                self.insert_khoa("CNTT", "Cong nghe thong tin")
                self.insert_khoa("KT", "Kinh te")
                self.insert_mon_hoc("MH01", "Lap trinh Python", 3)
                self.insert_mon_hoc("MH02", "Co so du lieu", 3)
                
                # 2. Lop hanh chinh
                self.cursor.execute("SELECT id FROM khoa LIMIT 1")
                res_kh = self.cursor.fetchone()
                if res_kh:
                    kh_id = res_kh[0]
                    self.insert_lop_hc("L01", "CNTT K15", kh_id)
                
                # 3. Giang vien (Pass mac dinh: 123)
                self.insert_giang_vien("GV01", "Nguyen Van A", "CNTT", "gv1@edu.vn", "0123456789")
                
                # 4. Sinh vien (Pass mac dinh: 123)
                self.cursor.execute("SELECT id FROM lop_hc LIMIT 1")
                res_lhc = self.cursor.fetchone()
                if res_lhc:
                    lhc_id = res_lhc[0]
                    self.insert_sinh_vien("2024001", "Tran Van B", "01/01/2004", "Nam", lhc_id)
                    self.insert_sinh_vien("2024002", "Le Thi C", "15/05/2004", "Nu", lhc_id)
                
                print("[System] Da nap du lieu mau thanh cong!")
        except Exception as e:
            print(f"[Seed Error] {e}")

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def add_user(self, username, password, role, reference_id=None):
        hashed_pw = self.hash_password(password)
        try:
            self.cursor.execute("INSERT INTO users (username, password, role, reference_id) VALUES (%s, %s, %s, %s)",
                               (username, hashed_pw, role, reference_id))
            self.conn.commit()
            return True
        except mysql.connector.Error: return False

    def verify_login(self, username, password):
        hashed_pw = self.hash_password(password)
        self.cursor.execute(
            "SELECT id, username, role, reference_id, is_active FROM users "
            "WHERE username=%s AND password=%s AND is_active=1",
            (username, hashed_pw)
        )
        return self.cursor.fetchone()

    def log_action(self, user_id, action, details):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO nhat_ky (user_id, hanh_dong, thoi_gian, chi_tiet) VALUES (%s, %s, %s, %s)", (user_id, action, now, details))
        self.conn.commit()

    def quy_doi_diem(self, tb):
        if tb >= 8.5: return ('A', 4.0)
        elif tb >= 7.0: return ('B', 3.0)
        elif tb >= 5.5: return ('C', 2.0)
        elif tb >= 4.0: return ('D', 1.0)
        else: return ('F', 0.0)

    # --- KHOA ---
    def insert_khoa(self, ma, ten):
        self._ping()
        try:
            self.cursor.execute("INSERT INTO khoa (ma_khoa, ten_khoa) VALUES (%s, %s)", (ma, ten))
            self.conn.commit(); return True
        except Exception as e:
            print(f"[insert_khoa] {e}"); return False

    def get_all_khoa(self):
        self.cursor.execute("SELECT * FROM khoa"); return self.cursor.fetchall()

    def update_khoa(self, id_k, ma, ten):
        try:
            self.cursor.execute("UPDATE khoa SET ma_khoa=%s, ten_khoa=%s WHERE id=%s", (ma, ten, id_k))
            self.conn.commit(); return True
        except Exception as e:
            print(f"[update_khoa] {e}"); return False

    def delete_khoa(self, id_k):
        # Kiểm tra lớp HC
        self.cursor.execute("SELECT 1 FROM lop_hc WHERE id_khoa=%s", (id_k,))
        if self.cursor.fetchone(): return False, "Đang có lớp hành chính thuộc khoa này!"
        self.cursor.execute("DELETE FROM khoa WHERE id=%s", (id_k,))
        self.conn.commit(); return True, "Xóa thành công"

    # --- LỚP HÀNH CHÍNH ---
    def insert_lop_hc(self, ma, ten, id_k):
        try:
            self.cursor.execute("INSERT INTO lop_hc (ma_lop, ten_lop, id_khoa) VALUES (%s, %s, %s)", (ma, ten, id_k))
            self.conn.commit(); return True
        except Exception as e:
            print(f"[insert_lop_hc] {e}"); return False

    def get_all_lop_hc(self):
        self.cursor.execute("SELECT l.id, l.ma_lop, l.ten_lop, k.ten_khoa FROM lop_hc l LEFT JOIN khoa k ON l.id_khoa=k.id")
        return self.cursor.fetchall()

    def update_lop_hc(self, id_l, ma, ten, id_k):
        try:
            self.cursor.execute("UPDATE lop_hc SET ma_lop=%s, ten_lop=%s, id_khoa=%s WHERE id=%s", (ma, ten, id_k, id_l))
            self.conn.commit(); return True
        except Exception as e:
            print(f"[update_lop_hc] {e}"); return False

    def delete_lop_hc(self, id_l):
        self.cursor.execute("SELECT 1 FROM sinh_vien WHERE id_lop_hc=%s", (id_l,))
        if self.cursor.fetchone(): return False, "Đang có sinh viên thuộc lớp này!"
        self.cursor.execute("DELETE FROM lop_hc WHERE id=%s", (id_l,))
        self.conn.commit(); return True, "Xóa thành công"

    # --- GIẢNG VIÊN ---
    def insert_giang_vien(self, ma, ho_ten, khoa, email, sdt):
        self._ping()
        try:
            # Dung 1 transaction duy nhat
            self.cursor.execute("INSERT INTO giang_vien (ma_gv, ho_ten, khoa, email, sdt) VALUES (%s, %s, %s, %s, %s)", (ma, ho_ten, khoa, email, sdt))
            gv_id = self.cursor.lastrowid
            
            # Them user lien ket
            hashed_pw = self.hash_password("123")
            self.cursor.execute("INSERT INTO users (username, password, role, reference_id) VALUES (%s, %s, 'teacher', %s)",
                               (ma, hashed_pw, gv_id))
            
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"[insert_giang_vien] {e}")
            return False

    def get_all_giang_vien(self):
        self.cursor.execute("SELECT id, ma_gv, ho_ten, khoa, email, sdt FROM giang_vien")
        return self.cursor.fetchall()

    def update_giang_vien(self, id_gv, ma, ho_ten, khoa, email, sdt):
        try:
            self.cursor.execute("SELECT ma_gv FROM giang_vien WHERE id=%s", (id_gv,))
            res = self.cursor.fetchone()
            if not res: return False
            old_ma = res[0]
            self.cursor.execute("UPDATE giang_vien SET ma_gv=%s, ho_ten=%s, khoa=%s, email=%s, sdt=%s WHERE id=%s", (ma, ho_ten, khoa, email, sdt, id_gv))
            if old_ma != ma:
                self.cursor.execute("UPDATE users SET username=%s WHERE username=%s AND role='teacher'", (ma, old_ma))
            self.conn.commit(); return True
        except Exception as e:
            self.conn.rollback(); print(f"[update_giang_vien] {e}"); return False

    def delete_giang_vien(self, id_gv):
        self.cursor.execute("SELECT 1 FROM lop_hoc_phan WHERE id_giang_vien=%s", (id_gv,))
        if self.cursor.fetchone(): return False, "Giảng viên đang có lớp dạy, không thể xóa!"
        self.cursor.execute("DELETE FROM users WHERE role='teacher' AND reference_id=%s", (id_gv,))
        self.cursor.execute("DELETE FROM giang_vien WHERE id=%s", (id_gv,))
        self.conn.commit(); return True, "Xóa thành công"

    # --- SINH VIÊN ---
    def insert_sinh_vien(self, ma, ho_ten, ngay_sinh, gioi_tinh, id_lhc):
        if not ma or not ho_ten: return False
        self._ping()
        try:
            # 1. Them vao bang sinh_vien
            self.cursor.execute("INSERT INTO sinh_vien (ma_sv, ho_ten, ngay_sinh, gioi_tinh, id_lop_hc) VALUES (%s, %s, %s, %s, %s)", 
                               (ma, ho_ten, ngay_sinh, gioi_tinh, id_lhc))
            sv_id = self.cursor.lastrowid
            
            # 2. Them vao bang users (Pass mac dinh 123)
            hashed_pw = self.hash_password("123")
            self.cursor.execute("INSERT INTO users (username, password, role, reference_id) VALUES (%s, %s, 'student', %s)",
                               (ma, hashed_pw, sv_id))
            
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"[insert_sinh_vien Error] {e}")
            return False

    def get_all_sinh_vien(self):
        query = """
            SELECT s.id, s.ma_sv, s.ho_ten, s.ngay_sinh, s.gioi_tinh, l.ten_lop, k.ten_khoa 
            FROM sinh_vien s 
            LEFT JOIN lop_hc l ON s.id_lop_hc = l.id
            LEFT JOIN khoa k ON l.id_khoa = k.id
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def update_sinh_vien(self, id_sv, ma, ho_ten, ns, gt, id_lhc):
        try:
            if not ma or not ho_ten: return False
            # Lấy mã cũ để cập nhật username trong bảng users
            self.cursor.execute("SELECT ma_sv FROM sinh_vien WHERE id=%s", (id_sv,))
            res = self.cursor.fetchone()
            if not res: return False
            old_ma = res[0]

            self.cursor.execute("UPDATE sinh_vien SET ma_sv=%s, ho_ten=%s, ngay_sinh=%s, gioi_tinh=%s, id_lop_hc=%s WHERE id=%s", (ma, ho_ten, ns, gt, id_lhc, id_sv))
            if old_ma != ma:
                self.cursor.execute("UPDATE users SET username=%s WHERE username=%s AND role='student'", (ma, old_ma))
            
            self.conn.commit(); return True
        except Exception as e:
            print(f"Error update_sinh_vien: {e}")
            return False

    def delete_sinh_vien(self, id_sv):
        self.cursor.execute("SELECT 1 FROM dang_ky_lop WHERE id_sinh_vien=%s", (id_sv,))
        if self.cursor.fetchone(): return False, "Sinh viên đang đăng ký học, không thể xóa!"
        self.cursor.execute("DELETE FROM users WHERE role='student' AND reference_id=%s", (id_sv,))
        self.cursor.execute("DELETE FROM sinh_vien WHERE id=%s", (id_sv,))
        self.conn.commit(); return True, "Xóa thành công"

    def get_grade_detail(self, id_sv, id_lhp):
        self.cursor.execute("SELECT diem_cc FROM diem WHERE id_sinh_vien=%s AND id_lop_hp=%s", (id_sv, id_lhp))
        res = self.cursor.fetchone()
        return res[0] if res else 0

    # --- MÔN HỌC ---
    def insert_mon_hoc(self, ma, ten, stc, mo_ta=""):
        try:
            self.cursor.execute("INSERT INTO mon_hoc (ma_mh, ten_mh, so_tin_chi, mo_ta) VALUES (%s, %s, %s, %s)", (ma, ten, stc, mo_ta))
            self.conn.commit(); return True
        except Exception as e:
            print(f"[insert_mon_hoc] {e}"); return False

    def get_all_mon_hoc(self):
        self.cursor.execute("SELECT * FROM mon_hoc"); return self.cursor.fetchall()

    def update_mon_hoc(self, id_m, ma, ten, stc, mo_ta):
        try:
            self.cursor.execute("UPDATE mon_hoc SET ma_mh=%s, ten_mh=%s, so_tin_chi=%s, mo_ta=%s WHERE id=%s", (ma, ten, stc, mo_ta, id_m))
            self.conn.commit(); return True
        except Exception as e:
            print(f"[update_mon_hoc] {e}"); return False

    def delete_mon_hoc(self, id_m):
        self.cursor.execute("SELECT 1 FROM lop_hoc_phan WHERE id_mon_hoc=%s", (id_m,))
        if self.cursor.fetchone(): return False, "Môn học đang có lớp học phần, không thể xóa!"
        self.cursor.execute("DELETE FROM mon_hoc WHERE id=%s", (id_m,))
        self.conn.commit(); return True, "Xóa thành công"

    # --- LỚP HỌC PHẦN ---
    def insert_lop_hoc_phan(self, ma, id_m, id_g, id_h, thu, ca):
        if not all([ma, id_m, id_g, id_h]):
            return False
        try:
            self.cursor.execute("INSERT INTO lop_hoc_phan (ma_lop_hp, id_mon_hoc, id_giang_vien, id_hoc_ky, thu, ca_hoc) VALUES (%s, %s, %s, %s, %s, %s)", (ma, id_m, id_g, id_h, thu, ca))
            self.conn.commit(); return True
        except Exception as e:
            print(f"[insert_lop_hoc_phan] {e}"); return False

    def update_lop_hoc_phan(self, id_l, ma, id_m, id_g, id_h, thu, ca):
        try:
            self.cursor.execute("UPDATE lop_hoc_phan SET ma_lop_hp=%s, id_mon_hoc=%s, id_giang_vien=%s, id_hoc_ky=%s, thu=%s, ca_hoc=%s WHERE id=%s", (ma, id_m, id_g, id_h, thu, ca, id_l))
            self.conn.commit(); return True
        except Exception as e:
            print(f"[update_lop_hoc_phan] {e}"); return False

    def get_all_lop_hp(self):
        self._ping()
        query = '''
            SELECT l.id, l.ma_lop_hp, m.ten_mh, g.ho_ten, CONCAT(h.ten_hoc_ky, ' ', h.nam_hoc), 
                   CONCAT(l.thu, ' (Ca ', l.ca_hoc, ')'), l.status
            FROM lop_hoc_phan l
            LEFT JOIN mon_hoc m ON l.id_mon_hoc=m.id
            LEFT JOIN giang_vien g ON l.id_giang_vien=g.id
            LEFT JOIN hoc_ky h ON l.id_hoc_ky=h.id
        '''
        self.cursor.execute(query); return self.cursor.fetchall()

    def delete_lop_hp(self, id_l):
        self.cursor.execute("SELECT 1 FROM dang_ky_lop WHERE id_lop_hp=%s", (id_l,))
        if self.cursor.fetchone(): return False, "Lớp đã có sinh viên đăng ký, không thể xóa!"
        self.cursor.execute("DELETE FROM lop_hoc_phan WHERE id=%s", (id_l,))
        self.conn.commit(); return True, "Xóa thành công"

    # --- HỌC KỲ ---
    def insert_hoc_ky(self, ten, nam):
        self.cursor.execute("INSERT INTO hoc_ky (ten_hoc_ky, nam_hoc) VALUES (%s, %s)", (ten, nam))
        self.conn.commit()

    def get_all_hoc_ky(self):
        self.cursor.execute("SELECT * FROM hoc_ky"); return self.cursor.fetchall()

    def delete_hoc_ky(self, id_h):
        self.cursor.execute("DELETE FROM hoc_ky WHERE id=%s", (id_h,))
        self.conn.commit(); return True

    # --- ĐIỂM & ĐĂNG KÝ ---
    def check_schedule_conflict(self, id_sv, id_lhp):
        """Kiểm tra xem lớp học phần mới có bị trùng lịch với các lớp đã đăng ký không."""
        self._ping()
        try:
            # 1. Lấy thông tin lịch học của lớp đang muốn đăng ký
            self.cursor.execute(
                "SELECT thu, ca_hoc, id_hoc_ky, ma_lop_hp FROM lop_hoc_phan WHERE id=%s", (id_lhp,)
            )
            new_class = self.cursor.fetchone()
            if not new_class: return False, "Không tìm thấy lớp học phần!"
            
            thu_new, ca_new, hk_new, ma_new = new_class
            
            # 2. Lấy danh sách lịch học của các lớp đã đăng ký trong CÙNG học kỳ
            query = """
                SELECT l.thu, l.ca_hoc, m.ten_mh, l.ma_lop_hp
                FROM dang_ky_lop dk
                JOIN lop_hoc_phan l ON dk.id_lop_hp = l.id
                JOIN mon_hoc m ON l.id_mon_hoc = m.id
                WHERE dk.id_sinh_vien = %s AND l.id_hoc_ky = %s
            """
            self.cursor.execute(query, (id_sv, hk_new))
            registered_classes = self.cursor.fetchall()
            
            # 3. So sánh
            for thu_old, ca_old, ten_old, ma_old in registered_classes:
                if thu_old == thu_new and ca_old == ca_new:
                    return True, f"Trùng lịch với lớp {ma_old} ({ten_old}) vào {thu_old}, {ca_new}"
            
            return False, "" # Không trùng
        except Exception as e:
            print(f"[check_conflict] {e}")
            return False, str(e)

    def dang_ky_sinh_vien_vao_lop(self, id_lop, id_sv):
        """Fix Bug: Kiem tra id_sv truoc khi insert de tranh loi FK/Null."""
        if not id_sv:
            return False, "Tài khoản của bạn chưa được liên kết với hồ sơ sinh viên!"
            
        self._ping()
        try:
            # Kiem tra xem da dang ky chua (tranh loi generic)
            self.cursor.execute("SELECT 1 FROM dang_ky_lop WHERE id_lop_hp=%s AND id_sinh_vien=%s", (id_lop, id_sv))
            if self.cursor.fetchone():
                return False, "Bạn đã đăng ký lớp học phần này rồi!"

            self.cursor.execute("INSERT INTO dang_ky_lop (id_lop_hp, id_sinh_vien) VALUES (%s, %s)", (id_lop, id_sv))
            self.cursor.execute("INSERT INTO diem (id_sinh_vien, id_lop_hp) VALUES (%s, %s)", (id_sv, id_lop))
            self.conn.commit()
            return True, "Đăng ký thành công!"
        except Exception as e:
            self.conn.rollback()
            print(f"[dang_ky] {e}")
            return False, f"Lỗi hệ thống: {str(e)}"

    def update_diem(self, id_sv, id_lop, d_cc, d_gk, d_ck, user_id):
        self._ping()
        # 1. Kiểm tra dải điểm hợp lệ (chỉ kiểm tra nếu khác None)
        for d in [d_cc, d_gk, d_ck]:
            if d is not None:
                if d < 0 or d > 10:
                    return False, "Điểm phải nằm trong khoảng từ 0 đến 10!"

        # 2. Lấy thông tin lớp
        self.cursor.execute("SELECT status, w_cc, w_gk, w_ck FROM lop_hoc_phan WHERE id=%s", (id_lop,))
        info = self.cursor.fetchone()
        if not info or info[0] == 'closed': return False, "Lớp đã khóa, không thể sửa điểm!"
        
        w_cc, w_gk, w_ck = info[1], info[2], info[3]
        
        # 3. Tính toán trạng thái và điểm trung bình
        if d_cc is None and d_gk is None and d_ck is None:
            # Trường hợp xóa hết điểm (Reset)
            d_tb = None
            d_chu, d_he4 = None, None
            trang_thai = "Đang học"
        else:
            # Trường hợp có nhập ít nhất 1 đầu điểm
            if d_cc is not None and d_cc < 4.0:
                trang_thai = "Cam thi"
                d_tb = (d_cc or 0) * w_cc + (d_gk or 0) * w_gk + 0 * w_ck
            else:
                trang_thai = "Du dieu kien"
                d_tb = (d_cc or 0) * w_cc + (d_gk or 0) * w_gk + (d_ck or 0) * w_ck
            
            d_chu, d_he4 = self.quy_doi_diem(d_tb)

        # 4. Lấy điểm cũ để log nhật ký
        self.cursor.execute("SELECT diem_cc, diem_gk, diem_ck FROM diem WHERE id_sinh_vien=%s AND id_lop_hp=%s", (id_sv, id_lop))
        old_scores = self.cursor.fetchone()

        try:
            # 4. Cập nhật điểm
            self.cursor.execute(
                "UPDATE diem SET diem_cc=%s, diem_gk=%s, diem_ck=%s, diem_tb=%s, diem_chu=%s, diem_he4=%s, trang_thai=%s "
                "WHERE id_sinh_vien=%s AND id_lop_hp=%s", 
                (d_cc, d_gk, d_ck, d_tb, d_chu, d_he4, trang_thai, id_sv, id_lop)
            )
            
            # 5. Lưu nhật ký chi tiết (Anti-fraud)
            details = f"SV ID {id_sv}, Lớp ID {id_lop}: "
            if old_scores:
                details += f"Cũ ({old_scores[0]},{old_scores[1]},{old_scores[2]}) -> Mới ({d_cc},{d_gk},{d_ck})"
            else:
                details += f"Nhập mới ({d_cc},{d_gk},{d_ck})"
            
            self.log_action(user_id, "Cập nhật điểm", details)
            
            self.conn.commit()
            return True, f"Cập nhật thành công! { '(Cấm thi)' if trang_thai == 'Cam thi' else '' }"
        except Exception as e:
            self.conn.rollback()
            return False, f"Lỗi hệ thống: {e}"

    # --- CÁC BÁO CÁO & THỐNG KÊ MỚI ---
    
    def get_thong_ke_lop(self, id_lop):
        """Thống kê phổ điểm của một lớp học phần."""
        query = """
            SELECT diem_chu, COUNT(*) 
            FROM diem 
            WHERE id_lop_hp=%s 
            GROUP BY diem_chu 
            ORDER BY diem_chu
        """
        self.cursor.execute(query, (id_lop,))
        return dict(self.cursor.fetchall())

    def get_ds_cam_thi(self, id_lop):
        """Lấy danh sách sinh viên bị cấm thi trong lớp."""
        query = """
            SELECT s.ma_sv, s.ho_ten, d.diem_cc, d.trang_thai 
            FROM diem d 
            JOIN sinh_vien s ON d.id_sinh_vien=s.id 
            WHERE d.id_lop_hp=%s AND d.trang_thai = 'Cấm thi'
        """
        self.cursor.execute(query, (id_lop,))
        return self.cursor.fetchall()

    def get_tien_do_sinh_vien(self, id_sv):
        """Thống kê số tín chỉ tích lũy của sinh viên."""
        query = """
            SELECT SUM(m.so_tin_chi) 
            FROM diem d 
            JOIN lop_hoc_phan l ON d.id_lop_hp=l.id 
            JOIN mon_hoc m ON l.id_mon_hoc=m.id 
            WHERE d.id_sinh_vien=%s AND d.diem_tb >= 4.0
        """
        self.cursor.execute(query, (id_sv,))
        res = self.cursor.fetchone()
        return int(res[0]) if res and res[0] else 0

    def get_top_sinh_vien(self, limit=10):
        """Lấy danh sách sinh viên xuất sắc nhất toàn trường (theo GPA)."""
        # Lưu ý: Đây là truy vấn phức tạp, tính trung bình có trọng số tín chỉ
        query = """
            SELECT s.ma_sv, s.ho_ten, 
                   ROUND(SUM(d.diem_he4 * m.so_tin_chi) / SUM(m.so_tin_chi), 2) as gpa
            FROM sinh_vien s
            JOIN diem d ON s.id = d.id_sinh_vien
            JOIN lop_hoc_phan l ON d.id_lop_hp = l.id
            JOIN mon_hoc m ON l.id_mon_hoc = m.id
            WHERE d.trang_thai != 'Đang học'
            GROUP BY s.id
            HAVING SUM(m.so_tin_chi) > 0
            ORDER BY gpa DESC
            LIMIT %s
        """
        self.cursor.execute(query, (limit,))
        return self.cursor.fetchall()

    def lock_lop_hoc_phan(self, id_l):
        """Khoa lop de khong cho phep sua diem nua."""
        try:
            self.cursor.execute("UPDATE lop_hoc_phan SET status='closed' WHERE id=%s", (id_l,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"[lock_lop] {e}"); return False

    def get_lhp_by_giang_vien(self, id_gv):
        query = "SELECT l.id, l.ma_lop_hp, m.ten_mh, CONCAT(l.thu, ' (Ca ', l.ca_hoc, ')'), l.status FROM lop_hoc_phan l JOIN mon_hoc m ON l.id_mon_hoc=m.id WHERE l.id_giang_vien=%s"
        self.cursor.execute(query, (id_gv,)); return self.cursor.fetchall()

    def get_bang_diem_lop(self, id_l):
        query = "SELECT s.id, s.ma_sv, s.ho_ten, d.diem_cc, d.diem_gk, d.diem_ck, d.diem_tb, d.diem_chu, d.trang_thai FROM diem d JOIN sinh_vien s ON d.id_sinh_vien=s.id WHERE d.id_lop_hp=%s"
        self.cursor.execute(query, (id_l,)); return self.cursor.fetchall()

    def get_diem_sinh_vien(self, id_sv):
        query = "SELECT m.ma_mh, m.ten_mh, m.so_tin_chi, d.diem_cc, d.diem_gk, d.diem_ck, d.diem_tb, d.diem_chu, d.diem_he4 FROM diem d JOIN lop_hoc_phan l ON d.id_lop_hp=l.id JOIN mon_hoc m ON l.id_mon_hoc=m.id WHERE d.id_sinh_vien=%s"
        self.cursor.execute(query, (id_sv,)); return self.cursor.fetchall()

    def get_gpa(self, id_sv):
        query = "SELECT SUM(d.diem_he4 * m.so_tin_chi), SUM(m.so_tin_chi) FROM diem d JOIN lop_hoc_phan l ON d.id_lop_hp=l.id JOIN mon_hoc m ON l.id_mon_hoc=m.id WHERE d.id_sinh_vien=%s AND d.trang_thai != 'Đang học'"
        self.cursor.execute(query, (id_sv,))
        res = self.cursor.fetchone()
        return round(float(res[0])/float(res[1]), 2) if res and res[0] is not None and res[1] else 0.0

    def get_available_classes(self, id_sv):
        """Bug #2 (tính năng): Chi hien thi lop thuoc hoc ky dang mo."""
        query = """
            SELECT l.id, l.ma_lop_hp, m.ten_mh, g.ho_ten,
                   CONCAT(l.thu, ' (Ca ', l.ca_hoc, ')')
            FROM lop_hoc_phan l
            JOIN mon_hoc m ON l.id_mon_hoc=m.id
            JOIN giang_vien g ON l.id_giang_vien=g.id
            JOIN hoc_ky h ON l.id_hoc_ky=h.id
            WHERE l.status='open'
              AND h.trang_thai='mo'
              AND IFNULL(l.si_so_toi_da, 60) > (SELECT COUNT(*) FROM dang_ky_lop WHERE id_lop_hp=l.id)
              AND l.id NOT IN (
                  SELECT id_lop_hp FROM dang_ky_lop WHERE id_sinh_vien=%s
              )
        """
        self.cursor.execute(query, (id_sv,)); return self.cursor.fetchall()

    def get_all_thong_bao(self):
        self.cursor.execute("SELECT * FROM thong_bao ORDER BY id DESC"); return self.cursor.fetchall()

    def insert_thong_bao(self, tieu_de, noi_dung, nguoi):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO thong_bao (tieu_de, noi_dung, ngay_dang, nguoi_dang) VALUES (%s, %s, %s, %s)", (tieu_de, noi_dung, now, nguoi))
        self.conn.commit(); return True

    def delete_thong_bao(self, id_t):
        self.cursor.execute("DELETE FROM thong_bao WHERE id=%s", (id_t,)); self.conn.commit()

    def get_user_profile(self, role, ref_id):
        if role == 'student': self.cursor.execute("SELECT s.ma_sv, s.ho_ten, l.ten_lop, s.ngay_sinh, s.gioi_tinh FROM sinh_vien s LEFT JOIN lop_hc l ON s.id_lop_hc=l.id WHERE s.id=%s", (ref_id,))
        elif role == 'teacher': self.cursor.execute("SELECT * FROM giang_vien WHERE id=%s", (ref_id,))
        else: return None
        return self.cursor.fetchone()

    def get_teacher_stats(self, id_gv):
        query = """
            SELECT m.ten_mh, l.ma_lop_hp, 
                   COUNT(CASE WHEN d.id_sinh_vien IS NOT NULL THEN 1 END) as tong,
                   SUM(CASE WHEN d.trang_thai != 'Đang học' AND d.diem_tb >= 4.0 THEN 1 ELSE 0 END) as dat,
                   SUM(CASE WHEN d.trang_thai != 'Đang học' AND d.diem_tb < 4.0 THEN 1 ELSE 0 END) as rot
            FROM lop_hoc_phan l 
            JOIN mon_hoc m ON l.id_mon_hoc=m.id 
            LEFT JOIN diem d ON l.id=d.id_lop_hp 
            WHERE l.id_giang_vien=%s 
            GROUP BY l.id
        """
        self.cursor.execute(query, (id_gv,)); return self.cursor.fetchall()

    def delete_user(self, id_u):
        """Bug #3 fix: Xoa nhat_ky truoc de tranh vi pham FK constraint."""
        try:
            self.cursor.execute("DELETE FROM nhat_ky WHERE user_id=%s", (id_u,))
            self.cursor.execute("DELETE FROM users WHERE id=%s", (id_u,))
            self.conn.commit(); return True
        except Exception as e:
            self.conn.rollback(); print(f"[delete_user] {e}"); return False

    def get_all_users(self):
        self._ping()
        self.cursor.execute(
            "SELECT id, username, role, is_active FROM users ORDER BY role, username"
        )
        return self.cursor.fetchall()

    def update_user_role(self, id_u, new_role):
        try:
            self.cursor.execute("UPDATE users SET role=%s WHERE id=%s", (new_role, id_u))
            self.conn.commit(); return True
        except Exception as e:
            print(f"[update_user_role] {e}"); return False

    def insert_user(self, username, password, role, reference_id=None):
        """Fix Bug: Cho phep admin lien ket reference_id khi tao thu cong."""
        hpw = self.hash_password(password)
        try:
            self.cursor.execute("INSERT INTO users (username, password, role, reference_id) VALUES (%s, %s, %s, %s)",
                                (username, hpw, role, reference_id))
            self.conn.commit(); return True
        except Exception as e:
            print(f"[insert_user] {e}"); return False

    def update_user(self, id_u, username, role):
        try:
            self.cursor.execute("UPDATE users SET username=%s, role=%s WHERE id=%s",
                                (username, role, id_u))
            self.conn.commit(); return True
        except Exception as e:
            print(f"[update_user] {e}"); return False

    def change_password(self, id_u, old_password, new_password):
        """Tinh nang moi: SV/GV tu doi mat khau ca nhan."""
        old_hash = self.hash_password(old_password)
        self.cursor.execute("SELECT id FROM users WHERE id=%s AND password=%s", (id_u, old_hash))
        if not self.cursor.fetchone():
            return False, "Mat khau cu khong dung!"
        new_hash = self.hash_password(new_password)
        self.cursor.execute("UPDATE users SET password=%s WHERE id=%s", (new_hash, id_u))
        self.conn.commit()
        return True, "Doi mat khau thanh cong!"

    def toggle_user_active(self, id_u):
        """Đổi trạng thái active/inactive của tài khoản."""
        self.cursor.execute("SELECT is_active FROM users WHERE id=%s", (id_u,))
        row = self.cursor.fetchone()
        if not row: return False
        new_status = 0 if row[0] == 1 else 1
        self.cursor.execute("UPDATE users SET is_active=%s WHERE id=%s", (new_status, id_u))
        self.conn.commit(); return True

    def reset_password(self, id_u, new_password="123"):
        hpw = self.hash_password(new_password)
        self.cursor.execute("UPDATE users SET password=%s WHERE id=%s", (hpw, id_u))
        self.conn.commit(); return True

    def get_nhat_ky(self):
        self.cursor.execute("SELECT u.username, n.hanh_dong, n.thoi_gian, n.chi_tiet FROM nhat_ky n JOIN users u ON n.user_id=u.id ORDER BY n.id DESC")
        return self.cursor.fetchall()
    def save_attendance(self, id_lhp, attendance_list, date_str):
        """attendance_list: [(id_sv, status), ...] where status: 1:Present, 0:Absent, 2:Excused"""
        try:
            self.cursor.execute("DELETE FROM diem_danh WHERE id_lop_hp=%s AND ngay=%s", (id_lhp, date_str))
            for id_sv, status in attendance_list:
                self.cursor.execute("INSERT INTO diem_danh (id_sinh_vien, id_lop_hp, ngay, trang_thai) VALUES (%s, %s, %s, %s)",
                                   (id_sv, id_lhp, date_str, status))
            
            # Rule: 1 tín chỉ = 5 buổi. Nghỉ KHÔNG PHÉP > 20% => Cấm thi.
            self.cursor.execute("""
                SELECT m.so_tin_chi 
                FROM lop_hoc_phan l 
                JOIN mon_hoc m ON l.id_mon_hoc = m.id 
                WHERE l.id = %s
            """, (id_lhp,))
            res = self.cursor.fetchone()
            tong_so_buoi = (res[0] * 5) if res and res[0] else 15
            
            # Đếm số buổi nghỉ KHÔNG PHÉP (status=0)
            self.cursor.execute("SELECT id_sinh_vien, COUNT(*) as nghi FROM diem_danh WHERE id_lop_hp=%s AND trang_thai=0 GROUP BY id_sinh_vien", (id_lhp,))
            stats = self.cursor.fetchall()
            for id_sv, nghi in stats:
                if nghi / tong_so_buoi > 0.2:
                    self.cursor.execute("UPDATE diem SET trang_thai='Cam thi' WHERE id_sinh_vien=%s AND id_lop_hp=%s", (id_sv, id_lhp))
                else:
                    self.cursor.execute("SELECT trang_thai FROM diem WHERE id_sinh_vien=%s AND id_lop_hp=%s", (id_sv, id_lhp))
                    curr = self.cursor.fetchone()
                    if curr and curr[0] == 'Cam thi':
                         self.cursor.execute("UPDATE diem SET trang_thai='Du dieu kien' WHERE id_sinh_vien=%s AND id_lop_hp=%s", (id_sv, id_lhp))

            self.conn.commit(); return True, "Đã lưu điểm danh thành công!"
        except Exception as e:
            self.conn.rollback()
            return False, f"Lỗi: {e}"

    def get_attendance_report(self, id_lhp):
        # Lấy số tín chỉ để tính tổng số buổi chuẩn
        self.cursor.execute("SELECT m.so_tin_chi FROM lop_hoc_phan l JOIN mon_hoc m ON l.id_mon_hoc = m.id WHERE l.id = %s", (id_lhp,))
        res = self.cursor.fetchone()
        tong_so_buoi = (res[0] * 5) if res and res[0] else 15

        # Query lấy danh sách sinh viên kèm theo thống kê nghỉ (K/P)
        query = """
            SELECT s.id, s.ma_sv, s.ho_ten, 
                   (SELECT COUNT(*) FROM diem_danh WHERE id_sinh_vien=s.id AND id_lop_hp=%s AND trang_thai=0) as nghi_k,
                   (SELECT COUNT(*) FROM diem_danh WHERE id_sinh_vien=s.id AND id_lop_hp=%s AND trang_thai=2) as nghi_p,
                   %s as tong_so_buoi
            FROM sinh_vien s
            JOIN dang_ky_lop dk ON s.id = dk.id_sinh_vien
            WHERE dk.id_lop_hp = %s
        """
        self.cursor.execute(query, (id_lhp, id_lhp, tong_so_buoi, id_lhp))
        return self.cursor.fetchall()

    def get_attendance_dates(self, id_lhp):
        self.cursor.execute("SELECT DISTINCT ngay FROM diem_danh WHERE id_lop_hp=%s ORDER BY ngay DESC", (id_lhp,))
        return [r[0] for r in self.cursor.fetchall()]

    def get_attendance_detail(self, id_lhp, date_str):
        self.cursor.execute("SELECT id_sinh_vien, trang_thai FROM diem_danh WHERE id_lop_hp=%s AND ngay=%s", (id_lhp, date_str))
        return {r[0]: r[1] for r in self.cursor.fetchall()}

    def get_student_attendance_summary(self, sv_id):
        """Lấy tóm tắt điểm danh của sinh viên ở tất cả các môn đang học."""
        query = """
            SELECT m.ma_mh, m.ten_mh, m.so_tin_chi,
                   COUNT(CASE WHEN dd.trang_thai=0 THEN 1 END) as nghi_k,
                   COUNT(CASE WHEN dd.trang_thai=2 THEN 1 END) as nghi_p,
                   (m.so_tin_chi * 5) as tong_buoi,
                   l.id as id_lhp
            FROM dang_ky_lop dk
            JOIN lop_hoc_phan l ON dk.id_lop_hp = l.id
            JOIN mon_hoc m ON l.id_mon_hoc = m.id
            LEFT JOIN diem_danh dd ON (dk.id_sinh_vien = dd.id_sinh_vien AND l.id = dd.id_lop_hp)
            WHERE dk.id_sinh_vien = %s
            GROUP BY l.id
        """
        self.cursor.execute(query, (sv_id,))
        return self.cursor.fetchall()

    def get_student_attendance_detail(self, sv_id, lhp_id):
        """Lấy chi tiết từng buổi điểm danh của sinh viên trong một lớp cụ thể."""
        query = """
            SELECT ngay, trang_thai
            FROM diem_danh
            WHERE id_sinh_vien = %s AND id_lop_hp = %s
            ORDER BY ngay DESC
        """
        self.cursor.execute(query, (sv_id, lhp_id))
        return self.cursor.fetchall()
