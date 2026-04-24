# Phần mềm Quản lý Điểm hệ Đại học v5.0

## 📖 Giới thiệu
**Phần mềm Quản lý Điểm hệ Đại học** là một ứng dụng Desktop hiện đại được xây dựng hoàn toàn bằng ngôn ngữ Python cơ bản. Phần mềm ứng dụng thư viện `Tkinter` (đã được làm lại giao diện theo phong cách thiết kế hiện đại) và hệ quản trị cơ sở dữ liệu `SQLite` gọn nhẹ.

Sản phẩm được thiết kế với kiến trúc phân quyền đa cấp, tích hợp đầy đủ tính năng dành cho **Quản trị viên**, **Giảng viên** và **Sinh viên**. 

---

## 🚀 Các tính năng nổi bật

### 1. Hệ thống Đăng nhập & Phân quyền (Role-based)
- **Mã hóa an toàn:** Mật khẩu được băm bằng chuẩn `SHA-256`.
- **Khóa/Mở tài khoản:** Hệ thống hỗ trợ khóa các tài khoản vi phạm.
- **Phân quyền chặt chẽ:** Giao diện và các chức năng tự động thích ứng với 3 loại tài khoản: `admin`, `teacher`, `student`.

### 2. Dành cho Quản trị viên (Admin)
- Quản lý toàn diện: **Sinh viên**, **Giảng viên**, **Tài khoản người dùng**.
- Quản lý cơ cấu đào tạo: **Khoa**, **Môn học**, **Lớp Hành chính**, **Lớp Học phần**, **Học kỳ**.
- **Đăng tải thông báo** chung cho toàn hệ thống.

### 3. Dành cho Giảng viên
- **Nhập điểm:** Tự động điền và tính toán theo chuẩn (CC, GK, CK). Giao diện nhập điểm hỗ trợ tự động tô sáng sinh viên đang chọn.
- **Thống kê giảng dạy:** Xem số lượng sinh viên đạt/trượt, tỷ lệ qua môn ở từng lớp học phần phụ trách.
- Xem bảng tin hệ thống.

### 4. Dành cho Sinh viên
- **Đăng ký môn học:** Xem danh sách các lớp học phần đang mở và đăng ký trực tuyến.
- **Bảng điểm cá nhân:** Theo dõi điểm số từng môn (Điểm hệ 10, Điểm chữ, Điểm hệ 4) và tự động tính **GPA tích lũy**.
- Bảng tin thông báo hệ thống.

---

## 📂 Cấu trúc mã nguồn

Dự án được chia tách theo mô hình module hóa rõ ràng:

- `main.py` : Tệp chạy chính (Entry point), điều hướng giao diện dựa theo Role đăng nhập.
- `database.py` : Chứa toàn bộ thao tác truy vấn (CRUD), xử lý thuật toán, tính toán GPA và mã hóa.
- `gui_auth.py` : Màn hình Đăng nhập giao diện hiện đại.
- `gui_admin.py` : Bảng điều khiển (Dashboard) dành riêng cho Admin.
- `gui_teacher.py`: Dashboard dành riêng cho Giảng viên.
- `gui_student.py`: Dashboard dành riêng cho Sinh viên.
- `gui_styles.py` : Hệ thống định dạng UI (Theme, màu sắc, Typography, custom widgets).
- `models.py` : Định nghĩa cấu trúc các đối tượng dữ liệu.
- `ql_diem.db` : Tệp cơ sở dữ liệu SQLite (Tự động khởi tạo nếu chưa có).

---

## 💻 Hướng dẫn Cài đặt & Chạy ứng dụng

**Yêu cầu hệ thống:** Python 3.8+ 

1. Mở Terminal / Command Prompt tại thư mục dự án `QuanLyDiemDH`.
2. Khởi động phần mềm bằng lệnh:
   ```bash
   python main.py
   ```
3. Đăng nhập với các tài khoản mặc định (Mật khẩu mặc định đều là `123`):
   - **Admin:** `admin`
   - **Giảng viên:** `GV001` (hoặc các mã GV khác)
   - **Sinh viên:** `SV001` (hoặc các mã SV khác)

---

## 🎨 Thông tin thiết kế UI/UX
- Ứng dụng không sử dụng thư viện giao diện bên thứ ba (PyQt, CustomTkinter) mà can thiệp trực tiếp vào `ttk.Style` và các phương thức vẽ đồ họa của Canvas để đem đến diện mạo Material/Flat Design sang trọng.
- Ứng dụng hỗ trợ thay đổi kích thước cửa sổ linh hoạt theo màn hình thực tế của người dùng.
