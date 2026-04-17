class User:
    def __init__(self, id, username, role, reference_id=None):
        self.id = id
        self.username = username
        self.role = role
        self.reference_id = reference_id

class SinhVien:
    def __init__(self, id, ma_sv, ho_ten, ngay_sinh, gioi_tinh, lop_hanh_chinh):
        self.id = id
        self.ma_sv = ma_sv
        self.ho_ten = ho_ten
        self.ngay_sinh = ngay_sinh
        self.gioi_tinh = gioi_tinh
        self.lop_hanh_chinh = lop_hanh_chinh

class GiangVien:
    def __init__(self, id, ma_gv, ho_ten, khoa, email, sdt):
        self.id = id
        self.ma_gv = ma_gv
        self.ho_ten = ho_ten
        self.khoa = khoa
        self.email = email
        self.sdt = sdt

class MonHoc:
    def __init__(self, id, ma_mh, ten_mh, so_tin_chi, mo_ta=""):
        self.id = id
        self.ma_mh = ma_mh
        self.ten_mh = ten_mh
        self.so_tin_chi = so_tin_chi
        self.mo_ta = mo_ta

class HocKy:
    def __init__(self, id, ten_hoc_ky, nam_hoc, trang_thai):
        self.id = id
        self.ten_hoc_ky = ten_hoc_ky
        self.nam_hoc = nam_hoc
        self.trang_thai = trang_thai

class LopHocPhan:
    def __init__(self, id, ma_lop_hp, id_mon_hoc, id_giang_vien, id_hoc_ky):
        self.id = id
        self.ma_lop_hp = ma_lop_hp
        self.id_mon_hoc = id_mon_hoc
        self.id_giang_vien = id_giang_vien
        self.id_hoc_ky = id_hoc_ky

class Diem:
    def __init__(self, id_sinh_vien, id_lop_hp, diem_cc, diem_gk, diem_ck, diem_tb):
        self.id_sinh_vien = id_sinh_vien
        self.id_lop_hp = id_lop_hp
        self.diem_cc = diem_cc
        self.diem_gk = diem_gk
        self.diem_ck = diem_ck
        self.diem_tb = diem_tb
