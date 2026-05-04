import sys
from database import Database

courses = [
    ('CNTT101', 'Nhập Môn Công Nghệ Thông Tin', 3, 'Kiến thức tổng quan về máy tính và CNTT'),
    ('CNTT102', 'Lập Trình C++ Cơ Bản', 3, 'Cấu trúc lập trình, vòng lặp, mảng, hàm'),
    ('CNTT201', 'Cấu Trúc Dữ Liệu Và Giải Thuật', 4, 'Danh sách liên kết, cây, đồ thị, thuật toán sắp xếp'),
    ('CNTT202', 'Lập Trình Hướng Đối Tượng', 3, 'Kế thừa, đa hình, đóng gói, trừu tượng (Java/C#)'),
    ('CNTT301', 'Cơ Sở Dữ Liệu', 3, 'Thiết kế ERD, truy vấn SQL, chuẩn hóa dữ liệu'),
    ('CNTT302', 'Lập Trình Web Cơ Bản', 3, 'HTML, CSS, JavaScript, PHP cơ bản'),
    ('CNTT303', 'Trí Tuệ Nhân Tạo', 3, 'Tìm kiếm, suy diễn logic, máy học cơ bản'),
    ('TOAN101', 'Toán Cao Cấp A1', 3, 'Giải tích hàm một biến, giới hạn, đạo hàm, tích phân'),
    ('TOAN102', 'Toán Cao Cấp A2', 3, 'Giải tích hàm nhiều biến, chuỗi số, phương trình vi phân'),
    ('TOAN201', 'Đại Số Tuyến Tính', 3, 'Ma trận, định thức, không gian vector'),
    ('TOAN202', 'Xác Suất Thống Kê', 3, 'Xác suất, biến ngẫu nhiên, ước lượng, kiểm định giả thuyết'),
    ('LLCT101', 'Triết Học Mác - Lênin', 3, 'Triết học Mác - Lênin và vai trò trong đời sống xã hội'),
    ('LLCT102', 'Kinh Tế Chính Trị Mác - Lênin', 2, 'Sản xuất hàng hóa, giá trị thặng dư, CNTB'),
    ('LLCT103', 'Chủ Nghĩa Xã Hội Khoa Học', 2, 'Giai cấp công nhân, CM XHCN, thời kỳ quá độ'),
    ('NNA101',  'Tiếng Anh Cơ Bản 1', 4, 'Ngữ pháp cơ bản, từ vựng giao tiếp sơ cấp'),
    ('NNA102',  'Tiếng Anh Cơ Bản 2', 4, 'Tiếng Anh trình độ Pre-Intermediate'),
    ('NNA201',  'Tiếng Anh Chuyên Ngành', 3, 'Tiếng Anh đọc hiểu tài liệu chuyên ngành CNTT/Kinh tế'),
    ('QTKD101', 'Quản Trị Học', 3, 'Nguyên lý quản trị, cơ cấu tổ chức, lãnh đạo'),
    ('QTKD102', 'Marketing Căn Bản', 3, 'Thị trường, khách hàng, chiến lược 4P'),
    ('KETO101', 'Nguyên Lý Kế Toán', 3, 'Tài khoản kế toán, bảng cân đối kế toán'),
    ('KETO102', 'Kế Toán Tài Chính', 3, 'Ghi chép sổ sách, báo cáo thu chi doanh nghiệp'),
    ('KTTC101', 'Kinh Tế Vi Mô', 3, 'Cung cầu, giá cả, hành vi người tiêu dùng'),
    ('KTTC102', 'Kinh Tế Vĩ Mô', 3, 'Lạm phát, thất nghiệp, tăng trưởng kinh tế, GDP'),
    ('LUAT101', 'Pháp Luật Đại Cương', 2, 'Hệ thống pháp luật VN, luật dân sự, luật hình sự'),
    ('KNS101',  'Kỹ Năng Giao Tiếp', 2, 'Kỹ năng thuyết trình, làm việc nhóm, giao tiếp hiệu quả'),
    ('GDQP101', 'Giáo Dục Quốc Phòng - An Ninh', 4, 'Đường lối quân sự, đội ngũ, chiến thuật cơ bản'),
    ('GDTC101', 'Giáo Dục Thể Chất 1', 1, 'Chạy cự ly ngắn, điền kinh cơ bản'),
    ('GDTC102', 'Giáo Dục Thể Chất 2', 1, 'Bóng chuyền / Bóng rổ / Cầu lông đại cương')
]

def import_data():
    try:
        db = Database()
        success = 0
        for ma, ten, stc, mota in courses:
            if db.insert_mon_hoc(ma, ten, stc, mota):
                print(f"✅ Đã thêm: {ma} - {ten}")
                success += 1
            else:
                print(f"⚠️ Bỏ qua (đã tồn tại hoặc lỗi): {ma} - {ten}")
        
        print(f"\n🎉 Đã import xong {success}/{len(courses)} môn học vào Database!")
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    import_data()
