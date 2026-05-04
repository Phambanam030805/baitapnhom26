# Phần mềm Quản lý Điểm hệ Đại học v5.0

## 📖 Giới thiệu
**Phần mềm Quản lý Điểm hệ Đại học** là một ứng dụng Desktop hiện đại được xây dựng hoàn toàn bằng ngôn ngữ Python. Ứng dụng sử dụng thư viện `Tkinter` cốt lõi nhưng được tùy biến sâu (custom styles) mang lại giao diện Material Design trẻ trung, chuyên nghiệp và hệ quản trị cơ sở dữ liệu `SQLite` gọn nhẹ không cần cài đặt thêm server.

Sản phẩm được thiết kế với kiến trúc phân quyền đa cấp (Role-based Access Control), tích hợp đầy đủ các luồng nghiệp vụ thực tế dành cho **Quản trị viên**, **Giảng viên** và **Sinh viên**.

---

## 🚀 Các tính năng nổi bật

### 1. Hệ thống Đăng nhập & Phân quyền (Role-based)
- **Mã hóa an toàn:** Mật khẩu được băm (hash) bằng thuật toán chuẩn `SHA-256`.
- **Khóa/Mở tài khoản:** Hệ thống hỗ trợ Admin khóa các tài khoản vi phạm.
- **Phân quyền chặt chẽ:** Tự động điều hướng và hiển thị các tính năng tương ứng với 3 loại tài khoản: `admin`, `teacher`, `student`.

### 2. Dành cho Quản trị viên (Admin)
- **Quản lý toàn diện:** Quản lý thông tin **Sinh viên**, **Giảng viên**, **Tài khoản người dùng**.
- **Quản lý cơ cấu đào tạo:** Dễ dàng thao tác thêm, sửa, xóa với **Khoa**, **Môn học**, **Lớp Hành chính**, **Lớp Học phần** và **Học kỳ**.
- **Bảng tin hệ thống:** Đăng tải thông báo chung hiển thị trên trang chủ của Giảng viên và Sinh viên.
- **Xuất dữ liệu:** Hỗ trợ xuất danh sách Sinh viên, danh sách Giảng viên ra file Excel.

### 3. Dành cho Giảng viên
- **Quản lý điểm số:** Giao diện nhập điểm trực quan, tự động tính toán điểm Trung bình (từ các cột Chuyên cần, Giữa kỳ, Cuối kỳ) và tự động xếp loại Điểm chữ.
- **Theo dõi lớp học:** Tô sáng sinh viên đang chọn, hỗ trợ phân loại sinh viên Đạt/Trượt.
- **Thống kê giảng dạy:** Xem số lượng sinh viên Đạt/Trượt, tỷ lệ qua môn ở từng Lớp học phần do mình phụ trách.
- **Xuất bảng điểm Excel:** Hỗ trợ xuất bảng điểm tổng kết của Lớp học phần phục vụ in ấn.
- Xem bảng tin thông báo từ hệ thống.

### 4. Dành cho Sinh viên
- **Đăng ký học phần:** Xem danh sách các Lớp học phần đang mở trong kỳ và thao tác Đăng ký/Hủy đăng ký môn học trực tuyến.
- **Theo dõi kết quả học tập:** Xem bảng điểm cá nhân chi tiết từng môn (Điểm hệ 10, Điểm chữ, Điểm hệ 4). Hệ thống tự động tính toán số Tín chỉ tích lũy và **GPA tổng**.
- **Xuất bảng điểm Excel:** Tải xuống bảng điểm cá nhân dưới dạng file Excel chuẩn form.
- Xem bảng tin thông báo từ Admin.

---

## 📂 Cấu trúc mã nguồn

Dự án được chia tách theo mô hình module hóa rõ ràng giúp dễ bảo trì và nâng cấp:

- `main.py` : Tệp chạy chính (Entry point), điều hướng giao diện dựa theo Role đăng nhập.
- `database.py` : Chứa toàn bộ các phương thức thao tác với CSDL (CRUD), xử lý business logic, tính toán GPA và mã hóa bảo mật.
- `gui_auth.py` : Màn hình Đăng nhập với giao diện hiện đại.
- `gui_admin.py` : Dashboard điều khiển dành riêng cho Quản trị viên.
- `gui_teacher.py`: Dashboard điều khiển dành riêng cho Giảng viên.
- `gui_student.py`: Dashboard điều khiển dành riêng cho Sinh viên.
- `gui_styles.py` : Hệ thống định dạng UI (Theme, màu sắc, Typography, custom widgets).
- `models.py` : (Tùy chọn) Định nghĩa cấu trúc các đối tượng dữ liệu.
- `excel_export.py` : Module chứa các tiện ích xuất báo cáo đa dạng ra định dạng Excel (sử dụng thư viện `openpyxl`).
- `ql_diem.db` : Tệp cơ sở dữ liệu SQLite (sẽ tự động khởi tạo nếu chưa tồn tại).
- Các tệp `import_*.py` : Bộ công cụ/scripts hỗ trợ nạp dữ liệu mẫu nhanh (ví dụ `import_sinh_vien.py`, `import_mon_hoc.py`...).
- `fix_db.py`, `reset_khoa_lop.py`: Các script hỗ trợ dọn dẹp hoặc sửa lỗi CSDL nếu cần.

---

## 💻 Hướng dẫn Cài đặt & Chạy ứng dụng

**Yêu cầu môi trường:** Python 3.8 trở lên.

1. Mở Terminal / Command Prompt tại thư mục dự án `QuanLyDiemDH`.
2. Cài đặt các thư viện phụ thuộc (nếu chưa có):
   ```bash
   pip install openpyxl
   ```
3. Khởi động phần mềm bằng lệnh:
   ```bash
   python main.py
   ```
4. Đăng nhập với các tài khoản mặc định (Mật khẩu mặc định đều là `123`):
   - **Admin:** `admin`
   - **Giảng viên:** `GV001`, `GV002`...
   - **Sinh viên:** `20240001`, `20240002`... (Dựa vào dữ liệu import)

> **Lưu ý:** Nếu chạy ứng dụng lần đầu và CSDL đang trống, bạn có thể chạy lần lượt các script có tiền tố `import_` (Ví dụ: `python import_sinh_vien.py`) để tự động khởi tạo dữ liệu mẫu thử nghiệm một cách nhanh chóng.

---

## 🎨 Thông tin thiết kế UI/UX

- Ứng dụng không phụ thuộc vào các thư viện giao diện nặng bên thứ ba (như PyQt, PySide, CustomTkinter). Thay vào đó, dự án can thiệp trực tiếp vào `ttk.Style` và các phương thức vẽ đồ họa của `Canvas` để mang đến diện mạo Material/Flat Design thực sự sang trọng.
- Hỗ trợ thay đổi kích thước cửa sổ (responsive) linh hoạt, các bảng biểu tự động dãn cách vừa vặn với kích thước màn hình.
- Tích hợp các hiệu ứng hover mượt mà cùng bảng màu Pastel/Indigo (Xanh chàm) chủ đạo đang là xu hướng hiện nay.
