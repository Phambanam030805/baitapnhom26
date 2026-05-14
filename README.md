# 🎓 Phần mềm Quản lý Điểm Hệ Đại học (UniGrade Manager)

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/database-MySQL-orange.svg)](https://www.mysql.com/)
[![UI Library](https://img.shields.io/badge/UI-Tkinter%20Custom-green.svg)](https://docs.python.org/3/library/tkinter.html)
[![Security](https://img.shields.io/badge/Security-SHA--256-red.svg)](https://en.wikipedia.org/wiki/SHA-2)

**UniGrade Manager** là giải pháp quản trị giáo dục hiện đại, hỗ trợ quản lý điểm số, nhân sự và đào tạo theo hệ thống tín chỉ. Ứng dụng được thiết kế với giao diện Dashboard trực quan, hiệu ứng chuyển động mượt mà và khả năng bảo mật dữ liệu cao.

---

## ✨ Điểm nổi bật về mặt lập trình

- **Giao diện Modern UI:** Tận dụng tối đa sức mạnh của Tkinter Canvas để vẽ Gradient, bo góc (Rounded Corners) và hiệu ứng Animation khi chuyển trang.
- **Phân quyền đa cấp (RBAC):** Hệ thống phân quyền chặt chẽ giữa 3 vai trò: **Quản trị viên**, **Giảng viên** và **Sinh viên**.
- **Xử lý dữ liệu thông minh:**
  - Tự động tính điểm trung bình hệ 10, hệ 4 và quy đổi điểm chữ (A, B, C, D, F).
  - Thống kê tỷ lệ học tập bằng biểu đồ **Matplotlib** trực quan.
  - Tìm kiếm và lọc dữ liệu thời gian thực (Instant Search).
- **Xuất báo cáo chuyên nghiệp:** Tích hợp bộ công cụ xuất file Excel (.xlsx) cho bảng điểm, danh sách sinh viên và nhật ký hệ thống.
- **Kiến trúc bền vững:** Sử dụng mô hình Module hóa, tách biệt logic nghiệp vụ (`database.py`) và giao diện (`gui_*.py`).

---

## 🚀 Tính năng cốt lõi

### 🔑 Hệ thống xác thực
- Đăng nhập bảo mật với mật khẩu mã hóa **SHA-256**.
- Tự động chuyển hướng đến Dashboard theo vai trò người dùng.
- Quản lý trạng thái tài khoản (Kích hoạt/Khóa).

### 👤 Module Quản trị viên (Admin)
- **Quản lý danh mục:** Khoa, Lớp hành chính, Môn học, Học kỳ.
- **Quản lý nhân sự:** Thêm, sửa, xóa, tìm kiếm Sinh viên và Giảng viên.
- **Quản lý tài khoản:** Cấp quyền và reset mật khẩu cho người dùng.
- **Hệ thống bảng tin:** Đăng thông báo quan trọng toàn trường.
- **Giám sát:** Theo dõi nhật ký hoạt động (Logs) của toàn bộ người dùng.
- **Bảng vàng:** Vinh danh những sinh viên có thành tích xuất sắc.

### 👨‍🏫 Module Giảng viên (Teacher)
- **Quản lý lớp học phần:** Xem danh sách các lớp đang phụ trách.
- **Nhập điểm chuyên sâu:** Nhập điểm Chuyên cần, Giữa kỳ, Thực hành, Cuối kỳ. Hệ thống tự động tính điểm tổng kết.
- **Điểm danh:** Theo dõi tình trạng đi học của sinh viên.
- **Thống kê:** Xem biểu đồ phân loại học lực của lớp học phần.
- **Báo cáo:** Xuất bảng điểm lớp học phần ra Excel.

### 🎓 Module Sinh viên (Student)
- **Tra cứu kết quả:** Xem bảng điểm chi tiết từng học kỳ và điểm tổng kết toàn khóa.
- **Theo dõi tiến độ:** Tự động tính số tín chỉ tích lũy và GPA.
- **Thông báo:** Nhận thông tin mới nhất từ nhà trường và giảng viên.
- **Tiện ích:** Xuất bảng điểm cá nhân ra file Excel để lưu trữ.

---

## 🛠 Công nghệ sử dụng (Tech Stack)

| Thành phần | Công nghệ |
|---|---|
| **Ngôn ngữ** | Python 3.8+ |
| **Giao diện (UI)** | Tkinter + ttk + Canvas (Custom Style) |
| **Đồ họa** | Matplotlib (Biểu đồ thống kê) |
| **Cơ sở dữ liệu** | MySQL (XAMPP) |
| **Xử lý Excel** | OpenPyXL |
| **Bảo mật** | Mã hóa SHA-256 |

---

## 📂 Cấu trúc dự án
```text
C:\Users\ADMIN\QuanLyDiemDH
├── main.py              # File chạy chính của ứng dụng
├── database.py          # Xử lý kết nối và truy vấn CSDL
├── gui_styles.py        # Định nghĩa Theme, Màu sắc và Styles
├── gui_auth.py          # Giao diện Đăng nhập & Xác thực
├── gui_admin.py         # Dashboard cho Quản trị viên
├── gui_teacher.py       # Dashboard cho Giảng viên
├── gui_student.py       # Dashboard cho Sinh viên
├── excel_export.py      # Module xuất dữ liệu ra Excel
├── models.py            # Định nghĩa các lớp đối tượng dữ liệu
└── README.md            # Tài liệu hướng dẫn dự án
```

---

## 🛠 Hướng dẫn Cài đặt & Triển khai

### 1. Chuẩn bị
- Cài đặt [Python 3.8+](https://www.python.org/).
- Cài đặt [XAMPP](https://www.apachefriends.org/) để sử dụng MySQL.

### 2. Thiết lập Cơ sở dữ liệu
- Mở XAMPP Control Panel, khởi động **Apache** và **MySQL**.
- Truy cập `localhost/phpmyadmin` và tạo database mới với tên: `ql_diem_dh`.
- *Lưu ý: Ứng dụng sẽ tự động tạo bảng và nạp dữ liệu mẫu trong lần chạy đầu tiên.*

### 3. Cài đặt thư viện cần thiết
Mở Terminal/Command Prompt và chạy lệnh:
```bash
pip install mysql-connector-python openpyxl matplotlib
```

### 4. Khởi chạy ứng dụng
```bash
python main.py
```

---

## 📜 Thông tin tác giả
- **Tác giả:** [Phạm Bá Nam/Nhóm 26]
- **Dự án:** Phần mềm Quản lý Điểm Hệ Đại học
- **Giấy phép:** MIT License



