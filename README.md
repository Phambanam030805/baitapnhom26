# 🎓 Phần mềm Quản lý Điểm Hệ Đại học (UniGrade Manager)

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/database-MySQL-orange.svg)](https://www.mysql.com/)
[![UI Library](https://img.shields.io/badge/UI-Tkinter%20Custom-green.svg)](https://docs.python.org/3/library/tkinter.html)

**UniGrade Manager** là một giải pháp quản lý đào tạo toàn diện dành cho các trường đại học, được phát triển trên nền tảng Python với tiêu chí: **Trực quan - Bảo mật - Hiệu quả**. Ứng dụng không chỉ đơn thuần là công cụ nhập liệu mà còn là một hệ sinh thái nhỏ kết nối giữa Quản trị viên, Giảng viên và Sinh viên.

---

## ✨ Điểm khác biệt so với các phần mềm cơ bản
Không giống như các bài tập quản lý điểm thông thường sử dụng file Text hay SQLite đơn giản, **UniGrade Manager** được đầu tư kỹ lưỡng về:
- **Trải nghiệm người dùng (UX):** Giao diện được tinh chỉnh bằng hệ thống Custom Styles, mô phỏng phong cách Material Design hiện đại, mang lại cảm giác chuyên nghiệp thay vì giao diện thô sơ mặc định của Tkinter.
- **Kiến trúc dữ liệu:** Sử dụng MySQL cho phép xử lý quan hệ phức tạp giữa Sinh viên - Lớp học phần - Điểm số một cách mượt mà và an toàn.
- **Tính tự động hóa:** Hệ thống tự động tính điểm trung bình, quy đổi điểm chữ (A, B, C, D, F), tính GPA hệ 4 và xếp loại học lực ngay khi giảng viên nhập điểm.

---

## 🛠 Công nghệ sử dụng (Tech Stack)

| Thành phần | Công nghệ | Chi tiết |
|---|---|---|
| **Ngôn ngữ** | Python 3.8+ | Ngôn ngữ lập trình chính |
| **Giao diện (UI)** | Tkinter + ttk.Style | Tùy biến sâu Canvas & Styles |
| **Cơ sở dữ liệu** | MySQL (XAMPP) | Quản trị dữ liệu quan hệ |
| **Xử lý Excel** | OpenPyXL | Xuất báo cáo, bảng điểm chuyên nghiệp |
| **Bảo mật** | SHA-256 | Mã hóa mật khẩu người dùng |

---

## 🚀 Tính năng cốt lõi

### 🔑 Hệ thống xác thực & Phân quyền
- **Đăng nhập đa vai trò:** Tự động nhận diện quyền hạn để hiển thị Dashboard tương ứng.
- **Bảo mật:** Mật khẩu được băm một chiều, ngăn chặn rò rỉ dữ liệu ngay cả khi lộ database.
- **Quản lý trạng thái:** Admin có quyền khóa/mở tài khoản linh hoạt.

### 👤 Module Quản trị viên (Admin)
- **Quản trị hệ thống:** Quản lý tập trung thông tin Khoa, Lớp hành chính, Môn học và Học kỳ.
- **Quản lý nhân sự:** Thêm mới/Chỉnh sửa thông tin hàng loạt Sinh viên và Giảng viên.
- **Thông báo:** Đăng tin tức lên bảng tin chung toàn trường.
- **Báo cáo:** Xuất danh sách nhân sự ra Excel chỉ với một click.

### 👨‍🏫 Module Giảng viên (Teacher)
- **Quản lý lớp học phần:** Theo dõi danh sách sinh viên trong từng lớp mình phụ trách.
- **Nhập điểm thông minh:** Giao diện lưới (Treeview) hỗ trợ nhập điểm thành phần. Hệ thống tự động "nhảy" điểm tổng kết và điểm chữ.
- **Thống kê:** Xem tỷ lệ Đạt/Trượt trực quan.
- **Báo cáo:** Xuất bảng điểm lớp học phần phục vụ lưu trữ/in ấn.

### 🎓 Module Sinh viên (Student)
- **Đăng ký môn học:** Quy trình đăng ký/hủy lớp học phần trực tuyến đơn giản.
- **Tra cứu kết quả:** Xem bảng điểm cá nhân chi tiết qua từng kỳ học.
- **Theo dõi tiến độ:** Tự động tính tổng tín chỉ tích lũy và GPA toàn khóa.
- **Cá nhân hóa:** Tự xuất bảng điểm cá nhân ra Excel.

---

## 📂 Cấu trúc dự án
```text
C:\Users\ADMIN\QuanLyDiemDH
├── main.py              # Điểm khởi đầu của ứng dụng
├── database.py          # Trái tim của hệ thống (Xử lý SQL & Business Logic)
├── models.py            # Định nghĩa các lớp đối tượng (POJO style)
├── gui_styles.py        # Định nghĩa màu sắc, font chữ, styles UI
├── gui_auth.py          # Màn hình đăng nhập & bảo mật
├── gui_admin.py         # Giao diện dành cho Quản trị viên
├── gui_teacher.py       # Giao diện dành cho Giảng viên
├── gui_student.py       # Giao diện dành cho Sinh viên
├── excel_export.py      # Tiện ích xuất dữ liệu báo cáo
├── import_*.py          # Các công cụ nạp dữ liệu mẫu nhanh
└── reset_khoa_lop.py    # Script dọn dẹp và khởi tạo lại danh mục
```

---

## 🛠 Hướng dẫn Cài đặt & Triển khai

### 1. Chuẩn bị môi trường
- Cài đặt **Python 3.8** hoặc mới hơn.
- Cài đặt **XAMPP** để chạy MySQL Server.

### 2. Thiết lập Database
1. Mở XAMPP, Start **Apache** và **MySQL**.
2. Vào `phpMyAdmin` tạo database tên: `ql_diem_dh`.
3. **Lưu ý:** Không cần import file SQL thủ công, phần mềm sẽ tự động khởi tạo cấu trúc bảng và dữ liệu mẫu khi chạy lần đầu.

### 3. Cài đặt thư viện
```bash
pip install mysql-connector-python openpyxl
```

### 4. Khởi chạy
```bash
python main.py
```

---

## ⚠️ Giải quyết sự cố thường gặp (Troubleshooting)

- **Lỗi kết nối CSDL:** Kiểm tra xem MySQL trong XAMPP đã Start chưa. Đảm bảo port mặc định là 3306.
- **Lỗi Font chữ:** Giao diện sử dụng font `Segoe UI`. Nếu bạn dùng Linux/macOS, hãy cài đặt font này hoặc chỉnh sửa trong `gui_styles.py`.
- **Lỗi xuất Excel:** Đảm bảo file Excel bạn đang định xuất không bị mở bởi một ứng dụng khác.

---

## 🗺 Lộ trình phát triển (Roadmap)
- [ ] Tích hợp biểu đồ thống kê bằng `Matplotlib`.
- [ ] Chế độ tối (Dark Mode) cho giao diện.
- [ ] Gửi thông báo điểm qua Email cho sinh viên.
- [ ] Chức năng sao lưu (Backup) database tự động.

---

## 📜 Giấy phép & Tác giả
- **Tác giả:** [Tên của bạn/Nhóm của bạn]
- **Học phần:** Kỹ thuật Đồ họa Máy tính - Nhóm 19
- **Giấy phép:** MIT License - Tự do sử dụng và phát triển thêm.

---
*Chúc bạn có trải nghiệm tuyệt vời với UniGrade Manager!*
