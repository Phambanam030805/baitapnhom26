import sys
import random
from database import Database

thu_list = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7"]
ca_list = ["1-3", "4-6", "7-9", "10-12"]

def import_lhp():
    try:
        db = Database()
        
        # Fetching necessary IDs
        db.cursor.execute("SELECT id, ma_mh, ten_mh FROM mon_hoc")
        mon_hocs = db.cursor.fetchall()
        
        db.cursor.execute("SELECT id, ho_ten FROM giang_vien")
        giang_viens = db.cursor.fetchall()
        
        # Tiêu điểm chọn các học kỳ thuộc năm 2024-2025 hoặc 2023-2024 để test
        db.cursor.execute("SELECT id, ten_hoc_ky, nam_hoc FROM hoc_ky WHERE nam_hoc LIKE '%2024-2025%'")
        hoc_kys = db.cursor.fetchall()
        
        if not hoc_kys:
            # Fallback if no 24-25
            db.cursor.execute("SELECT id, ten_hoc_ky, nam_hoc FROM hoc_ky ORDER BY id DESC LIMIT 3")
            hoc_kys = db.cursor.fetchall()

        if not mon_hocs or not giang_viens or not hoc_kys:
            print("❌ Lỗi: Cơ sở dữ liệu thiếu Môn học, Giảng viên hoặc Học kỳ!")
            return
            
        print("--- BẮT ĐẦU TẠO 30 LỚP HỌC PHẦN ---")
        success = 0
        
        # Để đảm bảo mã duy nhất khi chạy lại script
        db.cursor.execute("SELECT COUNT(*) FROM lop_hoc_phan")
        start_idx = db.cursor.fetchone()[0] + 1
        
        for i in range(start_idx, start_idx + 30):
            # Chọn ngẫu nhiên dữ liệu
            mh = random.choice(mon_hocs)
            gv = random.choice(giang_viens)
            hk = random.choice(hoc_kys)
            
            id_mh, ma_mh, ten_mh = mh
            id_gv, ten_gv = gv
            id_hk, ten_hk, nam_hk = hk
            
            thu = random.choice(thu_list)
            ca = random.choice(ca_list)
            
            # Format mã lớp học phần theo phong cách đại học: [Mã Môn]_[Hai số cuối của năm]_[Số thứ tự lớp]
            # Ví dụ: CNTT101_24_01
            nam_prefix = nam_hk[2:4] # "2024-2025" -> "24"
            ma_lop_hp = f"{ma_mh}_{nam_prefix}_{i:02d}"
            
            # Lưu vào database (hàm insert đã có tự động tạo try/except bên trong database.py)
            if db.insert_lop_hoc_phan(ma_lop_hp, id_mh, id_gv, id_hk, thu, ca):
                print(f"✅ Đã thêm: {ma_lop_hp:<15} | Môn: {ten_mh[:15]}... | {thu} (Ca {ca:<5}) | GV: {ten_gv}")
                success += 1
            else:
                print(f"⚠️ Bỏ qua do trùng mã: {ma_lop_hp}")
                
        print(f"\n🎉 HOÀN TẤT! Đã thêm thành công {success}/30 Lớp học phần chuẩn với khóa ngoại vào CSDL.")
        
    except Exception as e:
        print(f"Lỗi hệ thống: {e}")

if __name__ == "__main__":
    import_lhp()
