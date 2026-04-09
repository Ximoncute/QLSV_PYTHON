from sqlalchemy import Column, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from backend1.db.session import Base

class TK_XetTuyen(Base):
    __tablename__ = "tk_xet_tuyen"
    ma_tk = Column(String(12), primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    mat_khau = Column(String(255), nullable=False)
    
    hoso = relationship("HSO_XetTuyen", back_populates="tai_khoan", uselist=False)

class HSO_XetTuyen(Base):
    __tablename__ = "hso_xet_tuyen"
    ma_hso = Column(String(12), primary_key=True)
    ma_tk = Column(String(12), ForeignKey("tk_xet_tuyen.ma_tk"))
    ho_ten = Column(String(100), nullable=False)
    cccd = Column(String(12), unique=True, nullable=False)
    sdt = Column(String(15), unique=True, nullable=False)
    
    tai_khoan = relationship("TK_XetTuyen", back_populates="hoso")
    pt_xet_tuyens = relationship("PT_XetTuyen", back_populates="hoso")
    sinh_viens = relationship("SinhVien", back_populates="hoso")

class PT_XetTuyen(Base):
    __tablename__ = "pt_xet_tuyen"
    ma_ptxt = Column(String(12), primary_key=True)
    ma_nganh = Column(String(10), ForeignKey("nganh.ma_nganh"))
    phuong_thuc = Column(String(100), nullable=False)
    diem = Column(String(10), nullable=False)
    trang_thai = Column(String(100), nullable=False, default="Chờ duyệt")
    ma_hso = Column(String(10), ForeignKey("hso_xet_tuyen.ma_hso"))
    ma_qt = Column(String(10), ForeignKey("quan_tri.ma_qt"))
    
    hoso = relationship("HSO_XetTuyen", back_populates="pt_xet_tuyens")
    nganh = relationship("Nganh", back_populates="pt_xet_tuyens")
    admin = relationship("QuanTri", back_populates="pt_xet_tuyens")
