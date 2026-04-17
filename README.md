# Phần mềm Quản lý Điểm Đại học (BTL Python)

## Giới thiệu
Đây là bài tập lớn môn Python cơ bản, sử dụng thư viện `Tkinter` cho giao diện và `SQLite` cho cơ sở dữ liệu.

## Cấu trúc thư mục
- `main.py`: Tệp chạy chính.
- `gui.py`: Giao diện người dùng.
- `database.py`: Xử lý cơ sở dữ liệu.
- `models.py`: Định nghĩa các lớp đối tượng.
- `ql_diem.db`: Tệp cơ sở dữ liệu (tự động tạo khi chạy).

## Cách chạy
Để khởi động phần mềm, bạn chỉ cần mở terminal trong thư mục `QuanLyDiemDH` và chạy lệnh:
```bash
python main.py
```

## Tính năng
1. **Quản lý Sinh viên**: Thêm sinh viên mới vào danh sách.
2. **Quản lý Môn học**: Thêm môn học và số tín chỉ.
3. **Quản lý Điểm**: 
   - Nhập điểm thành phần (Chuyên cần, Giữa kỳ, Cuối kỳ) cho sinh viên theo từng môn học.
   - Tự động tính điểm trung bình (TB) theo công thức: `10% CC + 30% GK + 60% CK`.
   - Hiển thị bảng điểm tổng hợp.

## Lưu ý
Khi nhập điểm, bạn cần điền đúng **ID Sinh viên** và **ID Môn học** (là số thứ tự cột ID đầu tiên trong bảng Sinh viên và Môn học).
