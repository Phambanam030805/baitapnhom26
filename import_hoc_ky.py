import sys
from database import Database

semesters = [
    ("Học kỳ 1", "2018-2019"),
    ("Học kỳ 2", "2018-2019"),
    ("Học kỳ Hè", "2018-2019"),
    
    ("Học kỳ 1", "2019-2020"),
    ("Học kỳ 2", "2019-2020"),
    ("Học kỳ Hè", "2019-2020"),
    
    ("Học kỳ 1", "2020-2021"),
    ("Học kỳ 2", "2020-2021"),
    ("Học kỳ Hè", "2020-2021"),
    
    ("Học kỳ 1", "2021-2022"),
    ("Học kỳ 2", "2021-2022"),
    ("Học kỳ Hè", "2021-2022"),
    
    ("Học kỳ 1", "2022-2023"),
    ("Học kỳ 2", "2022-2023"),
    ("Học kỳ Hè", "2022-2023"),
    
    ("Học kỳ 1", "2023-2024"),
    ("Học kỳ 2", "2023-2024"),
    ("Học kỳ Hè", "2023-2024"),
    
    ("Học kỳ 1", "2024-2025"),
    ("Học kỳ 2", "2024-2025")
]

def import_semesters():
    try:
        db = Database()
        
        # Check if there are existing semesters to avoid duplicates if possible
        db.cursor.execute("SELECT ten_hoc_ky, nam_hoc FROM hoc_ky")
        existing = set((r[0], r[1]) for r in db.cursor.fetchall())
        
        print("--- BẮT ĐẦU TẠO 20 HỌC KỲ ---")
        success = 0
        
        for ten, nam in semesters:
            if (ten, nam) in existing:
                print(f"⚠️ Bỏ qua (đã tồn tại): {ten} - Năm học {nam}")
                continue
                
            # Hàm insert_hoc_ky trong database.py không bắt lỗi trả về False nên ta bọc lại
            try:
                db.insert_hoc_ky(ten, nam)
                print(f"✅ Đã thêm: {ten:<12} | Năm học: {nam}")
                success += 1
            except Exception as e:
                print(f"⚠️ Lỗi khi thêm {ten} {nam}: {e}")
                
        print(f"\n🎉 HOÀN TẤT! Đã thêm {success} Học kỳ mới vào cơ sở dữ liệu.")
        
    except Exception as e:
        print(f"Lỗi hệ thống: {e}")

if __name__ == "__main__":
    import_semesters()
