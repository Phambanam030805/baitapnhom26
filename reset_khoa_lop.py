import sys
from database import Database

khoa_list = [
    ('CNTT', 'Công Nghệ Thông Tin'),
    ('QTKD', 'Quản Trị Kinh Doanh'),
    ('KETO', 'Kế Toán'),
    ('NNA',  'Ngôn Ngữ Anh'),
    ('LUAT', 'Luật'),
    ('CKHI', 'Cơ Khí'),
    ('DDT',  'Điện - Điện Tử'),
    ('OTO',  'Kỹ Thuật Ô Tô'),
    ('TCNH', 'Tài Chính Ngân Hàng'),
    ('KHCB', 'Khoa Học Cơ Bản')
]

lop_list = [
    ('IT01',   'Công Nghệ Thông Tin K60', 'Công Nghệ Thông Tin'),
    ('IT02',   'Công Nghệ Thông Tin K61', 'Công Nghệ Thông Tin'),
    ('SE01',   'Kỹ Thuật Phần Mềm K60',   'Công Nghệ Thông Tin'),
    
    ('BA01',   'Quản Trị Kinh Doanh K60', 'Quản Trị Kinh Doanh'),
    ('BA02',   'Quản Trị Kinh Doanh K61', 'Quản Trị Kinh Doanh'),
    
    ('AC01',   'Kế Toán Kiểm Toán K60',   'Kế Toán'),
    ('AC02',   'Kế Toán Doanh Nghiệp K60','Kế Toán'),
    
    ('EN01',   'Ngôn Ngữ Anh K60',        'Ngôn Ngữ Anh'),
    ('EN02',   'Ngôn Ngữ Anh K61',        'Ngôn Ngữ Anh'),
    
    ('LW01',   'Luật Kinh Tế K60',        'Luật'),
    ('LW02',   'Luật Dân Sự K60',         'Luật'),
    
    ('MEC01',  'Cơ Khí Động Lực K60',     'Cơ Khí'),
    ('MEC02',  'Chế Tạo Máy K60',         'Cơ Khí'),
    
    ('EEE01',  'Điện Tử Viễn Thông K60',  'Điện - Điện Tử'),
    ('EEE02',  'Hệ Thống Điện K60',       'Điện - Điện Tử'),
    
    ('AUTO01', 'Kỹ Thuật Ô Tô K60',       'Kỹ Thuật Ô Tô'),
    ('AUTO02', 'Kỹ Thuật Ô Tô K61',       'Kỹ Thuật Ô Tô'),
    
    ('FI01',   'Tài Chính Ngân Hàng K60', 'Tài Chính Ngân Hàng'),
    
    ('MATH01', 'Sư Phạm Toán K60',        'Khoa Học Cơ Bản'),
    ('PHY01',  'Sư Phạm Lý K60',          'Khoa Học Cơ Bản')
]

def reset_and_import():
    try:
        db = Database()
        
        print("--- BẮT ĐẦU XÓA DỮ LIỆU CŨ ---")
        # 1. Ngắt kết nối lớp khỏi sinh viên (để không lỗi khóa ngoại)
        db.cursor.execute("UPDATE sinh_vien SET id_lop_hc = NULL")
        
        # 2. Xóa sạch lớp hành chính cũ
        db.cursor.execute("DELETE FROM lop_hc")
        
        # 3. Xóa sạch khoa cũ (để id reset hoặc kệ nó, nhưng xóa sạch dữ liệu)
        # Đặt lại auto increment nếu muốn (không bắt buộc)
        db.cursor.execute("DELETE FROM khoa")
        db.cursor.execute("ALTER TABLE khoa AUTO_INCREMENT = 1")
        db.cursor.execute("ALTER TABLE lop_hc AUTO_INCREMENT = 1")
        db.conn.commit()
        print("✅ Xóa xong dữ liệu rác cũ!")
        
        print("\n--- TẠO LẠI 10 KHOA MỚI HOÀN TOÀN ---")
        for ma, ten in khoa_list:
            db.insert_khoa(ma, ten)
            print(f"  + Tạo khoa: {ten}")
            
        # Lấy lại map Khoa
        db.cursor.execute("SELECT id, ten_khoa FROM khoa")
        khoa_map = {row[1]: row[0] for row in db.cursor.fetchall()}
        
        print("\n--- TẠO 20 LỚP HÀNH CHÍNH MỚI ---")
        success = 0
        for ma_lop, ten_lop, ten_khoa in lop_list:
            id_k = khoa_map.get(ten_khoa)
            if db.insert_lop_hc(ma_lop, ten_lop, id_k):
                print(f"✅ Đã thêm: {ma_lop} - {ten_lop} ({ten_khoa})")
                success += 1
                
        # 4. Sửa lại Giảng viên cho đúng tên Khoa mới (cập nhật đồng bộ)
        db.cursor.execute("UPDATE giang_vien SET khoa='Khoa Học Cơ Bản' WHERE khoa LIKE '%Toán%' OR khoa LIKE '%Lý%' OR khoa LIKE '%Hóa%'")
        db.cursor.execute("UPDATE giang_vien SET khoa='Kế Toán' WHERE khoa LIKE '%Kế Toán%'")
        db.cursor.execute("UPDATE giang_vien SET khoa='Ngôn Ngữ Anh' WHERE khoa LIKE '%Ngoại Ngữ%'")
        db.cursor.execute("UPDATE giang_vien SET khoa='Luật' WHERE khoa LIKE '%Luật%' OR khoa LIKE '%Chính Trị%'")
        db.cursor.execute("UPDATE giang_vien SET khoa='Cơ Khí' WHERE khoa LIKE '%Cơ Khí%' OR khoa LIKE '%Chế Tạo%'")
        db.cursor.execute("UPDATE giang_vien SET khoa='Điện - Điện Tử' WHERE khoa LIKE '%Quốc Phòng%' OR khoa LIKE '%Điện%'")
        db.cursor.execute("UPDATE giang_vien SET khoa='Kỹ Thuật Ô Tô' WHERE khoa LIKE '%Thể Chất%' OR khoa LIKE '%Ô Tô%'")
        db.conn.commit()
        print("\n✅ Đồng bộ xong dữ liệu Khoa của Giảng viên!")
        
        print(f"\n🎉 HOÀN TẤT! Đã tạo sạch sẽ {len(khoa_list)} Khoa và {success} Lớp hành chính không trùng lặp.")
        
    except Exception as e:
        print(f"Lỗi hệ thống: {e}")

if __name__ == "__main__":
    reset_and_import()
