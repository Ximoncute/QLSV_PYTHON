from sqlalchemy import Column, String, Date, Float, Integer, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from backend1.db.session import Base

class SinhVien(Base):
    __tablename__ = "sinh_vien"
    ma_sv = Column(String(15), primary_key=True)
    ho_ten = Column(String(100), nullable=False)
    ngay_sinh = Column(Date, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    so_dien_thoai = Column(String(15))
    cccd = Column(String(12), unique=True)
    mat_khau = Column(String(255), nullable=False)
    ma_lop = Column(String(15), ForeignKey("lop.ma_lop"))
    ma_hso = Column(String(10), ForeignKey("hso_xet_tuyen.ma_hso"))
    trang_thai = Column(String(20), default="Đang học")
    ngay_nhap_hoc = Column(Date)
    
    lop = relationship("Lop", back_populates="sinh_viens")
    hoso = relationship("HSO_XetTuyen", back_populates="sinh_viens")
    kq_hoc_taps = relationship("KQ_HocTap", back_populates="sinh_vien")
    tot_nghiep = relationship("TotNghiep", back_populates="sinh_vien", uselist=False)
    tb_nhans = relationship("TB_NguoiNhan", back_populates="sinh_vien")
    hoc_phis = relationship("HocPhi", back_populates="sinh_vien", cascade="all, delete-orphan")


class KQ_HocTap(Base):
    __tablename__ = "kq_hoc_tap"
    ma_sv = Column(String(15), ForeignKey("sinh_vien.ma_sv"), primary_key=True)
    ma_mh = Column(String(10), ForeignKey("mon_hoc.ma_mh"), primary_key=True)
    hoc_ky = Column(String(20), primary_key=True)
    diem = Column(Float, nullable=False)
    
    sinh_vien = relationship("SinhVien", back_populates="kq_hoc_taps")
    mon_hoc = relationship("MonHoc", back_populates="kq_hoc_taps")

class TotNghiep(Base):
    __tablename__ = "tot_nghiep"
    ma_sv = Column(String(15), ForeignKey("sinh_vien.ma_sv"), primary_key=True)
    gpa = Column(Float, nullable=False)
    xep_loai = Column(String(20), nullable=False)
    
    __table_args__ = (
        CheckConstraint("gpa >= 0 AND gpa <= 4.0", name="check_gpa_range"),
    )
    
    sinh_vien = relationship("SinhVien", back_populates="tot_nghiep")

class HocPhi(Base):
    __tablename__ = "hoc_phi"
    id = Column(Integer, primary_key=True)
    ma_sv = Column(String(15), ForeignKey("sinh_vien.ma_sv"))
    ten_hoc_ky = Column(String(100), nullable=False)
    tong_tien = Column(Float, nullable=False)
    da_dong = Column(Float, default=0)
    con_no = Column(Float, default=0)
    han_nop = Column(Date)
    trang_thai = Column(String(50))
    
    sinh_vien = relationship("SinhVien", back_populates="hoc_phis")
    chi_tiets = relationship("HocPhiChiTiet", back_populates="hoc_phi", cascade="all, delete-orphan")

class HocPhiChiTiet(Base):
    __tablename__ = "hoc_phi_chi_tiet"
    id = Column(Integer, primary_key=True)
    hoc_phi_id = Column(Integer, ForeignKey("hoc_phi.id"))
    ten_khoan_muc = Column(String(100), nullable=False)
    so_tien = Column(Float, nullable=False)
    trang_thai = Column(String(50))
    
    hoc_phi = relationship("HocPhi", back_populates="chi_tiets")
