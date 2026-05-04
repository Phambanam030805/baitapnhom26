import sys
from database import Database

lop_list = [
    ('IT01',   'Công Nghệ Thông Tin K60', 'Công Nghệ Thông Tin'),
    ('IT02',   'Công Nghệ Thông Tin K61', 'Công Nghệ Thông Tin'),
    ('SE01',   'Kỹ Thuật Phần Mềm K60',   'Công Nghệ Thông Tin'),
    
    ('BA01',   'Quản Trị Kinh Doanh K60', 'Quản Trị Kinh Doanh'),
    ('BA02',   'Quản Trị Kinh Doanh K61', 'Quản Trị Kinh Doanh'),
    
    ('MK01',   'Marketing K60',           'Marketing'),
    
    ('AC01',   'Kế Toán Kiểm Toán K60',   'Kế Toán'),
    
    ('FI01',   'Tài Chính Ngân Hàng K60', 'Tài Chính Ngân Hàng'),
    ('FI02',   'Tài Chính Ngân Hàng K61', 'Tài Chính Ngân Hàng'),
    
    ('EN01',   'Ngôn Ngữ Anh K60',        'Ngôn Ngữ Anh'),
    ('EN02',   'Ngôn Ngữ Anh K61',        'Ngôn Ngữ Anh'),
    
    ('CN01',   'Ngôn Ngữ Trung K60',      'Ngôn Ngữ Trung'),
    
    ('LW01',   'Luật Kinh Tế K60',        'Luật'),
    ('LW02',   'Luật Dân Sự K60',         'Luật'),
    
    ('MEC01',  'Cơ Khí Động Lực K60',     'Cơ Khí'),
    ('MEC02',  'Cơ Khí Chế Tạo K60',      'Công Nghệ Chế Tạo Máy'),
    
    ('AUTO01', 'Kỹ Thuật Ô Tô K60',       'Công Nghệ Kĩ Thuật Ô Tô'),
    ('AUTO02', 'Kỹ Thuật Ô Tô K61',       'Công Nghệ Kĩ Thuật Ô Tô'),
    
    ('EEE01',  'Điện Tử Viễn Thông K60',  'Công nghệ Kỹ thuật Điện  – Điện tử'),
    ('EEE02',  'Hệ Thống Điện K60',       'Công nghệ Kỹ thuật Điện  – Điện tử')
]

def import_data():
    try:
        db = Database()
        
        # Lấy id của các khoa gốc của DB
        all_khoa = db.get_all_khoa()
        khoa_map = {row[2]: row[0] for row in all_khoa} # Map Tên Khoa -> ID Khoa
        
        print("\n--- ĐANG THÊM LỚP HÀNH CHÍNH THEO KHOA GỐC ---")
        success = 0
        for ma_lop, ten_lop, ten_khoa in lop_list:
            id_k = khoa_map.get(ten_khoa)
            if not id_k:
                print(f"⚠️ Không tìm thấy Khoa gốc: '{ten_khoa}'. Vui lòng kiểm tra lại tên.")
                continue
            
            if db.insert_lop_hc(ma_lop, ten_lop, id_k):
                print(f"✅ Đã thêm lớp: {ma_lop} - {ten_lop} (Thuộc khoa: {ten_khoa})")
                success += 1
            else:
                print(f"⚠️ Bỏ qua (đã tồn tại): {ma_lop} - {ten_lop}")
        
        print(f"\n🎉 Đã import xong {success}/{len(lop_list)} lớp hành chính chuẩn!")
        
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    import_data()
