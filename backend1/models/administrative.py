from sqlalchemy import Column, String, Integer, Date, ForeignKey, DateTime, SmallInteger
from sqlalchemy.orm import relationship
from backend1.db.session import Base
import datetime

class QuanTri(Base):
    __tablename__ = "quan_tri"
    ma_qt = Column(String(10), primary_key=True)
    ho_ten = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    mat_khau = Column(String(255), nullable=False)
    
    thong_baos = relationship("ThongBao", back_populates="admin")
    pt_xet_tuyens = relationship("PT_XetTuyen", back_populates="admin")

class ThongBao(Base):
    __tablename__ = "thong_bao"
    ma_tb = Column(String(100), primary_key=True)
    tieu_de = Column(String(255))
    noi_dung = Column(String(1000), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    ma_qt = Column(String(10), ForeignKey("quan_tri.ma_qt"))
    gui_den = Column(String(20), default="all") # all, lop, nganh
    
    admin = relationship("QuanTri", back_populates="thong_baos")
    tb_nhans = relationship("TB_NguoiNhan", back_populates="thong_bao")

class TB_NguoiNhan(Base):
    __tablename__ = "tb_nguoi_nhan"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ma_tb = Column(String(100), ForeignKey("thong_bao.ma_tb"))
    ma_sv = Column(String(15), ForeignKey("sinh_vien.ma_sv"))
    da_doc = Column(SmallInteger, default=0) # 0: Chua doc, 1: Da doc
    thoi_gian_doc = Column(DateTime)
    
    thong_bao = relationship("ThongBao", back_populates="tb_nhans")
    sinh_vien = relationship("SinhVien", back_populates="tb_nhans")
