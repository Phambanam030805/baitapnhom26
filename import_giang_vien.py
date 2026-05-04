import sys
from database import Database

teachers = [
    ('GV001', 'PGS.TS. Nguyễn Văn An', 'Công Nghệ Thông Tin', 'nvan@dh.edu.vn', '0901234567'),
    ('GV002', 'ThS. Trần Thị Bích', 'Công Nghệ Thông Tin', 'ttbich@dh.edu.vn', '0912345678'),
    ('GV003', 'TS. Lê Hoàng Cường', 'Công Nghệ Thông Tin', 'lhcuong@dh.edu.vn', '0923456789'),
    ('GV004', 'ThS. Phạm Duy Vũ', 'Công Nghệ Thông Tin', 'pdvu@dh.edu.vn', '0934567890'),
    ('GV005', 'PGS.TS. Vũ Thị Dung', 'Khoa Học Cơ Bản', 'vtdung@dh.edu.vn', '0945678901'),
    ('GV006', 'TS. Hoàng Anh Tuấn', 'Khoa Học Cơ Bản', 'hatuan@dh.edu.vn', '0956789012'),
    ('GV007', 'ThS. Đinh Quang Minh', 'Khoa Học Cơ Bản', 'dqminh@dh.edu.vn', '0967890123'),
    ('GV008', 'TS. Bùi Thị Mai', 'Ngoại Ngữ', 'btmai@dh.edu.vn', '0978901234'),
    ('GV009', 'ThS. Ngô Văn Nam', 'Ngoại Ngữ', 'nvnam@dh.edu.vn', '0989012345'),
    ('GV010', 'PGS.TS. Đỗ Khắc Hiếu', 'Quản Trị Kinh Doanh', 'dkhieu@dh.edu.vn', '0990123456'),
    ('GV011', 'ThS. Trương Mai Lan', 'Quản Trị Kinh Doanh', 'tmlan@dh.edu.vn', '0909876543'),
    ('GV012', 'TS. Phan Thanh Tùng', 'Kế Toán - Kiểm Toán', 'pttung@dh.edu.vn', '0918765432'),
    ('GV013', 'ThS. Lương Thị Hoa', 'Kế Toán - Kiểm Toán', 'lthoa@dh.edu.vn', '0927654321'),
    ('GV014', 'TS. Dương Ngọc Hùng', 'Tài Chính Ngân Hàng', 'dnhung@dh.edu.vn', '0936543210'),
    ('GV015', 'PGS.TS. Trần Kim Yến', 'Lý Luận Chính Trị', 'tkyen@dh.edu.vn', '0945432109'),
    ('GV016', 'ThS. Nguyễn Bích Ngọc', 'Lý Luận Chính Trị', 'nbngoc@dh.edu.vn', '0954321098'),
    ('GV017', 'TS. Vũ Tiến Đạt', 'Luật Kinh Tế', 'vtdat@dh.edu.vn', '0963210987'),
    ('GV018', 'ThS. Đào Hồng Quang', 'Giáo Dục Quốc Phòng', 'dhquang@dh.edu.vn', '0972109876'),
    ('GV019', 'ThS. Lê Cẩm Tú', 'Khoa Học Cơ Bản', 'lctu@dh.edu.vn', '0981098765'),
    ('GV020', 'ThS. Nguyễn Tuấn Anh', 'Giáo Dục Thể Chất', 'ntanh@dh.edu.vn', '0990987654')
]

def import_data():
    try:
        db = Database()
        success = 0
        for ma, ten, khoa, email, sdt in teachers:
            # db.insert_giang_vien() sẽ tự động tạo luôn tài khoản users (pass: 123)
            if db.insert_giang_vien(ma, ten, khoa, email, sdt):
                print(f"✅ Đã thêm giảng viên: {ma} - {ten}")
                success += 1
            else:
                print(f"⚠️ Bỏ qua (đã tồn tại hoặc lỗi): {ma} - {ten}")
        
        print(f"\n🎉 Đã import xong {success}/{len(teachers)} giảng viên vào Database (Kèm tài khoản login mặc định)!")
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    import_data()
