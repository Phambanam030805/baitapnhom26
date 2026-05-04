import sys
import random
from datetime import datetime, timedelta
from database import Database

ho_list = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
dem_nam = ["Văn", "Đức", "Hữu", "Hoàng", "Gia", "Thanh", "Minh", "Quang", "Tiến", "Nhật", "Hải", "Trọng"]
dem_nu = ["Thị", "Ngọc", "Thu", "Hoàng", "Phương", "Thanh", "Bích", "Mai", "Kim", "Diễm", "Bảo", "Nhã"]
ten_nam = ["Anh", "Bình", "Cường", "Dương", "Đạt", "Hải", "Hùng", "Huy", "Khang", "Khoa", "Lâm", "Long", "Minh", "Nam", "Phong", "Phúc", "Quân", "Sơn", "Thắng", "Thành", "Tuấn", "Việt", "Vũ"]
ten_nu = ["An", "Bích", "Châu", "Chi", "Diệp", "Dung", "Hà", "Hằng", "Hoa", "Hương", "Huyền", "Lan", "Linh", "Mai", "Ngọc", "Nhi", "Nhung", "Oanh", "Phương", "Quyên", "Thảo", "Trang", "Uyên", "Yến"]

def random_date_of_birth():
    # Random DOB for college students (born between 2003 and 2005)
    start_date = datetime(2003, 1, 1)
    end_date = datetime(2005, 12, 31)
    random_days = random.randrange((end_date - start_date).days)
    dob = start_date + timedelta(days=random_days)
    return dob.strftime("%d/%m/%Y")

def import_students():
    try:
        db = Database()
        db.cursor.execute("SELECT id, ma_lop FROM lop_hc")
        classes = db.cursor.fetchall()
        
        if not classes:
            print("❌ Lỗi: Chưa có lớp hành chính nào trong cơ sở dữ liệu!")
            return
            
        print(f"--- BẮT ĐẦU TẠO 50 SINH VIÊN ---")
        
        success = 0
        base_ma_sv = 20240000
        
        # Để đảm bảo mã SV không bị trùng nếu chạy lại script nhiều lần, 
        # tìm mã lớn nhất bắt đầu bằng 20 trong DB
        db.cursor.execute("SELECT ma_sv FROM sinh_vien WHERE ma_sv LIKE '20%' ORDER BY ma_sv DESC LIMIT 1")
        last_msv = db.cursor.fetchone()
        if last_msv:
            try:
                base_ma_sv = int(last_msv[0])
            except:
                pass
                
        for i in range(1, 51):
            base_ma_sv += 1
            ma_sv = str(base_ma_sv)
            
            is_male = random.choice([True, False])
            ho = random.choice(ho_list)
            if is_male:
                dem = random.choice(dem_nam)
                ten = random.choice(ten_nam)
                gioi_tinh = "Nam"
            else:
                dem = random.choice(dem_nu)
                ten = random.choice(ten_nu)
                gioi_tinh = "Nữ"
                
            ho_ten = f"{ho} {dem} {ten}"
            ngay_sinh = random_date_of_birth()
            
            # Chọn ngẫu nhiên một lớp hành chính (ưu tiên phân bổ đều)
            lop_hc = classes[i % len(classes)]
            id_lop = lop_hc[0]
            ten_lop = lop_hc[1]
            
            # db.insert_sinh_vien sẽ tự động tạo User account
            if db.insert_sinh_vien(ma_sv, ho_ten, ngay_sinh, gioi_tinh, id_lop):
                print(f"✅ Đã thêm: {ma_sv} | {ho_ten:<20} | {ngay_sinh} | {gioi_tinh:<3} | Lớp: {ten_lop}")
                success += 1
            else:
                print(f"⚠️ Lỗi khi thêm {ma_sv} - {ho_ten}")
                
        print(f"\n🎉 HOÀN TẤT! Đã nhập {success}/50 sinh viên thành công.")
        print("Tất cả sinh viên đều đã có tài khoản (Username: Mã SV, Password: 123)")
        
    except Exception as e:
        print(f"Lỗi hệ thống: {e}")

if __name__ == "__main__":
    import_students()
