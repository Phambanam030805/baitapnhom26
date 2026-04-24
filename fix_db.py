import sqlite3

def fix_database():
    conn = sqlite3.connect("ql_diem.db")
    cursor = conn.cursor()
    
    print("--- Đang kiểm tra và sửa lỗi Database ---")
    
    try:
        # 1. Tạo bảng lop_hc nếu chưa có
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lop_hc (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ma_lop TEXT UNIQUE NOT NULL,
                ten_lop TEXT NOT NULL,
                id_khoa INTEGER
            )
        ''')
        print("[OK] Đã kiểm tra bảng lop_hc")

        # 2. Kiểm tra cột id_lop_hc trong bảng sinh_vien
        cursor.execute("PRAGMA table_info(sinh_vien)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'id_lop_hc' not in columns:
            print("[!] Phát hiện thiếu cột id_lop_hc. Đang nâng cấp bảng sinh_vien...")
            # Thêm cột mới
            cursor.execute("ALTER TABLE sinh_vien ADD COLUMN id_lop_hc INTEGER")
            print("[OK] Đã thêm cột id_lop_hc vào bảng sinh_vien")
        
        # 3. Kiểm tra cột thu, ca_hoc trong bảng lop_hoc_phan
        cursor.execute("PRAGMA table_info(lop_hoc_phan)")
        lhp_columns = [column[1] for column in cursor.fetchall()]
        if 'thu' not in lhp_columns:
            cursor.execute("ALTER TABLE lop_hoc_phan ADD COLUMN thu TEXT")
            print("[OK] Đã thêm cột 'thu' vào bảng lop_hoc_phan")
        if 'ca_hoc' not in lhp_columns:
            cursor.execute("ALTER TABLE lop_hoc_phan ADD COLUMN ca_hoc TEXT")
            print("[OK] Đã thêm cột 'ca_hoc' vào bảng lop_hoc_phan")

        conn.commit()
        print("--- Hoàn tất sửa lỗi! Bây giờ bạn có thể chạy lại main.py ---")
    except Exception as e:
        print(f"[LỖI] Không thể sửa lỗi tự động: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database()
